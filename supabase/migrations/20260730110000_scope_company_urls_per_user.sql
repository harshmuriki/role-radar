alter table public.role_radar_companies
  drop constraint if exists role_radar_companies_careers_url_key;

alter table public.role_radar_companies
  add constraint role_radar_companies_user_id_careers_url_key
  unique (user_id, careers_url);
