create table public.role_radar_runs (
  id uuid primary key default gen_random_uuid(),
  generated_at timestamptz not null default now(),
  source_count integer not null check (source_count >= 0),
  fetched_count integer not null check (fetched_count >= 0),
  matched_count integer not null check (matched_count >= 0)
);

create table public.role_radar_jobs (
  id text primary key,
  last_seen_run_id uuid not null references public.role_radar_runs(id) on delete cascade,
  title text not null,
  company text not null,
  ats text not null,
  location text,
  remote boolean,
  employment_type text,
  department text,
  posted_at timestamptz,
  posted_text text,
  posted_days_ago integer check (posted_days_ago >= 0),
  url text not null,
  requisition_id text,
  description text,
  updated_at timestamptz not null default now()
);

create index role_radar_jobs_active_posted_idx
  on public.role_radar_jobs (last_seen_run_id, posted_days_ago, title);

create index role_radar_runs_generated_at_idx
  on public.role_radar_runs (generated_at desc);

alter table public.role_radar_runs enable row level security;
alter table public.role_radar_jobs enable row level security;

grant select on table public.role_radar_runs to anon;
grant select on table public.role_radar_jobs to anon;

create policy "Published runs are publicly readable"
  on public.role_radar_runs for select to anon using (true);

create policy "Published jobs are publicly readable"
  on public.role_radar_jobs for select to anon using (true);
