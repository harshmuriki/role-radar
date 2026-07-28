"""Generate static job data from company career URLs with ats-scrapers.

Run this locally on a schedule. It reads data/companies.json and data/filters.json,
then writes the frontend-ready public/jobs.json and public/pipeline.json files.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ats_scrapers import get_scraper_for_url
from ats_scrapers.models import Job
from ats_scrapers.scrapers import get_scraper
from ats_scrapers.scrapers.workday import WorkdayScraper
from supabase import Client, create_client

ROOT = Path(__file__).parent
DEFAULT_COMPANIES = ROOT / "data" / "companies.json"
DEFAULT_FILTERS = ROOT / "data" / "filters.json"
DEFAULT_OUTPUT = ROOT / "public" / "jobs.json"
DEFAULT_PIPELINE = ROOT / "public" / "pipeline.json"
DEFAULT_SUPABASE_URL = "https://xcijdgzgecnizcwskzcb.supabase.co"
LOCALE_PATH = re.compile(r"^(https://[^/]+\.myworkdayjobs\.com)/(?:[a-z]{2}(?:-[A-Z]{2})?)/([^/?#]+)", re.I)
WORKDAY_URL = re.compile(r"^https://[^.]+\.wd\d+\.myworkdayjobs\.com/", re.I)
POSTED_DAYS = re.compile(r"posted\s+(\d+)\+?\s+days?\s+ago", re.I)


class RoleRadarWorkdayScraper(WorkdayScraper):
    """Keep the Workday relative posting date exposed by ats-scrapers' listing API.

    The upstream adapter deliberately leaves `posted_at` empty because Workday
    supplies a relative string. Storing that string in `raw` lets this app apply
    an accurate last-N-days filter while still using the upstream adapter to
    fetch and normalize every job.
    """

    def _parse_job(self, item: dict[str, Any], base_url: str, company: str) -> Job:
        job = super()._parse_job(item, base_url, company)
        raw = dict(job.raw or {})
        raw["role_radar_posted_on"] = item.get("postedOn") or ""
        return job.model_copy(update={"raw": raw})


def load_local_env() -> None:
    """Load this project's ignored local .env file without another dependency."""
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        key, separator, value = line.partition("=")
        if separator and key and not key.lstrip().startswith("#"):
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def normalize_url(url: str) -> str:
    match = LOCALE_PATH.match(url.rstrip("/"))
    return f"{match.group(1)}/{match.group(2)}" if match else url.rstrip("/")


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [part.strip() for part in str(value).split(",") if part.strip()]


def contains_any(value: object, keywords: list[str]) -> bool:
    text = str(value or "").lower()
    return not keywords or any(keyword.lower() in text for keyword in keywords)


def contains_all(value: object, keywords: list[str]) -> bool:
    text = str(value or "").lower()
    return not keywords or all(keyword.lower() in text for keyword in keywords)


def relative_days(value: object) -> int | None:
    text = str(value or "")
    if re.search(r"posted\s+today", text, re.I):
        return 0
    if re.search(r"posted\s+yesterday", text, re.I):
        return 1
    match = POSTED_DAYS.search(text)
    if not match:
        return None
    return int(match.group(1)) + (1 if "+" in text else 0)


def age_in_days(job: Job) -> int | None:
    if job.posted_at:
        posted = job.posted_at if job.posted_at.tzinfo else job.posted_at.replace(tzinfo=UTC)
        return max(0, (datetime.now(UTC) - posted).days)
    return relative_days((job.raw or {}).get("role_radar_posted_on"))


def job_matches(job: Job, filters: dict[str, Any]) -> bool:
    title = job.title or ""
    description = job.description or ""
    department = job.department or ""
    if not contains_any(title, as_list(filters.get("title"))):
        return False
    if not contains_all(title, as_list(filters.get("title_all"))):
        return False
    if not contains_any(job.location, as_list(filters.get("location"))):
        return False
    if not contains_any(job.company, as_list(filters.get("company"))):
        return False
    role = as_list(filters.get("role") or filters.get("department"))
    if role and not contains_any(f"{department} {title}", role):
        return False
    if not contains_any(job.employment_type, as_list(filters.get("employment_type"))):
        return False
    if not contains_any(job.requisition_id, as_list(filters.get("requisition_id"))):
        return False
    if not contains_any(description, as_list(filters.get("description"))):
        return False
    if not contains_all(description, as_list(filters.get("description_all"))):
        return False
    excluded = as_list(filters.get("exclude_any"))
    if excluded and contains_any(f"{title} {department} {description}", excluded):
        return False
    if filters.get("remote") is True and job.is_remote is not True:
        return False
    if filters.get("remote") is False and job.is_remote is True:
        return False
    if filters.get("posted_within_days") is not None:
        days = age_in_days(job)
        if days is None or days > int(filters["posted_within_days"]):
            return False
    return True


def load_companies(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data if isinstance(data, list) else data.get("links", data.get("companies", []))
    companies: list[dict[str, Any]] = []
    for row in rows:
        if isinstance(row, str):
            companies.append({"name": "", "url": row, "posted_within_days": None})
        elif isinstance(row, dict) and row.get("url"):
            companies.append({
                "name": str(row.get("name") or ""),
                "url": str(row["url"]),
                "posted_within_days": row.get("posted_within_days"),
                "ats_type": row.get("ats_type"),
                "ats_slug": row.get("ats_slug"),
            })
    if not companies:
        raise ValueError(f"No company links found in {path}")
    return companies


def load_supabase_companies() -> list[dict[str, Any]]:
    """Read the editable company list from Supabase using the local secret key."""
    secret_key = os.getenv("SUPABASE_SECRET_KEY")
    if not secret_key:
        return []
    client: Client = create_client(os.getenv("SUPABASE_URL", DEFAULT_SUPABASE_URL), secret_key)
    response = (
        client.table("role_radar_companies")
        .select("name, careers_url, ats_type, ats_slug, posted_within_days, role_filters")
        .eq("active", True)
        .order("created_at")
        .execute()
    )
    return [
        {
            "name": row["name"],
            "url": row["careers_url"],
            "ats_type": row.get("ats_type"),
            "ats_slug": row.get("ats_slug"),
            "posted_within_days": row.get("posted_within_days"),
            "role_filters": row.get("role_filters") or {},
        }
        for row in response.data
    ]


def scraper_for(url: str, company_name: str, needs_description: bool, ats_type: str | None = None, ats_slug: str | None = None):
    normalized = normalize_url(url)
    options = {"company_name": company_name or None, "include_descriptions": needs_description}
    if ats_type and ats_slug:
        return get_scraper(ats_type, ats_slug, **options)
    if WORKDAY_URL.match(normalized):
        return RoleRadarWorkdayScraper.from_url(normalized, **options)
    return get_scraper_for_url(normalized, **options)


def serialise_job(job: Job, company_name: str) -> dict[str, Any]:
    raw = job.raw or {}
    return {
        "id": str(job.global_id or job.url),
        "title": str(job.title or "Untitled"),
        "company": company_name or str(job.company or ""),
        "ats": str(job.ats_type),
        "location": str(job.location) if job.location else None,
        "remote": job.is_remote,
        "employmentType": job.employment_type or job.commitment,
        "department": job.department or job.team,
        "postedAt": job.posted_at.isoformat() if job.posted_at else None,
        "postedText": raw.get("role_radar_posted_on") or None,
        "postedDaysAgo": age_in_days(job),
        "url": str(job.apply_url or job.url),
        "requisitionId": str(job.requisition_id) if job.requisition_id else None,
        "description": job.description,
    }


def publish_to_supabase(
    jobs: list[dict[str, Any]], *, source_count: int, fetched_count: int
) -> None:
    """Publish one complete scan; only the latest run is visible to the dashboard."""
    secret_key = os.getenv("SUPABASE_SECRET_KEY")
    if not secret_key:
        raise RuntimeError(
            "SUPABASE_SECRET_KEY is required to publish jobs. "
            "Add it to your local environment; never commit it or expose it to Vercel."
        )
    client: Client = create_client(os.getenv("SUPABASE_URL", DEFAULT_SUPABASE_URL), secret_key)
    run = (
        client.table("role_radar_runs")
        .insert(
            {
                "source_count": source_count,
                "fetched_count": fetched_count,
                "matched_count": len(jobs),
            }
        )
        .execute()
    )
    run_id = run.data[0]["id"]
    rows = [
        {
            "id": job["id"],
            "last_seen_run_id": run_id,
            "title": job["title"],
            "company": job["company"],
            "ats": job["ats"],
            "location": job["location"],
            "remote": job["remote"],
            "employment_type": job["employmentType"],
            "department": job["department"],
            "posted_at": job["postedAt"],
            "posted_text": job["postedText"],
            "posted_days_ago": job["postedDaysAgo"],
            "url": job["url"],
            "requisition_id": job["requisitionId"],
            "description": job["description"],
            "updated_at": datetime.now(UTC).isoformat(),
        }
        for job in jobs
    ]
    if rows:
        client.table("role_radar_jobs").upsert(rows, on_conflict="id").execute()
    client.table("role_radar_jobs").delete().neq("last_seen_run_id", run_id).execute()
    print(f"Published scan {run_id} to Supabase.")


def process_queued_tests() -> None:
    secret_key = os.getenv("SUPABASE_SECRET_KEY")
    if not secret_key:
        return
    client: Client = create_client(os.getenv("SUPABASE_URL", DEFAULT_SUPABASE_URL), secret_key)
    tests = client.table("role_radar_company_tests").select("id, company_id, role_radar_companies(name, careers_url, ats_type, ats_slug)").eq("status", "queued").execute().data
    for test in tests:
        source = test["role_radar_companies"]
        try:
            jobs = scraper_for(source["careers_url"], source["name"], False, source.get("ats_type"), source.get("ats_slug")).fetch()
            sample = [{"title": job.title, "location": job.location} for job in jobs[:5]]
            client.table("role_radar_company_tests").update({"status": "passed", "fetched_count": len(jobs), "sample_jobs": sample, "tested_at": datetime.now(UTC).isoformat()}).eq("id", test["id"]).execute()
            print(f"Test passed for {source['name']}: {len(jobs)} jobs")
        except Exception as exc:
            client.table("role_radar_company_tests").update({"status": "failed", "error": str(exc), "tested_at": datetime.now(UTC).isoformat()}).eq("id", test["id"]).execute()
            print(f"Test failed for {source['name']}: {exc}")


def main() -> None:
    load_local_env()
    parser = argparse.ArgumentParser(description="Generate and publish Role Radar jobs with ats-scrapers.")
    parser.add_argument("--companies", type=Path, default=DEFAULT_COMPANIES)
    parser.add_argument("--filters", type=Path, default=DEFAULT_FILTERS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--pipeline-output", type=Path, default=DEFAULT_PIPELINE)
    parser.add_argument("--skip-upload", action="store_true", help="Create local JSON snapshots without publishing to Supabase.")
    parser.add_argument("--test-company", help="Fetch one careers URL and print a sample without writing or publishing anything.")
    parser.add_argument("--test-name", default="Test company", help="Display name used with --test-company.")
    parser.add_argument("--test-ats", help="Optional ats-scrapers platform override for --test-company.")
    parser.add_argument("--test-slug", help="Optional company slug for --test-ats.")
    parser.add_argument("--test-limit", type=int, default=8, help="Maximum sample roles to show during a company test.")
    args = parser.parse_args()

    process_queued_tests()

    if args.test_company:
        if bool(args.test_ats) != bool(args.test_slug):
            parser.error("--test-ats and --test-slug must be provided together.")
        print(f"Testing {args.test_name}: {args.test_company}")
        try:
            jobs = scraper_for(args.test_company, args.test_name, False, args.test_ats, args.test_slug).fetch()
        except Exception as exc:
            print(f"TEST FAILED: {exc}")
            raise SystemExit(1) from exc
        print(f"TEST PASSED: detected {jobs[0].ats_type if jobs else 'ATS'} and fetched {len(jobs)} jobs.")
        for job in jobs[:max(0, args.test_limit)]:
            print(f"- {job.title or 'Untitled'} | {job.location or 'Location not listed'}")
        return

    companies_config = json.loads(args.companies.read_text(encoding="utf-8"))
    companies = load_supabase_companies() or load_companies(args.companies)
    filters = json.loads(args.filters.read_text(encoding="utf-8"))
    if filters.get("posted_within_days") is None and isinstance(companies_config, dict):
        filters["posted_within_days"] = companies_config.get("posted_within_days", 7)
    needs_description = bool(as_list(filters.get("description")) or as_list(filters.get("description_all")))
    all_jobs: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    fetched = 0

    for index, company in enumerate(companies, start=1):
        name, url = company["name"].strip(), company["url"].strip()
        print(f"[{index}/{len(companies)}] {name or url}")
        try:
            jobs = scraper_for(
                url,
                name,
                needs_description,
                company.get("ats_type"),
                company.get("ats_slug"),
            ).fetch()
            fetched += len(jobs)
            company_filters = dict(filters)
            if company.get("posted_within_days") is not None:
                company_filters["posted_within_days"] = company["posted_within_days"]
            for key, value in (company.get("role_filters") or {}).items():
                if value not in (None, [], ""):
                    company_filters[key] = value
            matches = [serialise_job(job, name) for job in jobs if job_matches(job, company_filters)]
            all_jobs.extend(matches)
            print(f"  {len(matches)} relevant / {len(jobs)} fetched")
        except Exception as exc:
            failures.append({"company": name or url, "error": str(exc)})
            print(f"  ERROR: {exc}")

    all_jobs.sort(key=lambda job: (job["postedDaysAgo"] is None, job["postedDaysAgo"] or 9999, job["title"] or ""))
    generated_at = datetime.now(UTC).isoformat()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"generatedAt": generated_at, "filters": filters, "fetched": fetched, "jobs": all_jobs, "failures": failures}, indent=2, default=str), encoding="utf-8")
    args.pipeline_output.parent.mkdir(parents=True, exist_ok=True)
    args.pipeline_output.write_text(json.dumps({"generatedAt": generated_at, "companies": companies}, indent=2), encoding="utf-8")
    print(f"Wrote {len(all_jobs)} matching jobs to {args.output}")
    if not args.skip_upload:
        publish_to_supabase(all_jobs, source_count=len(companies), fetched_count=fetched)


if __name__ == "__main__":
    main()
