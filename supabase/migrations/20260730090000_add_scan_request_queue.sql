create table public.role_radar_scan_requests (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  status text not null default 'queued' check (status in ('queued', 'running', 'completed', 'failed')),
  error text,
  requested_at timestamptz not null default now(),
  started_at timestamptz,
  completed_at timestamptz
);

alter table public.role_radar_scan_requests enable row level security;
grant select, insert on public.role_radar_scan_requests to authenticated;

create policy "Users manage own scan requests"
  on public.role_radar_scan_requests for all to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);
