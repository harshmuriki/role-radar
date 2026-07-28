"use client";

import { FormEvent, useEffect, useState } from "react";
import { ChevronDown, ChevronUp, Link2, LoaderCircle, Plus, Trash2 } from "lucide-react";
import { supabase } from "@/lib/supabase";

type Company = { id: string; name: string; careers_url: string; ats_type: string | null; ats_slug: string | null; posted_within_days: number };

export function CompanyManager() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [expanded, setExpanded] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const [days, setDays] = useState("7");
  const [atsType, setAtsType] = useState("");
  const [atsSlug, setAtsSlug] = useState("");

  async function loadCompanies() {
    const { data, error: loadError } = await supabase
      .from("role_radar_companies")
      .select("id, name, careers_url, ats_type, ats_slug, posted_within_days")
      .eq("active", true)
      .order("created_at");
    if (loadError) setError("Could not load your company list.");
    else setCompanies(data ?? []);
  }

  useEffect(() => { void loadCompanies(); }, []);

  async function addCompany(event: FormEvent) {
    event.preventDefault();
    setError("");
    if ((atsType && !atsSlug) || (!atsType && atsSlug)) {
      setError("Add both the ATS platform and its company slug, or leave both blank for auto-detection.");
      return;
    }
    setBusy(true);
    const { error: insertError } = await supabase.from("role_radar_companies").insert({
      name: name.trim(),
      careers_url: url.trim(),
      posted_within_days: Number(days),
      ats_type: atsType.trim() || null,
      ats_slug: atsSlug.trim() || null,
    });
    setBusy(false);
    if (insertError) { setError(insertError.message.includes("unique") ? "That careers URL is already tracked." : insertError.message); return; }
    setName(""); setUrl(""); setDays("7"); setAtsType(""); setAtsSlug(""); setExpanded(false);
    await loadCompanies();
  }

  async function removeCompany(id: string) {
    setBusy(true); setError("");
    const { error: deleteError } = await supabase.from("role_radar_companies").delete().eq("id", id);
    setBusy(false);
    if (deleteError) { setError(deleteError.message); return; }
    await loadCompanies();
  }

  return <aside className="control-panel company-manager">
    <div className="panel-heading"><div><p className="eyebrow">Company sources</p><h2>{companies.length} tracked {companies.length === 1 ? "company" : "companies"}</h2></div><Link2 size={20} /></div>
    <div className="company-list">{companies.map((company) => <div className="company-row" key={company.id}><div><strong>{company.name}</strong><span>{company.ats_type ? `${company.ats_type} override` : "Auto-detect ATS"} · last {company.posted_within_days}d</span></div><button className="delete-company" aria-label={`Remove ${company.name}`} onClick={() => void removeCompany(company.id)} disabled={busy}><Trash2 size={14} /></button></div>)}</div>
    <button className="add-company-toggle" onClick={() => { setExpanded(!expanded); setError(""); }}><Plus size={15} />Add careers site{expanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}</button>
    {expanded && <form className="company-form" onSubmit={addCompany}>
      <label>Company name<input required value={name} onChange={(event) => setName(event.target.value)} placeholder="Acme" /></label>
      <label>Careers URL<input required type="url" value={url} onChange={(event) => setUrl(event.target.value)} placeholder="https://jobs.example.com" /></label>
      <label>Only roles posted within<input required type="number" min="0" max="90" value={days} onChange={(event) => setDays(event.target.value)} /><span>days</span></label>
      <details><summary>ATS override for custom domains</summary><p>Leave this blank for automatic detection. If a site is not recognized, enter its ATS name and company slug.</p><label>ATS platform<input value={atsType} onChange={(event) => setAtsType(event.target.value)} placeholder="greenhouse" /></label><label>Company slug<input value={atsSlug} onChange={(event) => setAtsSlug(event.target.value)} placeholder="acme" /></label></details>
      {error && <p className="company-error" role="alert">{error}</p>}
      <button className="primary-button" disabled={busy}>{busy ? <><LoaderCircle className="spin" size={15} />Saving…</> : "Save company"}</button>
    </form>}
    {!expanded && error && <p className="company-error" role="alert">{error}</p>}
    <div className="local-note"><Link2 size={16} /><p>New sites are picked up the next time you run the local scraper.</p></div>
  </aside>;
}
