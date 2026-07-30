# Run a Role Radar local worker

Use this guide on each account's computer. One Docker worker serves one signed-in Role Radar account and never exposes the computer to the internet.

## 1. Get the code

```bash
git clone https://github.com/harshmuriki/role-radar.git
cd role-radar
```

Install and open Docker Desktop before continuing.

## 2. Create local secrets

```bash
cp .env.example .env
```

Edit `.env` and set these values:

```bash
SUPABASE_SECRET_KEY=sb_secret_your_project_secret
ROLE_RADAR_USER_EMAIL=the-email-used-to-sign-in@example.com
```

Never commit `.env`. The secret key stays only on this computer.

## 3. Start the always-on worker

```bash
docker compose -p role-radar up -d --build
```

The worker polls Supabase every three seconds. Clicking **Run scan now** in the Vercel dashboard triggers an immediate full scrape and publish for this account. The test-tube button next to a company similarly runs an immediate source test. This worker performs both operations and writes the results back.

## 4. Check or stop it

```bash
docker compose -p role-radar ps
docker compose -p role-radar logs -f
docker compose -p role-radar down
```

## Run a full scan manually

The worker handles test requests. To publish the latest jobs for this account, run:

```bash
docker compose -p role-radar exec role-radar-worker python generate_jobs.py
```

Each worker is scoped to `ROLE_RADAR_USER_EMAIL`, so accounts cannot process or view one another's company sources, tests, scans, or jobs.
