# Role Radar

Role Radar is a static Vercel dashboard for jobs generated locally with `ats-scrapers`. Add company career URLs to a JSON file, run one Python command on your laptop, and the frontend displays only roles matching your filters from the last N days.

## Architecture

- **Static Next.js frontend**: Vercel hosts the exported dashboard. It does not run scraping code or backend functions.
- **Local Python generator**: `generate_jobs.py` uses `ats-scrapers` to discover the ATS from each company career URL, scrape and normalize the listings, apply your filters, and write static JSON.
- **Workday dates**: a minimal `ats-scrapers` subclass retains Workday relative posting dates so last-N filtering stays accurate.

## Run locally

```bash
conda activate role-radar
pip install -r requirements.txt
python generate_jobs.py
npm install
npm run build
```

Edit `data/companies.json` to add a company careers link. Edit `data/filters.json` to define what relevant means to you. The generator writes `public/jobs.json` and `public/pipeline.json`; commit/push those files when you want Vercel to update.

## Deploy

Import the repository into Vercel as a static Next.js project. No environment variables or Vercel Functions are required.

## Conda environment

The local environment is named `role-radar`. Recreate it on another machine with `conda env create -f environment.yml`.
