"use client";

import {
  ArrowUpRight,
  BriefcaseBusiness,
  Building2,
  LoaderCircle,
  LogOut,
  MapPin,
  Radar,
  RefreshCw,
  Search,
  Sparkles,
} from "lucide-react";
import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import type { Session } from "@supabase/supabase-js";
import { supabase } from "@/lib/supabase";
import { CompanyManager } from "@/components/company-manager";
import { scanStatusMessage, type ScanRequestResult } from "@/lib/scan-request";
import { accessDeniedMessage, signUpSuccessMessage } from "@/lib/access";

type Job = {
  id: string;
  title: string;
  company: string;
  ats: string;
  location: string | null;
  remote: boolean | null;
  employmentType: string | null;
  department: string | null;
  postedAt: string | null;
  postedText: string | null;
  postedDaysAgo: number | null;
  url: string;
};

type Run = {
  id: string;
  generated_at: string;
  source_count: number;
  fetched_count: number;
  matched_count: number;
};

export function Dashboard() {
  const [session, setSession] = useState<Session | null>(null);
  const [accessAllowed, setAccessAllowed] = useState<boolean | null>(null);
  const [run, setRun] = useState<Run | null>(null);
  const [jobsData, setJobsData] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [error, setError] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSignUp, setIsSignUp] = useState(false);
  const [authBusy, setAuthBusy] = useState(false);
  const [scanBusy, setScanBusy] = useState(false);
  const [scanMessage, setScanMessage] = useState("");

  const loadPipeline = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const { data: latest, error: runError } = await supabase
        .from("role_radar_runs")
        .select("*")
        .order("generated_at", { ascending: false })
        .limit(1)
        .maybeSingle();
      if (runError) throw runError;

      setRun(latest);
      if (!latest) {
        setJobsData([]);
        return;
      }

      const { data: rows, error: jobsError } = await supabase
        .from("role_radar_jobs")
        .select("*")
        .eq("last_seen_run_id", latest.id)
        .order("posted_days_ago", { ascending: true })
        .order("title");
      if (jobsError) throw jobsError;

      setJobsData(
        (rows ?? []).map((job) => ({
          id: job.id,
          title: job.title,
          company: job.company,
          ats: job.ats,
          location: job.location,
          remote: job.remote,
          employmentType: job.employment_type,
          department: job.department,
          postedAt: job.posted_at,
          postedText: job.posted_text,
          postedDaysAgo: job.posted_days_ago,
          url: job.url,
        })),
      );
    } catch {
      setError("Your account is signed in, but it has not been granted Role Radar access yet.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    async function setSessionAccess(nextSession: Session | null) {
      setSession(nextSession);
      if (!nextSession) {
        setAccessAllowed(null);
        return;
      }
      const { data } = await supabase.rpc("role_radar_access_allowed");
      setAccessAllowed(data === true);
    }
    supabase.auth.getSession().then(async ({ data }) => {
      await setSessionAccess(data.session);
      setLoading(false);
    });
    const { data: listener } = supabase.auth.onAuthStateChange((_event, nextSession) => { void setSessionAccess(nextSession); });
    return () => listener.subscription.unsubscribe();
  }, []);

  useEffect(() => {
    if (session && accessAllowed === true) void loadPipeline();
  }, [accessAllowed, loadPipeline, session]);

  const jobs = useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (!needle) return jobsData;
    return jobsData.filter((job) =>
      `${job.title} ${job.company} ${job.location} ${job.department}`.toLowerCase().includes(needle),
    );
  }, [jobsData, query]);

  async function authenticate(event: FormEvent) {
    event.preventDefault();
    setAuthBusy(true);
    setError("");
    const result = isSignUp
      ? await supabase.auth.signUp({ email, password, options: { emailRedirectTo: window.location.origin } })
      : await supabase.auth.signInWithPassword({ email, password });
    if (result.error) setError(result.error.message);
    else if (isSignUp) setError(signUpSuccessMessage(Boolean(result.data.session)));
    setAuthBusy(false);
  }

  async function runScanNow() {
    setScanBusy(true);
    setError("");
    setScanMessage("Sending scan request to your local worker…");
    try {
      const { data: request, error: requestError } = await supabase
        .from("role_radar_scan_requests")
        .insert({})
        .select("id")
        .single();
      if (requestError || !request) throw new Error(requestError?.message || "Could not start the scan.");

      const deadline = Date.now() + 15 * 60_000;
      while (Date.now() < deadline) {
        await new Promise((resolve) => window.setTimeout(resolve, 1_000));
        const { data: current, error: pollError } = await supabase
          .from("role_radar_scan_requests")
          .select("status, error")
          .eq("id", request.id)
          .single();
        if (pollError) throw new Error(pollError.message);
        const scan = current as ScanRequestResult | null;
        if (scan?.status === "completed") {
          setScanMessage(scanStatusMessage(scan));
          await loadPipeline();
          return;
        }
        if (scan?.status === "failed") throw new Error(scanStatusMessage(scan));
        setScanMessage(scan ? scanStatusMessage(scan) : "Running your scan now…");
      }
      throw new Error("The scan did not finish within 15 minutes. Confirm your local worker is running.");
    } catch (scanError) {
      setScanMessage("");
      setError(scanError instanceof Error ? scanError.message : "Could not run the scan.");
    } finally {
      setScanBusy(false);
    }
  }

  if (!session) {
    return (
      <main className="auth-page">
        <div className="auth-orb auth-orb-one" />
        <div className="auth-orb auth-orb-two" />
        <section className="auth-card" aria-labelledby="auth-title">
          <div className="brand auth-brand"><span className="brand-mark"><Radar size={19} /></span><span>Role Radar</span></div>
          <div className="auth-copy">
            <p className="eyebrow">Private job intelligence</p>
            <h1 id="auth-title">{isSignUp ? "Create your account" : "Welcome back"}</h1>
            <p>Role Radar is available to approved accounts only.</p>
          </div>
          <form className="auth-form" onSubmit={authenticate}>
            <label>Email address<input required type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" placeholder="you@example.com" /></label>
            <label>Password<input required type="password" minLength={6} value={password} onChange={(event) => setPassword(event.target.value)} autoComplete={isSignUp ? "new-password" : "current-password"} placeholder="At least 6 characters" /></label>
            {error && <p className="auth-error" role="alert">{error}</p>}
            <button className="primary-button" disabled={authBusy}>{authBusy ? <><LoaderCircle className="spin" size={16} />Working…</> : isSignUp ? "Create account" : "Sign in"}</button>
          </form>
          <button className="text-button" onClick={() => { setIsSignUp(!isSignUp); setError(""); }}>
            {isSignUp ? "Already have an account? Sign in" : "New here? Create your approved account"}
          </button>
        </section>
      </main>
    );
  }

  if (accessAllowed === null) return <main className="auth-page"><LoaderCircle className="spin" /></main>;

  if (!accessAllowed) {
    return <main className="auth-page"><section className="auth-card"><div className="brand auth-brand"><span className="brand-mark"><Radar size={19} /></span><span>Role Radar</span></div><h1>Access restricted</h1><p className="auth-error">{accessDeniedMessage(session.user.email || "This account")}</p><button className="text-button" onClick={() => void supabase.auth.signOut()}>Sign out</button></section></main>;
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="topbar-inner">
          <div className="brand"><span className="brand-mark"><Radar size={19} /></span><span>Role Radar</span></div>
          <div className="account-menu"><span className="account-email">{session.user.email}</span><button className="logout" onClick={() => supabase.auth.signOut()}><LogOut size={15} />Sign out</button></div>
        </div>
      </header>

      <div className="page-content">
        <section className="hero" aria-labelledby="page-title">
          <div>
            <p className="eyebrow">Your focused job pipeline</p>
            <h1 id="page-title">Find the roles worth<br />your attention.</h1>
            <p className="hero-copy">A clear, curated view of newly posted roles across your company list.</p>
          </div>
          <div className="scan-status"><span className={run ? "status-dot" : "status-dot idle"} /><div><strong>{scanBusy ? "Scan in progress" : run ? "Pipeline is current" : "Awaiting a scan"}</strong><span>{scanMessage || (run ? `Updated ${formatDate(run.generated_at)}` : "Run a scan to publish roles")}</span><button className="scan-button" onClick={() => void runScanNow()} disabled={scanBusy}>{scanBusy ? <><LoaderCircle className="spin" size={14} />Running…</> : <><RefreshCw size={14} />Run scan now</>}</button></div></div>
        </section>

        {error && <p className="feedback error" role="alert">{error}</p>}

        <section className="stats" aria-label="Pipeline summary">
          <Metric icon={<Building2 size={17} />} label="Companies tracked" value={run?.source_count ?? 0} />
          <Metric icon={<Sparkles size={17} />} label="Relevant roles" value={run?.matched_count ?? 0} />
          <Metric icon={<BriefcaseBusiness size={17} />} label="Listings scanned" value={run?.fetched_count ?? 0} />
        </section>

        <section className="workspace">
          <CompanyManager />

          <section className="results-panel" aria-labelledby="roles-heading">
            <div className="results-heading">
              <div><p className="eyebrow">Matching positions</p><h2 id="roles-heading">Latest opportunities <span>{loading ? "" : `(${jobs.length})`}</span></h2></div>
              <div className="results-actions"><label className="search"><Search size={17} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search roles" aria-label="Search results" /></label><button className="icon-button" onClick={() => void loadPipeline()} disabled={loading} aria-label="Refresh pipeline"><RefreshCw className={loading ? "spin" : ""} size={17} /></button></div>
            </div>

            {loading ? <div className="empty-state"><LoaderCircle className="spin" /><p>Loading current job data…</p></div> : jobs.length ? <div className="table-wrap"><table><thead><tr><th>Position</th><th>Company</th><th>Location</th><th>Posted</th><th aria-label="Open job" /></tr></thead><tbody>{jobs.map((job) => <tr key={job.id}><td><a href={job.url} target="_blank" rel="noreferrer" className="job-title">{job.title}</a><span className="job-meta">{job.department || job.employmentType || job.ats}</span></td><td><span className="company-cell">{job.company}</span></td><td><span className="location-cell"><MapPin size={14} />{job.location || "Location not listed"}</span>{job.remote && <span className="remote-tag">Remote</span>}</td><td><strong className="posted-date">{formatPosted(job)}</strong></td><td><a className="open-link" href={job.url} target="_blank" rel="noreferrer" aria-label={`Open ${job.title} at ${job.company}`}><ArrowUpRight size={17} /></a></td></tr>)}</tbody></table></div> : <div className="empty-state"><Radar size={32} /><h3>{query ? "No roles match that search" : "No roles in this scan yet"}</h3><p>{query ? "Try a different job title, company, or location." : "Publish a local scan to bring the latest matches here."}</p></div>}
          </section>
        </section>
      </div>
    </main>
  );
}

function formatDate(date: string) { return new Date(date).toLocaleString([], { dateStyle: "medium", timeStyle: "short" }); }
function formatPosted(job: Job) { if (job.postedDaysAgo === 0) return "Today"; if (job.postedDaysAgo === 1) return "Yesterday"; if (job.postedDaysAgo !== null) return `${job.postedDaysAgo}d ago`; if (job.postedAt) return new Date(job.postedAt).toLocaleDateString(); return job.postedText || "Unknown"; }
function Metric({ icon, label, value }: { icon: React.ReactNode; label: string; value: number }) { return <div className="metric"><span className="metric-icon">{icon}</span><div><span>{label}</span><strong>{value}</strong></div></div>; }
