create table public.role_radar_companies (
  id uuid primary key default gen_random_uuid(),
  name text not null check (char_length(trim(name)) > 0),
  careers_url text not null unique check (careers_url ~* '^https?://'),
  ats_type text,
  ats_slug text,
  posted_within_days smallint not null default 7 check (posted_within_days between 0 and 90),
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check ((ats_type is null and ats_slug is null) or (ats_type is not null and ats_slug is not null))
);

create index role_radar_companies_active_idx
  on public.role_radar_companies (active, created_at desc);

alter table public.role_radar_companies enable row level security;

grant select, insert, update, delete on table public.role_radar_companies to authenticated;

create policy "Role Radar admins can read companies"
  on public.role_radar_companies for select to authenticated
  using (exists (select 1 from public.role_radar_admins where user_id = (select auth.uid())));

create policy "Role Radar admins can add companies"
  on public.role_radar_companies for insert to authenticated
  with check (exists (select 1 from public.role_radar_admins where user_id = (select auth.uid())));

create policy "Role Radar admins can update companies"
  on public.role_radar_companies for update to authenticated
  using (exists (select 1 from public.role_radar_admins where user_id = (select auth.uid())))
  with check (exists (select 1 from public.role_radar_admins where user_id = (select auth.uid())));

create policy "Role Radar admins can delete companies"
  on public.role_radar_companies for delete to authenticated
  using (exists (select 1 from public.role_radar_admins where user_id = (select auth.uid())));

insert into public.role_radar_companies (name, careers_url, posted_within_days)
values ('Owens & Minor', 'https://owensminor.wd1.myworkdayjobs.com/en-US/OMCareers', 7)
on conflict (careers_url) do nothing;
