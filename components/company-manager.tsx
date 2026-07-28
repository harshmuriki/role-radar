"use client";

import { FormEvent, useEffect, useState } from "react";
import { ChevronDown, ChevronUp, Link2, LoaderCircle, Pencil, Plus, Trash2 } from "lucide-react";
import { supabase } from "@/lib/supabase";

type Filters = { title?: string[]; exclude_any?: string[]; location?: string[]; remote?: boolean };
type Company = { id: string; name: string; careers_url: string; ats_type: string | null; ats_slug: string | null; posted_within_days: number; role_filters: Filters };
const join = (items?: string[]) => (items ?? []).join(", ");
const split = (value: string) => value.split(",").map((item) => item.trim()).filter(Boolean);

export function CompanyManager() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [expanded, setExpanded] = useState(false);
  const [editing, setEditing] = useState<Company | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const [days, setDays] = useState("7");
  const [include, setInclude] = useState("");
  const [exclude, setExclude] = useState("");
  const [locations, setLocations] = useState("");
  const [remote, setRemote] = useState("any");
  const [atsType, setAtsType] = useState("");
  const [atsSlug, setAtsSlug] = useState("");

  async function loadCompanies() {
    const { data, error: loadError } = await supabase.from("role_radar_companies").select("id, name, careers_url, ats_type, ats_slug, posted_within_days, role_filters").eq("active", true).order("created_at");
    if (loadError) setError("Could not load your company list."); else setCompanies(data ?? []);
  }
  useEffect(() => { void loadCompanies(); }, []);

  function resetForm() { setName(""); setUrl(""); setDays("7"); setInclude(""); setExclude(""); setLocations(""); setRemote("any"); setAtsType(""); setAtsSlug(""); setEditing(null); }
  function openEditor(company?: Company) {
    setError(""); setExpanded(true);
    if (!company) { resetForm(); return; }
    setEditing(company); setName(company.name); setUrl(company.careers_url); setDays(String(company.posted_within_days)); setInclude(join(company.role_filters?.title)); setExclude(join(company.role_filters?.exclude_any)); setLocations(join(company.role_filters?.location)); setRemote(company.role_filters?.remote === true ? "remote" : company.role_filters?.remote === false ? "onsite" : "any"); setAtsType(company.ats_type ?? ""); setAtsSlug(company.ats_slug ?? "");
  }

  async function saveCompany(event: FormEvent) {
    event.preventDefault(); setError("");
    if ((atsType && !atsSlug) || (!atsType && atsSlug)) { setError("Add both the ATS platform and its company slug, or leave both blank for auto-detection."); return; }
    const role_filters: Filters = { title: split(include), exclude_any: split(exclude), location: split(locations) };
    if (remote !== "any") role_filters.remote = remote === "remote";
    const payload = { name: name.trim(), careers_url: url.trim(), posted_within_days: Number(days), ats_type: atsType.trim() || null, ats_slug: atsSlug.trim() || null, role_filters };
    setBusy(true);
    const { error: saveError } = editing ? await supabase.from("role_radar_companies").update(payload).eq("id", editing.id) : await supabase.from("role_radar_companies").insert(payload);
    setBusy(false);
    if (saveError) { setError(saveError.message.includes("unique") ? "That careers URL is already tracked." : saveError.message); return; }
    resetForm(); setExpanded(false); await loadCompanies();
  }

  async function removeCompany(id: string) { setBusy(true); setError(""); const { error: deleteError } = await supabase.from("role_radar_companies").delete().eq("id", id); setBusy(false); if (deleteError) { setError(deleteError.message); return; } await loadCompanies(); }

  return <aside className="control-panel company-manager">
    <div className="panel-heading"><div><p className="eyebrow">Company sources</p><h2>{companies.length} tracked {companies.length === 1 ? "company" : "companies"}</h2></div><Link2 size={20} /></div>
    <div className="company-list">{companies.map((company) => <div className="company-row" key={company.id}><div><strong>{company.name}</strong><span>{company.role_filters?.title?.length ? company.role_filters.title.join(", ") : "All roles"} · last {company.posted_within_days}d</span></div><div className="company-actions"><button className="edit-company" aria-label={`Edit ${company.name}`} onClick={() => openEditor(company)} disabled={busy}><Pencil size={14} /></button><button className="delete-company" aria-label={`Remove ${company.name}`} onClick={() => void removeCompany(company.id)} disabled={busy}><Trash2 size={14} /></button></div></div>)}</div>
    <button className="add-company-toggle" onClick={() => { if (expanded) { setExpanded(false); resetForm(); } else openEditor(); }}><Plus size={15} />Add careers site{expanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}</button>
    {expanded && <form className="company-form" onSubmit={saveCompany}>
      <p className="filter-intro">Use role keywords to focus each company on exactly the jobs you want.</p>
      <label>Company name<input required value={name} onChange={(event) => setName(event.target.value)} placeholder="Acme" /></label>
      <label>Careers URL<input required type="url" value={url} onChange={(event) => setUrl(event.target.value)} placeholder="https://jobs.example.com" /></label>
      <label>Target role keywords<input value={include} onChange={(event) => setInclude(event.target.value)} placeholder="software engineer, backend" /></label>
      <label>Exclude keywords<input value={exclude} onChange={(event) => setExclude(event.target.value)} placeholder="sales, intern" /></label>
      <label>Location keywords<input value={locations} onChange={(event) => setLocations(event.target.value)} placeholder="remote, san francisco" /></label>
      <label>Workplace<select value={remote} onChange={(event) => setRemote(event.target.value)}><option value="any">Any workplace</option><option value="remote">Remote only</option><option value="onsite">On-site / hybrid only</option></select></label>
      <label>Only roles posted within<input required type="number" min="0" max="90" value={days} onChange={(event) => setDays(event.target.value)} /><span>days</span></label>
      <details><summary>ATS override for custom domains</summary><p>Leave this blank for automatic detection. If a site is not recognized, enter its ATS name and company slug.</p><label>ATS platform<input value={atsType} onChange={(event) => setAtsType(event.target.value)} placeholder="greenhouse" /></label><label>Company slug<input value={atsSlug} onChange={(event) => setAtsSlug(event.target.value)} placeholder="acme" /></label></details>
      {error && <p className="company-error" role="alert">{error}</p>}
      <button className="primary-button" disabled={busy}>{busy ? <><LoaderCircle className="spin" size={15} />Saving…</> : editing ? "Save filters" : "Save company"}</button>
    </form>}
    {!expanded && error && <p className="company-error" role="alert">{error}</p>}
    <div className="local-note"><Link2 size={16} /><p>Filters are applied the next time you run the local scraper.</p></div>
  </aside>;
}
