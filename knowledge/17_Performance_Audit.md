**Static profile of all 141 SPA views** is in [app-performance-profile](C:\Users\AbhishekGajera\.cursor\projects\d-BLUE-WATER\canvases\app-performance-profile.canvas.tsx) — open it beside the chat for the interactive page explorer, charts, and backlog.

There is no APM (no Sentry/Datadog/React Query). Numbers are mount-time from code + Django SQL/payload estimates, not live heap/byte samples.

### Headline
| Metric | Finding |
|--------|---------|
| Views | 141 (`viewMaps`) — ~34 with **0** mount APIs |
| Peak mount APIs | **7** (`showEditQcRule`) |
| Critical | Buyer pipeline, Freedom tape, Exceptions, Missing docs, TapeDetails, QuickCommit, LoanPipeline double-fetch |
| Cache | Almost none (LocMem ~5s; no Redis/React Query) |

### Confirmed waste
- `showLoanPipeline` — `/msrx/pre-close` **×2** every visit  
- `showQuickCommit` — `/msrx/fetch-buyers` **×2**  
- `showTapeDetails` — `/msrx/fetch-tape` **×2**  
- Global `dataLoading` → Main re-renders on every axios call  
- `withSubscription` reconnects unused Title Toolbox / DD slices on most pages  

### Largest payloads / slowest paths
Unpaginated loan dumps (buyer pipeline, ST exceptions/missing docs, Freedom tape). N+1 on Agg sellers SRP + DD deal ratings. PuLP optimize, win-loss raw SQL/pandas/PDF, S3 grid presign N.

Use the canvas domain/page selectors for per-page SQL, APIs, renders, transfer, memory, repeats, cache, and fixes. I can next instrument a staging pass for exact bytes/renders on the critical six, or start implementing the top backlog items.