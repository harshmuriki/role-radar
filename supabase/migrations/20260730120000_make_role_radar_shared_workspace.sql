-- Convert the allowlisted accounts to one shared Role Radar workspace.
-- Existing rows retain their user_id as provenance, but all allowed users can use them.

drop policy if exists "Allowed users manage own companies" on public.role_radar_companies;
create policy "Allowed users manage shared companies"
  on public.role_radar_companies for all to authenticated
  using (public.role_radar_access_allowed())
  with check (public.role_radar_access_allowed());

drop policy if exists "Allowed users read own runs" on public.role_radar_runs;
create policy "Allowed users read shared runs"
  on public.role_radar_runs for select to authenticated
  using (public.role_radar_access_allowed());

drop policy if exists "Allowed users read own jobs" on public.role_radar_jobs;
create policy "Allowed users read shared jobs"
  on public.role_radar_jobs for select to authenticated
  using (public.role_radar_access_allowed());

drop policy if exists "Allowed users manage own tests" on public.role_radar_company_tests;
create policy "Allowed users manage shared tests"
  on public.role_radar_company_tests for all to authenticated
  using (public.role_radar_access_allowed())
  with check (public.role_radar_access_allowed());

drop policy if exists "Allowed users manage own scan requests" on public.role_radar_scan_requests;
create policy "Allowed users manage shared scan requests"
  on public.role_radar_scan_requests for all to authenticated
  using (public.role_radar_access_allowed())
  with check (public.role_radar_access_allowed());
