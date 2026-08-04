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

## 5. Configure and schedule the daily email

Add these server-only values to `.env`. `EMAIL_FROM` must be a verified sender in Brevo:

```bash
BREVO_API_KEY=xkeysib-your-brevo-api-key
EMAIL_TO=your-recipient@example.com
EMAIL_FROM=verified-sender@yourdomain.com
EMAIL_FROM_NAME=Role Radar
EMAIL_TIMEZONE=America/Los_Angeles
EMAIL_STATE_FILE=/var/lib/role-radar/email-state.json
```

For the two private accounts, use one environment file per worker so each
person receives only their own filtered roles:

| Worker | `ROLE_RADAR_USER_EMAIL` | `EMAIL_TO` | `EMAIL_STATE_FILE` |
| --- | --- | --- | --- |
| Harsh | `harshsuhith@gmail.com` | `harshsuhith@gmail.com` | `/var/lib/role-radar/harsh-email-state.json` |
| Arshiya | `arshiya.chhabra3@gmail.com` | `arshiya.chhabra3@gmail.com` | `/var/lib/role-radar/arshiya-email-state.json` |

Copy `.env.example` to `.env`, then create `.env.harsh` and `.env.arshiya`
with the account-specific values. The profile files are ignored by Git and
inherit the shared Supabase settings from `.env`. Set `EMAIL_FROM` in both to
the same sender address verified in Brevo. Start them as separate Compose projects:

```bash
ROLE_RADAR_ENV_FILE=.env.harsh docker compose -p role-radar-harsh up -d --build
ROLE_RADAR_ENV_FILE=.env.arshiya docker compose -p role-radar-arshiya up -d --build
```

Test without sending or changing delivery state:

```bash
docker compose -p role-radar run --rm role-radar-worker python send_daily_digest.py --dry-run
```

Send a real one-time test digest containing all currently filtered jobs:

```bash
docker compose -p role-radar run --rm role-radar-worker python send_daily_digest.py --all
```

Run it daily from the server's crontab (this example sends at 8:00 AM server time):

```cron
0 8 * * * cd /opt/role-radar && ROLE_RADAR_ENV_FILE=.env.harsh docker compose -p role-radar-harsh run --rm role-radar-worker python send_daily_digest.py >> /var/log/role-radar-harsh-digest.log 2>&1
0 8 * * * cd /opt/role-radar && ROLE_RADAR_ENV_FILE=.env.arshiya docker compose -p role-radar-arshiya run --rm role-radar-worker python send_daily_digest.py >> /var/log/role-radar-arshiya-digest.log 2>&1
```

By default, each job is included only once. The Compose volume keeps delivery state on the server at `.role-radar-state/`. Remove that directory only if you intentionally want to rebuild the sent-job history.
