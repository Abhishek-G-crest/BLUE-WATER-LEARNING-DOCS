# Developer Takeover Forensic Audit

**Audience:** Development team taking over/supporting MSRX (not product/business owners)  
**Date:** 2026-07-24  
**Scope:** `msrx_v2.0`, `msrx-frontend`, `super_transfer_client`  
**Method:** Read-only forensic inspection — builds on prior audits without repeating them  
**Companion:** Interactive canvas at [developer-takeover-forensic-audit](file:///C:/Users/AbhishekGajera/.cursor/projects/d-BLUE-WATER/canvases/developer-takeover-forensic-audit.canvas.tsx)

**Evidence labels:** `[CONFIRMED FROM CODE]` · `[CONFIRMED FROM KT]` · `[CODE + KT CONFIRMED]` · `[LIKELY / INFERRED]` · `[NOT FOUND]` · `[UNCLEAR — ASK IN KT]`

**Central question answered:** *If the original developers disappeared tomorrow, what technical knowledge would still be missing that could break production, block incident debugging, corrupt data, cause bad deploys, or mislead us about workflows?*

---

## Executive Takeover Risk Dashboard

| Severity | Count | Top themes |
|----------|-------|------------|
| **P0 Critical** | 12 | SQS contract mismatch, confirm-before-side-effects, duplicate schedulers, silent SQS failures, `ApiCommitConfirm` bypass |
| **P1 High** | 18 | No transactions on multi-table writes, detached threads, logout/cookie bugs, status string drift |
| **P2 Medium** | 15 | LocMemCache multi-instance, CSRF header gap, legacy dual tables |
| **P3 Low** | 8 | Dead imports, commented routes, typo fields |

**New vs prior audits:** This document focuses on **hidden runtime**, **failure modes**, **transaction gaps**, **concurrency**, **deployment blast radius**, and **code↔KT contradictions** — not business flow narration.

---

## 1. Hidden Runtime Behavior

### P0 — Side effects that are easy to miss

| ID | FILE | FUNCTION | TRIGGER | ENV | SIDE EFFECT | WHAT CAN BREAK | VERIFY |
|----|------|----------|---------|-----|-------------|----------------|--------|
| HR-01 | `msrx_v2.0/ebdjango/wsgi.py:22-25` | `leader_election_process` thread | Every WSGI worker boot | All (scheduler only if `ENV_FLAG=CLOUD`) | APScheduler + email monitor | Crons never run locally; duplicate leaders | `LeaderElection` table; logs "Starting leader election" |
| HR-02 | `msrx_v2.0/api/urls/urls.py:39-45` | module import | First `api.urls` load | UAT/DEMO/LIVE only | ST + boarding `BackgroundScheduler` per worker | **Duplicate SFTP deliveries** | Count scheduler threads per EB instance |
| HR-03 | `msrx_v2.0/api/utils/misc.py:1840-1843` | `leader_election_process` | New leader elected | CLOUD | `remove_all_jobs()` wipes django-apscheduler store | Job gap on failover | `django_apscheduler_djangojob` before/after |
| HR-04 | `msrx_v2.0/EmailTrading/supporting/refresh.py:130-150` | `enable_emailmonitor` | Leader startup | CLOUD leader | 5 jobs × **15s** O365 poll | Duplicate tape processing, rate limits | `EmailTrading_Log` spike |
| HR-05 | `super_transfer_client/scripts/helper_functions.py:182` | `ensure_model_context()` | **Any import** of helper_functions | EC2 | NLTK + pickle models + boto3 + Secrets Manager | 30s+ cold start, import failure | `time python3 -c "import helper_functions"` |
| HR-06 | `super_transfer_client/scripts/main.py:140` | `main()` | Import or cron | EC2 | Infinite SQS loop (no `if __name__`) | Accidental worker start in tests | `ps aux \| grep main.py` |
| HR-07 | `super_transfer_client/base/workflows/process_flag.py:97-102` | `process_flag()` | Each loop iteration | EC2 | Reads DynamoDB `supertransfer-deploymentDB` | Worker stops mid-deploy | Query DDB `process_flag` by git branch |
| HR-08 | `msrx-frontend/server/utils.js:4-29` | axios response interceptor | Every proxied backend call | All | Logs all responses; mutates global axios headers | PII in logs; header bleed | Enable pino debug |
| HR-09 | `msrx-frontend/prebuild-script.js:70-71` | `getPlatformConfigs()` | `npm run prebuild` | CI/build | Fetches platform JSON + S3 logos | Stale white-label in dist if skipped | Compare `platform_configs.json` mtime |
| HR-10 | `msrx_v2.0/api/views/auth.py:52-76` | `Login.get_response` | Every login | All | `HTTP_HOSTNAME` platform gate | Login fails if BFF omits header | curl with/without `hostname` |

### P1 — Request-time hidden behavior

| ID | FILE | TRIGGER | SIDE EFFECT |
|----|------|---------|-------------|
| HR-11 | `api/api_handler.py` (~830, 1084) | Tape upload HTTP return | `threading.Thread` async DB insert |
| HR-12 | `api/supporting/support_pricing.py:1612` | Pricing HTTP return | Async price `bulk_update` thread |
| HR-13 | `api/supporting/services/msr_commit.py:241` | Confirm | Resell thread after status flip |
| HR-14 | `base/middleware/middleware.py:57-123` | Every API request | `APIActivityLog.objects.create` |
| HR-15 | `msrx-frontend/server/utils.js:32-42` | Every `/msrx/*` | `refreshToken` slides 2h cookie |

**`manage.py runserver` does NOT load `wsgi.py`** → leader election OFF locally. [CONFIRMED FROM CODE]

**No Django signals (`@receiver`) found** in custom apps. [CONFIRMED FROM CODE]

**No `AppConfig.ready()` active** — election moved from commented `api/apps.py` to WSGI. [CONFIRMED FROM CODE]

---

## 2. Production-Only Behavior Matrix

| Concern | LOCAL | DEV | UAT | DEMO | LIVE |
|---------|-------|-----|-----|------|------|
| Central APScheduler | OFF (`ENV_FLAG` default LOCAL) | OFF unless EB CLOUD | ON (leader) | ON + 17:00 email deactivation | ON + full LIVE job set |
| ST/Boarding URL schedulers | OFF | OFF | **ON every worker** | ON every worker | ON every worker |
| ST EC2 worker (git branch) | N/A | `Dev` | `UAT` | `Demo` | `Live` |
| Email 15s monitor | No | No | Yes (leader) | Yes | Yes |
| `LOG_LEVEL` | `.env` | `.env` | `.env` | `.env` | **Hardcoded ERROR** (`live.py`) |
| FNMA API | Sandbox URLs | Sandbox | Sandbox | Sandbox | **Prod URLs** |
| EPIC credentials | TEST | TEST | TEST | TEST | **PROD** |
| Laura Mac | UAT creds in shared | UAT | UAT | UAT | PROD |
| CRA cron jobs | No | No | No | No | **Yes** (`misc.py:1883-1887`) |
| Frontend CSRF | Relaxed | Relaxed in dev | Production if `NODE_ENV=production` | Same | Strict CSP + CSRF |
| Django `ALLOWED_HOSTS` | `*` included | `*` | `*` | `*` | `*` |

**"Works locally but differs in production":**
1. Async upload/pricing/commit threads appear synchronous locally (low latency) but race under load. [CONFIRMED FROM CODE]
2. `ENV_FLAG=CLOUD` required for crons — local pointed at cloud DB still won't run jobs. [CONFIRMED FROM CODE]
3. `MSRX_ENV` drives S3/SQS names at runtime (`supertransfer-{env}`) — LOCAL may mismatch settings file bucket. [LIKELY / INFERRED]
4. Multi-worker EB → duplicate ST schedulers (not visible on `runserver`). [CONFIRMED FROM CODE]

---

## 3. Configuration & Secret Dependency Map

### Critical keys (sample — full list in canvas)

| CONFIG KEY | USED BY | SOURCE | REQUIRED | ENV | FAILURE IF MISSING | SECRET | ROTATION IMPACT |
|------------|---------|--------|----------|-----|-------------------|--------|-----------------|
| `MSRX_ENV` | Settings router, S3/SQS names | `manage_*.py` / EB | **Yes** | All | Wrong DB/bucket | No | High |
| `ENV_FLAG` | Leader election | `.env` / EB | Prod: **Yes** | CLOUD vs LOCAL | No crons OR accidental leader | No | High |
| `SECRET_KEY` | Django | `shared.py` | **Yes** | All | App won't start securely | **Yes** | Session invalidation |
| `AWS_ACCESS_KEY` / `AWS_SECRET_KEY` | All boto3 | `shared.py` | **Yes** | All | S3/SQS fail | **Yes** | All AWS ops break |
| `AWS_ACCOUNT_ID` | SQS URL construction | `shared.py` | **Yes** | All | SQS send fails | No | Queue URL wrong |
| `AZURE_CLIENT_ID` / `AZURE_SECRET` | O365 email | env-specific settings | **Yes** | All | Email fails | **Yes** | All notifications |
| `BACKEND_URL` | Express proxy | `msrx-frontend/.env` | **Yes** | All FE | All API 503 | No | Total outage |
| `WEB_TOKEN_SECRET` | Cookie signing | `msrx-frontend/.env` | **Yes** | All FE | Auth cookies invalid | **Yes** | Force re-login |
| `HTTP_HOSTNAME` (header) | Login platform check | BFF → Django | **Yes** | All | Login rejected | No | Platform lockout |
| `user_details` JSON | Per-user flags | `msrx_msrx_user` DB | Per feature | All | Feature silently off | No | Per-user |
| `PlatformConfiguration` | MFA, hostname, UI | DB table | Login | All | Unauthorized platform | No | Per-platform |
| ST Secrets Manager | `API_KEYS`, `msrx-urls`, `SUPER_TRANSFER_AWS_VARIABLES` | AWS SM | **Yes** EC2 | Dev/UAT/Demo/Live | Worker won't start | **Yes** | Worker outage |
| Git branch on EC2 | ST env selection | `base/utils/git.py` | **Yes** ST | Per deploy | Wrong queue/DB | No | Cross-env processing |

**Easily missed:**
- `ENV_FLAG` is separate from `MSRX_ENV` [CONFIRMED FROM CODE]
- Per-brand O365 creds (`FMX_MSR_CLIENT_ID`, etc.) in `shared.py` [CONFIRMED FROM CODE]
- `user_details.authorized_platform` must match request hostname [CONFIRMED FROM CODE]
- `config.py` referenced by ST `env_variables.py` but **not in repo** [NOT FOUND]

---

## 4. External Integration Contracts

| Integration | ENTRY POINT | AUTH | TIMEOUT/RETRY | IF DOWN | DB EFFECT |
|-------------|-------------|------|---------------|---------|-----------|
| **SQS loansToprocess** | `support_committing.py:post_loan_to_sqs` | AWS keys | **None**; bare except | Silent False; commit still succeeds | None |
| **SQS filesToBedrock** | `support_bedrock_process_helpers.py` | AWS keys | **None** | 500 to caller | None |
| **S3** | `TapeManager/support_s3storage.py`, ST paths | AWS keys | SDK default | Upload/pricing/ST fail | Orphan tapes |
| **O365 Graph** | `EmailTrading/utils.py:send_email_notif` | Azure + S3 token file | Library default | Notifications fail | None |
| **FNMA API** | `freedom/supporting/pricing/agency/fnma_api.py` | Token endpoint | [NOT FOUND explicit] | `mbs failed` status | Freedom tape stuck |
| **PHH par** | `api/supporting/support_par.py` | [UNCLEAR] | [NOT FOUND] | Par rate fallback? | Buyer par stale |
| **RoundPoint SFTP** | `analytics/support_ftp/file_transfer.py` | SFTP creds in config | Cron retry next day | Trial balance miss | None |
| **Laura Mac** | DD views | `LAURA_MAC_*` | [NOT FOUND] | DD marketplace fail | DD records |
| **EPIC** | `supertransfer/supporting/guidance.py` | `EPIC_*` LIVE | [NOT FOUND] | Guidance post fail | `EpicRecord` log |
| **Voxtur/InfoEx** | `voxtur/supporting/api.py` | Okta | [NOT FOUND] | Title order fail | None |
| **Benutech** | `benutech/title_toolbox_api.py` | API login | [NOT FOUND] | Property lookup fail | None |
| **Bedrock worker** | SQS consumer (external) | N/A from Django | External | Docs unprocessed | DD doc status |
| **Super Transfer worker** | SQS consumer | PG + API key | Heartbeat 600s | Loans stuck unprocessed | DD loan status |

### Undocumented assumptions
1. S3 folder must exist **before** `post_loan_to_sqs` — Django checks, worker assumes docs present. [CONFIRMED FROM CODE]
2. ST worker requires `loan_id` in SQS body — Django does not send it. [CONFIRMED FROM CODE] — see Section 14
3. `seller-loan_id` format `{seller}-{buyer}_{loan}` is authoritative in Django+DDB; ST TypedDict comment is wrong. [CONFIRMED FROM CODE]

---

## 5. Failure-Mode Audit

### Tape upload failure diagram

```
POST uploadtape_csv
  → S3 upload (failure: logged, may continue) [tape_upload.py:74-86]
  → raw_tape_crack validation (failure: HTTP error)
  → Client_Coissue_Seller saved status=uploaded [api_handler.py:710]
  → Thread: bulk_create loans (failure: partial loans, no atomic) [api_handler.py:1752]
  → upload_progress may never reach 100 on success [api_handler.py:1744-1763]
```

**Stuck state:** `uploaded` with partial loans or `upload_progress` < 100.

### Confirm commit failure diagram (P0)

```
confirm_commit [msr_commit.py:98]
  → tape.status = "confirmed" + SAVE          ← POINT OF NO RETURN
  → asset_commit_postprocess()
  → FOR EACH loan:
      → post_loan_to_sqs()                  ← may return False silently
  → create_commit_dd_records_and_values()     ← may fail, still returns success
  → loan number burn (atomic section)       ← only this part wrapped
  → emails
```

**Stuck state:** `confirmed` but no SQS, no DD records, no loan numbers.

### Super Transfer message failure (P0)

```
Django: {"seller-loan_id": "117-42_2208066387"}
  → ST main.py: commitment_check() → if True:
      → if 'loan_id' in res: processLoan()   ← SKIPPED for Django message
  → delete_queue_message() ALWAYS            ← message lost
```

[CONFIRMED FROM CODE] — `main.py:98-115`

### Alternate confirm path bypass (P0)

`api/views/api.py:ApiCommitConfirm` sets `status=confirmed` **without** `confirm_commit()` — no SQS, no DD, no delivery_month. [CONFIRMED FROM CODE]

---

## 6. Transaction & Data-Integrity Audit

| WORKFLOW | TABLES | `transaction.atomic`? | PARTIAL FAILURE | SEVERITY |
|----------|--------|----------------------|-----------------|----------|
| Tape async upload | `Client_Coissue_Seller`, `Client_Coissue_Tape` | **No** | Partial loans | P0 |
| Pricing async | `Client_Coissue_Tape.price`, seller status | **No** | Partial prices | P1 |
| `commit_group` | loans commitment JSON + tape status | **No** | Loans committed, tape not pre-commit | P1 |
| `confirm_commit` | status + SQS + DD + loan numbers | **Partial** (loan numbers only) | confirmed without side effects | P0 |
| `create_commit_dd_records_and_values` | DD Loan, Document, Value, Boarding_Staging | **No** | Orphan DD rows | P0 |
| `UlddFile` boarding | LoanNumbers + Boarding_Staging | **Scope too narrow** | Numbers burned, no boarding row | P0 |
| Seasoned commit caps | `Client_Commit_Cycle` | **Yes** + `select_for_update` | Protected | Good |
| Loan number burn on confirm | `LoanNumbers` | **Yes** + `select_for_update` | Protected | Good |

---

## 7. Concurrency & Race Conditions

| RISK | PROTECTION EXISTS? | EVIDENCE |
|------|-------------------|----------|
| Two users price same tape | **No** | Detached threads; JSONField last-write-wins |
| Two users commit same tape | **No** | No `select_for_update` on tape row |
| Duplicate APScheduler (leader + URL import) | **No** | `urls.py:39` + `wsgi.py:24` |
| N EB workers × ST scheduler | **No** | Per-worker BackgroundScheduler |
| SQS message processed twice | Partial | `current_processing` in-memory only (`main.py:47`) |
| Email monitor duplicate instances | Detection only | `email_monitor_duplicate_check` emails, doesn't stop |
| `status_details` JSON concurrent update | **No** | Read-modify-write pattern throughout |

---

## 8. Status / State Corruption Audit

### MSR `Client_Coissue_Seller.status`

| Value | SET BY | VALID FROM | CAN STUCK? |
|-------|--------|------------|------------|
| `uploaded` | `clean_tape_upload_to_DB` | — | Yes (async fail) |
| `approved` | `approve_tape` | uploaded | Rare |
| `priced` | `pricing_to_DB_asyn_worker` | approved | Yes (`pricing_progress`<100) |
| `pre-commit` | `commit_group` | priced | Yes (`commit_failed_message`) |
| `confirmed` | `confirm_commit` / `ApiCommitConfirm` | pre-commit | **Side effects may be incomplete** |

**Inconsistencies:**
- Model comment: `pre-committed`; code uses `pre-commit` [CONFIRMED FROM CODE]
- UI filter uses `pre-committed` in places [CONFIRMED FROM CODE]
- `transfer_complete` in model comment; no active setter found [NOT FOUND]

### `Boarding_Staging.status`

- SQL filters expect `'Processed'` (`duediligence/utils/boarding_file.py:28`)
- **No Python writer sets this field** [CONFIRMED FROM CODE]
- Code uses `cleared`, `delivered`, `boarding_file_delivered` booleans instead

### Freedom `Tape.status` (separate vocabulary)

`uploaded` → `priced` / `priced - sent` / `priced - held` / `priced - split` / `mbs failed` → `confirmed`

---

## 9. Data Ownership / Source-of-Truth

| CONCEPT | PRIMARY SOT | COPIES / STAGING | SYNC | STALE RISK |
|---------|-------------|------------------|------|------------|
| MSR loan (coissue) | `msrx_client_coissue_tape` | `*_updated`, `*_deleted` | Manual merge on edit | price JSON vs normalized WL price |
| WL loan | `freedom_loan` | `freedom_loansnapshot` | Snapshot at pricing/commit | Snapshot frozen, loan mutates |
| DD loan | `duediligence_loan` | Links via FK | `create_commit_dd_records` on confirm | DD may not exist if confirm partial-fails |
| Boarding | `msrx_boarding_staging` | `rp_boarding_staging_table` (legacy) | Separate code paths | Two schemas in production? [UNCLEAR] |
| ST tracking | DynamoDB `supertransfer-{env}DB` | — | Worker `update_table` | Django doesn't read DDB |
| Commitment (MSR) | `Client_Coissue_Tape.commitment` JSON | `status_details.best_ex` | Built in postprocess | Summary can desync from loans |
| Commitment (WL) | `freedom_wholeloancommit` | — | Freedom commit service | Parallel to MSR JSON |
| Price (MSR) | `Client_Coissue_Tape.price` JSON | — | Pricing worker | Overwritten on re-price |
| Price (WL) | `freedom_wholeloanprice` | — | Freedom engine | Normalized rows |
| User identity | `msrx_msrx_user` | `auth_user` + login tables | `Django_user_to_msrx_user` | Flag vs relationship drift |

---

## 10. Delete / Update Impact

| DELETE X | CASCADE DESTROYS | SEVERITY |
|----------|-------------------|----------|
| `Client_Coissue_Seller` | All `Client_Coissue_Tape` loans | P0 |
| `Client_Coissue_Tape` row | `Boarding_Staging` row (FK CASCADE) | P0 |
| `MSRX_User` (seller) | All tapes, Freedom tapes, boarding rows | P0 |
| `MSRX_User` (buyer) | Boarding staging, ST loan refs | P1 |
| `duediligence.Deal` | All DD loans, docs, values | P1 |
| `freedom.Tape` | All `freedom.Loan` | P1 |

**Safe:** `Client_Coissue_Seller.psa_deal` → `PROTECT`

---

## 11. API Contract Audit (critical paths)

### MSR pricing poll contract

```
React step4-price.js → POST /msrx/run-pricing
  → Express msrCoissue.postRunPricing → Django POST /msrx/api/pricing/
  → Express polls GET /msrx/check-pricing-status every 3s
  → Expects status_details.pricing_progress == 100
```

**Fragility:** Progress set in async thread; HTTP 200 before completion. [CONFIRMED FROM CODE]

### Login response shape

Django returns `user_role`, `aggregator_flag`, `side_panel_items` (via platform/user). Frontend persists subset to localStorage. **Stale `side_panel_items` if admin changes template without re-login.** [CONFIRMED FROM CODE]

### GET causing writes

`BuyerCommittedTapes.get` updates `transfer_status` to `complete` in DB. [CONFIRMED FROM CODE] — `api/views/views.py:361-373`

---

## 12. Express BFF Deep Audit

| Topic | Finding | Evidence |
|-------|---------|----------|
| Why Express exists | CSRF cookie, httpOnly auth, response shaping, local XLSX/PDF, S3 uploads | `server/index.js`, route modules |
| CSRF | Production only; header from `metas[0]` — likely **wrong meta tag** | `store.js`, `index.js:24-31` |
| Auth cookie | 2h `auth` {key, login_key, username}; refreshed every request | `utils.js:32-42` |
| Token forward | `Authorization: Token ${cookie.key}`; alias via `Aliasedusertoken` | `wholeLoan.js`, `auth.js` |
| Full logout bug | Django logout called but **`auth` cookie not cleared** on full logout | `auth.js` [CONFIRMED FROM CODE] |
| No axios timeout | Hung Django blocks Express until nginx 300s | `utils.js` |
| Local S3 | `superTransfer/s3Bucket.js` — missing docs, bulk package | Not proxied to Django |
| Email local | `mailer.js` — forgot password, Freedom commitment Excel | Bypasses Django |
| Restart impact | All in-flight proxied requests fail; cookies survive; schedulers N/A | — |

---

## 13. Frontend State / Session Risks

| Issue | Symptom looks like backend bug | Evidence |
|-------|-------------------------------|----------|
| `localStorage` never cleared on logout | Wrong user data after switch | No `removeItem` in client [CONFIRMED] |
| `isAuth` restored without server check | UI shows logged in, APIs 401 | `localStorage.js` + `Router.js` |
| Redux tape/pricing state persists | Stale prices displayed | Only auth slice cleared |
| No multi-tab sync | Tab B active after Tab A logout | No storage listener |
| `viewMaps` has no permission guard | `setView("showX")` renders any mapped view | `viewMaps.js` |
| `showQCVariables` vs `showDueDiligenceQCVariables` mismatch | Blank panel on sidebar click | [CONFIRMED FROM KT doc] |

---

## 14. File Lifecycle Audit

```
Loan tape CSV/XLSX:
  Browser → Express multer uploads/ → stream → Django S3 priced_tapes/msr/{...}
  → tape crack → DB Client_Coissue_*

Super Transfer docs:
  External/SFTP/manual → S3 SuperTransfer/{seller}/{buyer}/{loan}/
  → Django post_loan_to_sqs (if folder non-empty)
  → ST worker downloads to local_loan_files/ → processes → S3 artifacts + SFTP

Boarding file:
  Boarding_Staging rows → supertransfer boarding generator → SFTP scheduled

O365 tokens:
  S3 EmailTrading/tokens/{brand}/ + o365_token.txt

Temp files:
  msrx-frontend uploads/ (multer) — cleanup [NOT FOUND explicit]
  ST local_loan_files/ — deleted/regenerated on idle (main.py:128)
```

---

## 15. Logging & Incident Debugging Map

| INCIDENT | LOOK HERE FIRST | USEFUL QUERY / COMMAND |
|----------|-----------------|------------------------|
| Upload stuck | `status_details.upload_failed_message`; `APIActivityLog` | `SELECT loancount, (SELECT count(*) FROM msrx_client_coissue_tape WHERE tapeinfo_id=X)` |
| Pricing stuck | `pricing_progress`, `pricing_failed_message` | Activity log action `pricing` |
| Commit stuck | `commit_progress`, `commit_failed_message` | `SELECT status, status_details FROM msrx_client_coissue_seller WHERE id=X` |
| Confirmed no ST | `activity_log` "Post success/Failed to post" | S3 `aws s3 ls s3://supertransfer-live/SuperTransfer/{s}/{b}/{loan}/` |
| SQS backlog | ST `DO_NOT_DELETE_THIS.txt` | `aws sqs get-queue-attributes --queue-url .../loansToprocess-live` |
| Email monitor dead | `MonitoredMailbox.last_active_ping` | Leader election row; `EmailTrading_Log` |
| SFTP duplicate | Multiple schedulers | Compare delivery timestamps; EB instance count |
| DD loan missing | `duediligence_loan` by `loan_number` | Re-run `create_commit_dd_records_and_values` |
| ST worker stopped | DDB `process_flag` | `crontab -l`; `ps aux \| grep main.py` |

**No Sentry / CloudWatch SDK in app code.** [NOT FOUND]

---

## 16. Deployment Blast Radius

| REPO DEPLOYED | RESTARTS | INTERRUPTS | DUPLICATES |
|---------------|----------|------------|------------|
| **msrx_v2.0 Django** | All WSGI workers; leader election thread; URL-import schedulers | In-flight HTTP; APScheduler jobs wiped on new leader | ST/boarding scheduler per worker |
| **msrx-frontend** | Express process | In-flight proxy requests (300s nginx) | None |
| **super_transfer_client** | `stop_cron.sh` → **pkill -9 python3**; `start_cron.sh` | SQS messages in visibility timeout; `process_flag` gate | flock prevents duplicate main.py |

**Migrations:** `collectstatic` on EB deploy; **no auto-migrate in `.ebextensions`** [CONFIRMED FROM CODE] — manual? [UNCLEAR]

**ST deploy:** `process_flag=false` → worker drains → email → sleep 600s → CodeDeploy → `upload_model.py` → cron restart [CONFIRMED FROM CODE]

---

## 17. Database Migration Risk

| Risk | Evidence |
|------|----------|
| RunPython data migrations | 3 found in `duediligence/migrations/0071-0073` (deal FK backfill) |
| Large msrx migration history | 160+ migrations in msrx app |
| **Checklist for THIS project:** | |
| 1. Never migrate LIVE without UAT replay | |
| 2. Check RunPython for production data assumptions | |
| 3. `Client_Coissue_*` tables are huge — avoid blocking ALTER | |
| 4. CRA app not in INSTALLED_APPS — migrations may not apply | |
| 5. Test rollback plan — no documented procedure [NOT FOUND] | |

---

## 18. Dead / Legacy / Partially Disabled Code

| Item | Classification | Evidence |
|------|----------------|----------|
| `CRA` app | **PARTIALLY DISABLED — PRODUCTION DEPENDENT** | Not in INSTALLED_APPS; URL + LIVE cron active |
| `rp` app | **LEGACY BUT POSSIBLY PRODUCTION DEPENDENT** | `Transfer/views.py` still imports |
| `ApiCommitConfirm` | **ACTIVE — DANGEROUS** | Bypasses full confirm pipeline |
| `commit_portfolio_level` | **LEGACY BUT POSSIBLY USED** | Superseded by loan-level |
| `empower_commit_report_send` cron | **SAFE-LOOKING UNUSED** | Defined, never registered |
| `@agg_sellers_only` decorator | **SAFE-LOOKING UNUSED** | Never applied |
| Freedom `wholeloan-shadow-bid` | **UNKNOWN** | No frontend references |
| `showEmailmonitorStatus` view | **UNKNOWN** | Orphan viewMaps entry |

---

## 19. Manual Operational Processes

| OPERATION | EVIDENCE | RISK | KT NEEDED? |
|-----------|----------|------|------------|
| DD loan reprocess | `duediligence/urls.py:175` `reprocess_loan/<id>/` | Deletes DDB + S3 prefix | Who approves? |
| ST manual loan notebook | `Manual_Loan_Process.ipynb` | Full message with `loan_id` | Production use? |
| `resetLoanDict.py` / `resetCustDict.py` | ST scripts folder | Data reset | [UNCLEAR] |
| Admin token lookup | `GET /msrx/api/admin/token_lookup` | Credential recovery | Who has superuser? |
| SQL tapecrack template upload | `tapecrack/views/sql.py` | Per-client SQL in DB | Seller onboarding |
| Fixture loading | `fixtures/README.md` | Local dev only | — |
| EB env var management | `.ebextensions/ebextensions.config` | Wrong var → wrong env | Ops ownership |
| DDB `process_flag` toggle | ST `process_flag.py` | Stops all processing | Deploy procedure |
| `pkill -9 python3` on ST deploy | `stop_cron.sh` | Kills all Python on host | Co-hosted services? |

---

## 20. Code ↔ KT Contradictions

| Topic | KT / PRIOR AUDIT | CODE | VERDICT |
|-------|------------------|------|---------|
| ST SQS contract | "Unclear if worker derives loan_id" | Worker **requires** `loan_id` in body; Django doesn't send | **[CODE PROVES GAP]** — enrichment must be external or path broken |
| `committed_buyer` field | Mentioned in KT context | **Not in codebase** | KT conflated with `commitment.buyer_id` |
| Super Transfer API `seller-loan_id` | Composite key | `ReceiveMissingLoans` uses loan number only | **[CONTRADICTION]** |
| CRA app status | Various | Disabled in apps, active in URLs/cron | **[CONTRADICTION]** |
| Celery/Redis | Some docs mention async | **Not present** | KT outdated if mentioned |
| `transfer_complete` status | In model comments | No setter found | KT overstates lifecycle |
| CSRF protection | Assumed working | Header source likely broken meta | **[CODE RISK]** |

### Confirmed by code only (not in KT)
- `scheduler.pause` missing `()` bug — `support_boarding_file_generation.py:304`
- `Boarding_Staging.status='Processed'` never set in Python
- Full logout doesn't clear httpOnly cookie (Express)
- `remove_all_jobs()` on leader failover

---

## 21. Tribal Knowledge Questions

### P0 MUST ASK
1. What enriches SQS `loansToprocess` messages with `loan_id`? (Lambda? Older producer? Manual notebook only?)
2. Who uploads docs to `SuperTransfer/{seller}/{buyer}/{loan}/` and when relative to confirm?
3. How are failed `post_loan_to_sqs` recovered in production?
4. Is `ApiCommitConfirm` (`/msrx/api/commit-confirm/`) used by any external client?
5. How many EB instances per env — duplicate scheduler exposure?
6. What is the migration deploy procedure for LIVE?
7. Who owns AWS Secrets Manager keys for ST worker?
8. Is `rp_boarding_staging_table` still written in production?
9. What is the SQS DLQ/redrive policy (not in app code)?
10. Does `pkill -9 python3` on ST box kill other services?

### P1 SHOULD ASK
11. Is `ENV_FLAG` set to CLOUD on all non-local EB environments?
12. Who receives `email_monitor_duplicate_check` alerts?
13. Production observability stack (if not Sentry/CloudWatch SDK)?
14. Is portfolio-level commit still used?
15. CSRF — is production HTML different from dist (token meta present)?

### P2 NICE TO KNOW
16. History of `ApiCommitConfirm` vs wizard confirm
17. Why CRA removed from INSTALLED_APPS but not URLs
18. `config.py` on ST EC2 — what does it contain?

---

## 22. Dangerous Code Hotspots (Top 30)

| Rank | FILE:FUNCTION | WHY DANGEROUS |
|------|---------------|---------------|
| 1 | `api/supporting/services/msr_commit.py:confirm_commit` | Sets confirmed before SQS/DD; no rollback |
| 2 | `api/views/api.py:ApiCommitConfirm` | Bypasses entire confirm pipeline |
| 3 | `api/urls/urls.py:39-45` | Duplicate schedulers per worker |
| 4 | `api/utils/misc.py:leader_election_process` | Wipes all jobs on leader change |
| 5 | `api/api_handler.py:clean_tape_upload_to_DB*` | Async partial upload |
| 6 | `api/api_handler.py:commit_group` | Multi-loan commit without atomic |
| 7 | `api/supporting/support_committing.py:post_loan_to_sqs` | Silent SQS failure |
| 8 | `api/supporting/support_committing.py:create_commit_dd_records_and_values` | Multi-table no atomic |
| 9 | `api/supporting/support_pricing.py:asset_price_v3` | Async pricing threads |
| 10 | `supertransfer/views/files.py:UlddFile` | Atomic scope bug |
| 11 | `super_transfer_client/scripts/main.py:main` | Deletes messages without processing |
| 12 | `super_transfer_client/scripts/process_loan_handler.py:processLoan` | Swallows exceptions |
| 13 | `msrx-frontend/server/routes/auth.js:postLogout` | Cookie not cleared |
| 14 | `msrx-frontend/client/src/store/localStorage.js` | Stale auth state |
| 15 | `api/views/auth.py:Login.get_response` | Hostname gate |
| 16 | `EmailTrading/supporting/refresh.py:enable_emailmonitor` | 15s polling |
| 17 | `api/views/views.py:BuyerCommittedTapes` | GET writes DB |
| 18 | `supertransfer/support_super_transfer.py:deliver_documents_bulk` | Partial SFTP success |
| 19 | `freedom/views/pre_close.py` | Sets confirmed outside MSR service |
| 20 | `duediligence/utils/rules/threaded_rule_check.py` | Background QC races |
| 21 | `secondlien/supporting/support_secondlien_ingestion.py` | SFTP ingest no atomic |
| 22 | `api/views/admin.py:AdminUsersModify` | Missing staff decorator |
| 23 | `super_transfer_client/scripts/stop_cron.sh` | pkill all python3 |
| 24 | `super_transfer_client/scripts/helper_functions.py:ensure_model_context` | Import-time side effects |
| 25 | `api/api_handler.py` (whole file) | 6400-line bottleneck |
| 26 | `Transfer/views.py` | 2700+ lines, RP integration |
| 27 | `freedom/views/views.py` | Investor/counterparty mutations |
| 28 | `msrx-frontend/server/msrxRoutes.js` | 200+ routes, single file |
| 29 | `msrx-frontend/client/src/components/apiHoc.js` | 4000-line API surface |
| 30 | `duediligence/utils/reprocess_loan_helpers.py` | Deletes DDB+S3 |

---

## 23. Test Coverage / Safe Change Map

| MODULE | TESTS? | COVERED | NOT COVERED | SAFE TO REFACTOR? |
|--------|--------|---------|-------------|-------------------|
| `api/` core flows | Partial (`api/tests/`) | user mgmt, par update, process logger | upload, pricing, commit, confirm, SQS | **NO** |
| `freedom/` | Yes (`freedom/tests/`) | pricing model, FNMA, helpers | full commit flow | Partial |
| `duediligence/` | Yes | deals, portfolios, ext API, evaluator | reprocess, Bedrock | Partial |
| `supertransfer/` | Stub (`tests.py`) | Minimal | SFTP delivery, boarding | **NO** |
| `EmailTrading/` | Stub | Minimal | 15s monitor | **NO** |
| `super_transfer_client/` | Notebooks only | Manual | SQS consumer, main loop | **NO** |
| `msrx-frontend/` | **NOT FOUND** | — | Everything | **NO** |
| Express routes | **NOT FOUND** | — | Auth, proxy, S3 | **NO** |

**CI runs:** `.github/workflows/actions.yml` — Ruff + `api.tests` only. [CONFIRMED FROM CODE]

---

## 24. Before-You-Change Guides

### BEFORE CHANGING PRICING
- Read: `support_pricing.py:asset_price_v3`, `msr_pricing.py`
- Tables: `msrx_client_coissue_tape.price` (JSON), `msrx_client_coissue_buyer*`
- Check: async thread completion (`pricing_progress`)
- Test: approved tape → price → verify all buyer keys in price JSON
- **Do not** assume sync HTTP means pricing done

### BEFORE CHANGING COMMIT
- Read: `msr_commit.py:confirm_commit`, `api_handler.py:commit_group`
- **Never** use `ApiCommitConfirm` as reference implementation
- Tables: `commitment` JSON, `status_details.best_ex`
- Test: pre-commit → confirm → verify SQS + DD + loan numbers
- Ask: is external API commit path still active?

### BEFORE CHANGING SUPER TRANSFER
- Read: `support_committing.py:post_loan_to_sqs`, ST `main.py:98-115`
- Verify message contract with worker team
- S3 path must exist before enqueue
- Test: confirm → SQS message → worker processes (need full message shape)
- Check DDB `process_flag` before EC2 deploy

### BEFORE CHANGING AUTH
- Read: `api/views/auth.py`, `base/utils/users.py`
- Express: `auth.js`, `utils.js:refreshToken`
- Test: login, logout (both soft and full), multi-tab, password expiry
- Verify `HTTP_HOSTNAME` header from BFF

### BEFORE CHANGING SCHEDULERS
- Read: `wsgi.py`, `api/urls/urls.py`, `misc.py:leader_election_process`
- Know: `ENV_FLAG` vs `MSRX_ENV`
- Test on EB with 2+ workers — check for duplicate deliveries
- **Do not** add jobs only to URL import path

### BEFORE CHANGING DATABASE MODELS
- Check CASCADE chains (Section 10)
- Run migrations on UAT first
- Watch for CRA app not in INSTALLED_APPS
- Large tables: `msrx_client_coissue_tape`, `msrx_boarding_staging`

---

## 25. Final Takeover Risk Register

| ID | RISK | SEV | COMPONENT | LOCATION | TRIGGER | IMPACT | DETECTION | RECOVERY | PROVEN? | KT? |
|----|------|-----|-----------|----------|---------|--------|-----------|----------|---------|-----|
| R-01 | SQS message missing `loan_id` | P0 | ST integration | `main.py:100`, `support_committing.py:181` | Confirm commit | Loans never processed | SQS depth + no DDB update | Manual notebook? Re-queue with full body | Yes | **P0** |
| R-02 | Confirm before side effects | P0 | Commit | `msr_commit.py:98-133` | Confirm | confirmed without ST/DD | Activity log gaps | Manual scripts | Yes | P1 |
| R-03 | Duplicate ST schedulers | P0 | Scheduler | `api/urls/urls.py:39` | EB multi-worker | Duplicate SFTP | Duplicate files | Leader-only fix | Yes | P1 |
| R-04 | `ApiCommitConfirm` bypass | P0 | External API | `api/views/api.py:284` | API commit-confirm | No ST/DD/numbers | Missing DD loans | Run `confirm_commit` | Yes | **P0** |
| R-05 | Silent SQS failure | P0 | Commit | `support_committing.py:186` | No S3 docs | No processing | "Failed to post" log | Upload docs + manual SQS | Yes | **P0** |
| R-06 | Partial tape upload | P0 | Upload | `api_handler.py:1752` | Upload | Orphan/partial tape | loancount mismatch | Re-upload | Yes | P1 |
| R-07 | DD create no atomic | P0 | DD | `support_committing.py:313` | Confirm | Orphan DD | Missing values | Re-run function | Yes | P1 |
| R-08 | Logout cookie leak | P1 | Frontend auth | `auth.js` postLogout | Logout | Session persists | Cookie present | Manual clear | Yes | P2 |
| R-09 | Stale localStorage auth | P1 | Frontend | `localStorage.js` | Refresh | Ghost UI | 401 on API | Clear storage | Yes | P2 |
| R-10 | `Boarding_Staging.status` never set | P1 | Boarding | `boarding_file.py:28` | Boarding file gen | Empty files | No matching rows | Fix filter or set status | Yes | P1 |
| R-11 | `pre-commit` vs `pre-committed` | P2 | Status | Multiple files | UI filters | Missing tapes in lists | Query mismatch | Standardize strings | Yes | P2 |
| R-12 | `pkill -9 python3` on ST deploy | P1 | ST deploy | `stop_cron.sh` | CodeDeploy | Collateral process kill | Host monitoring | Isolate ST EC2 | Yes | **P0** |
| R-13 | Leader job wipe | P1 | Scheduler | `misc.py:1842` | Leader failover | Missed crons | Job table empty moment | Wait for re-register | Yes | P1 |
| R-14 | No axios timeout | P2 | Express | `utils.js` | Slow Django | Hung requests | 300s nginx 504 | Restart Express | Yes | P2 |
| R-15 | CASCADE delete user | P0 | DB | `msrx/models/*` | Admin delete user | Mass data loss | FK audit | Restore from backup | Yes | P1 |

---

## Chat / Session Recommendation

**Keep this chat** for continuity — prior audit context (roles, pricing, KT questions) is already loaded. Use a **new chat** only for focused deep-dives (e.g., "fix R-01 SQS contract only") to avoid context limit noise.

---

## Related Artifacts

| Document | Relationship |
|----------|--------------|
| `MSRX_BACKEND_DEEP_AUDIT_AND_KT.md` | Business flow + KT questions (don't repeat) |
| `deployement_review_of_super_transfer_cilent.md` | ST deploy (this audit adds failure modes) |
| `hidden_feature.md` | Frontend visibility (referenced in §13) |
| `context/BACKEND_HOTSPOTS.md` | Prior hotspot list (superseded by §22) |
| Canvas: `developer-takeover-forensic-audit.canvas.tsx` | Searchable/filterable version of this audit |

---

*End of forensic audit. Read-only — no source files modified.*
