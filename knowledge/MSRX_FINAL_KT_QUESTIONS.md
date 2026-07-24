# MSRX Final Knowledge Transfer Questions

**Audience:** Development team taking over MSRX production support  
**Date:** 2026-07-24  
**Sources cross-referenced:** `msrx_v2.0`, `msrx-frontend`, `super_transfer_client` audits; `20_Developer_Takeover_Forensic_Audit.md`; `21_MS_RX_FINAL_KT_KNOWLEDGE_GAP_AUDIT.md`; `MSRX_ONBOARDING_GUIDE.md`; `MSRX_BACKEND_DEEP_AUDIT_AND_KT.md`; `MSRX_Frontend_audit.md`; prior handover meeting notes (EC2/S3/SQS/phagevolve — no full transcript in repo)

**Rule applied:** If the answer is confidently derivable from code or prior KT notes, the question is **not** listed below.

---

## 1. Executive Summary

| Metric | Count |
|--------|------:|
| **Total questions** | **32** |
| **P0 — Must ask before takeover** | **11** |
| **P1 — Important** | **14** |
| **P2 — Useful** | **7** |

### Five biggest takeover risks if unanswered

1. **Super Transfer SQS contract** — Django sends `seller-loan_id` only; worker requires `loan_id`; messages may be deleted without processing. Unknown enrichment path (Lambda?).
2. **Silent confirm side-effect failures** — `post_loan_to_sqs` can fail after tape is `confirmed`; no documented recovery runbook.
3. **LIVE deployment + migrations** — No auto-migrate in EB config; rollback/hotfix authority unknown.
4. **Production observability** — No Sentry/CloudWatch SDK in app code; incident detection appears email/manual; on-call unknown.
5. **Duplicate schedulers / ENV_FLAG** — APScheduler leader election + per-worker ST/boarding schedulers; crons may not run or may double-run.

---

## 2. P0 — Must Ask Before Takeover

### KT-001 — Super Transfer SQS message enrichment

**Priority:** P0  
**Area:** Super Transfer / AWS  
**Best person to answer:** Backend lead + DevOps

**What we already know:** Django `post_loan_to_sqs` sends only `{"seller-loan_id": "..."}` (`msrx_v2.0/api/supporting/support_committing.py:181`). Worker `main.py:100` hard-gates on `'loan_id' in res` before `processLoan()`. Worker does **not** call `STLoanLookupView`. `STLoanLookupView` docstring says "used by Lambda" (`loanviews.py:228-232`).

**What is still unknown:** What production component adds `loan_id`, `deal_id`, and related fields before the worker consumes the message; timing vs `create_commit_dd_records`.

**Question to ask:**  
*"After Django posts to `loansToprocess-{env}` with only `seller-loan_id`, what adds `loan_id` before the Super Transfer worker runs — is there a Lambda, Step Function, or second producer deployed outside these three repos?"*

**Why we need this:** Without this, we cannot explain whether confirmed loans are actually processed or silently dropped.

**Evidence:** `super_transfer_client/scripts/main.py:98-115`, `msrx_v2.0/api/supporting/support_committing.py:157-187`

---

### KT-002 — Failed `post_loan_to_sqs` recovery runbook

**Priority:** P0  
**Area:** Operations / Super Transfer  
**Best person to answer:** Operations + Backend lead

**What we already know:** `post_loan_to_sqs` returns `False` on missing S3 docs or SQS error (bare `except`); `confirm_commit` still marks tape `confirmed` (`msr_commit.py:98+`). Only `activity_log` records failure.

**What is still unknown:** Production detection, manual re-queue steps, who is notified.

**Question to ask:**  
*"When confirm succeeds but `post_loan_to_sqs` fails — how do you detect it in production today, and what is the exact step-by-step recovery procedure?"*

**Why we need this:** Confirmed loans can exist with no ST pipeline entry and no user-visible error.

**Evidence:** `msrx_v2.0/api/supporting/support_committing.py:157-187`, `msrx_v2.0/api/supporting/services/msr_commit.py:133-152`

---

### KT-003 — Who uploads SuperTransfer S3 documents and when

**Priority:** P0  
**Area:** Operations / Workflow  
**Best person to answer:** Operations + Backend lead

**What we already know:** SQS fires only if `SuperTransfer/{seller}/{buyer}/{loan}/` is non-empty before `post_loan_to_sqs`. Upload paths exist in frontend BFF (`msrx-frontend/server/superTransfer/s3Bucket.js`), Django (`supertransfer/support_super_transfer.py`), and SFTP schedulers.

**What is still unknown:** Which path is used per client/seller; ordering relative to confirm.

**Question to ask:**  
*"For a typical LIVE coissue confirm, who uploads documents into `SuperTransfer/{seller}/{buyer}/{loan}/` — seller SFTP, portal upload, Transfer module, or manual ops — and at what step relative to confirm?"*

**Why we need this:** No docs → no SQS → no processing, with no frontend error to the user.

**Evidence:** `support_committing.py:169-176`, `msrx-frontend/server/superTransfer/s3Bucket.js`

---

### KT-004 — `ApiCommitConfirm` production consumers

**Priority:** P0  
**Area:** Workflow / Integration  
**Best person to answer:** Backend lead

**What we already know:** `POST /msrx/api/commit-confirm/` is mounted (`api/urls/index.py:179`). Handler sets `confirmed` and starts resell thread only — does **not** call `confirm_commit` (no SQS, DD records, loan numbers, `delivery_month`). 600-second upload window enforced in code.

**What is still unknown:** Which external system/client uses this endpoint in LIVE; whether it is intentional long-term.

**Question to ask:**  
*"Who uses `POST /msrx/api/commit-confirm/` in production today, and is it intentionally supposed to bypass the normal `confirm_commit` pipeline — including Super Transfer, DD record creation, and loan-number assignment?"*

**Why we need this:** External confirms may leave loans in a state the UI and ops tools do not expect.

**Evidence:** `msrx_v2.0/api/views/api.py:249-304`, `api/urls/index.py:179`

---

### KT-005 — LIVE Django migration and rollback procedure

**Priority:** P0  
**Area:** Deployment / Database  
**Best person to answer:** DevOps + Backend lead

**What we already know:** `.ebextensions/django.config` runs `collectstatic` only — no `migrate`. Branch promotion workflow exists (`patch.yml`: feature → uat/demo/Live).

**What is still unknown:** Who runs migrations, when, maintenance window, rollback if migration fails.

**Question to ask:**  
*"Walk us through a LIVE backend deployment today — when and how are Django migrations run, who executes them, and what is the rollback plan if a migration or deploy fails?"*

**Why we need this:** Schema drift or failed deploy can block all API traffic.

**Evidence:** `msrx_v2.0/.ebextensions/django.config`, `msrx_v2.0/.github/workflows/patch.yml`

---

### KT-006 — EB topology, `ENV_FLAG`, and scheduler duplication

**Priority:** P0  
**Area:** AWS / Operations  
**Best person to answer:** DevOps

**What we already know:** Central APScheduler runs only when `ENV_FLAG=CLOUD` and leader elected (`misc.py:1827-1831`, `wsgi.py:24`). ST + boarding `BackgroundScheduler` starts on **every** worker via URL import (`api/urls/urls.py:39-45`) without leader gate.

**What is still unknown:** Instance count per env, actual `ENV_FLAG` values, whether duplicate ST SFTP deliveries are a known/accepted issue.

**Question to ask:**  
*"How many Elastic Beanstalk instances run in DEV, UAT, DEMO, and LIVE, what is `ENV_FLAG` on each, and are duplicate Super Transfer or boarding schedulers a known production issue?"*

**Why we need this:** Crons may never run, or may run N times per schedule.

**Evidence:** `msrx_v2.0/ebdjango/wsgi.py:22-25`, `msrx_v2.0/api/urls/urls.py:39-45`, `msrx_v2.0/api/utils/misc.py:1827-1831`

---

### KT-007 — SQS DLQ configuration and replay procedure

**Priority:** P0  
**Area:** AWS / Super Transfer  
**Best person to answer:** DevOps

**What we already know:** Application code deletes SQS messages even when `commitment_check` fails or `loan_id` is absent (`main.py:115`). No DLQ handling in worker or Django producer.

**What is still unknown:** Whether AWS DLQs exist, redrive policy, ops replay steps.

**Question to ask:**  
*"Do `loansToprocess-{env}` and `filesToBedrock-{env}` have DLQs configured in AWS, and what is your procedure to detect backlog and replay or redrive messages?"*

**Why we need this:** Lost messages have no in-app recovery path.

**Evidence:** `super_transfer_client/scripts/main.py:98-115`, `deployement_review_of_super_transfer_cilent.md` §13

---

### KT-008 — DynamoDB initial loan record creation

**Priority:** P0  
**Area:** Super Transfer / AWS  
**Best person to answer:** Backend lead + DevOps

**What we already know:** Worker uses `update_table` / `query` on `supertransfer-{env}DB`; no `put_item` in monorepo. Notebook has commented `put_item`.

**What is still unknown:** What creates the initial DDB row before worker processing.

**Question to ask:**  
*"What creates the initial DynamoDB record in `supertransfer-{env}DB` for a loan — S3 event, Lambda, Django, manual notebook, or something else not in these repos?"*

**Why we need this:** Worker may fail on empty DDB lookup; recovery depends on knowing the writer.

**Evidence:** `super_transfer_client/scripts/helper_functions.py`, `Manual_Loan_Process.ipynb`

---

### KT-009 — RDS backup, restore, and authorization

**Priority:** P0  
**Area:** Database / DevOps  
**Best person to answer:** DevOps / DBA

**What we already know:** Per-env DB names in settings (`msrx_live_new`, etc.). No backup/restore procedure in repo.

**What is still unknown:** Backup schedule, last restore test, who can authorize PITR.

**Question to ask:**  
*"What is the LIVE RDS backup schedule, has a restore been tested recently, and who can authorize a point-in-time recovery?"*

**Why we need this:** Data-loss scenario with no documented recovery path.

**Evidence:** `msrx_v2.0/ebdjango/settings/*.py`

---

### KT-010 — Emergency LIVE hotfix approval chain

**Priority:** P0  
**Area:** Deployment  
**Best person to answer:** Engineering manager + DevOps

**What we already know:** `patch.yml` automates patch PRs across env branches. No documented hotfix bypass.

**What is still unknown:** Whether direct LIVE deploy is ever allowed, who approves, rollback steps.

**Question to ask:**  
*"For a production incident, can we deploy a hotfix directly to LIVE or must it go dev → uat → demo → Live — and who approves an emergency bypass?"*

**Why we need this:** Incident response authority is undefined.

**Evidence:** `msrx_v2.0/.github/workflows/patch.yml`, `msrx-frontend/.github/workflows/patch.yml`

---

### KT-011 — Services and scripts outside the three repos

**Priority:** P0  
**Area:** Architecture / Operations  
**Best person to answer:** Backend lead + DevOps + Operations

**What we already know:** Handover mentioned `phagevolve_ingestion.py` (not in repo). `STLoanLookupView` implies Lambda. `config.py` referenced by ST worker but not in repo. `apiGoogleSheetsPA.js` in frontend unused.

**What is still unknown:** Full inventory of Lambdas, cron hosts, external scripts, and their owners.

**Question to ask:**  
*"List every production service, Lambda, cron host, or script that is **not** in `msrx_v2.0`, `msrx-frontend`, or `super_transfer_client` but is required for MSRX to work — including where each is deployed and who owns it."*

**Why we need this:** Incomplete system picture causes blind spots on day one.

**Evidence:** Handover notes; `super_transfer_client/scripts/env_variables.py:8`; `loanviews.py:228-232`

---

## 3. P1 — Important Questions

### KT-012 — Production observability and on-call

**Priority:** P1 | **Area:** Monitoring | **Best person:** DevOps + Operations

**What we already know:** `APIActivityLog`, email alerts (loan numbers, email monitor duplicate, scheduler missed job). No Sentry/CloudWatch SDK in app. ST logs to `DO_NOT_DELETE_THIS.txt` and per-loan `.log` files.

**What is still unknown:** CloudWatch log group names, dashboards, on-call rotation, first place to look at 2 AM.

**Question to ask:**  
*"When something fails in production overnight, where do you look first — CloudWatch log groups, email, Teams — and is there an on-call rotation?"*

**Why we need this:** Cannot debug incidents without log locations and escalation path.

**Evidence:** `msrx_v2.0/ebdjango/settings/shared.py:157-172` (LOGGING commented); `20_Developer_Takeover_Forensic_Audit.md` §15

---

### KT-013 — Super Transfer EC2 deploy and `process_flag` ownership

**Priority:** P1 | **Area:** Deployment / Super Transfer | **Best person:** DevOps

**What we already know:** CodeDeploy + `stop_cron.sh` (`pkill -9 python3`) + `process_flag` DDB gate + 600s sleep + `upload_model.py` (`appspec.yml`, `process_flag.py`).

**What is still unknown:** Who toggles `process_flag`, notification recipients, whether EC2 is dedicated per env, co-hosted services at risk from `pkill`.

**Question to ask:**  
*"Who owns Super Transfer CodeDeploy today — who sets `process_flag`, who gets the deploy-ready email, and is the EC2 instance dedicated or shared with other Python jobs?"*

**Why we need this:** Deploy can stop all processing or kill unrelated services.

**Evidence:** `super_transfer_client/scripts/stop_cron.sh`, `base/workflows/process_flag.py`

---

### KT-014 — Frontend LIVE deployment and secrets

**Priority:** P1 | **Area:** Deployment | **Best person:** DevOps + Frontend lead

**What we already know:** CodeBuild `buildspec.yml` (Node 22 vs `.nvmrc` 18.20.8), `printenv > .env`, EB prebuild white-label hook, `BACKEND_URL`/`WEB_TOKEN_SECRET` required. EB hook uses `/msrx/api/label-configs`; local `prebuild-script.js` uses `/msrx/api/admin/label-configs` (likely wrong).

**What is still unknown:** Branch→env mapping, who triggers deploy, where secrets are set in EB, whether `NODE_ENV=production` on all envs.

**Question to ask:**  
*"How is `msrx-frontend` deployed to each environment — branch mapping, who triggers the build, and where are `BACKEND_URL`, `WEB_TOKEN_SECRET`, and `NODE_ENV` set for LIVE?"*

**Why we need this:** Wrong `BACKEND_URL` or env breaks all API calls; CSRF behavior depends on `NODE_ENV`.

**Evidence:** `msrx-frontend/buildspec.yml`, `.platform/hooks/prebuild/01_white_label.sh`, `prebuild-script.js:27`

---

### KT-015 — Production CSRF behavior verification

**Priority:** P1 | **Area:** Security / Frontend | **Best person:** DevOps + Frontend lead

**What we already know:** CSRF enforced only when `NODE_ENV=production` (`index.js:25`). Client sets `X-CSRF-Token` from `metas[0].getAttribute("token")` but `template.hbs` has no token meta tag. Server sets signed `x-csrf-token` cookie on `GET /`.

**What is still unknown:** Whether production HTML injects token via undocumented deploy step, or CSRF is effectively disabled/misconfigured.

**Question to ask:**  
*"In LIVE, open browser devtools on a logged-in session — is `X-CSRF-Token` sent on `/msrx/*` requests, and how is that value populated given `template.hbs` has no CSRF meta tag?"*

**Why we need this:** Code suggests mismatch; production may differ or all API calls may fail CSRF checks.

**Evidence:** `msrx-frontend/client/src/store/store.js:32`, `server/index.js:24-32`, `client/src/template.hbs`

---

### KT-016 — Logout and session clearing in production

**Priority:** P1 | **Area:** Security / Frontend | **Best person:** Backend + DevOps

**What we already know:** `postLogout` clears `auth` cookie only on `softLogout && !login_key` (`auth.js:200-202`). Full logout calls Django but does not `clearCookie("auth")`. Buyers use soft logout (`headerPanel.js:22`). `localStorage` (`msrxSerializedState`) not cleared on logout.

**What is still unknown:** Whether ALB/nginx clears cookies, whether this is known/accepted, MFA partial-session behavior.

**Question to ask:**  
*"After a seller logs out in LIVE, is the `auth` httpOnly cookie actually cleared — and is stale `localStorage` a known issue when switching users on the same browser?"*

**Why we need this:** Ghost sessions and wrong-user UI state.

**Evidence:** `msrx-frontend/server/routes/auth.js:192-211`, `client/src/panels/headerPanel.js:19-27`, `client/src/store/localStorage.js`

---

### KT-017 — AWS credentials model on EB and ST EC2

**Priority:** P1 | **Area:** Security / AWS | **Best person:** DevOps

**What we already know:** Django passes explicit `AWS_ACCESS_KEY`/`AWS_SECRET_KEY` to boto3. ST worker uses default credential chain (likely instance role). ST `config.py` not in repo.

**What is still unknown:** Whether EB uses IAM roles or long-lived keys in prod; rotation procedure.

**Question to ask:**  
*"Do Elastic Beanstalk and Super Transfer EC2 use IAM instance roles or long-lived access keys in production, and what is the credential rotation procedure?"*

**Why we need this:** Security model and outage risk on key expiry.

**Evidence:** `msrx_v2.0/ebdjango/settings/shared.py:251-252`, `deployement_review_of_super_transfer_cilent.md` §11

---

### KT-018 — Boarding staging source of truth

**Priority:** P1 | **Area:** Database / Workflow | **Best person:** Backend lead

**What we already know:** `msrx_boarding_staging` and legacy `rp_boarding_staging_table` both referenced. SQL filter uses `Boarding_Staging.status='Processed'` (`boarding_file.py:28`) but no Python setter for `status`; booleans `cleared`/`delivered` used elsewhere.

**What is still unknown:** Which table drives LIVE boarding file generation; whether `status` column is dead.

**Question to ask:**  
*"In production, which boarding staging table is authoritative — `msrx_boarding_staging` or `rp_boarding_staging_table` — and is the `status='Processed'` filter actually used or do you rely on the boolean flags?"*

**Why we need this:** Boarding files may be empty due to filter mismatch.

**Evidence:** `msrx_v2.0/duediligence/utils/boarding_file.py:28`, `msrx_v2.0/msrx/models/boarding_staging.py`

---

### KT-019 — Authoritative pricing engine per buyer

**Priority:** P1 | **Area:** Business rules | **Best person:** Backend lead + Operations

**What we already know:** Grid and middleware (DPX) both run in coissue pricing (`support_pricing.py`). No code declares single winner.

**What is still unknown:** Which result ops treats as binding; middleware-only vs grid-only buyers.

**Question to ask:**  
*"For coissue pricing, when grid and middleware both run, which result is authoritative in production — and are any buyers on middleware-only or grid-only?"*

**Why we need this:** Wrong pricing changes if we modify pricing code without business rules.

**Evidence:** `msrx_v2.0/api/supporting/support_pricing.py:1403+`

---

### KT-020 — Best execution / winning buyer selection

**Priority:** P1 | **Area:** Business rules | **Best person:** Backend lead + Operations

**What we already know:** Multiple code paths (`commit_portfolio_level`, `msr_best_ex`, seasoned cap logic, Freedom workflows).

**What is still unknown:** Operational rule for winner selection; client-specific exceptions.

**Question to ask:**  
*"How is the winning buyer chosen at commit in production — highest price, cap-aware, buyer priority, or contractual rules per seller?"*

**Why we need this:** Incorrect commits if we change selection logic.

**Evidence:** `support_pricing.py`, `freedom/supporting/pricing/msrx/msrx.py`

---

### KT-021 — Commit reversal procedure

**Priority:** P1 | **Area:** Operations / Business rules | **Best person:** Operations + Backend lead

**What we already know:** `auto_resell_async` exists (`support_committing.py:60-96`). No documented reversal workflow across DB/S3/SQS/DD/boarding.

**What is still unknown:** Whether reversal is supported; systems to update; approval chain.

**Question to ask:**  
*"Can a confirmed commitment be reversed in production — and if yes, what is the full procedure across database, S3, SQS, due diligence, and boarding?"*

**Why we need this:** Data corruption if we attempt reversal without ops playbook.

**Evidence:** `msrx_v2.0/api/supporting/support_committing.py:60-96`

---

### KT-022 — `reprocess_loan` operational use

**Priority:** P1 | **Area:** Operations / Super Transfer | **Best person:** Operations + Backend lead

**What we already know:** `POST /duediligence/reprocess_loan/<id>/` deletes DDB records, S3 artifacts, resets DD state (`reprocess_loan_helpers.py`).

**What is still unknown:** When ops uses it, approval required, frequency in LIVE.

**Question to ask:**  
*"When do you use `reprocess_loan` in production, who approves it, and what do you check before running it?"*

**Why we need this:** Destructive operation without guardrails in code.

**Evidence:** `msrx_v2.0/duediligence/views/reprocess_loanviews.py`

---

### KT-023 — `commitment_check` failure and SQS message deletion

**Priority:** P1 | **Area:** Super Transfer / Operations | **Best person:** Backend + Operations

**What we already know:** If `commitment_check()` returns False, worker skips `processLoan` but still deletes SQS message (`main.py:98-115`). `query_msrx.py` prints failure.

**What is still unknown:** Whether this is intentional; how ops recovers unprocessed loans.

**Question to ask:**  
*"When Super Transfer `commitment_check` fails and the SQS message is still deleted, how do you detect and recover those loans in production?"*

**Why we need this:** Silent job loss with no in-app retry.

**Evidence:** `super_transfer_client/scripts/main.py:98-115`, `super_transfer_client/scripts/query_msrx.py:56-57`

---

### KT-024 — Secrets Manager rotation (Super Transfer)

**Priority:** P1 | **Area:** Security / AWS | **Best person:** DevOps

**What we already know:** ST uses Secrets Manager ARNs for `API_KEYS`, `msrx-urls`, `SUPER_TRANSFER_AWS_VARIABLES` (`env_variables.py:19-22`).

**What is still unknown:** Rotation schedule, who executes, downtime window.

**Question to ask:**  
*"What is the rotation schedule and procedure for Super Transfer Secrets Manager secrets, and what breaks if they expire?"*

**Why we need this:** Worker outage on expired secrets.

**Evidence:** `super_transfer_client/scripts/env_variables.py`

---

### KT-025 — O365 token failure procedure

**Priority:** P1 | **Area:** Integration / Operations | **Best person:** Operations

**What we already know:** O365 tokens stored in S3 (`EmailTrading/utils.py`, `o365_token.txt`). Email monitor polls every 15s on leader.

**What is still unknown:** Who fixes expired tokens; alert recipients; impact scope (all brands vs one).

**Question to ask:**  
*"When O365 authentication fails or tokens in S3 expire, who gets alerted and what is the fix procedure?"*

**Why we need this:** All email notifications and email-monitor trading stop.

**Evidence:** `msrx_v2.0/EmailTrading/utils.py`

---

## 4. P2 — Useful Questions

### KT-026 — Upload path v1 vs v2 by seller

**Priority:** P2 | **Area:** Workflow | **Best person:** Backend + Operations

**What we already know:** Both `uploadtape_csv/` and `uploadtape_csv/v2/` mounted; v2 comment says RP commit format. Frontend BFF uses v1 only (`msrCoissue.postUploadTape`).

**Question to ask:**  
*"Which sellers or clients still use `uploadtape_csv/v2` in production versus the standard upload path?"*

**Evidence:** `api/urls/index.py:101-102`, `msrx-frontend/server/routes/msrCoissue.js:522`

---

### KT-027 — CRA hybrid state in LIVE

**Priority:** P2 | **Area:** Legacy | **Best person:** Backend lead

**What we already know:** CRA not in `INSTALLED_APPS` but URLs mounted and LIVE-only cron jobs registered.

**Question to ask:**  
*"CRA is removed from INSTALLED_APPS but LIVE crons still reference it — is CRA actively used in production or should we disable those jobs?"*

**Evidence:** `shared.py:101`, `misc.py:1883-1887`

---

### KT-028 — LIVE-critical integrations and vendor contacts

**Priority:** P2 | **Area:** Integrations | **Best person:** Operations + Backend lead

**What we already know:** Code exists for PHH par, RoundPoint SFTP, Laura Mac, EPIC, FNMA/FHLMC, Benutech, Voxtur, Investor Connect, Bedrock queue.

**Question to ask:**  
*"For LIVE, which of PHH, RoundPoint SFTP, Laura Mac, EPIC, and FNMA/FHLMC are business-critical today — and who is the vendor contact when each breaks?"*

**Evidence:** Multiple apps; `MSRX_BACKEND_DEEP_AUDIT_AND_KT.md` §integrations

---

### KT-029 — `phagevolve_ingestion` ownership (follow-up from handover)

**Priority:** P2 | **Area:** Operations / Legacy | **Best person:** Operations

**What we already know (from handover):** Script runs ~every 15 minutes, checks funding files. **Not in any repo.**

**What is still unknown:** Where deployed, who maintains, failure alerts. *(Do not re-ask what the script does.)*

**Question to ask:**  
*"Handover mentioned `phagevolve_ingestion.py` on a 15-minute schedule — who owns that job today, where is it deployed, and how do you know when it fails?"*

**Evidence:** Handover notes; `deployement_review_of_super_transfer_cilent.md` §10

---

### KT-030 — `user_details` JSON safety-critical flags

**Priority:** P2 | **Area:** Configuration | **Best person:** Backend lead + Operations

**What we already know:** Feature flags in `MSRX_User.user_details` gate behavior (`super_transfer_commit_check`, `msrx_viewer`, etc.). No JSON schema in repo.

**Question to ask:**  
*"Is there a client configuration guide for `user_details` JSON — which flags are safety-critical and must not be changed without ops approval?"*

**Evidence:** Grep across `msrx_v2.0` for `user_details[` patterns

---

### KT-031 — Bedrock queue consumer ownership

**Priority:** P2 | **Area:** Integration / AWS | **Best person:** Backend + DevOps

**What we already know:** Django produces to `filesToBedrock-{env}` (`support_bedrock_process_helpers.py`). Consumer not in these repos.

**Question to ask:**  
*"Who owns the consumer for `filesToBedrock-{env}` and what is the procedure when DD documents stay unprocessed?"*

**Evidence:** `msrx_v2.0/duediligence/utils/support_bedrock_process_helpers.py`

---

### KT-032 — Freedom / shadow-bid email workflows

**Priority:** P2 | **Area:** Legacy / Freedom | **Best person:** Backend lead

**What we already know:** `EmailTrading` shadow-bid token paths exist; no frontend references to `wholeloan-shadow-bid`.

**Question to ask:**  
*"Are Freedom shadow-bid or email-only whole-loan workflows still active in LIVE, and which clients use them?"*

**Evidence:** `msrx_v2.0/EmailTrading/tokens/`

---

## 5. Contradictions Requiring Human Confirmation

| ID | Code says | Other evidence says | What is unclear | Question to ask | Risk |
|----|-----------|---------------------|-----------------|-----------------|------|
| C-01 | Django SQS body: only `seller-loan_id` | Worker requires `loan_id` to process | Enrichment path | "What adds `loan_id` before the worker runs?" | Loans never processed |
| C-02 | `ApiCommitConfirm` sets `confirmed` + resell only | `confirm_commit` runs SQS + DD + loan numbers | Who uses alternate path | "Who uses `/commit-confirm/` and is bypass intentional?" | Missing ST/DD |
| C-03 | Code sets `pre-commit` | Model comment / some filters use `pre-committed` | Canonical prod data | "Which status string is canonical in LIVE data?" | UI filters miss tapes |
| C-04 | SQL filters `Boarding_Staging.status='Processed'` | No Python writer sets `status` | Boarding trigger | "Is boarding driven by booleans instead of `status`?" | Empty boarding files |
| C-05 | ST worker deletes SQS on `commitment_check` fail | No retry in worker | Expected behavior | "How do you recover when commit check fails?" | Silent job loss |
| C-06 | `postLogout` full path | No `clearCookie("auth")` on success | Prod session behavior | "Is auth cookie cleared on logout in LIVE?" | Ghost sessions |
| C-07 | CSRF: header from meta `token` | `template.hbs` has no token meta | Prod CSRF setup | "How is CSRF token delivered to the browser in LIVE?" | API block or CSRF bypass |
| C-08 | `create_commit_dd_records` after SQS post | Worker may need DD `loan_id` in message | Ordering / timing | "Is message enrichment timed after DD record creation?" | Race before DD exists |
| C-09 | Settings `supertransfer-dev` bucket name | Runtime `supertransfer-{MSRX_ENV}` | Bucket per env | "Confirm S3 bucket name for each environment." | Wrong bucket writes |
| C-10 | CRA not in INSTALLED_APPS | LIVE crons call CRA jobs | Active or dead | "Is CRA live or should crons be removed?" | Runtime errors / noise |

---

## 6. External Integration Checklist

| Integration | Active in production? | Clients using it | Credential owner | Failure fallback | Monitoring | External contact | Still unknown? |
|-------------|----------------------|------------------|------------------|------------------|------------|------------------|----------------|
| O365 / Graph | **ASK** | Multiple brands | **ASK** | **ASK** | Email duplicate check | **ASK** | Yes — all columns |
| SQS `loansToprocess` | Likely yes | Coissue confirm path | DevOps/AWS | **ASK** | **ASK** | N/A | Enrichment, DLQ |
| SQS `filesToBedrock` | **ASK** | DD workflows | DevOps/AWS | **ASK** | **ASK** | N/A | Consumer owner |
| S3 (tapes, ST, grids) | Yes (code) | All | DevOps/AWS | **ASK** | **ASK** | AWS support | Lifecycle policies |
| FNMA API | **ASK** | Freedom/agency | **ASK** | `mbs failed` status | **ASK** | **ASK** | LIVE vs sandbox |
| FHLMC API | **ASK** | Freedom/agency | **ASK** | **ASK** | **ASK** | **ASK** | Same |
| PHH par | **ASK** | **ASK** | **ASK** | **ASK** | **ASK** | **ASK** | Active in LIVE? |
| RoundPoint SFTP | **ASK** | **ASK** | **ASK** | Cron next day | **ASK** | **ASK** | Schedule owner |
| Laura Mac | **ASK** | DD | **ASK** | **ASK** | **ASK** | **ASK** | Prod creds |
| EPIC | **ASK** | ST guidance | **ASK** | **ASK** | **ASK** | **ASK** | TEST vs PROD mix |
| Voxtur / InfoEx | **ASK** | Title orders | **ASK** | **ASK** | **ASK** | **ASK** | Cert expiry |
| Benutech | Yes (BFF+API) | Title Toolbox | **ASK** | **ASK** | **ASK** | **ASK** | Contract/outage |
| Investor Connect / Encompass | **ASK** | Transfer module | **ASK** | **ASK** | **ASK** | **ASK** | Active clients |
| AWS Textract | **ASK** | ST worker | AWS | **ASK** | **ASK** | AWS | Active vs legacy |
| SFTP (buyer delivery, 2nd lien) | **ASK** | **ASK** | **ASK** | **ASK** | **ASK** | Partners | Credential matrix |
| Bedrock | **ASK** | DD | **ASK** | **ASK** | **ASK** | AWS | Consumer location |

---

## 7. Production Operations Checklist

| Operation | Status | Notes |
|-----------|--------|-------|
| Deploy frontend | **PARTIALLY KNOWN** | CodeBuild + EB; branch mapping and secret injection **UNKNOWN** |
| Deploy backend (Django) | **PARTIALLY KNOWN** | EB WSGI; migrate not automated **UNKNOWN** |
| Deploy Super Transfer | **PARTIALLY KNOWN** | CodeDeploy + cron; `process_flag` owner **UNKNOWN** |
| Run migrations | **UNKNOWN — ASK** | Not in `.ebextensions` |
| Rollback (any service) | **UNKNOWN — ASK** | No runbook in repo |
| Recover stuck tape (upload) | **PARTIALLY KNOWN** | `status_details.upload_*` fields; ops steps **UNKNOWN** |
| Recover failed pricing | **PARTIALLY KNOWN** | `pricing_progress` / `pricing_failed_message`; re-trigger procedure **UNKNOWN** |
| Recover failed commit | **PARTIALLY KNOWN** | `commit_progress`; confirm side-effects **UNKNOWN** |
| Requeue Super Transfer loan | **UNKNOWN — ASK** | No documented re-queue; `reprocess_loan` exists |
| Reprocess documents (ST) | **PARTIALLY KNOWN** | `reprocess_loan` API; approval **UNKNOWN** |
| Regenerate boarding file | **PARTIALLY KNOWN** | Schedulers exist; manual trigger **UNKNOWN** |
| Restore database | **UNKNOWN — ASK** | No backup/restore docs |
| Rotate credentials | **UNKNOWN — ASK** | Keys in env + Secrets Manager; no rotation SOP |
| Recover `post_loan_to_sqs` failure | **UNKNOWN — ASK** | Silent failure documented in code only |
| Loan number pool exhaustion | **PARTIALLY KNOWN** | Email alert in code; replenishment **UNKNOWN** |
| O365 token refresh | **UNKNOWN — ASK** | S3 token file; fix procedure **UNKNOWN** |

---

## 8. Top 15 Questions for the Live KT Meeting

Read these verbatim during the meeting:

1. "Can you walk us through exactly how a LIVE backend deployment is done today — including when migrations run and how we roll back if something breaks?"

2. "The Django code sends only `seller-loan_id` to the Super Transfer queue, but the worker checks for `loan_id` before processing. What component adds the remaining fields in production — is there a Lambda or another service not in our three repos?"

3. "When confirm succeeds but Super Transfer never picks up the loan — for example `post_loan_to_sqs` fails or S3 docs are missing — how do you detect that today and what is the recovery procedure?"

4. "Who uploads documents to the `SuperTransfer/{seller}/{buyer}/{loan}/` S3 path in production, and at what point relative to confirm?"

5. "Is anyone using `POST /msrx/api/commit-confirm/` in LIVE, and is that endpoint supposed to skip the normal confirm pipeline including Super Transfer and due diligence record creation?"

6. "How many Elastic Beanstalk instances run per environment, what is `ENV_FLAG` on each, and are duplicate Super Transfer or boarding schedulers a known issue?"

7. "Do our SQS queues have dead-letter queues configured, and what is the procedure to replay messages when processing fails?"

8. "What creates the initial DynamoDB record in `supertransfer-{env}DB` before the Super Transfer worker runs?"

9. "When something breaks at 2 AM, where do you look first — CloudWatch, email, something else — and is there an on-call rotation?"

10. "For a production incident, can we hotfix LIVE directly or must changes go through dev, uat, demo, and Live — who approves an emergency bypass?"

11. "List every Lambda, cron host, or script outside our three repositories that production still depends on — including `phagevolve_ingestion` if it is still running."

12. "Who owns Super Transfer CodeDeploy — who sets `process_flag`, and is the EC2 instance dedicated or shared with other Python processes?"

13. "How is the frontend deployed to LIVE — which branch, where are `BACKEND_URL` and `WEB_TOKEN_SECRET` set, and is `NODE_ENV` production on all environments?"

14. "In LIVE, after logout, is the auth cookie actually cleared — and how is CSRF working given the HTML template does not include a CSRF token meta tag?"

15. "What is the RDS backup schedule for LIVE, has a restore been tested, and who can authorize point-in-time recovery?"

---

## Questions We Intentionally Removed

These were considered but **excluded** because code or prior notes already answer them:

| Removed question | Why excluded |
|------------------|--------------|
| What technology does MSRX use? | Django + React + Express + PostgreSQL + S3 + SQS — documented in all audits |
| How does authentication work? | DRF Token in httpOnly cookie via BFF — `auth.py`, `server/routes/auth.js` |
| What database does MSRX use? | PostgreSQL RDS per env — settings files |
| What does the Express server do? | BFF proxy + local file/email processing — `msrx-frontend/server/` |
| What is Super Transfer? | SQS worker on EC2 for doc classify/extract — `super_transfer_client` + handover |
| How does tape upload work? | End-to-end traced in audits — `dropZone.js` → `uploadtape_csv/` |
| What roles exist? | `user_role`, flags, `side_panel_items` — `auth.py`, `MSRX_User` model |
| Where is pricing implemented? | `support_pricing.py`, Freedom pricing — backend audit |
| Does MSRX use Celery? | No — APScheduler only; grep confirms |
| How does Redux navigation work? | `side_panel_items` → `view` → `pageMaps` — frontend audit |
| What is the Express BFF's role? | Answered in onboarding guide §10 |
| Where does the funding file come from? (PHH) | Partially covered in handover; replaced with ownership/cron follow-up (KT-029) |
| What is Super Transfer hosted on? | Handover + deploy review: EC2 — **KNOWN FROM PREVIOUS KT** |
| Is `commit-confirm` mounted? | Yes — `api/urls/index.py:179` |
| What SQS queue names are used? | `loansToprocess-{env}`, `filesToBedrock-{env}` — settings + env_variables |
| What are tape status values? | uploaded → approved → priced → pre-commit → confirmed — model + code |
| Is there a separate BFF repo? | No — `msrx-frontend` contains Express + React |
| Does worker call `STLoanLookupView`? | No — confirmed in code |
| How is ST worker started? | crontab + flock + `main.py` — deploy review |
| What is the branch promotion pattern? | `patch.yml` auto patch PRs — **KNOWN FROM CODE** |

---

*End of final KT question list. Read-only synthesis — no source files modified.*
