create table public.role_radar_allowed_emails (
  email text primary key check (email = lower(email)),
  created_at timestamptz not null default now()
);

insert into public.role_radar_allowed_emails (email)
values
  ('harshsuhith@gmail.com'),
  ('arshiya.chhabra3@gmail.com')
on conflict (email) do nothing;

alter table public.role_radar_allowed_emails enable row level security;

create or replace function public.role_radar_access_allowed()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.role_radar_allowed_emails
    where email = lower(coalesce(auth.jwt() ->> 'email', ''))
  );
$$;

revoke all on function public.role_radar_access_allowed() from public;
grant execute on function public.role_radar_access_allowed() to authenticated;

drop policy if exists "Users manage own companies" on public.role_radar_companies;
create policy "Allowed users manage own companies"
  on public.role_radar_companies for all to authenticated
  using ((select auth.uid()) = user_id and public.role_radar_access_allowed())
  with check ((select auth.uid()) = user_id and public.role_radar_access_allowed());

drop policy if exists "Users read own runs" on public.role_radar_runs;
create policy "Allowed users read own runs"
  on public.role_radar_runs for select to authenticated
  using ((select auth.uid()) = user_id and public.role_radar_access_allowed());

drop policy if exists "Users read own jobs" on public.role_radar_jobs;
create policy "Allowed users read own jobs"
  on public.role_radar_jobs for select to authenticated
  using ((select auth.uid()) = user_id and public.role_radar_access_allowed());

drop policy if exists "Users manage own tests" on public.role_radar_company_tests;
create policy "Allowed users manage own tests"
  on public.role_radar_company_tests for all to authenticated
  using ((select auth.uid()) = user_id and public.role_radar_access_allowed())
  with check ((select auth.uid()) = user_id and public.role_radar_access_allowed());

drop policy if exists "Users manage own scan requests" on public.role_radar_scan_requests;
create policy "Allowed users manage own scan requests"
  on public.role_radar_scan_requests for all to authenticated
  using ((select auth.uid()) = user_id and public.role_radar_access_allowed())
  with check ((select auth.uid()) = user_id and public.role_radar_access_allowed());
