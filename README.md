# Role Radar

Role Radar is a static Vercel dashboard for jobs generated locally with `ats-scrapers` and stored in Supabase. Add company career URLs to a JSON file, run one Python command on your laptop, and the frontend displays only roles matching your filters from the last N days.

## Architecture

- **Static Next.js frontend**: Vercel hosts the exported dashboard and reads the current job data directly from Supabase with a publishable key.
- **Local Python generator**: `generate_jobs.py` uses `ats-scrapers` to discover the ATS from each company career URL, scrape and normalize the listings, apply your filters, and publish the result to Supabase.
- **Workday dates**: a minimal `ats-scrapers` subclass retains Workday relative posting dates so last-N filtering stays accurate.

## Run locally

```bash
conda activate role-radar
pip install -r requirements.txt
export SUPABASE_SECRET_KEY="your-sb-secret-key"
python generate_jobs.py
npm install
npm run build
```

Edit `data/filters.json` to define what relevant means to you. The generator writes its local JSON snapshots and publishes the latest matching jobs to Supabase. The secret key is local-only and must never be committed.

## Add company careers sites

Sign into the dashboard, use **Add careers site**, and enter the company name plus its careers-page URL. The next local `generate_jobs.py` run reads that list from Supabase and uses `ats-scrapers` to detect and scrape supported ATS pages directly (including Workday, Greenhouse, Lever, Ashby, Workable, iCIMS, and more).

For a custom-domain careers page that cannot be detected from its URL, expand **ATS override** and add the platform name and company slug. Unsupported sites are reported clearly in the local run output instead of being silently ignored.

## Private access

The dashboard uses Supabase Auth. Sign up on the site, then grant that account access from your laptop:

```bash
export SUPABASE_SECRET_KEY="your-sb-secret-key"
conda run -n role-radar python grant_access.py your-email@example.com
```

Only users added to `role_radar_admins` can read runs or jobs.

## Deploy

Import the repository into Vercel as a static Next.js project. The public Supabase URL and publishable key are configured for this project; no Vercel Functions are required.

## Conda environment

The local environment is named `role-radar`. Recreate it on another machine with `conda env create -f environment.yml`.
