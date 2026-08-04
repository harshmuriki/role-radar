# Graph Report - role-radar  (2026-08-04)

## Corpus Check
- 51 files · ~19,835 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 255 nodes · 321 edges · 25 communities (16 shown, 9 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e81d9bfd`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- generate_jobs.py
- dashboard.tsx
- compilerOptions
- What You Must Do When Invoked
- send_daily_digest.py
- package.json
- Run a Role Radar local worker
- FakeQuery
- devDependencies
- graphify reference: extra exports and benchmark
- graphify reference: query, path, explain
- grant_access.py
- test_shared_workspace.py
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- layout.tsx
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- CompanyUniquenessMigrationTests
- AGENTS.md
- extraction-spec.md
- next.config.ts
- next-env.d.ts

## God Nodes (most connected - your core abstractions)
1. `compilerOptions` - 17 edges
2. `main()` - 13 edges
3. `What You Must Do When Invoked` - 12 edges
4. `main()` - 10 edges
5. `/graphify` - 10 edges
6. `graphify reference: extra exports and benchmark` - 8 edges
7. `load_local_env()` - 7 edges
8. `job_matches()` - 7 edges
9. `process_queued_scans()` - 7 edges
10. `FakeQuery` - 7 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `load_local_env()`  [EXTRACTED]
  send_daily_digest.py → generate_jobs.py
- `Dashboard()` --calls--> `accessDeniedMessage()`  [EXTRACTED]
  components/dashboard.tsx → lib/access.ts
- `main()` --calls--> `load_local_env()`  [EXTRACTED]
  worker.py → generate_jobs.py
- `main()` --calls--> `worker_user_id()`  [EXTRACTED]
  send_daily_digest.py → generate_jobs.py
- `main()` --calls--> `process_queued_tests()`  [EXTRACTED]
  worker.py → generate_jobs.py

## Import Cycles
- None detected.

## Communities (25 total, 9 thin omitted)

### Community 0 - "generate_jobs.py"
Cohesion: 0.13
Nodes (29): age_in_days(), as_list(), contains_all(), contains_any(), job_matches(), load_companies(), load_local_env(), load_supabase_companies() (+21 more)

### Community 1 - "dashboard.tsx"
Cohesion: 0.11
Nodes (16): Company, CompanyManager(), Filters, join(), Dashboard(), formatDate(), formatPosted(), Job (+8 more)

### Community 2 - "compilerOptions"
Cohesion: 0.07
Nodes (27): dom, dom.iterable, esnext, next-env.d.ts, .next/types/**/*.ts, node_modules, **/*.ts, **/*.tsx (+19 more)

### Community 3 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 4 - "send_daily_digest.py"
Cohesion: 0.22
Nodes (20): datetime, Client, worker_user_id(), build_bodies(), build_subject(), digest_jobs(), env_required(), format_posted() (+12 more)

### Community 5 - "package.json"
Cohesion: 0.10
Nodes (20): lucide-react, next, dependencies, lucide-react, next, react, react-dom, @supabase/supabase-js (+12 more)

### Community 6 - "Run a Role Radar local worker"
Cohesion: 0.12
Nodes (14): 1. Get the code, 2. Create local secrets, 3. Start the always-on worker, 4. Check or stop it, 5. Configure and schedule the daily email, Run a full scan manually, Run a Role Radar local worker, Add company careers sites (+6 more)

### Community 7 - "FakeQuery"
Cohesion: 0.16
Nodes (5): dict, patch, FakeClient, FakeQuery, ProcessQueuedScansTests

### Community 8 - "devDependencies"
Cohesion: 0.18
Nodes (11): devDependencies, @types/node, @types/react, @types/react-dom, typescript, vitest, @types/node, @types/react (+3 more)

### Community 9 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 10 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 11 - "grant_access.py"
Cohesion: 0.50
Nodes (4): load_local_env(), main(), Grant a signed-in Supabase user access to the private Role Radar dashboard., Load the ignored local .env file without adding another dependency.

### Community 13 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 14 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 15 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

## Knowledge Gaps
- **102 isolated node(s):** `metadata`, `Filters`, `Company`, `Job`, `Run` (+97 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `process_queued_scans()` connect `generate_jobs.py` to `FakeQuery`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **What connects `metadata`, `Filters`, `Company` to the rest of the system?**
  _102 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `generate_jobs.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12701612903225806 - nodes in this community are weakly interconnected._
- **Should `dashboard.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.11330049261083744 - nodes in this community are weakly interconnected._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.07142857142857142 - nodes in this community are weakly interconnected._
- **Should `What You Must Do When Invoked` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._