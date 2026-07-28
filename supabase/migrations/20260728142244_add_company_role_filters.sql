alter table public.role_radar_companies
  add column role_filters jsonb not null default '{}'::jsonb
  check (jsonb_typeof(role_filters) = 'object');
