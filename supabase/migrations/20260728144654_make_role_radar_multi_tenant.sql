alter table public.role_radar_companies add column user_id uuid references auth.users(id);
alter table public.role_radar_runs add column user_id uuid references auth.users(id);
alter table public.role_radar_jobs add column user_id uuid references auth.users(id);
alter table public.role_radar_company_tests add column user_id uuid references auth.users(id);

update public.role_radar_companies set user_id = (select user_id from public.role_radar_admins limit 1) where user_id is null;
update public.role_radar_runs set user_id = (select user_id from public.role_radar_admins limit 1) where user_id is null;
update public.role_radar_jobs set user_id = (select user_id from public.role_radar_admins limit 1) where user_id is null;
update public.role_radar_company_tests set user_id = (select user_id from public.role_radar_admins limit 1) where user_id is null;

alter table public.role_radar_companies alter column user_id set not null;
alter table public.role_radar_runs alter column user_id set not null;
alter table public.role_radar_jobs alter column user_id set not null;
alter table public.role_radar_company_tests alter column user_id set not null;
alter table public.role_radar_companies alter column user_id set default auth.uid();
alter table public.role_radar_company_tests alter column user_id set default auth.uid();

drop policy "Role Radar admins can read companies" on public.role_radar_companies;
drop policy "Role Radar admins can add companies" on public.role_radar_companies;
drop policy "Role Radar admins can update companies" on public.role_radar_companies;
drop policy "Role Radar admins can delete companies" on public.role_radar_companies;
drop policy "Role Radar admins can read runs" on public.role_radar_runs;
drop policy "Role Radar admins can read jobs" on public.role_radar_jobs;
drop policy "Admins can read source tests" on public.role_radar_company_tests;
drop policy "Admins can request source tests" on public.role_radar_company_tests;

create policy "Users manage own companies" on public.role_radar_companies for all to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "Users read own runs" on public.role_radar_runs for select to authenticated using ((select auth.uid()) = user_id);
create policy "Users read own jobs" on public.role_radar_jobs for select to authenticated using ((select auth.uid()) = user_id);
create policy "Users manage own tests" on public.role_radar_company_tests for all to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
