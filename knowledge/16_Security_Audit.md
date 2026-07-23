**17 evidence-backed findings** (3 Critical, 7 High, 6 Medium, 1 Low). XSS and direct SSRF: **not confirmed** in source. Full report with proof: [security-audit](C:\Users\AbhishekGajera\.cursor\projects\d-BLUE-WATER\canvases\security-audit.canvas.tsx) (open beside chat).

| Severity | Location (file:line) | Finding |
|---|---|---|
| Critical | `api/views/views.py:456` + `support_strats_viewer.py:34,1274` | SQL injection via `tape_id_list`/`buyer_id` string-replaced into `WHERE tapeinfo_id in (@1)` then `c.execute(sql)` |
| Critical | `msrx/views.py:42` | Failed admin login returns username **and password** in the HTTP body |
| Critical | `ebdjango/settings/dev.py:56` (also uat/demo) | Hardcoded `FNMA_TSP_AUTH_CODE` in source |
| High | `base/middleware/middleware.py:59-113` | `Authorization` tokens stored in `APIActivityLog` |
| High | `freedom/views/tape_management.py:834-847` | `Aliasedusertoken` switches identity with no link check |
| High | `api/views/tapes.py:33-78` | IDOR: `LoanIdsUpdate` loads tape by id with no ownership check |
| High | `api/views/views.py:456-477` | Broken access control: `ViewerStrat` accepts arbitrary tape IDs |
| High | `api/views/seasoned.py:202,1154` | IDOR: seasoned tape `get(pk=…)` without client filter |
| High | `ebdjango/settings/live.py` vs `dev.py:24-31` | Rate limiting only in DEV, absent in LIVE |
| High | `msrx-frontend/server/index.js:24-31` | CSRF enforced only when `NODE_ENV === "production"` |
| Medium | `ebdjango/settings/live.py:11` | `ALLOWED_HOSTS` includes `*` |
| Medium | `tapecrack/supporting/tapecrack.py:102-109` | Upload trusts `.sql` extension only, then executes SQL |
| Medium | `duediligence/views/documentviews.py:43-50` | DocumentType GET by id skips company/superuser gate |
| Medium | Widespread `str(e)` responses | Exception details returned to API clients |
| Medium | `ebdjango/settings/shared.py:35` | `DEBUG = eval(...)` |
| Medium | `msrx-frontend/server/utils.js:35` | Auth/CSRF cookies missing `SameSite` |
| Low | `msrx-frontend/.env`, `msrx_v2.0/.env` | Local credential material (gitignored; weak `ADMIN_PW` pattern) |

**Not confirmed (searched, no proof):** XSS sinks in `client/src`; direct user-controlled SSRF.