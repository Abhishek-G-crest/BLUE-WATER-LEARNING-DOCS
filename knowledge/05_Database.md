Static audit of `msrx_v2.0` is in [database-query-audit](C:\Users\AbhishekGajera\.cursor\projects\d-BLUE-WATER\canvases\database-query-audit.canvas.tsx) — open it beside the chat for interactive hot-path traces, ORM→SQL tables, and execution diagrams. A canvas is a live React panel for this kind of structured analysis.

### Verdict
Every authenticated API pays **2–3 baseline queries + 1 INSERT** (Token auth + optional aliased token + `APIActivityLog`). On top of that, the worst cost is **confirmed N+1** in Freedom / DD / Supertransfer serializers — not missing FK indexes.

### Highest-impact findings

| Priority | Issue | Impact |
|----------|--------|--------|
| P0 | Supertransfer `get_missing_count` → `MissingFile.filter` per loan | **1+N queries** |
| P0 | Freedom `LoanSerializer` → `wl_price` / `wl_commit` / `notes` `.last()` per loan | **3N** (unless prefetched) |
| P0 | DD `DocumentValuesSerializer` runs the **same QC query twice** per value | **2N** |
| P1 | `ActivityLogMiddleware` sync INSERT (often with large `response_body`) | Write load on every request |
| P1 | Pipeline report: **4 correlated Subqueries** on boarding staging | Slow aggregator report |
| P2 | MSR ViewSets use bare `.all()` | Full-table scans; indexes unused |

### Index gaps (most valuable)
- `freedom_wholeloanprice (loan_id) WHERE selected`
- `freedom_tape (root_id, status)`
- `boarding_staging (seller_loan_number, updated_at DESC)` for PreClose `DISTINCT ON`
- `duediligence_qualitycontrol (loan_id, triggered)`
- `api_activity_log (created_at)` / partition + TTL

### Unused / low-value indexes
Many `db_index=True` columns on coissue tables are **unused by ViewSet `.all()`** dumps; they still help pricing/commit filters. `api_activity_log` FK indexes are write-costly and rarely read.

### Good pattern already in the codebase
DD `LoanQuerySet.with_qc_count()` / `with_missing_document_count()` — Subquery annotate instead of MethodField queries. Copy that pattern to Freedom and Supertransfer.

Costs in the canvas are **planner-shape estimates**. Validate on UAT with `EXPLAIN (ANALYZE, BUFFERS)` before shipping index migrations. I can implement the P0 serializer/queryset fixes next if you want.