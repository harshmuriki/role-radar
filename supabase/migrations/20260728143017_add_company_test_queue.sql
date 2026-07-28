create table public.role_radar_company_tests (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.role_radar_companies(id) on delete cascade,
  status text not null default 'queued' check (status in ('queued', 'passed', 'failed')),
  fetched_count integer,
  sample_jobs jsonb,
  error text,
  requested_at timestamptz not null default now(),
  tested_at timestamptz
);
alter table public.role_radar_company_tests enable row level security;
grant select, insert on public.role_radar_company_tests to authenticated;
create policy "Admins can read source tests" on public.role_radar_company_tests for select to authenticated using (exists (select 1 from public.role_radar_admins where user_id = (select auth.uid())));
create policy "Admins can request source tests" on public.role_radar_company_tests for insert to authenticated with check (exists (select 1 from public.role_radar_admins where user_id = (select auth.uid())));
