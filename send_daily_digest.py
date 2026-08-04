"""Send the newest filtered Role Radar jobs through Brevo."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from generate_jobs import DEFAULT_SUPABASE_URL, load_local_env, worker_user_id
from supabase import Client, create_client

ROOT = Path(__file__).parent
DEFAULT_STATE_FILE = ROOT / ".role-radar-email-state.json"
BREVO_SEND_URL = "https://api.brevo.com/v3/smtp/email"


def env_required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required.")
    return value


def recipients() -> list[str]:
    values = [item.strip() for item in env_required("EMAIL_TO").split(",")]
    if any("@" not in item for item in values):
        raise RuntimeError("EMAIL_TO must contain comma-separated email addresses.")
    return values


def state_path() -> Path:
    return Path(os.getenv("EMAIL_STATE_FILE", str(DEFAULT_STATE_FILE))).expanduser()


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"sent_job_ids": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Cannot read email state file {path}: {exc}") from exc
    return data if isinstance(data, dict) else {"sent_job_ids": []}


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_jobs(client: Client, user_id: str) -> list[dict[str, Any]]:
    response = (
        client.table("role_radar_jobs")
        .select(
            "id, title, company, location, remote, employment_type, department, "
            "posted_at, posted_text, posted_days_ago, url"
        )
        .eq("user_id", user_id)
        .order("posted_days_ago", desc=False)
        .order("company", desc=False)
        .order("title", desc=False)
        .execute()
    )
    return response.data or []


def format_posted(job: dict[str, Any]) -> str:
    if job.get("posted_text"):
        return str(job["posted_text"])
    if job.get("posted_days_ago") == 0:
        return "Posted today"
    if job.get("posted_days_ago") is not None:
        return f"Posted {job['posted_days_ago']} days ago"
    if job.get("posted_at"):
        return str(job["posted_at"])[:10]
    return "Posting date not listed"


def job_location(job: dict[str, Any]) -> str:
    location = str(job.get("location") or "Location not listed")
    if job.get("remote") is True and "remote" not in location.lower():
        location += " · Remote"
    return location


def build_subject(jobs: list[dict[str, Any]], now: datetime) -> str:
    plural = "s" if len(jobs) != 1 else ""
    return f"Role Radar: {len(jobs)} new filtered role{plural} · {now.strftime('%b %-d')}"


def build_bodies(jobs: list[dict[str, Any]], now: datetime) -> tuple[str, str]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for job in jobs:
        grouped.setdefault(str(job.get("company") or "Other"), []).append(job)

    plural = "s" if len(jobs) != 1 else ""
    text_lines = [f"Role Radar — {len(jobs)} new filtered role{plural}", now.strftime("%B %-d, %Y"), ""]
    html_parts = [
        '<div style="font-family:Arial,sans-serif;max-width:720px;color:#172033">',
        f'<h1>Role Radar</h1><p>{len(jobs)} new filtered role{plural} · {html.escape(now.strftime("%B %-d, %Y"))}</p>',
    ]
    for company, company_jobs in grouped.items():
        html_parts.append(f"<h2>{html.escape(company)}</h2><ul>")
        text_lines.append(company)
        for job in company_jobs:
            title = str(job.get("title") or "Untitled")
            location = job_location(job)
            posted = format_posted(job)
            url = str(job.get("url") or "")
            html_parts.append(
                "<li style=\"margin:0 0 14px\"><a href=\""
                f"{html.escape(url, quote=True)}\"><strong>{html.escape(title)}</strong></a>"
                f"<br><span>{html.escape(location)} · {html.escape(posted)}</span></li>"
            )
            text_lines.extend([f"- {title}", f"  {location} · {posted}", f"  {url}"])
        html_parts.append("</ul>")
        text_lines.append("")
    html_parts.append('<p style="color:#667085">Generated from your current Role Radar filters.</p></div>')
    return "\n".join(text_lines), "".join(html_parts)


def send_with_brevo(subject: str, text_content: str, html_content: str) -> str:
    payload = {
        "sender": {"email": env_required("EMAIL_FROM"), "name": os.getenv("EMAIL_FROM_NAME", "Role Radar")},
        "to": [{"email": address} for address in recipients()],
        "subject": subject,
        "textContent": text_content,
        "htmlContent": html_content,
    }
    request = Request(
        os.getenv("BREVO_SEND_URL", BREVO_SEND_URL),
        data=json.dumps(payload).encode("utf-8"),
        headers={"accept": "application/json", "api-key": env_required("BREVO_API_KEY"), "content-type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Brevo rejected the email ({exc.code}): {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Could not reach Brevo: {exc.reason}") from exc
    return str(result.get("messageId") or "unknown")


def digest_jobs(jobs: list[dict[str, Any]], state: dict[str, Any]) -> list[dict[str, Any]]:
    sent = {str(item) for item in state.get("sent_job_ids", [])}
    return [job for job in jobs if str(job.get("id")) not in sent]


def main() -> int:
    load_local_env()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print the digest without sending or changing state.")
    parser.add_argument("--all", action="store_true", help="Include all currently filtered jobs, even previously sent ones.")
    args = parser.parse_args()

    secret_key = env_required("SUPABASE_SECRET_KEY")
    client: Client = create_client(os.getenv("SUPABASE_URL", DEFAULT_SUPABASE_URL), secret_key)
    user_id = worker_user_id(client)
    jobs = load_jobs(client, user_id)
    path = state_path()
    state = load_state(path)
    selected = jobs if args.all else digest_jobs(jobs, state)
    if not selected:
        print("No new filtered roles; no email sent.")
        return 0

    timezone = ZoneInfo(os.getenv("EMAIL_TIMEZONE", "UTC"))
    now = datetime.now(timezone)
    subject = build_subject(selected, now)
    text_content, html_content = build_bodies(selected, now)
    print(f"Digest has {len(selected)} role(s): {subject}")
    if args.dry_run:
        print(text_content)
        return 0

    message_id = send_with_brevo(subject, text_content, html_content)
    sent_ids = {str(item) for item in state.get("sent_job_ids", [])}
    sent_ids.update(str(job["id"]) for job in selected)
    state.update({
        "last_sent_at": datetime.now(UTC).isoformat(),
        "last_message_id": message_id,
        "last_job_count": len(selected),
        "last_job_ids_hash": hashlib.sha256(",".join(sorted(sent_ids)).encode()).hexdigest(),
        "sent_job_ids": sorted(sent_ids),
    })
    save_state(path, state)
    print(f"Sent Brevo message {message_id} to {len(recipients())} recipient(s).")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, ValueError, KeyError) as exc:
        print(f"Digest failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
