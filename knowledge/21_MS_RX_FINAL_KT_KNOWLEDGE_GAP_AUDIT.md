# MSRX Final KT Knowledge-Gap Audit

**Audience:** Development/support team taking over MSRX (not product owners)  
**Date:** 2026-07-24  
**Scope:** `msrx_v2.0`, `msrx-frontend`, `super_transfer_client` + all prior audits in this session  
**Method:** Read-only re-verification of prior unknowns against code; new gap hunt; contradiction analysis  
**Companion:** [20_Developer_Takeover_Forensic_Audit.md](./20_Developer_Takeover_Forensic_Audit.md)

**Evidence labels:** `[CONFIRMED FROM CODE]` · `[RESOLVED FROM CODE]` · `[INFERRED]` · `[UNKNOWN — MUST ASK]` · `[CONTRADICTION]`

**Central question:** *If the existing MSRX developers disappear after KT, what must we extract from them beforehand to safely operate, debug, deploy, and modify this system?*

---

## Phase 1 — Prior Unknowns Re-Verified

Items from prior audits were re-checked in source. **Resolved items are removed from the KT list.** **Confirmed gaps remain.**

### Resolved from code (do NOT ask in KT)

| Prior unknown | Resolution | Evidence |
|---------------|------------|----------|
| Is Express BFF a separate repo? | **No** — `msrx-frontend` IS the BFF (Express + React) | `msrx-frontend/server/index.js`, `msrxRoutes.js` |
| What auth mechanism? | DRF Token via httpOnly cookie proxy | `api/views/auth.py`, `server/routes/auth.js` |
| `committed_buyer` field? | **Does not exist** — use `commitment.buyer_id` | Grep: no matches |
| Celery/Redis? | **Not present** | No celery.py, no redis client |
| `transfer_complete` status actively set? | **No setter found** — legacy comment only | Grep `transfer_complete =`: no matches |
| Is `commit-confirm` API mounted? | **Yes, active** | `api/urls/index.py:179` → `ApiCommitConfirm` |
| Does ST worker require `loan_id` in SQS body? | **Yes** — hard gate | `super_transfer_client/scripts/main.py:100` |
| Does Django producer send `loan_id`? | **No** — only `seller-loan_id` | `support_committing.py:181` |
| Does worker call `STLoanLookupView`? | **No** — lookup exists for Lambda, not used by worker | `loanviews.py:228-232` vs worker code |
| ST deploy mechanism? | CodeDeploy → EC2 + crontab + `process_flag` DDB gate | `appspec.yml`, `process_flag.py` |
| Django auto-migrate on deploy? | **No** — only `collectstatic` in ebextensions | `.ebextensions/django.config` |
| Branch promotion pattern? | PR patch workflow: feature → uat/demo/Live with auto patch PRs to lower envs | `.github/workflows/patch.yml` |

### Confirmed gaps (remain KT questions)

All items below could **not** be answered from code alone.

---

## Phase 2 — New Knowledge Gaps by Domain

### Production infrastructure [UNKNOWN — MUST ASK]

Code references AWS resources by **name pattern** but not account topology:

| Resource | What code shows | What we cannot know |
|----------|-----------------|---------------------|
| Elastic Beanstalk | WSGI, `.ebextensions`, nginx 300s/400MB | Instance count, instance types, autoscaling, which env names map to which EB app |
| RDS | Host in settings (`bwftwebappsmall...`), DB names per env | Backup schedule, restore procedure, who has access, read replicas |
| S3 | `msrx{env}`, `supertransfer-{env}`, `priced_tapes/`, `SuperTransfer/` | Lifecycle policies, versioning, cross-account access |
| SQS | `loansToprocess-{env}`, `filesToBedrock-{env}` | DLQ config, redrive policy, visibility timeout overrides, message retention |
| DynamoDB | `supertransfer-{env}DB`, `supertransfer-deploymentDB` | Who creates initial loan records, TTL, backup |
| Secrets Manager | ST uses `API_KEYS`, `msrx-urls`, `SUPER_TRANSFER_AWS_VARIABLES` ARNs | Rotation schedule, who manages, IAM policies |
| IAM | Long-lived `AWS_ACCESS_KEY` in Django settings | Whether EB uses instance roles vs keys in prod |
| SFTP | `sftp.bluewater.com` (LIVE/Demo in ST env_variables) | Host ownership, credential rotation, IP whitelist |
| ST EC2 | CodeDeploy destination `/home/ec2-user/super_transfer_client/` | Instance count per env, co-hosted services, GPU requirement |
| DNS/TLS | Hostnames in `ALLOWED_HOSTS` | Certificate management, CloudFront?, Route53 ownership |

**`config.py`** referenced by ST `env_variables.py:8` but **not in repo** — deployed artifact with `account_id`. [CONFIRMED FROM CODE]

### Deployment [UNKNOWN — MUST ASK]

| Gap | Code evidence | Missing |
|-----|---------------|---------|
| LIVE migration procedure | No migrate in ebextensions | Who runs `migrate`, when, rollback |
| Frontend deploy | EB config exists (`msrx-frontend/.ebextensions/`) | Build pipeline, `prebuild-script`, NPM_TOKEN, branch→env |
| Backend deploy | EB + WSGI | Who clicks deploy, approval gates, hotfix path |
| ST deploy | CodeDeploy + `process_flag=false` + 600s sleep | Who toggles flag, notification recipients |
| Scheduler after deploy | Leader election restarts; URL-import schedulers per worker | Expected duplicate delivery window |
| Zero-downtime | Not documented | Rolling deploy behavior, in-flight requests |

### Production operations [UNKNOWN — MUST ASK]

| Operation | Code path exists | Operational procedure unknown |
|-----------|------------------|-------------------------------|
| ST loan reprocess | `duediligence/reprocess_loan/<id>/` | Who approves, when used, prod frequency |
| Failed SQS post recovery | `post_loan_to_sqs` returns False silently | Manual re-queue procedure |
| Stuck tape (upload/pricing/commit) | `status_details.*_progress` fields | Runbook steps |
| Loan number pool exhaustion | `start_loan_number_monitoring` cron + email alerts | Who receives, replenishment procedure |
| Email monitor duplicate | `email_monitor_duplicate_check` emails BW | Who acts on alert |
| Boarding file missing | `Boarding_Staging` booleans | Manual regeneration steps |
| Data fix SQL | Not in repo | Whether prod SQL is ever run ad hoc |
| `phagevolve_ingestion.py` | **Not in repo** (mentioned in handover docs) | Whether still runs, where |

### Monitoring [UNKNOWN — MUST ASK]

| What code has | What code lacks |
|---------------|----------------|
| `APIActivityLog`, `User_Activity_Log` DB tables | CloudWatch log group names |
| Email alerts (loan numbers low, email monitor duplicate, scheduler missed job) | Pager/on-call rotation |
| EB enhanced health (`.ebextensions/enhanced-health.config`) | Dashboards, Sentry, Datadog |
| ST `DO_NOT_DELETE_THIS.txt` cron log | Centralized log aggregation |
| `print()` in ST worker on failure | Alert routing |

**Key question for every workflow:** *How would the current team know this failed in production?* — For most paths, answer is **email to specific people** or **manual user report**, not automated alerting. [INFERRED from code]

### External integrations — per-integration KT gaps

| Integration | Code entry | Unknown for takeover |
|-------------|------------|----------------------|
| **O365/Graph** | `EmailTrading/utils.py`, per-brand Azure IDs | Token refresh failures, who renews app registrations |
| **Super Transfer SQS** | `post_loan_to_sqs` | Message enrichment (Lambda?), DLQ, recovery |
| **Bedrock SQS** | `support_bedrock_process_helpers.py` | Consumer owner, retry |
| **FNMA** | `freedom/supporting/pricing/agency/fnma_api.py` | Prod vs sandbox creds rotation, rate limits, outage fallback |
| **FHLMC** | `freddie_contract_commit.py` | Same |
| **PHH par** | `support_par.py`, `Grid_Converter.py` | Active in prod?, outage behavior |
| **RoundPoint SFTP** | `analytics/support_ftp/file_transfer.py` | Schedule owner, file format changes contact |
| **Laura Mac** | `LAURA_MAC_*` settings, UAT host in shared.py | Prod credentials, vendor escalation |
| **EPIC** | `supertransfer/supporting/guidance.py`, LIVE vs TEST creds | Prod usage scope, failure impact |
| **Voxtur/InfoEx** | `voxtur/supporting/api.py` (Okta) | Cert expiry, rate limits |
| **Benutech** | `title_toolbox_api.py` | Contract, outage fallback |
| **Investor Connect / Encompass** | `Transfer/views.py`, EM API | Active clients, credential owner |
| **AWS Textract** | Bucket `textraction` referenced | Who pays, active vs legacy |
| **Lambda (ST enrichment)** | `STLoanLookupView` docstring "used by Lambda" | Is it deployed? What triggers it? |

### Database operations [UNKNOWN — MUST ASK]

| Gap | Why it matters |
|-----|----------------|
| Backup/restore procedure | No code documentation |
| Which table is SOT when duplicates exist (`Boarding_Staging` vs `rp_boarding_staging_table`) | Both have active code paths |
| `user_details` JSON schema per client | Flags gate features; no JSON schema in repo |
| `status_details` JSON evolution | Breaking changes risk |
| Prod data conventions (loan numbers, seller codes) | Business rules in data |
| Archive/cleanup jobs | Unknown if any run |

### Business rules required for safe development [UNKNOWN — MUST ASK]

| Rule area | Code shows multiple paths | Need prod truth |
|-----------|---------------------------|-----------------|
| Active upload path | v1 `uploadtape_csv` vs v2 (RP format) | Which sellers use which |
| Active commit path | Wizard `confirm_commit` vs `ApiCommitConfirm` vs portfolio | Which clients use which |
| Pricing authority | Grid + middleware both in `asset_price_v3` | Which is authoritative per buyer |
| Best execution | Multiple algorithms | Business rule for winner selection |
| Commit reversal | `auto_resell_async` exists | Is reversal supported in prod? |
| Partial commit | `commit_details: full/partial` | Legal/ops meaning |
| `super_transfer_commit_check` | Per-seller `user_details` flag | Which sellers require it |
| 600-second window on `ApiCommitConfirm` | Only confirms if upload < 10 min ago | Why? Who uses this? |

### Legacy vs active [UNKNOWN — MUST ASK]

| Item | Code state | Production status unknown |
|------|------------|---------------------------|
| `CRA` app | Not in INSTALLED_APPS; URL + LIVE cron active | Is CRA live? |
| `rp` boarding table | Legacy model; `Transfer/views.py` still imports | Still written? |
| `commit_portfolio_level` | Exists; loan-level is primary UI path | Still used? |
| `ApiCommitConfirm` | Active route; bypasses full pipeline | Which external client? |
| `TapeManager` v1 converters | Still routed | Per-seller usage? |
| Freedom `wholeloan-shadow-bid` | No frontend references | Email-only workflow? |
| `empower_commit_report_send` cron | Defined, never registered | Ever needed? |
| `phagevolve_ingestion.py` | Not in repo | External script still running? |

---

## Phase 3 — Contradiction Hunt

| ID | SOURCE A | SOURCE B | CONFLICT | PROD RISK | KT QUESTION |
|----|----------|----------|----------|-----------|-------------|
| C-01 | Django `post_loan_to_sqs` sends only `seller-loan_id` (`support_committing.py:181`) | ST `main.py:100` requires `loan_id` in body to call `processLoan` | Producer/consumer contract mismatch | **Loans may never process; messages deleted** | What enriches messages with `loan_id` before worker consumes? Is Lambda deployed? |
| C-02 | `ApiCommitConfirm` sets `confirmed` + resell only (`api.py:284-304`) | `confirm_commit` runs SQS + DD + loan numbers (`msr_commit.py:98+`) | Two confirm paths with different side effects | **External API confirms without ST/DD** | Who uses `POST /msrx/api/commit-confirm/`? Can it be disabled? |
| C-03 | Model comment: `pre-committed` (`coissue.py:19`) | Code sets/checks `pre-commit` (`commit_group`, `msr_commit.py:98`) | Status string inconsistency | **UI filters may miss tapes** (`views.py:209` accepts `pre-committed` query) | Which string is canonical in prod data? |
| C-04 | `Boarding_Staging.status='Processed'` in SQL filter (`boarding_file.py:28`) | No Python code sets `Boarding_Staging.status` | Filter may never match | **Boarding files empty** | Is boarding driven by `cleared`/`delivered` booleans instead? |
| C-05 | ST `misc.py:16` comment: `seller_id_buyer_id-loan_number` format | Actual format: `{seller}-{buyer}_{loan}` (Django + DDB) | Documentation wrong in worker types | Developer confusion | Confirm composite key format is authoritative |
| C-06 | `CRA` commented out of INSTALLED_APPS (`shared.py:101`) | CRA URLs mounted + LIVE cron jobs (`urls.py:29`, `misc.py:1883`) | App disabled but jobs/URLs active | **Runtime errors or silent failures** | Is CRA intentionally hybrid? Should we fix or remove? |
| C-07 | Django settings `supertransfer-dev` bucket (settings files) | Runtime `supertransfer-{MSRX_ENV.lower()}` (`support_committing.py:169`) | Two bucket naming patterns | Wrong bucket in edge cases | Which bucket name is correct per env? |
| C-08 | Full logout calls Django logout (`auth.js`) | `auth` httpOnly cookie not cleared on full logout | Session persists after "logout" | **Security / ghost sessions** | Is this known? Workaround? |
| C-09 | `commitment_check` in ST can return False and skip processing (`query_msrx.py:56-57`) | `main.py:115` still deletes SQS message | Unconfirmed loans removed from queue | **Silent job loss** | Is commit check expected to block? How to recover? |
| C-10 | `create_commit_dd_records` runs **after** SQS post (`msr_commit.py:133` before `:220`) | Worker may need DD `loan_id` in SQS message | Ordering race | **Worker runs before DD record exists** | Is Lambda enrichment timed after DD create? |

---

## Phase 4 — Final KT Question Bank

Format: evidence-backed questions only. ~35 questions total.

---

## KT-001 — SQS loan_id enrichment path

**CATEGORY:** Super Transfer / AWS  
**QUESTION TO ASK:** "After Django sends `loansToprocess` messages with only `seller-loan_id`, what component adds `loan_id` before the Super Transfer worker processes them? Is there a Lambda, Step Function, or second producer?"  
**WHY WE NEED TO ASK:** Worker hard-gates on `loan_id` (`main.py:100`) but Django does not send it (`support_committing.py:181`). Worker does not call `STLoanLookupView`.  
**WHAT WE ALREADY KNOW:** `STLoanLookupView` exists with API key, docstring says "used by Lambda" (`loanviews.py:228-232`). Manual notebook uses full message shape.  
**WHAT IS UNKNOWN:** Production enrichment path, timing relative to DD record creation.  
**EVIDENCE:** `super_transfer_client/scripts/main.py:100`, `msrx_v2.0/api/supporting/support_committing.py:181`  
**RISK IF WE DON'T KNOW:** Critical — loans never processed, messages deleted  
**WHO SHOULD ANSWER:** Backend lead + DevOps

---

## KT-002 — Failed post_loan_to_sqs recovery

**CATEGORY:** Operations / Super Transfer  
**QUESTION TO ASK:** "When `post_loan_to_sqs` returns False during confirm (no S3 docs or SQS error), what is the production recovery procedure?"  
**WHY WE NEED TO ASK:** Bare `except: return False`; commit still succeeds; only activity_log entry.  
**WHAT WE ALREADY KNOW:** Precondition: S3 folder `SuperTransfer/{seller}/{buyer}/{loan}/` non-empty.  
**WHAT IS UNKNOWN:** Who uploads docs, when, and how ops re-triggers processing.  
**EVIDENCE:** `support_committing.py:157-187`, `msr_commit.py:133-152`  
**RISK:** Critical — confirmed loans never enter ST pipeline  
**WHO:** Operations + Backend

---

## KT-003 — Who uploads SuperTransfer S3 documents

**CATEGORY:** Operations / Workflow  
**QUESTION TO ASK:** "Who or what uploads PDFs to `SuperTransfer/{seller}/{buyer}/{loan}/` — seller SFTP, frontend upload, Transfer module, or manual ops? At what point relative to commit confirm?"  
**WHY WE NEED TO ASK:** SQS only fires if folder exists; multiple upload paths in code (frontend S3, `support_super_transfer.py`).  
**EVIDENCE:** `msrx-frontend/server/superTransfer/s3Bucket.js`, `supertransfer/support_super_transfer.py:252`  
**RISK:** Critical — no docs = no SQS = no processing  
**WHO:** Operations + Backend

---

## KT-004 — ApiCommitConfirm external consumers

**CATEGORY:** Workflow / Integration  
**QUESTION TO ASK:** "Is `POST /msrx/api/commit-confirm/` used by any production client? If yes, which one and is the 600-second upload window intentional?"  
**WHY WE NEED TO ASK:** Active route bypasses `confirm_commit` — no SQS, DD, loan numbers; only resell thread.  
**EVIDENCE:** `api/urls/index.py:179`, `api/views/api.py:249-304`  
**RISK:** Critical — external confirms without downstream effects  
**WHO:** Backend lead

---

## KT-005 — LIVE database migration procedure

**CATEGORY:** Deployment / Database  
**QUESTION TO ASK:** "What is the exact procedure to run Django migrations on LIVE? Who executes, is there a maintenance window, and what is the rollback plan?"  
**WHY WE NEED TO ASK:** `.ebextensions/django.config` only runs `collectstatic`, not migrate.  
**EVIDENCE:** `msrx_v2.0/.ebextensions/django.config`  
**RISK:** Critical — schema drift or failed deploy  
**WHO:** DevOps + Backend lead

---

## KT-006 — EB instance count and scheduler ownership

**CATEGORY:** AWS / Operations  
**QUESTION TO ASK:** "How many Elastic Beanstalk instances run per environment, and is only one expected to be the APScheduler leader? Are duplicate Super Transfer SFTP schedulers a known issue?"  
**WHY WE NEED TO ASK:** Leader election exists but ST/boarding schedulers start per worker without leader gate (`api/urls/urls.py:39-45`).  
**EVIDENCE:** `wsgi.py:24`, `api/urls/urls.py:39-45`, `misc.py:leader_election_process`  
**RISK:** Critical — duplicate deliveries, missed crons  
**WHO:** DevOps

---

## KT-007 — ENV_FLAG production values

**CATEGORY:** AWS / Configuration  
**QUESTION TO ASK:** "What is `ENV_FLAG` set to on each EB environment? Is it `CLOUD` for UAT/DEMO/LIVE?"  
**WHY WE NEED TO ASK:** Scheduler only runs when `ENV_FLAG=CLOUD`, separate from `MSRX_ENV`.  
**EVIDENCE:** `api/utils/misc.py:1827-1831`  
**RISK:** Critical — no crons if misconfigured  
**WHO:** DevOps

---

## KT-008 — Production observability stack

**CATEGORY:** Monitoring  
**QUESTION TO ASK:** "Where do you look for production errors today — CloudWatch log groups, email alerts, Teams, something else? Is there an on-call rotation?"  
**WHY WE NEED TO ASK:** No Sentry/CloudWatch SDK in app; LOGGING commented out; alerts appear email-based.  
**EVIDENCE:** `shared.py:157-172` commented, `support_util.py` loan number alert emails  
**RISK:** High — cannot debug incidents  
**WHO:** DevOps + Operations

---

## KT-009 — SQS DLQ and redrive policy

**CATEGORY:** AWS / Super Transfer  
**QUESTION TO ASK:** "Do `loansToprocess-{env}` and `filesToBedrock-{env}` queues have DLQs configured? What is the redrive/replay procedure?"  
**WHY WE NEED TO ASK:** No DLQ handling in application code; messages deleted even when not processed.  
**EVIDENCE:** `main.py:115`, `support_committing.py:186`  
**RISK:** Critical — lost messages with no recovery  
**WHO:** DevOps

---

## KT-010 — DynamoDB initial loan record creator

**CATEGORY:** Super Transfer / AWS  
**QUESTION TO ASK:** "What creates the initial DynamoDB record in `supertransfer-{env}DB` before the worker runs? S3 event, Lambda, manual, or something else?"  
**WHY WE NEED TO ASK:** No `put_item` in monorepo; only `update_item` in worker. Notebook has commented put_item.  
**EVIDENCE:** `helper_functions.py:2825`, `Manual_Loan_Process.ipynb`  
**RISK:** High — worker may fail on empty DDB lookup  
**WHO:** Backend + DevOps

---

## KT-011 — ST EC2 deployment and co-hosted services

**CATEGORY:** Deployment / Super Transfer  
**QUESTION TO ASK:** "Is the Super Transfer EC2 instance dedicated per environment? Does `stop_cron.sh` killing all `python3` affect other services on the same host?"  
**WHY WE NEED TO ASK:** `pkill -9 python3` in stop script.  
**EVIDENCE:** `super_transfer_client/scripts/stop_cron.sh`  
**RISK:** High — collateral damage on deploy  
**WHO:** DevOps

---

## KT-012 — Boarding staging source of truth

**CATEGORY:** Database / Workflow  
**QUESTION TO ASK:** "In production, is boarding driven by `msrx_boarding_staging` or `rp_boarding_staging_table`? Is `Boarding_Staging.status` used or only the boolean flags?"  
**WHY WE NEED TO ASK:** SQL filters `status='Processed'` but no Python setter; booleans used elsewhere.  
**EVIDENCE:** `duediligence/utils/boarding_file.py:28`, `msrx/models/boarding_staging.py`  
**RISK:** High — boarding files may be empty  
**WHO:** Backend lead

---

## KT-013 — Active pricing engine per buyer

**CATEGORY:** Workflow / Business rules  
**QUESTION TO ASK:** "For coissue tapes, when both grid and middleware (DPX) pricing run, which result is authoritative? Are there buyers on middleware-only or grid-only?"  
**WHY WE NEED TO ASK:** Both run in `asset_price_v3`; no code declares winner logic clearly.  
**EVIDENCE:** `api/supporting/support_pricing.py:1403+`  
**RISK:** High — wrong prices if we change pricing code  
**WHO:** Backend lead + Operations

---

## KT-014 — Best execution business rule

**CATEGORY:** Business rules  
**QUESTION TO ASK:** "How is the winning buyer selected at commit — highest price, cap-aware, buyer priority, or contractual rules per seller?"  
**WHY WE NEED TO ASK:** Multiple code paths (`commit_portfolio_level`, `msr_best_ex`, seasoned cap logic).  
**EVIDENCE:** `support_pricing.py`, `freedom/supporting/pricing/msrx/msrx.py`  
**RISK:** High — incorrect commits  
**WHO:** Backend lead + Operations

---

## KT-015 — Commit reversal policy

**CATEGORY:** Business rules / Operations  
**QUESTION TO ASK:** "Can a confirmed commitment be reversed in production? If yes, what is the procedure and which systems must be updated (DB, S3, SQS, DD, boarding)?"  
**WHY WE NEED TO ASK:** `auto_resell_async` exists; no documented reversal workflow.  
**EVIDENCE:** `support_committing.py:60-96`  
**RISK:** High — data corruption if we attempt reversal incorrectly  
**WHO:** Operations + Backend

---

## KT-016 — Production upload path (v1 vs v2)

**CATEGORY:** Workflow  
**QUESTION TO ASK:** "Which sellers use `uploadtape_csv` vs `uploadtape_csv/v2` (RP format) in production?"  
**WHY WE NEED TO ASK:** Both active; v2 comment says RP commit format.  
**EVIDENCE:** `api/urls/index.py:101-102`  
**RISK:** Medium — wrong path if we change upload code  
**WHO:** Backend + Operations

---

## KT-017 — CRA app production status

**CATEGORY:** Legacy  
**QUESTION TO ASK:** "CRA is removed from INSTALLED_APPS but URLs and LIVE cron jobs still run. Is CRA active in production? Should we re-enable the app or remove the jobs?"  
**EVIDENCE:** `shared.py:101`, `ebdjango/urls.py:29`, `misc.py:1883-1887`  
**RISK:** Medium — runtime errors or dead cron load  
**WHO:** Backend lead

---

## KT-018 — AWS credentials: keys vs IAM roles

**CATEGORY:** Security / AWS  
**QUESTION TO ASK:** "Do EB instances use IAM instance roles or the `AWS_ACCESS_KEY`/`AWS_SECRET_KEY` from environment variables?"  
**WHY WE NEED TO ASK:** All boto3 calls pass explicit keys from `get_env_var`.  
**EVIDENCE:** `support_committing.py:146-147`, `shared.py:251-252`  
**RISK:** High — rotation/security model  
**WHO:** DevOps

---

## KT-019 — RDS backup and restore

**CATEGORY:** Database  
**QUESTION TO ASK:** "What is the RDS backup schedule for LIVE, and has a restore been tested? Who can authorize a point-in-time recovery?"  
**RISK:** Critical — data loss scenario  
**WHO:** DevOps + DBA

---

## KT-020 — Frontend deployment pipeline

**CATEGORY:** Deployment  
**QUESTION TO ASK:** "How is msrx-frontend deployed to each environment — branch mapping, build steps, who runs prebuild-script, and where are BACKEND_URL and secrets set?"  
**WHY WE NEED TO ASK:** prebuild fetches platform configs; EB config references NPM_TOKEN.  
**EVIDENCE:** `prebuild-script.js`, `msrx-frontend/.ebextensions/01_files.config`  
**RISK:** High — wrong backend URL breaks all API calls  
**WHO:** DevOps + Frontend lead

---

## KT-021 — Secrets Manager rotation

**CATEGORY:** Security / AWS  
**QUESTION TO ASK:** "What is the rotation schedule and procedure for Secrets Manager secrets used by Super Transfer (`API_KEYS`, `msrx-urls`, `SUPER_TRANSFER_AWS_VARIABLES`)?"  
**EVIDENCE:** `super_transfer_client/scripts/env_variables.py:19-22`  
**RISK:** High — worker outage on expired secrets  
**WHO:** DevOps

---

## KT-022 — FNMA/FHLMC outage procedure

**CATEGORY:** Integration  
**QUESTION TO ASK:** "What happens operationally when FNMA or FHLMC pricing APIs are down? Is there a manual fallback or do tapes stay in `mbs failed`?"  
**EVIDENCE:** `freedom/views/pricing.py:338` sets `mbs failed`  
**RISK:** Medium — stuck Freedom tapes  
**WHO:** Backend + Operations

---

## KT-023 — PHH par rate integration status

**CATEGORY:** Integration  
**QUESTION TO ASK:** "Is PHH realtime par pricing active in LIVE? Who is the technical contact if the integration breaks?"  
**EVIDENCE:** `api/supporting/support_par.py`  
**RISK:** Medium  
**WHO:** Backend lead

---

## KT-024 — RoundPoint SFTP operational ownership

**CATEGORY:** Integration / Operations  
**QUESTION TO ASK:** "Who monitors the RoundPoint trial balance SFTP job, and what do you do when files are missing or malformed?"  
**EVIDENCE:** `analytics/support_ftp/file_transfer.py`, cron in `misc.py`  
**RISK:** Medium  
**WHO:** Operations

---

## KT-025 — Laura Mac and EPIC production usage

**CATEGORY:** Integration  
**QUESTION TO ASK:** "Which LIVE workflows call Laura Mac and EPIC? Are EPIC TEST credentials ever accidentally used in DEMO/LIVE?"  
**EVIDENCE:** `live.py` EPIC_PROD_* vs `uat.py` EPIC_TEST_*  
**RISK:** Medium  
**WHO:** Backend lead

---

## KT-026 — Reprocess loan operational procedure

**CATEGORY:** Operations  
**QUESTION TO ASK:** "When do you use `POST /duediligence/reprocess_loan/<id>/` in production? What approval is required?"  
**EVIDENCE:** `duediligence/views/reprocess_loanviews.py`, `reprocess_loan_helpers.py`  
**RISK:** Medium — destructive cleanup of DDB + S3  
**WHO:** Operations + Backend

---

## KT-027 — aggregator_seller_flag data integrity

**CATEGORY:** Roles / Data  
**QUESTION TO ASK:** "Is `aggregator_seller_flag` reliably set True for all production aggregator sellers, or do you rely on `Client_Aggregator_Seller` relationship existence?"  
**WHY WE NEED TO ASK:** `AggregatorSellerCreate` does not set flag; many code paths filter on flag.  
**EVIDENCE:** `api/views/aggregator.py`, `msrx/models/user.py`  
**RISK:** Medium — sellers invisible in pricing UI  
**WHO:** Backend lead

---

## KT-028 — Investor portal logins

**CATEGORY:** Roles  
**QUESTION TO ASK:** "Do any `user_role=investor` accounts have MSRX portal logins, or are investors Freedom-only entities?"  
**EVIDENCE:** `freedom/views/*`, `get_investor_for_correspondent`  
**RISK:** Low-Medium  
**WHO:** Backend lead

---

## KT-029 — Portfolio-level commit usage

**CATEGORY:** Legacy / Workflow  
**QUESTION TO ASK:** "Is `commit_portfolio_level` still used by any production client or is everything loan-level now?"  
**EVIDENCE:** `api/urls/index.py`, `api_handler.py:commit_portfolio_level`  
**RISK:** Medium if still used  
**WHO:** Backend lead

---

## KT-030 — Emergency hotfix procedure

**CATEGORY:** Deployment  
**QUESTION TO ASK:** "What is the emergency hotfix procedure for LIVE — can you deploy directly to LIVE or must it go dev→uat→demo→Live? Who approves?"  
**EVIDENCE:** `patch.yml` shows promotion chain  
**RISK:** Critical for incident response  
**WHO:** DevOps + Engineering manager

---

## KT-031 — O365 token failure handling

**CATEGORY:** Integration / Operations  
**QUESTION TO ASK:** "When O365 tokens in S3 expire or auth fails, who gets alerted and what is the fix procedure?"  
**EVIDENCE:** `EmailTrading/utils.py`, S3 `o365_token.txt`  
**RISK:** High — all email notifications stop  
**WHO:** Operations

---

## KT-032 — Bedrock queue consumer ownership

**CATEGORY:** Integration / AWS  
**QUESTION TO ASK:** "Who owns the consumer for `filesToBedrock-{env}` SQS queue? Is it the same team as Super Transfer?"  
**EVIDENCE:** `duediligence/utils/support_bedrock_process_helpers.py`  
**RISK:** Medium — DD docs stuck unprocessed  
**WHO:** Backend + DevOps

---

## KT-033 — SFTP partner credential ownership

**CATEGORY:** Integration / Security  
**QUESTION TO ASK:** "For each SFTP integration (buyer delivery, RoundPoint, second lien, seller ingest), who owns credentials and what is the renewal process?"  
**EVIDENCE:** Multiple SFTP paths across `supertransfer/`, `secondlien/`, `analytics/`  
**RISK:** High — delivery failures  
**WHO:** Operations + DevOps

---

## KT-034 — user_details JSON conventions

**CATEGORY:** Database / Configuration  
**QUESTION TO ASK:** "Is there documentation or a template for `MSRX_User.user_details` JSON per client? Which flags are safety-critical and must not be changed?"  
**EVIDENCE:** Feature flags throughout (`msrx_viewer`, `super_transfer_commit_check`, etc.)  
**RISK:** Medium — breaking client configs  
**WHO:** Backend lead + Operations

---

## KT-035 — phagevolve_ingestion status

**CATEGORY:** Legacy / Operations  
**QUESTION TO ASK:** "Is `phagevolve_ingestion.py` or any external script still running on a schedule outside this repo?"  
**EVIDENCE:** Referenced in handover docs; not in repo  
**RISK:** Medium — unknown background process  
**WHO:** Operations + Backend lead

---

## Phase 5 — Prioritization

### MUST ASK IN KT (blocking takeover)

| ID | Question (short) | Risk |
|----|------------------|------|
| KT-001 | SQS loan_id enrichment (Lambda?) | Lost ST processing |
| KT-002 | Failed post_loan_to_sqs recovery | Confirmed loans stuck |
| KT-003 | Who uploads SuperTransfer S3 docs | No SQS trigger |
| KT-004 | ApiCommitConfirm consumers | Wrong confirm path |
| KT-005 | LIVE migration procedure | Deploy failure |
| KT-006 | EB instances + scheduler duplicates | Duplicate/missed jobs |
| KT-007 | ENV_FLAG values | No crons |
| KT-009 | SQS DLQ/redrive | Lost messages |
| KT-010 | DynamoDB initial record creator | Worker failures |
| KT-019 | RDS backup/restore | Data loss |
| KT-030 | Emergency hotfix procedure | Incident response |

### SHOULD ASK

KT-008, KT-011, KT-012, KT-013, KT-014, KT-015, KT-018, KT-020, KT-021, KT-026, KT-031, KT-033

### CAN ASK LATER

KT-016, KT-017, KT-022, KT-023, KT-024, KT-025, KT-027, KT-028, KT-029, KT-032, KT-034, KT-035

---

## Phase 6 — 60-Minute KT Call Plan

### 0–10 min — Production architecture & deployment
**Lead:** DevOps

| # | Exact wording | Who | Why | Follow-up |
|---|---------------|-----|-----|-----------|
| 1 | "Walk us through one LIVE deploy for Django and one for frontend — who clicks what, in what order?" | DevOps | No migrate in ebextensions | "Where do you run migrations?" |
| 2 | "How many EB instances per env and what is ENV_FLAG set to?" | DevOps | Scheduler depends on it | "Do you know about duplicate ST schedulers per worker?" |
| 3 | "IAM roles or access keys on EB?" | DevOps | Security model | "Rotation procedure?" |

### 10–20 min — Critical workflows (commit & pricing)
**Lead:** Backend developer

| # | Exact wording | Who | Why | Follow-up |
|---|---------------|-----|-----|-----------|
| 4 | "Who uses POST /msrx/api/commit-confirm/ and why does it skip SQS and DD?" | Backend | Two confirm paths | "Can we deprecate it?" |
| 5 | "Grid vs middleware pricing — which wins for a typical buyer?" | Backend | Dual engines | "Any middleware-only buyers?" |
| 6 | "How is best execution / winning buyer chosen?" | Backend + Ops | Multiple algorithms | "Contractual exceptions?" |
| 7 | "Can confirmed commitments be reversed? Procedure?" | Ops | No documented reversal | "Which tables/systems touched?" |

### 20–30 min — Super Transfer & operational jobs
**Lead:** Backend + DevOps

| # | Exact wording | Who | Why | Follow-up |
|---|---------------|-----|-----|-----------|
| 8 | "What adds loan_id to SQS messages after Django sends seller-loan_id only?" | Backend/DevOps | **#1 risk** | "Is Lambda deployed? Show us." |
| 9 | "Who uploads docs to SuperTransfer S3 path and when vs confirm?" | Ops | SQS precondition | "SFTP vs frontend upload?" |
| 10 | "What do you do when post_loan_to_sqs fails — runbook?" | Ops | Silent failure | "Manual re-queue steps?" |
| 11 | "ST deploy: who toggles process_flag and is EC2 dedicated?" | DevOps | pkill python3 risk | "Co-hosted services?" |

### 30–40 min — Database & recovery
**Lead:** DevOps + Backend

| # | Exact wording | Who | Why | Follow-up |
|---|---------------|-----|-----|-----------|
| 12 | "RDS backup schedule and last restore test?" | DevOps | Data loss | "PITR procedure?" |
| 13 | "Boarding: msrx_boarding_staging or rp table? status field used?" | Backend | SQL filter bug | "Who generates boarding files?" |
| 14 | "When do you use reprocess_loan API?" | Ops | Destructive op | "Approval required?" |
| 15 | "Any production SQL run ad hoc? Who approves?" | Ops + DBA | Data integrity | "Examples?" |

### 40–50 min — Integrations & monitoring
**Lead:** Backend + Ops

| # | Exact wording | Who | Why | Follow-up |
|---|---------------|-----|-----|-----------|
| 16 | "Where do you look when something fails at 2 AM?" | Ops | No Sentry in code | "CloudWatch groups? Email?" |
| 17 | "SQS DLQ configured? Replay procedure?" | DevOps | Messages deleted in app | "Show AWS console." |
| 18 | "FNMA/PHH/RP SFTP — which are LIVE-critical and who is vendor contact?" | Ops | Integration outages | "Fallback?" |
| 19 | "O365 token expires — who fixes?" | Ops | Email stops | "S3 token path?" |

### 50–60 min — Remaining critical unknowns
**Lead:** Engineering manager

| # | Exact wording | Who | Why | Follow-up |
|---|---------------|-----|-----|-----------|
| 20 | "CRA app disabled but cron runs — intentional?" | Backend | Hybrid state | "Fix plan?" |
| 21 | "Emergency hotfix to LIVE — allowed?" | Eng manager | Incident response | "Approval chain?" |
| 22 | "Anything not in repo we must know about — external scripts, Lambdas, manual processes?" | All | Tribal knowledge | "Document where?" |
| 23 | "Who do we contact for each integration outage?" | Ops | Escalation | "Get contact list." |
| 24 | "What keeps you up at night about this system?" | All | Prioritize risks | Open discussion |

---

## Phase 7 — Don't Let KT End Without These

**The 12 questions we must not leave without answers:**

1. **What enriches SQS `loansToprocess` messages with `loan_id`?** (C-01) — without this, ST pipeline may be broken or depends on invisible Lambda.
2. **Who uploads `SuperTransfer/{seller}/{buyer}/{loan}/` S3 docs and when?** — without this, SQS never fires.
3. **What is the runbook when `post_loan_to_sqs` fails?** — silent failure on every confirm.
4. **Who uses `ApiCommitConfirm` and can we route them to full `confirm_commit`?** — data integrity gap.
5. **LIVE migration procedure and rollback.** — deploy safety.
6. **EB instance count, ENV_FLAG, and scheduler duplicate awareness.** — operational correctness.
7. **SQS DLQ/redrive configuration.** — message recovery.
8. **RDS backup/restore tested procedure.** — disaster recovery.
9. **Production observability: where are logs, who is on-call?** — incident response.
10. **DynamoDB initial record creation for ST loans.** — worker prerequisite.
11. **Emergency hotfix approval chain for LIVE.** — incident deploy authority.
12. **External scripts/Lambdas/services not in these three repos.** — complete system picture.

**Also obtain (not questions — deliverables):**
- Contact list per integration vendor
- AWS console access for dev team (read-only minimum)
- Secrets Manager secret names list (not values)
- CloudWatch log group names per service
- SFTP credential ownership matrix
- One worked example: tape upload → confirm → ST complete (with loan IDs and S3 paths)

---

## Appendix — Chat Session Recommendation

**Keep this chat** for KT prep — all prior audit context is loaded. Use a **new chat** for implementation tasks after KT.

---

*End of KT Knowledge-Gap Audit. Read-only — no source files modified.*
