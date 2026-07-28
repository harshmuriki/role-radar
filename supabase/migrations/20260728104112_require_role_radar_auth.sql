create table public.role_radar_admins (
  user_id uuid primary key references auth.users(id) on delete cascade,
  created_at timestamptz not null default now()
);

alter table public.role_radar_admins enable row level security;

grant select on table public.role_radar_admins to authenticated;
grant select on table public.role_radar_runs to authenticated;
grant select on table public.role_radar_jobs to authenticated;
revoke select on table public.role_radar_runs from anon;
revoke select on table public.role_radar_jobs from anon;

drop policy "Published runs are publicly readable" on public.role_radar_runs;
drop policy "Published jobs are publicly readable" on public.role_radar_jobs;

create policy "Users can see their own access"
  on public.role_radar_admins for select to authenticated
  using ((select auth.uid()) = user_id);

create policy "Role Radar admins can read runs"
  on public.role_radar_runs for select to authenticated
  using (exists (select 1 from public.role_radar_admins where user_id = (select auth.uid())));

create policy "Role Radar admins can read jobs"
  on public.role_radar_jobs for select to authenticated
  using (exists (select 1 from public.role_radar_admins where user_id = (select auth.uid())));
