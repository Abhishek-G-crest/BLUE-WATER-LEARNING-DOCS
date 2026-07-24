# MSRX Backend Deep Audit

**Repository audited:** `d:\BLUE-WATER\msrx_v2.0` (local folder name; referred to in prompts as `msrx_v2.0-dev`)  
**Audit date:** 2026-07-24  
**Purpose:** Backend takeover / Monday KT preparation  
**Method:** Full source inspection — models, views, URLs, services, settings, deployment files, cron, AWS integrations, tests, migrations, internal docs. No source files were modified.

**Classification legend used throughout:**
- **[CONFIRMED FROM CODE]** — directly evidenced in repository
- **[LIKELY / INFERRED]** — reasonable inference from code patterns, not explicitly documented
- **[NOT FOUND IN REPO]** — searched, absent or not implemented here
- **[UNCLEAR — ASK IN KT]** — contradictory, incomplete, or production-dependent

---

## 1. Executive Repository Map

### 1.1 What exactly is this repository?

**[CONFIRMED FROM CODE]** `msrx_v2.0` is the **primary Django backend** for Blue Water Financial Technologies' MSR-X / MSRX platform. It is a **modular monolith**: one Django project (`ebdjango`) hosting ~20 domain apps, with the core MSR coissue workflow centered in `api/` + `msrx/`, and parallel whole-loan workflows in `freedom/`.

| Question | Answer | Classification |
|----------|--------|----------------|
| What is it? | Django 5.2 + DRF backend for MSR trading, pricing, commitment, transfer, boarding, DD | CONFIRMED |
| Primary backend? | Yes — `/msrx/api/` is the main REST surface | CONFIRMED |
| What it owns | Auth, tape upload, MSR pricing, commitment, aggregator management, buyer grids, Super Transfer orchestration, Freedom WL platform, DD/QC, email trading, analytics, recon | CONFIRMED |
| What it does NOT own | React frontend, Express BFF (referenced externally only), Super Transfer **worker** (separate repo), likely some OCR/Bedrock consumers | INFERRED + UNCLEAR |
| Architecture | Modular monolith — apps share PostgreSQL, not microservices | CONFIRMED |

**Entry point:** `manage.py` → `DJANGO_SETTINGS_MODULE=ebdjango.settings` → env selected by `MSRX_ENV` (`DEV`/`UAT`/`DEMO`/`LIVE`/`LOCAL`).

### 1.2 Repository / module map (derived from code)

```
msrx_v2.0/
│
├── ebdjango/                    # Django project — settings, root URLs, WSGI
│
├── api/                         # ★ PRIMARY REST API (/msrx/api/)
│   ├── urls/                    # Route registry
│   ├── views/                   # DRF views (auth, pricing, commit, aggregator, admin…)
│   ├── api_handler.py           # ★ Central orchestration (~6400+ lines)
│   ├── supporting/services/     # tape_upload, msr_pricing, msr_commit
│   ├── supporting/              # support_pricing, support_committing, support_util
│   ├── cron_jobs.py             # APScheduler job registration
│   └── utils/misc.py            # Leader election + scheduler bootstrap
│
├── msrx/                        # ★ Core domain models + Django admin panel
│   ├── models/                  # MSRX_User, coissue, buyer, seasoned, platform, boarding…
│   └── views.py                 # Legacy admin panel (session login)
│
├── base/                        # Cross-cutting: ActivityLogMiddleware, decorators, utils
├── bw_middleware/               # HTTPS headers + CSP middleware only
│
├── TapeManager/                 # Legacy tape format cracking → MSR-X CSV
├── tapecrack/                   # SQL-based tape cracking configs
│
├── freedom/                     # ★ Whole-loan platform (separate product line in same repo)
│   ├── models/                  # Tape, Loan, PricingModel, WholeLoanPrice, WholeLoanCommit
│   ├── views/                   # 100+ routes — upload, price, commit, pools, optimization
│   └── supporting/pricing/      # Agency pricing, workflows, MSR overlay
│
├── middleware/                  # DPX pricing model training/fit (not HTTP middleware)
│
├── Transfer/                    # Transfer Solutions / Investor Connect
├── supertransfer/               # Super Transfer — QC, boarding files, SFTP delivery
├── duediligence/                # QC Exceptions 3.0 — loans, docs, rules, Bedrock
├── commitrecon/                 # Commit vs settlement recon, purchase advice
├── secondlien/                  # Second-lien commitment tracking
├── caas/                        # Configurable loan builder + workflow engine
├── analytics/                   # Agency cash, poly assumptions, investor pricing
├── EmailTrading/                # O365 email monitor + branded notifications
├── voxtur/                      # InfoEx title orders, WYCHS AOL
├── benutech/                    # Title Toolbox property lookup
├── rp/                          # RoundPoint boarding staging model (legacy, model-only)
├── terms/                       # T&C and privacy policy acceptance
├── CRA/                         # CRA check — NOT in INSTALLED_APPS but still routed
│
├── .ebextensions/               # AWS Elastic Beanstalk config
├── .platform/                   # nginx, prebuild hooks, postdeploy security agent
└── .github/workflows/           # Ruff lint + api.tests CI
```

### 1.3 Major Django applications and responsibilities

| App | Route prefix | Business responsibility |
|-----|--------------|------------------------|
| `api` | `/msrx/api/` | Core MSR-X REST API — login, tapes, pricing, commit, aggregator, admin |
| `msrx` | `/` (admin panel) | Domain models, Django admin, legacy admin panel views |
| `freedom` | `/freedom/` | Whole-loan trading platform (Freedom Mortgage correspondent workflow) |
| `supertransfer` | `/supertransfer/` | Document transfer, boarding file generation, SFTP delivery, exceptions |
| `duediligence` | `/duediligence/` (via urls) | QC loan/document management, Bedrock doc processing trigger |
| `Transfer` | `/transfer/` | Investor Connect monitoring, EM API, RoundPoint integration |
| `commitrecon` | `/recon/` | Boarding reconciliation, purchase advice, agency loan numbers |
| `TapeManager` | `/` | Seller-specific tape format conversion |
| `tapecrack` | `/tapecrack/` | SQL tape cracking configuration |
| `EmailTrading` | `/email/` | Monitored mailbox trading + `send_email_notif()` |
| `analytics` | `/analytics/` | Agency cash screening, poly assumptions |
| `caas` | `/caas/` | Loan builder forms, single-loan pricing, workflows |
| `secondlien` | `/secondlien/` | Second-lien SFTP ingest + commitment reports |
| `middleware` | `/msrx/middleware/` | DPX model create/train (pricing science tooling) |
| `voxtur` | `/voxtur/` | Title/InfoEx integration |
| `benutech` | `/benutech/` | Property lookup API |
| `terms` | `/terms/` | Legal terms acceptance |
| `base` | (no routes) | Shared infra — logging, decorators, base views |
| `bw_middleware` | (no routes) | Security headers middleware |
| `rp` | (no routes) | RoundPoint `boarding_staging_table` model only |

### 1.4 What belongs to other repositories/services

| Component | Evidence in this repo | Classification |
|-----------|----------------------|----------------|
| React frontend | `FrontendComponents`, `FrontendComponentConfigs` models; `HTTP_HOSTNAME` header checks | CONFIRMED (frontend is separate) |
| Express BFF | Not referenced by name; user context indicates BFF proxies to Django | **[UNCLEAR — ASK IN KT]** |
| Super Transfer worker/client | SQS producer only; consumer is external | CONFIRMED |
| Bedrock document processor | SQS `filesToBedrock-{env}` producer | CONFIRMED |
| Bloomberg tooling | `Bloomberg/` folder — operational scripts | LIKELY separate/adjacent |

---

## 2. Application Startup

### 2.1 Bootstrap chain

**[CONFIRMED FROM CODE]**

```
python manage_{env}.py runserver   OR   EB WSGI worker
        ↓
manage.py sets DJANGO_SETTINGS_MODULE=ebdjango.settings
        ↓
ebdjango/settings/__init__.py routes by MSRX_ENV:
  DEMO→demo, LIVE→live, LOCAL→local, UAT→uat, else→dev
        ↓
shared.py: INSTALLED_APPS, MIDDLEWARE, REST_FRAMEWORK, caches
        ↓
{env}.py: DATABASES, S3 buckets, ALLOWED_HOSTS, integration creds
        ↓
get_wsgi_application()  [ebdjango/wsgi.py]
        ↓
Thread: leader_election_process()  [api/utils/misc.py]
        ↓
(import side effect) api/urls/urls.py — if MSRX_ENV not DEV/LOCAL:
  start_super_transfer_delivery_schedule()
  start_boarding_file_delivery_schedule()
        ↓
(if ENV_FLAG=CLOUD and leader elected) APScheduler jobs from api/cron_jobs.py
```

### 2.2 What runs ONCE at startup vs PER REQUEST

| Runs once (startup) | Runs per request |
|---------------------|------------------|
| Django settings load | `SecurityMiddleware` → sessions → `HttpsHeadersMiddleware` → `CSPMiddleware` → `CommonMiddleware` → `CsrfViewMiddleware` → `AuthenticationMiddleware` → `ActivityLogMiddleware` |
| WSGI `leader_election_process` thread | DRF `TokenAuthentication` + `IsAuthenticated` |
| Super Transfer SFTP schedulers (non-DEV/LOCAL) | URL routing → view → `api_handler` / services |
| APScheduler jobs (CLOUD + leader only) | `activity_log()` on API calls |
| `collectstatic` on EB deploy | DB queries, S3, SQS, external HTTP |

**Files:**
- `ebdjango/wsgi.py` — WSGI + leader election thread
- `api/urls/urls.py:39-45` — Super Transfer schedulers on import
- `api/utils/misc.py` — `leader_election_process()`, `ENV_FLAG=CLOUD` gate
- `ebdjango/settings/shared.py:136-148` — middleware stack

### 2.3 AppConfig.ready()

**[CONFIRMED FROM CODE]** No active `AppConfig.ready()` hooks in custom apps. `api/apps.py` has commented-out ready() (leader election moved to WSGI).

### 2.4 Production startup

**[CONFIRMED FROM CODE]**
- **Platform:** AWS Elastic Beanstalk Python platform
- **WSGI:** `ebdjango.wsgi:application` (`.ebextensions/django.config`)
- **Process manager:** EB-managed (no gunicorn config in repo)
- **Reverse proxy:** nginx — 400MB body, 300s timeouts (`.platform/nginx/conf.d/proxy.conf`)
- **Post-deploy:** Trend Micro Deep Security agent (`.platform/hooks/postdeploy/90_AgentDeploymentScript.sh`)
- **No Docker, Celery, ASGI, Procfile, appspec.yml** in repo

**[LIKELY / INFERRED]** Multi-worker EB instances; only one instance becomes scheduler "leader" via `LeaderElection` model + EC2 metadata.

---

## 3. Authentication

### 3.1 Login flow (end-to-end)

**[CONFIRMED FROM CODE]**

```
POST /msrx/api/login/  (alias: /msrx/api/rest-auth/login/)
        ↓
api.views.auth.Login (extends dj_rest_auth.views.LoginView)
        ↓
authenticate(username, password) → auth_user
        ↓
dj_rest_auth issues DRF Token (rest_framework.authtoken.models.Token)
        ↓
Login.get_response():
  - HTTP_HOSTNAME header → authorized_platform check
  - admin hostname → requires is_staff/is_superuser
  - Django_user_to_msrx_user() → MSRX_User
  - Password expiry: last_password_change null or ≥60 days
  - Terms/privacy checks
  - Returns: key, user_role, aggregator_flag, aggregator_seller_flag, platform_config
  - MSRX_User_additional linked user → swaps token to aggregator's django user
        ↓
Response with Token key
```

**Subsequent requests:** `Authorization: Token <key>` — `REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES = TokenAuthentication`

### 3.2 auth_user ↔ msrx_msrx_user relationship

**[CONFIRMED FROM CODE]** `base/utils/users.py` → `Django_user_to_msrx_user(user)`:

1. `MSRX_User.objects.filter(user=user)` — direct OneToOne
2. `Client_Aggregator_Seller_Login.objects.filter(user=user)` → returns parent agg-seller `MSRX_User`
3. `MSRX_User_additional.objects.filter(django_user=user)` → returns linked `msrx_user`

| Table | Stores | Why both exist |
|-------|--------|----------------|
| `auth_user` | Django credentials, `is_staff`, `is_superuser`, groups | Standard Django auth |
| `msrx_msrx_user` | Business identity: role, flags, platform, margins, counterparty JSON | MSRX domain layer — one auth user can map to business personas via additional/login tables |

### 3.3 Token, logout, password, MFA

| Feature | Implementation | Classification |
|---------|----------------|----------------|
| Token type | DRF `TokenAuthentication` — persistent until deleted | CONFIRMED |
| Token lifetime | **No expiry configured** | CONFIRMED |
| Logout | `POST /msrx/api/rest-auth/logout/` → deletes token | CONFIRMED |
| Password change | `POST /msrx/api/user_change_pw/` — min 14 chars | CONFIRMED |
| Admin password reset | `GET /msrx/api/admin/token_lookup` — superuser returns/creates token | CONFIRMED |
| Admin user create | min 6 chars (weaker than user change) | CONFIRMED |
| MFA | `PlatformConfiguration.mfa` exists; OTP via `POST /msrx/api/one_time_passcode/` | CONFIRMED — **no server-side login gate for MFA** |
| Account lockout | **Not found** | NOT FOUND IN REPO |

---

## 4. Roles and Permissions

### 4.1 Role representation in database

**[CONFIRMED FROM CODE]** `msrx/models/user.py` → `MSRX_User`:

| Field | Type | Meaning |
|-------|------|---------|
| `user_role` | CharField(60), no DB constraint | Comment: `# buyer/seller/investor` |
| `aggregator_flag` | BooleanField | User is an aggregator |
| `aggregator_seller_flag` | BooleanField | User is an aggregator-seller entity |
| `correspondent_buyer_flag` | BooleanField | Freedom correspondent buyer |
| `is_staff` / `is_superuser` | On `auth_user` | Django admin access |

**Values found in code for `user_role`:** `"buyer"`, `"seller"`, `"investor"`  
**Pseudo-roles via flags:** aggregator (`aggregator_flag`), aggregator seller (`aggregator_seller_flag`), correspondent buyer (`correspondent_buyer_flag`)

### 4.2 Permission enforcement

**Decorators** (`base/decorators/user_level_decorators.py`):
- `@aggregators_only` — `aggregator_flag`
- `@agg_sellers_only` — `aggregator_seller_flag` (**defined but never applied**)
- `@agg_and_agg_sellers` — either flag
- `@admin_only` — `is_superuser`
- `@staff_only` — `is_staff`
- `@bwft_only` — Django group `"BWFT"`

**Default:** `IsAuthenticated` on all `/msrx/api/*`. Role gating is mostly inline `if` checks, not DRF Permission classes.

### 4.3 Aggregator → Client_Aggregator_Seller → Seller mapping

**[CONFIRMED FROM CODE]**

```
AGGREGATOR (MSRX_User, aggregator_flag=True)
    │ Client_Aggregator_Seller.aggregator FK
    ▼
AGG SELLER (MSRX_User, user_role="seller")
    │ OneToOne Client_Aggregator_Seller
    ▼
AGS SUB-LOGIN (Client_Aggregator_Seller_Login → auth_user)
    access_view / access_pricing / access_commit / access_exception
```

**Creation:** `api/views/aggregator.py` → `AggregatorSellerCreate` creates `MSRX_User` + `Client_Aggregator_Seller` but **does not explicitly set `aggregator_seller_flag=True`**.

**Resolution:** `get_aggregator(msrx_user)` uses `Client_Aggregator_Seller` FK, not the flag.

**[UNCLEAR — ASK IN KT]** Whether `aggregator_seller_flag` is always set correctly in production or if relationship existence is the real gate.

### 4.4 Role → API access (key examples)

| Role | Key APIs | File |
|------|----------|------|
| Aggregator | `aggregator/get_tapes`, `aggregator/seller/*`, settings | `api/views/aggregator.py` |
| Seller | `uploadtape_csv`, `pricing`, `commit_loan_level`, `seller_tapes` | `api/urls/index.py` |
| Buyer | `buyer_committed_tapes`, `get_active_buyer` | `api/views/views.py` |
| Investor | Freedom routes — `user_role=="investor"`, `correspondent` FK | `freedom/views/*` |
| Staff | `admin/users`, `admin/ags_users` | `api/views/users.py` |
| Superuser | `admin/registration`, `admin/token_lookup`, grids | `api/views/admin.py` |

---

## 5. Database Architecture

### 5.1 Hub table

**[CONFIRMED FROM CODE]** `msrx_msrx_user` (`MSRX_User`) is the identity hub for all business actors.

### 5.2 Domain groupings (important tables only)

#### Identity / Access
| Model | Table | PK | Key FKs |
|-------|-------|-----|---------|
| `MSRX_User` | `msrx_msrx_user` | id | user→auth_user, correspondent→self, platform |
| `Client_Aggregator_Seller` | `msrx_client_aggregator_seller` | id | user→MSRX_User, aggregator→MSRX_User |
| `Client_Aggregator_Seller_Login` | `msrx_client_aggregator_seller_login` | id | seller→Client_Aggregator_Seller, user→auth_user |
| `APIActivityLog` | `api_activity_log` | id | — |

#### Seller / Tape / Loan (MSR coissue)
| Model | Table | Purpose |
|-------|-------|---------|
| `Client_Coissue_Seller` | `msrx_client_coissue_seller` | Tape header — status, loancount, upb, status_details |
| `Client_Coissue_Tape` | `msrx_client_coissue_tape` | Loan rows — price JSON, commitment JSON |
| `Client_Seasoned_Seller/Tape` | `msrx_client_seasoned_*` | Seasoned MSR path |

#### Buyer / Pricing (MSR)
| Model | Table | Purpose |
|-------|-------|---------|
| `Client_Coissue_Buyer` | `msrx_client_coissue_buyer` | Buyer pricing grid (JSON `grid_info`) |
| `Client_Coissue_Buyer_Criteria` | `msrx_client_coissue_buyer_criteria` | Per buyer-seller criteria |
| `Client_Coissue_Buyer_Middleware` | `msrx_client_coissue_buyer_middleware` | DPX middleware model config |
| `Client_Coissue_Buyer_Par` | `msrx_client_coissue_buyer_par` | Par coupon formulas |

#### Pricing (Freedom whole-loan)
| Model | Table | Purpose |
|-------|-------|---------|
| `PricingModel` | `freedom_pricingmodel` | Root WL pricing container |
| `WholeLoanPrice` | `freedom_wholeloanprice` | Normalized price rows per loan/buyer |
| `Tape` / `Loan` | `freedom_tape` / `freedom_loan` | WL tape + loan SOT |

#### Commitment
| Storage | Location | Format |
|---------|----------|--------|
| MSR loan-level | `Client_Coissue_Tape.commitment` | JSON: buyer_id, remit, price, agency |
| MSR tape summary | `Client_Coissue_Seller.status_details` | JSON: best_ex, commit_progress, priced_buyer_list |
| WL structured | `WholeLoanCommit` | `freedom_wholeloancommit` |
| Commit caps | `Client_Commit_Cycle` | `msrx_client_commit_cycle` |

#### Transfer / Boarding / DD
| Model | Table | Purpose |
|-------|-------|---------|
| `Boarding_Staging` | `msrx_boarding_staging` | Primary boarding flat schema |
| `EMResource` | `transfer_emresource` | eMortgage transfer state |
| `Loan` (supertransfer) | `supertransfer_loan` | ST document delivery tracking |
| `Loan` (duediligence) | `duediligence_loan` | QC hub — links to coissue + freedom loans |

### 5.3 SOT vs staging vs history

| Classification | Examples | Evidence |
|----------------|----------|----------|
| **Source of truth** | `msrx_client_coissue_tape`, `freedom_loan`, `msrx_msrx_user` | Active operational FKs |
| **Staging** | `msrx_boarding_staging`, `rp_boarding_staging_table` | Boarding prep before delivery |
| **History/audit** | `*_deleted`, `freedom_loansnapshot`, `msrx_buyer_par_history`, `api_activity_log` | Naming + immutability patterns |
| **Cache/denormalized** | `Client_Coissue_Tape.price` JSON, `msrx_markettemprto` | Alongside normalized `WholeLoanPrice` |

### 5.4 Key relationship diagram

```
auth_user ──OneToOne──► msrx_msrx_user
                              │
         ┌────────────────────┼──────────────────────┐
         ▼                    ▼                      ▼
Client_Aggregator_Seller   Client_Coissue_Seller   freedom.Tape
  .aggregator FK            .client FK              .client FK
         │                    │                      │
         │                    ▼                      ▼
         │              Client_Coissue_Tape      freedom.Loan
         │                .price JSON              .WholeLoanPrice
         │                .commitment JSON         .WholeLoanCommit
         │                    │
         └────────────────────┼──────► Boarding_Staging
                              └──────► duediligence.Loan
```

---

## 6. Tape / Loan Upload

### 6.1 Primary endpoints

| Route | View | Service |
|-------|------|---------|
| `POST /msrx/api/uploadtape_csv/` | `UploadTapeCSV` | `tape_upload.upload_tape_csv()` |
| `POST /msrx/api/uploadtape_csv/v2/` | `UploadTapeCsvV2` | `raw_tape_crack_v2()` → `clean_tape_upload_to_DB_v2()` |
| `POST /msrx/api/approve_tape/` | `ApproveTape` | status → `approved` |
| `POST /freedom/price-tape/` | Freedom `Pricing` | `tape_to_db()` |

### 6.2 MSR upload flow

**[CONFIRMED FROM CODE]**

```
POST /msrx/api/uploadtape_csv/
  → api/views/pricing.py::UploadTapeCSV
  → api/supporting/services/tape_upload.py::upload_tape_csv()
      → inmemory_to_s3(S3_BUCKET_NAME, priced_tapes/msr/{owner}_{client}_{date}_{file})
      → raw_tape_crack() [TapeManager/supporting/support_util.py]
          → data_from_csv_or_excel()
          → select_and_run_tapecrack() or Tape_General_Converter
          → check_asset_df() / check_loans()
      → clean_tape_upload_to_DB() [api/api_handler.py]
          → [async thread] clean_tape_upload_to_DB_asyn_worker()
              → Client_Coissue_Seller (status=uploaded, loancount, upb)
              → Client_Coissue_Tape.bulk_create()
```

### 6.3 Validation rules (highlights)

- Required fields in `clean_tape_upload_to_DB` (`api/api_handler.py:638-671`)
- States, product types, numeric ranges, `service_rate` 0.19–1.125
- ARM loans (`loan_type != "fixed"`) excluded to `removed_loans`
- v2: `check_loans_v2()`, acquisition_id match, FMX property_type checks

### 6.4 loancount / UPB

**[CONFIRMED FROM CODE]** `api/api_handler.py`:
```python
seller.loancount = len(objects_all)      # fixed loans only
seller.upb = good_loan_balance           # sum(loan_balance)
```

### 6.5 Tape status lifecycle (MSR coissue)

**[CONFIRMED FROM CODE]** `msrx/models/coissue.py:17-19` comment + code transitions:

```
uploaded
   ↓ approve_tape()
approved
   ↓ msr_pricing() → asset_price_v3()
priced
   ↓ commit_group() / loan_level_commit_helper()
pre-commit
   ↓ confirm_commit()
confirmed
   ↓ (commented) transfer_complete
```

**Progress tracking:** `status_details.upload_progress`, `pricing_progress`, `commit_progress` (0–100 + failure messages).

**[UNCLEAR — ASK IN KT]** Whether `transfer_complete` is still actively set anywhere.

---

## 7. Price Management

### 7.1 What "pricing" means in MSRX

**[CONFIRMED FROM CODE]** Pricing = running eligible buyer pricing engines against tape loans to populate per-loan `price` JSON on `Client_Coissue_Tape`, enabling comparison and commitment.

Two parallel systems:
1. **MSR coissue pricing** — grid + middleware (DPX) via `api/supporting/support_pricing.py`
2. **Freedom whole-loan pricing** — `freedom/supporting/pricing/` + `PricingModel` tree

### 7.2 Aggregator Price Management screen backend

```
GET /msrx/api/aggregator/get_tapes?level=summary
  → AggregatorGetTapes [api/views/aggregator.py]
  → aggregator_get_tape_summary(msrx_user) [api/api_handler.py:2960]
      → Client_Aggregator_Seller.filter(aggregator=msrx_user) → seller IDs
      → Client_Coissue_Seller.filter(client_id__in=seller_list)
```

### 7.3 Pricing trigger flow (MSR)

```
POST /msrx/api/pricing/
  → msr_pricing() [api/supporting/services/msr_pricing.py]
      → status gate: approved | priced | pre-commit
      → pricing_pre_check() → buyer_to_grid_id(), buyer_to_middleware_id()
      → seller.status = "priced"
      → asset_price_v3() [api/supporting/support_pricing.py:1403]
          → price_through_grid_as_of_date()
          → price_through_middleware()
          → bulk_update Client_Coissue_Tape.price
          → status_details.priced_buyer_list, pricing_progress
```

### 7.4 Buyer price storage

**[CONFIRMED FROM CODE]** `Client_Coissue_Tape.price` JSON — keyed by `buyer_id` string:
- `price_ss`, `price_sa`, `price_aa`, multiples, `exclusion`, timestamps

Buyer config tables:
- `msrx_client_coissue_buyer` — grid
- `msrx_client_coissue_buyer_middleware` — DPX models
- `msrx_client_coissue_buyer_par` — par formulas
- `msrx_client_coissue_buyer_criteria` — seller-specific overlays

### 7.5 Best execution

**[CONFIRMED FROM CODE]**
- Portfolio: `commit_portfolio_level()` picks best buyer per loan group
- Post-commit: `status_details.best_ex` array built in `get_pre_commit()` and `asset_commit_postprocess()`
- Freedom overlay: `msr_best_ex()` in `freedom/supporting/pricing/msrx/msrx.py`

### 7.6 `pricer_id` and `execution`

| Concept | Location | Values |
|---------|----------|--------|
| `pricer` | `Client_Coissue_Seller.pricer` FK → auth.User | Who priced the tape |
| `execution` | `Client_Coissue_Seller.execution` CharField | `bulk`, `coissue`, `external_api_pricing` |
| Freedom `execution` | `freedom.Tape.execution` | `coissue`, `bulk`, `seasoned` |

**[CONFIRMED FROM CODE]** `pricer_id` is not a coissue DB column — Freedom uses `WholeLoanPrice.pricer` FK.

---

## 8. Stratify / Details / Results

**[CONFIRMED FROM CODE]** No backend endpoint named "Stratify" — maps to these APIs:

### STRATIFY → `GET /msrx/api/viewer_strat/`

- **View:** `ViewerStrat` (`api/views/views.py:456`)
- **Handler:** `viewer_commit_strats(buyer_id_list, tape_id_list, level, method)`
- **Params:** `buyer_id_list`, `tape_id_list`, `level` (details/summary), `method` (sync/async)
- **Purpose:** Stratification/grouping of committed or priced loans across tapes, optionally filtered by buyer
- **Also:** `GET /msrx/api/aggregator/get_tapes?level=loan_strats`

### DETAILS → `GET /msrx/api/viewer_loanlevel/`

- **View:** `ViewerLoanLevelInternal` (`api/views/views.py:485`)
- **Handler:** `viewer_commit_loanlevel_internal()`
- **Purpose:** Loan-level details with min/max/median/avg pricing across buyer_id_list × tape_id_list

### RESULTS → pricing/commit status endpoints

| UI "Results" | API | Returns |
|--------------|-----|---------|
| Pricing progress | `GET /msrx/api/pricing/?level=status` | `pricing_progress`, `pricing_failed_message` |
| Commit progress | `GET /msrx/api/commit_loan_level/?level=status` | `commit_progress` |
| Freedom tape details | `GET /freedom/tape-details/<tape_id>/` | WL tape detail |
| Freedom indicative | `GET /freedom/indicative-details/<tape_id>/` | Indicative pricing detail |

**[LIKELY / INFERRED]** Frontend "Stratify / Details / Results" buttons map to `viewer_strat`, `viewer_loanlevel`, and pricing status — confirm in KT.

---

## 9. Pricing Engine

### 9.1 MSR coissue engines

| Engine | Entry | Tables |
|--------|-------|--------|
| Grid pricing | `price_through_grid_as_of_date()` | `msrx_client_coissue_buyer`, `msrx_client_coissue_buyer_criteria` |
| Middleware/DPX | `price_through_middleware()` | `msrx_client_coissue_buyer_middleware` |
| Par rates | `api/supporting/support_par.py` | `msrx_client_coissue_buyer_par`, PHH realtime |
| Seasoned | Seasoned-specific paths in `api/views/seasoned.py` | `msrx_client_seasoned_*` |

### 9.2 Freedom whole-loan engine

| Component | Path |
|-----------|------|
| Pricing model service | `freedom/supporting/services/pricing.py` |
| Agency (FNMA/FHLMC) | `freedom/supporting/pricing/agency/` |
| Rules engine | `freedom/models/rules_based.py` — Step → Rule |
| MSR overlay on WL | `freedom/supporting/pricing/msrx/msrx.py` |
| Workflows | `freedom/supporting/pricing/workflows/` |

### 9.3 One loan through pricing (MSR)

```
Client_Coissue_Tape (approved)
  → msr_pricing() selects active buyers (grid inuse=True, coissue flag)
  → asset_price_v3()
      → for each buyer: grid price and/or middleware price
      → margin overlay from MSRX_User.user_details
  → tape.price[buyer_id] = {price_ss, price_sa, price_aa, exclusion, ...}
  → seller.status_details.priced_buyer_list updated
```

---

## 10. Commitment

### 10.1 What is a commitment?

**[CONFIRMED FROM CODE]** A commitment assigns each loan to a specific buyer at a specific price/remit/agency, stored in `Client_Coissue_Tape.commitment` JSON, with tape-level status progressing to `confirmed`.

### 10.2 Flow

```
POST /msrx/api/commit_loan_level/
  → CommitLoanLevel [api/views/commit.py]
  → loan_level_commit_helper() [api/api_handler.py:2454]
      → asset_price_v3() per commit group (re-price)
      → commit_group() [api/api_handler.py:4968]
          → writes commitment JSON per loan
          → tape.status = "pre-commit"

POST /msrx/api/confirm_commit/
  → confirm_commit() [api/supporting/services/msr_commit.py:80]
      → if status == "pre-commit":
          → status = "confirmed"
          → asset_commit_postprocess()
          → post_loan_to_sqs() per loan
          → create_commit_dd_records_and_values(commit_type="msrx_coissue")
          → delivery_month assignment
          → loan number assignment (if configured)
          → email notifications
```

### 10.3 commitment JSON structure

**[CONFIRMED FROM CODE]** `Client_Coissue_Tape.commitment`:
```json
{"buyer_id": "...", "remit": "...", "agency": "...", "price": "...", "commitment_date": "..."}
```

**[CONFIRMED FROM CODE]** `status_details.best_ex` — array of buyer/agency/remit/price groups at tape level.

**[NOT FOUND IN REPO]** Field `committed_buyer` — use `commitment.buyer_id` or `best_ex[].buyer_id`.

**[CONFIRMED FROM CODE]** `commit_type` only in `create_commit_dd_records_and_values()` — values `"msrx_coissue"` | `"whole_loan"` for DD record creation, not a tape status.

### 10.4 Bulk vs loan-level

| Type | Endpoint | Function |
|------|----------|----------|
| Loan-level | `commit_loan_level` | `commit_group()` per selected loans |
| Portfolio-level | `commit_portfolio_level` | `commit_portfolio_level()` — legacy |
| Quick commit | `commit_loan_level_quick` | No re-price |
| Freedom WL | `POST /freedom/commit-tape/` | `CommitTape` |
| External API | `POST /msrx/api/commit/` + `commit-confirm/` | `api/views/api.py` |

### 10.5 Cancellation/reversal

**[UNCLEAR — ASK IN KT]** Limited evidence of commit reversal in code; `auto_resell_async` exists in `support_committing.py` — confirm production support.

---

## 11. Buyer Workflow

### 11.1 Buyer representation

**[CONFIRMED FROM CODE]** `MSRX_User` with `user_role="buyer"`. Pricing config in `Client_Coissue_Buyer*` tables keyed by `client` FK.

### 11.2 What Buyer sees / does

| Action | API | Logic |
|--------|-----|-------|
| View committed tapes | `GET /msrx/api/buyer_committed_tapes/` | Filters `status=confirmed` where buyer in `priced_buyer_list` |
| Transfer status check | Same endpoint — updates `status_details.transfer_status` | Checks `Client_Coissue_Tape.transfer` field |
| Active buyer discovery | `GET /msrx/api/get_active_buyer/` | Buyers with active grids for seller |
| Grid management | Admin: `GET/POST /msrx/api/grid/` | `Client_Coissue_Buyer.grid_info` |
| Par rates | `GET /msrx/api/buyer_par/` | `Client_Coissue_Buyer_Par` |
| Analytics | `api/views/analytics.py` | Buyer-scoped reporting |

### 11.3 How tapes reach buyers

**[CONFIRMED FROM CODE]** Buyers don't "receive" tapes directly — sellers/aggregators upload, pricing runs against buyer grids, commitment selects buyer, confirmation triggers Super Transfer SQS + SFTP delivery to buyer.

### 11.4 Buyer eligibility

**[CONFIRMED FROM CODE]** `Client_Coissue_Buyer_Criteria` — per buyer-seller JSON criteria; `pricing_pre_check()` validates buyer grid/middleware availability; `counterparty` JSON on `MSRX_User` links buyers to aggregators.

---

## 12. Investor Workflow

### 12.1 What "Investor" means here

**[CONFIRMED FROM CODE]** `MSRX_User` with `user_role="investor"` — primarily a **Freedom whole-loan concept**, not a standard MSR-X portal login role.

| Attribute | Value |
|-----------|-------|
| DB | `user_role="investor"`, `correspondent` FK → aggregator `MSRX_User` |
| Login | Typically **no django User** — created by Freedom without login |
| API | `get_investor_for_correspondent()` — `api/supporting/user_management.py` |
| Freedom | Investor management, margins, counterparty in `freedom/views/views.py` |
| EOD reports | `email_investor_eod_pricingsummary()` — cron in LIVE |

**[CONFIRMED FROM CODE]** Buyer ≠ Investor. In reports, `end_investor` often means committed buyer name from `commitment.buyer_name`.

**[UNCLEAR — ASK IN KT]** Whether any investors have MSRX portal logins in production or are Freedom-only entities.

---

## 13. Post-Commit Workflow

### 13.1 After confirmation

**[CONFIRMED FROM CODE]**

```
confirm_commit()
  → asset_commit_postprocess()        # best_ex summary, emails
  → post_loan_to_sqs() per loan       # if S3 docs exist
  → create_commit_dd_records_and_values("msrx_coissue")  # DD loan records
  → delivery_month assignment
  → assign_deals_to_loans()           # PSA deals
  → loan number assignment (LoanNumbers table)
  → email_commit() / email_notification()
```

### 13.2 Transfer

| Component | Role |
|-----------|------|
| `EMResource` | eMortgage transfer state on `Client_Coissue_Tape.transfer` |
| `Transfer/` app | Investor Connect monitoring, EM API logs, KPI |
| `BuyerCommittedTapes` | Buyer-side transfer completion check |

### 13.3 Boarding

| Component | Role |
|-----------|------|
| `Boarding_Staging` | Wide flat schema for boarding file generation |
| `supertransfer/support_boarding_file_generation.py` | Scheduled SFTP boarding file delivery |
| `commitrecon/` | RP boarding reconciliation, purchase advice |

### 13.4 Due Diligence

| Component | Role |
|-----------|------|
| `duediligence.Loan` | QC hub — `msrx_coissue_loan` FK |
| `create_commit_dd_records_and_values()` | Auto-creates DD records on confirm |
| Bedrock SQS | Document AI processing trigger |

### 13.5 What MSRX owns vs hands off

| Phase | Owned here | External |
|-------|-----------|----------|
| Commit confirm | Yes | — |
| SQS loan processing | Producer only | Super Transfer worker (separate repo) |
| Document OCR/classification | Trigger only | Bedrock consumer |
| SFTP delivery | Yes (supertransfer) | Buyer SFTP endpoints |
| Boarding file generation | Yes | — |
| eMortgage transfer | Partial (EMResource) | eMortgage API |

---

## 14. Super Transfer Integration

### 14.1 MSRX as SQS producer

**[CONFIRMED FROM CODE]** Single production SQS send for loan processing:

**File:** `api/supporting/support_committing.py:157-187`  
**Function:** `post_loan_to_sqs(seller_id, buyer_id, loan_number)`  
**Called from:** `api/supporting/services/msr_commit.py:133` (inside `confirm_commit()`)

```
Precondition: S3 folder exists and non-empty
  Bucket: supertransfer-{MSRX_ENV.lower()}
  Path: SuperTransfer/{seller_id}/{buyer_id}/{loan_number}/

Queue: https://sqs.us-east-1.amazonaws.com/{AWS_ACCOUNT_ID}/loansToprocess-{MSRX_ENV.lower()}
Message: {"seller-loan_id": "{seller_id}-{buyer_id}_{loan_number}"}
Example: {"seller-loan_id": "117-42_2208066387"}

Retry: NONE — bare try/except returns False
```

### 14.2 seller-loan_id vs loan_id contract

| Context | Key | Format |
|---------|-----|--------|
| SQS `loansToprocess` | `seller-loan_id` | `{seller_id}-{buyer_id}_{loan_number}` |
| DynamoDB (reprocess) | `seller-loan_id` | Same composite — `duediligence/utils/reprocess_loan_helpers.py` |
| ST API `ReceiveMissingLoans` | `seller-loan_id` | **Misleading — value is loan number only** (`supertransfer/views/views.py`) |
| ST HTTP SFTP upload | `loan_id` | Seller loan number string |
| Bedrock SQS | `loan_id` | DD DB integer PK |

**[UNCLEAR — MUST ASK IN KT]** Whether the Super Transfer worker derives internal `loan_id` from `seller-loan_id` + S3 path, or whether message contract mismatch with `super_transfer_client` repo is a version drift issue.

### 14.3 Super Transfer app (in-repo)

| Capability | Path |
|------------|------|
| Exception checking | `supertransfer/views/exceptions.py` |
| Boarding file generation | `supertransfer/supporting/support_boarding_file_generation.py` |
| SFTP document delivery | `supertransfer/support_super_transfer.py` |
| Scheduled delivery | Started from `api/urls/urls.py:39-45` |
| Missing loans API | `POST /supertransfer/missing_loans/` (API-key auth) |
| Epic integration | `supertransfer/supporting/guidance.py` |

### 14.4 DynamoDB

**[CONFIRMED FROM CODE]** `duediligence/utils/reprocess_loan_helpers.py` — tables `supertransfer-{env}DB`. Used for reprocess tracking; deleted on reprocess.

---

## 15. AWS Integrations

| Service | Status | Purpose | Key files | Env vars |
|---------|--------|---------|-----------|----------|
| **S3** | ACTIVE | Tapes, ST docs, O365 tokens, grids | `TapeManager/supporting/support_s3storage.py`, `EmailTrading/utils.py` | `S3_BUCKET_NAME`, `SUPER_TRANSFER_S3_BUCKET_NAME`, `AWS_ACCESS_KEY`, `AWS_SECRET_KEY` |
| **SQS** | ACTIVE | Loan processing + Bedrock docs | `support_committing.py`, `support_bedrock_process_helpers.py` | `AWS_ACCOUNT_ID`, `MSRX_ENV` |
| **DynamoDB** | ACTIVE (narrow) | ST loan tracking | `reprocess_loan_helpers.py` | `AWS_REGION` |
| **SES** | NOT FOUND | — | — | — |
| **SNS** | NOT FOUND | — | — | — |
| **Lambda** | EXTERNAL | No boto3 client in repo | — | — |
| **Secrets Manager** | NOT FOUND | Uses python-decouple | `ebdjango/settings/shared.py` | Direct env vars |
| **Cognito** | NOT FOUND | — | — | — |
| **CloudWatch** | PASSIVE | EB enhanced health only | `.ebextensions/enhanced-health.config` | — |
| **Textract** | INDIRECT | Bucket `textraction` referenced | `supertransfer/views/views.py` | — |

**S3 buckets by environment** (`ebdjango/settings/{dev,uat,demo,live}.py`):
- General: `msrxtape` (dev), `msrxuat`, `msrxdemo`, `msrxlive`
- Super Transfer: `supertransfer-{env}`

---

## 16. Email

### 16.1 Production implementation — O365 / Microsoft Graph

**[CONFIRMED FROM CODE]**

| Component | Path |
|-----------|------|
| Core send | `EmailTrading/utils.py` → `send_email_notif()`, `send_branded_email_notif()` |
| Auth | `AZURE_CLIENT_ID` + `AZURE_SECRET` from env |
| Token storage | S3: `o365_token.txt`, `EmailTrading/tokens/{brand}/` |
| Library | `O365==2.1.2` |

**Widespread callers:** commit emails, Freedom reports, DD notifications, Super Transfer, analytics, CAAS workflows.

### 16.2 Email monitoring (production)

**[CONFIRMED FROM CODE]** APScheduler every 15s on leader: `EmailTrading/supporting/refresh.py` → `enable_emailmonitor()`. Registered in `api/utils/misc.py`.

### 16.3 SES — NOT USED

**[NOT FOUND IN REPO]** No `boto3.client('ses')`.

### 16.4 Legacy

**[LIKELY LEGACY]** `api/supporting/refinitiv_rto/Refinitiv_Rate_Checker.py` — raw SMTP, not integrated with `send_email_notif`.

---

## 17. Background Jobs

### 17.1 No Celery / Redis

**[NOT FOUND IN REPO]** No `celery.py`, `shared_task`, Redis broker.

### 17.2 APScheduler + django-apscheduler (primary)

**[CONFIRMED FROM CODE]**

| Component | Path |
|-----------|------|
| Bootstrap | `ebdjango/wsgi.py` → `leader_election_process()` |
| Leader election | `api/utils/misc.py` — `LeaderElection` model, `ENV_FLAG=CLOUD` |
| Job registry | `api/cron_jobs.py` (~20+ jobs) |
| Job store | `django_apscheduler.jobstores.DjangoJobStore` |

**Sample jobs** (`api/cron_jobs.py` + `api/utils/misc.py`):

| Job | Trigger | Purpose |
|-----|---------|---------|
| Email monitor refresh | 15s interval | `EmailTrading/supporting/refresh.py` |
| Email monitor duplicate check | Scheduled | Duplicate detection |
| RoundPoint trial balance | Cron | `analytics/support_ftp/file_transfer.py` |
| Second lien SFTP ingest | Cron | `secondlien/supporting/` |
| Freedom/Greenway/ServiceMac daily emails | Cron | Branded reports |
| CAAS workflow jobs | Cron | `caas/engine/workflow.py` |
| FNMA pricing history | Cron | `freedom/cron_jobs/metaproduct_pricing_history.py` |
| Investor Connect monitoring | Cron | `Transfer/supporting/monitoring.py` |
| CRA daily/weekly | LIVE only | `freedom/supporting/cra/` |
| Super Transfer SFTP delivery | On URL import (non-DEV) | `supertransfer/support_super_transfer.py` |
| Boarding file delivery | On URL import (non-DEV) | `support_boarding_file_generation.py` |

### 17.3 Management commands (dev/seed only)

- `msrx/management/commands/seed.py`
- `msrx/management/commands/seedSeason.py`
- `msrx/management/commands/dataGenerator.py`

### 17.4 Failure behavior

**[CONFIRMED FROM CODE]** `custom_listener` in `api/utils/misc.py` emails on missed `deactivate_emailmonitor_daily` job. Most jobs lack in-app retry/DLQ.

---

## 18. External Integrations

| Integration | Status | MSRX → External | Credentials |
|-------------|--------|---------------|-------------|
| **Freedom / FNMA** | ACTIVE | Pricing API, tape mgmt, FNMA updates | `FNMA_TOKEN_ENDPOINT`, `FNMA_API_URL` in settings |
| **PHH** | ACTIVE | Par rate realtime, grid converter | In support_par.py, Grid_Converter.py |
| **RoundPoint** | ACTIVE | Trial balance SFTP, QC rules, boarding | `analytics/support_ftp/`, `Transfer/supporting/roundpoint/` |
| **Microsoft O365** | ACTIVE | All production email | `AZURE_CLIENT_ID`, `AZURE_SECRET` |
| **Laura Mac** | ACTIVE | DD marketplace API | `LAURA_MAC_*` in live.py |
| **EPIC** | ACTIVE | Super Transfer guidance/post | `EPIC_*` in live.py |
| **Voxtur/InfoEx** | ACTIVE | Title orders | `voxtur/supporting/api.py` (Okta) |
| **Benutech** | ACTIVE | Property lookup | `benutech/title_toolbox_api.py` |
| **Refinitiv** | PARTIAL | Credentials model; SMTP checker legacy | `freedom/models/` RefinitivCreds |
| **SFTP** | ACTIVE | ST delivery, second lien, DD deals | `SFTPConfig`, Paramiko throughout |
| **Stripe** | NOT FOUND | — | — |

---

## 19. Error Handling / Logging

| Mechanism | Status | Path |
|-----------|--------|------|
| `activity_log()` | ACTIVE | `base/utils/logs.py` → `User_Activity_Log` |
| `ActivityLogMiddleware` | ACTIVE | `base/middleware/middleware.py` → `APIActivityLog` |
| Super Transfer logs | ACTIVE | `supertransfer/models.py` `Logs` |
| Freedom epic_log | ACTIVE | `freedom/supporting/logging/` |
| Django LOGGING | COMMENTED OUT | `ebdjango/settings/shared.py:157-172` |
| Sentry | NOT FOUND | — |
| CloudWatch SDK | NOT FOUND | EB health only |
| Scheduler alerts | ACTIVE | Email on missed jobs |

### Investigating failures

| Failure type | Where to look |
|--------------|---------------|
| Upload | `status_details.upload_failed_message`, `activity_log` entries for `UploadTapeCSV`, `Tape_Cracking_Log` |
| Pricing | `status_details.pricing_failed_message`, `pricing_progress` |
| Commit | `status_details.commit_failed_message`, `Confirm_commit` activity logs |
| SQS post | `activity_log` in `msr_commit.py` — "Post success/Failed to post" |
| External integration | Domain-specific logs (EM API, Epic, Freedom Log model) |

---

## 20. Deployment

### 20.1 Environments

| Env | `MSRX_ENV` | DB (from settings) | S3 bucket | Host |
|-----|-----------|-------------------|-----------|------|
| DEV | DEV | `msrx_internal_dev` | `msrxtape` | `dev.bluewater-fintech-msrx.com` |
| UAT | UAT | `msrx_uat_new` | `msrxuat` | `uat.bluewater-fintech-msrx.com` |
| DEMO | DEMO | `msrx_demo_new` | `msrxdemo` | `proddemo.bluewater-fintech-msrx.com` |
| LIVE | LIVE | `msrx_live_new` | `msrxlive` | `prodlive.bluewater-fintech-msrx.com` |
| LOCAL | LOCAL | `msrx_v2` on `LOCAL_DB_HOST` | `msrxtape` | — |

**RDS host (LIVE):** `bwftwebappsmall.cb5kkst328ej.us-east-1.rds.amazonaws.com` — `ebdjango/settings/live.py`

### 20.2 Deployment architecture

**[CONFIRMED FROM CODE]**
- AWS Elastic Beanstalk Python platform
- WSGI via `ebdjango.wsgi:application`
- nginx reverse proxy (400MB upload, 300s timeout)
- `collectstatic` on deploy
- TLS 1.3 on ELB
- CI: `.github/workflows/actions.yml` — Ruff + `api.tests` on PRs
- Patch automation: `.github/workflows/patch.yml`

### 20.3 Environment variables

Loaded via `python-decouple` `config()` in settings. Key vars: `SECRET_KEY`, `AWS_ACCESS_KEY`, `AWS_SECRET_KEY`, `AWS_ACCOUNT_ID`, `MSRX_ENV`, `ENV_FLAG`, DB credentials, `AZURE_CLIENT_ID`, `AZURE_SECRET`, integration-specific creds per env file.

---

## 21. Legacy / Dead Code Candidates

| Item | Classification | Evidence |
|------|----------------|----------|
| `CRA` app | **DISABLED in INSTALLED_APPS, ACTIVE in URLs + LIVE cron** | `shared.py` commented; `ebdjango/urls.py` includes `CRA.urls`; `misc.py` CRA jobs |
| `rp` app | **LIKELY LEGACY** | Model-only; superseded by `Boarding_Staging` |
| `@agg_sellers_only` decorator | **DEAD** | Defined, never applied |
| `Client_Aggregator_Seller_Login.access_*` flags | **LIKELY UNUSED server-side** | Stored but not enforced in decorators |
| Refinitiv SMTP checker | **LEGACY SCRIPT** | Not in production email path |
| SES/SNS/Cognito | **NEVER EXISTED** | — |
| Celery/Redis | **NEVER EXISTED** | — |
| `transfer_complete` status | **LIKELY LEGACY** | Commented in model; no active setter found |
| `commit_portfolio_level` | **LIKELY LEGACY** | Superseded by loan-level commit |
| `supertransfer.Loan` model | **LIKELY LEGACY?** | Parallel to `Boarding_Staging` |
| Duplicate `tape_preprocess` | **ACTIVE DUPLICATES** | TapeManager, secondlien, local tool |
| Commented scheduler stops | **DEAD CODE** | `misc.py:1902-1927` |
| `api_handler.py` monolith | **ACTIVE but high-risk** | Central bottleneck — refactor candidate |

**[LIKELY LEGACY — NEED CONFIRMATION]** for all items above.

---

## 22. Complete End-to-End Business Flow

**[CONFIRMED FROM CODE]** Evidence-based flow with key transitions:

```
1. USER LOGIN
   POST /msrx/api/login/
   → auth_user + Token
   → MSRX_User resolution (Django_user_to_msrx_user)
   → role/flags returned
   Tables: auth_user, msrx_msrx_user

2. ROLE RESOLUTION
   aggregator_flag / aggregator_seller_flag / user_role
   → decorators + inline checks
   Tables: msrx_msrx_user, msrx_client_aggregator_seller

3. SELLER/AGGREGATOR — TAPE UPLOAD
   POST /msrx/api/uploadtape_csv/
   → S3: priced_tapes/msr/{...}
   → raw_tape_crack → validation
   → Client_Coissue_Seller (status=uploaded, loancount, upb)
   → Client_Coissue_Tape bulk_create
   Tables: msrx_client_coissue_seller, msrx_client_coissue_tape

4. VALIDATION / APPROVAL
   POST /msrx/api/approve_tape/
   → status: uploaded → approved
   Function: approve_tape()

5. PRICING
   POST /msrx/api/pricing/
   → msr_pricing() → asset_price_v3()
   → price_through_grid + price_through_middleware
   → Client_Coissue_Tape.price JSON updated
   → status: approved → priced
   Tables: msrx_client_coissue_buyer*, msrx_client_coissue_tape

6. PRICE MANAGEMENT (Aggregator view)
   GET /msrx/api/aggregator/get_tapes?level=summary
   → aggregator_get_tape_summary()
   Stratify: GET /msrx/api/viewer_strat/
   Details: GET /msrx/api/viewer_loanlevel/

7. COMMIT (PRE-COMMIT)
   POST /msrx/api/commit_loan_level/
   → loan_level_commit_helper() → commit_group()
   → Client_Coissue_Tape.commitment JSON per loan
   → status: priced → pre-commit
   → status_details.best_ex built

8. CONFIRM
   POST /msrx/api/confirm_commit/
   → status: pre-commit → confirmed
   → asset_commit_postprocess()
   → post_loan_to_sqs() per loan [if S3 docs exist]
   → create_commit_dd_records_and_values("msrx_coissue")
   → delivery_month, loan numbers, emails
   External: SQS loansToprocess-{env}

9. BUYER VIEW
   GET /msrx/api/buyer_committed_tapes/
   → transfer_status tracking

10. SUPER TRANSFER (external worker)
    SQS message → worker processes S3 docs
    → DynamoDB tracking
    → MSRX supertransfer app: QC, boarding files, SFTP delivery

11. BOARDING / DD
    Boarding_Staging populated
    → boarding file generation + SFTP
    → duediligence.Loan QC workflow
    → Bedrock SQS for doc AI (optional)

12. RECON / COMPLETION
    commitrecon: purchase advice, agency loan numbers
    BuyerCommittedTapes: transfer_status → complete
```

**Parallel path:** Freedom whole-loan (`/freedom/price-tape/` → commit → `WholeLoanCommit`) — separate status vocabulary, linked via `Client_Coissue_Seller.whole_loan_tape` FK.

---

## 23. Cross-Repository Architecture

**[CONFIRMED FROM CODE]** + **[LIKELY / INFERRED]** where noted:

```
Browser
  ↓
React Frontend (separate repo)
  ↓ HTTP_HOSTNAME header, Token auth
Express BFF (separate repo — UNCLEAR, not referenced by name)
  ↓
MSRX Django (this repo) — AWS Elastic Beanstalk
  ├── PostgreSQL (RDS)
  │     msrx_* tables, freedom_* tables, duediligence_* tables
  ├── S3
  │     ├── msrx{env} — tapes, grids, tokens
  │     └── supertransfer-{env} — ST documents
  ├── SQS
  │     ├── loansToprocess-{env} → Super Transfer Client (separate repo)
  │     └── filesToBedrock-{env} → Bedrock processor (external)
  ├── DynamoDB
  │     └── supertransfer-{env}DB
  ├── O365 (Microsoft Graph)
  │     └── EmailTrading notifications
  ├── SFTP
  │     ├── Buyer delivery (Super Transfer)
  │     ├── RoundPoint trial balance
  │     └── Second lien ingest
  └── External APIs
        ├── FNMA (Freedom)
        ├── PHH (par rates)
        ├── Laura Mac (DD)
        ├── EPIC (Super Transfer)
        ├── Voxtur/InfoEx (title)
        └── Benutech (property)
```

---

## 24. Security / Operational Risks

**[CONFIRMED FROM CODE]** Read-only review — questions for KT, not fixes:

| Risk | Evidence | KT question |
|------|----------|-------------|
| `ALLOWED_HOSTS = ["...", "*"]` | All env settings files | Is `*` intentional in production? |
| No token expiry | DRF Token default | Token revocation procedure? |
| Long-lived AWS access keys | `AWS_ACCESS_KEY`/`AWS_SECRET_KEY` in all boto3 calls | Are IAM roles available on EB instances? |
| Password policy mismatch | Admin create: 6 chars; user change: 14 chars | Which policy is authoritative? |
| `AdminUsersModify` lacks staff decorator | `api/views/users.py` | Is this endpoint protected in production? |
| SQS no retry/DLQ | `post_loan_to_sqs` bare except | How are failed SQS posts recovered? |
| Leader election ambiguity | WSGI thread + URL import schedulers | Guaranteed single scheduler in multi-worker EB? |
| `CRA` app disabled but routed | `INSTALLED_APPS` vs `urls.py` | Is CRA endpoint live in production? |
| Activity log may capture sensitive data | `ActivityLogMiddleware` | Payload redaction policy? |
| `.env`, `CM.env` in repo root | Present (not audited for secrets) | Are these gitignored in real remote? |
| Credentials in settings files | `live.py` integration creds via config() | Secrets rotation process? |
| `seller-loan_id` contract inconsistency | Multiple naming conventions | Which contract is authoritative for ST worker? |
| `api_handler.py` monolith | Single file ~6400 lines | Incident debugging ownership? |
| No Sentry/structured logging | LOGGING commented out | Production observability stack? |

---

## 25. Confirmed Findings

1. **This is the primary MSRX Django backend** — `/msrx/api/` is the core REST surface.
2. **Modular monolith** with ~20 Django apps sharing one PostgreSQL database.
3. **Token auth** via DRF `TokenAuthentication` — no expiry configured.
4. **`MSRX_User` is the business identity hub** — linked to `auth_user` via OneToOne + auxiliary tables.
5. **Roles:** `user_role` (buyer/seller/investor) + boolean flags (aggregator, aggregator_seller, correspondent_buyer).
6. **MSR coissue workflow** centers on `Client_Coissue_Seller` → `Client_Coissue_Tape` with JSON price/commitment.
7. **Tape status lifecycle:** uploaded → approved → priced → pre-commit → confirmed.
8. **Pricing** uses grid + middleware (DPX) engines writing to `Client_Coissue_Tape.price`.
9. **Commitment** stores per-loan JSON in `commitment` field; tape summary in `status_details.best_ex`.
10. **Super Transfer integration** is SQS producer on confirm — `loansToprocess-{env}` queue.
11. **No Celery/Redis** — APScheduler + leader election on EB.
12. **Email is O365/Graph** — not SES.
13. **Deployed on AWS Elastic Beanstalk** with nginx, WSGI, multi-env via `MSRX_ENV`.
14. **Freedom is a parallel whole-loan platform** in the same repo with its own models/pricing/commit.
15. **Dual boarding staging:** `msrx_boarding_staging` (canonical) + `rp_boarding_staging_table` (legacy).

---

## 26. Unclear Findings

1. **Express BFF contract** — not referenced in code; how routes map to Django endpoints.
2. **Super Transfer worker message contract** — `seller-loan_id` format vs worker's expected `loan_id`.
3. **`aggregator_seller_flag` reliability** — not set on `AggregatorSellerCreate`; relationship vs flag as gate.
4. **`transfer_complete` status** — documented but no active setter found.
5. **Which pricing path is authoritative in production** — MSR grid vs middleware vs Freedom overlay for coissue.
6. **CRA app status** — disabled in INSTALLED_APPS but URL-routed and LIVE cron jobs active.
7. **MFA enforcement** — `PlatformConfiguration.mfa` exists but no login gate; frontend-only?
8. **Investor portal access** — Freedom-only or some have MSRX logins?
9. **Commit reversal/cancellation** — limited code evidence.
10. **Production observability** — no Sentry/CloudWatch SDK; how are incidents detected?
11. **Multi-worker scheduler guarantees** — leader election reliability on EB.
12. **Source of truth for boarding** — `Boarding_Staging` vs `rp_boarding_staging_table` in production.
13. **Which workflows are legacy vs active** — portfolio commit, CRA, TapeManager converters.
14. **Bedrock processor ownership** — separate service/repo?
15. **Environment promotion process** — patch.yml exists but full release workflow unclear.

---

## 27. KT Questions

### 1. Overall architecture

| # | Question | Priority | Why ask | Code evidence |
|---|----------|----------|---------|---------------|
| A1 | Is this Django repo the sole production backend for MSR-X, or are there other active backends? | 🔴 MUST ASK | Determines debugging ownership | Only Django backend found |
| A2 | What is the Express BFF's role and route mapping to `/msrx/api/`? | 🔴 MUST ASK | BFF not in repo | User context only |
| A3 | How many EB instances run per environment and how is scheduler leadership guaranteed? | 🔴 MUST ASK | Multi-worker + leader election | `wsgi.py`, `LeaderElection` model |
| A4 | What is the production observability stack (Sentry, CloudWatch, Datadog)? | 🔴 MUST ASK | No structured logging found | LOGGING commented out |

### 2. Roles

| # | Question | Priority | Why ask | Code evidence |
|---|----------|----------|---------|---------------|
| R1 | Is `aggregator_seller_flag` always set in production when `Client_Aggregator_Seller` exists? | 🔴 MUST ASK | Flag not set on create | `AggregatorSellerCreate` |
| R2 | Are `Client_Aggregator_Seller_Login.access_*` flags enforced anywhere (frontend only)? | 🟡 CONFIRM | Stored but not in decorators | `user.py` model |
| R3 | Do any investors have MSRX portal logins? | 🟡 CONFIRM | Freedom creates without User | `freedom/views/` |
| R4 | What is the MFA flow — is `PlatformConfiguration.mfa` enforced client-side? | 🟡 CONFIRM | No server login gate | `platform.py`, `auth.py` |

### 3. Seller/Aggregator

| # | Question | Priority | Why ask | Code evidence |
|---|----------|----------|---------|---------------|
| S1 | What is the canonical seller onboarding path — admin registration vs aggregator self-service? | 🟡 CONFIRM | Multiple creation paths | `admin.py`, `aggregator.py` |
| S2 | How are aggregator-to-seller relationships maintained when sellers are deactivated? | 🟡 CONFIRM | No soft-delete pattern clear | `Client_Aggregator_Seller` |

### 4. Tape upload

| # | Question | Priority | Why ask | Code evidence |
|---|----------|----------|---------|---------------|
| T1 | Is v1 (`uploadtape_csv`) or v2 (`uploadtape_csv/v2`) the production upload path? | 🔴 MUST ASK | Two parallel paths | `api/urls/index.py` |
| T2 | Which tape cracking path is used per seller — TapeManager, tapecrack SQL, or seller-specific? | 🟡 CONFIRM | Multiple converters | `TapeManager/`, `tapecrack/` |
| T3 | Is `transfer_complete` status still used? | 🟡 CONFIRM | Commented in model | `coissue.py:19` |

### 5. Pricing

| # | Question | Priority | Why ask | Code evidence |
|---|----------|----------|---------|---------------|
| P1 | For coissue tapes, is grid pricing, middleware (DPX), or both authoritative? | 🔴 MUST ASK | Both run in `asset_price_v3` | `support_pricing.py` |
| P2 | How is "best execution" determined — highest price, cap-aware, buyer priority? | 🔴 MUST ASK | Multiple algorithms | `commit_portfolio_level`, `msr_best_ex` |
| P3 | What does the Price Management "Results" button call? | 🟡 CONFIRM | No exact backend name | Maps to pricing status likely |
| P4 | Is Freedom pricing used for any coissue tapes via `whole_loan_tape` FK? | 🟡 CONFIRM | FK exists | `Client_Coissue_Seller.whole_loan_tape` |
| P5 | Who maintains buyer grids — BWFT admin or buyers themselves? | 🟡 CONFIRM | Admin endpoints exist | `api/views/admin.py`, `grid.py` |

### 6. Buyer

| # | Question | Priority | Why ask | Code evidence |
|---|----------|----------|---------|---------------|
| B1 | How do buyers receive notification of new commitments? | 🟡 CONFIRM | Email functions exist | `email_commit()` |
| B2 | What is the buyer's role in transfer completion — passive or active? | 🟡 CONFIRM | `transfer_status` on buyer endpoint | `BuyerCommittedTapes` |

### 7. Commitment

| # | Question | Priority | Why ask | Code evidence |
|---|----------|----------|---------|---------------|
| C1 | Is loan-level commit the only active commit path, or is portfolio-level still used? | 🔴 MUST ASK | Both exist | `commit_portfolio_level` vs `commit_loan_level` |
| C2 | Can commitments be reversed after confirm? | 🔴 MUST ASK | Limited code | `auto_resell_async` |
| C3 | What triggers `create_commit_dd_records_and_values` failures and how are they recovered? | 🟡 CONFIRM | try/except in confirm | `msr_commit.py` |

### 8. Post-close

| # | Question | Priority | Why ask | Code evidence |
|---|----------|----------|---------|---------------|
| PC1 | What is the full post-confirm pipeline — which steps are MSRX vs external? | 🔴 MUST ASK | Multiple handoffs | SQS, DD, ST, boarding |
| PC2 | Is `Boarding_Staging` or `rp_boarding_staging_table` the production boarding source? | 🔴 MUST ASK | Dual staging tables | Both exist |
| PC3 | When are boarding files generated — on confirm, on schedule, or on demand? | 🟡 CONFIRM | Scheduled + on-demand paths | `support_boarding_file_generation.py` |

### 9. Super Transfer

| # | Question | Priority | Why ask | Code evidence |
|---|----------|----------|---------|---------------|
| ST1 | What is the authoritative SQS message contract for `loansToprocess`? | 🔴 MUST ASK | seller-loan_id vs loan_id uncertainty | `support_committing.py:181` |
| ST2 | How does the ST worker resolve `loan_id` from `seller-loan_id`? | 🔴 MUST ASK | Worker is separate repo | Message format |
| ST3 | What happens when `post_loan_to_sqs` returns False (no S3 docs)? | 🔴 MUST ASK | Silent failure | `msr_commit.py:144-152` |
| ST4 | Is there a manual reprocess procedure for failed ST loans? | 🔴 MUST ASK | `reprocess_loan_helpers.py` exists | DynamoDB reprocess |
| ST5 | Who uploads documents to `SuperTransfer/{seller}/{buyer}/{loan}/` in S3? | 🔴 MUST ASK | Precondition for SQS | `folder_exists_and_not_empty` |

### 10. Database

| # | Question | Priority | Why ask | Code evidence |
|---|----------|----------|---------|---------------|
| D1 | Which tables are source-of-truth vs deprecated? | 🔴 MUST ASK | Dual paradigms | MSR vs Freedom, boarding staging |
| D2 | Are DEV/UAT/DEMO databases refreshed from LIVE? How? | 🟡 CONFIRM | Multiple DB names | settings files |
| D3 | What is the migration deployment process? | 🟡 CONFIRM | Many migrations | `msrx/migrations/` |

### 11. AWS

| # | Question | Priority | Why ask | Code evidence |
|---|----------|----------|---------|---------------|
| AW1 | Are EB instances using IAM roles or access keys? | 🔴 MUST ASK | Keys in code | `get_env_var("AWS_ACCESS_KEY")` |
| AW2 | What is the SQS DLQ and retry policy (outside Django)? | 🔴 MUST ASK | No in-app retry | `post_loan_to_sqs` |
| AW3 | Who owns the Bedrock SQS consumer? | 🟡 CONFIRM | Producer only | `support_bedrock_process_helpers.py` |

### 12. Background jobs

| # | Question | Priority | Why ask | Code evidence |
|---|----------|----------|---------|---------------|
| J1 | Full list of production cron jobs per environment | 🔴 MUST ASK | LIVE-only vs all-env | `misc.py:1873-1899` |
| J2 | What happens if leader election fails? | 🔴 MUST ASK | Jobs may not run | `leader_election_process` |
| J3 | Is email monitor (15s interval) running in all non-DEV envs? | 🟡 CONFIRM | High frequency | `misc.py:1850` |

### 13. External integrations

| # | Question | Priority | Why ask | Code evidence |
|---|----------|----------|---------|---------------|
| E1 | Which integrations are active in LIVE — PHH, RoundPoint, Laura Mac, EPIC? | 🔴 MUST ASK | All coded, unclear which used | Multiple apps |
| E2 | Is FNMA API pricing live or staging? | 🟡 CONFIRM | `FNMA_API_URL` in settings | `freedom/supporting/pricing/agency/` |
| E3 | Email trading — which mailboxes are monitored in production? | 🟡 CONFIRM | Multiple brands | `EmailTrading/models.py` |

### 14. Deployment

| # | Question | Priority | Why ask | Code evidence |
|---|----------|----------|---------|---------------|
| DP1 | What is the release process (dev → uat → demo → live)? | 🔴 MUST ASK | patch.yml exists | `.github/workflows/` |
| DP2 | Are database migrations run automatically on deploy? | 🔴 MUST ASK | Not in ebextensions | `.ebextensions/django.config` |
| DP3 | Who has access to LIVE EB environment? | 🟡 CONFIRM | Operational | — |

### 15. Monitoring/error recovery

| # | Question | Priority | Why ask | Code evidence |
|---|----------|----------|---------|---------------|
| M1 | How do you investigate a failed tape upload in production? | 🔴 MUST ASK | Multiple log tables | activity_log, status_details |
| M2 | How do you re-trigger pricing for a stuck tape? | 🔴 MUST ASK | Async workers | `pricing_progress` |
| M3 | What is the incident response runbook? | 🔴 MUST ASK | Not in repo | — |

### 16. Legacy/current functionality

| # | Question | Priority | Why ask | Code evidence |
|---|----------|----------|---------|---------------|
| L1 | Is the CRA app (`/cra-check/`) live despite being removed from INSTALLED_APPS? | 🔴 MUST ASK | Hybrid state | `shared.py`, `urls.py` |
| L2 | Is `TapeManager` still used or fully replaced by `tapecrack`? | 🟡 CONFIRM | Both active | Both apps routed |
| L3 | Is `rp` app safe to ignore? | 🟡 CONFIRM | Still imported | `Transfer/views.py` |
| L4 | What Freedom features are actively used vs dormant? | 🟡 CONFIRM | 100+ routes | `freedom/urls.py` |

### 🟢 ANSWERED FROM CODE (don't waste KT time)

- Auth mechanism: DRF Token auth
- Login endpoint: `POST /msrx/api/login/`
- Core tape model: `Client_Coissue_Seller` + `Client_Coissue_Tape`
- Tape status values: uploaded, approved, priced, pre-commit, confirmed
- Pricing storage: `Client_Coissue_Tape.price` JSON
- Commitment storage: `Client_Coissue_Tape.commitment` JSON
- SQS queue name pattern: `loansToprocess-{env}`
- Email provider: O365/Microsoft Graph
- No Celery/Redis
- Deployment: AWS Elastic Beanstalk
- Environments: DEV, UAT, DEMO, LIVE, LOCAL

---

## 28. Top 20 Monday KT Questions

| Rank | Question | Category |
|------|----------|----------|
| **#1** | What is the authoritative SQS message contract for Super Transfer (`seller-loan_id` format) and how does the worker process it? | Super Transfer |
| **#2** | What happens when `post_loan_to_sqs` fails (no S3 docs or SQS error) — is there recovery? | Super Transfer |
| **#3** | Who uploads loan documents to `SuperTransfer/{seller}/{buyer}/{loan}/` in S3 and when? | Super Transfer |
| **#4** | What is the full post-confirm pipeline (MSRX vs external services) step by step? | Post-close |
| **#5** | Which pricing engine is authoritative for coissue — grid, middleware (DPX), or both? | Pricing |
| **#6** | How is "best execution" / winning buyer actually determined? | Pricing |
| **#7** | Is loan-level commit the only active commit path in production? | Commitment |
| **#8** | Can commitments be reversed after confirm? | Commitment |
| **#9** | Is v1 or v2 tape upload the production path? | Tape upload |
| **#10** | Which tables are source-of-truth vs deprecated (boarding staging, rp, dual loan models)? | Database |
| **#11** | How many EB instances per env and how is scheduler leadership guaranteed? | Architecture |
| **#12** | What is the production observability/incident response stack? | Monitoring |
| **#13** | What is the release/deployment process (dev → uat → demo → live)? | Deployment |
| **#14** | Are EB instances using IAM roles or long-lived AWS access keys? | AWS |
| **#15** | What is the Express BFF's role and how does it map to Django routes? | Architecture |
| **#16** | Which external integrations are actively used in LIVE (PHH, RP, Laura Mac, EPIC, FNMA)? | Integrations |
| **#17** | Is `aggregator_seller_flag` reliably set, or is `Client_Aggregator_Seller` relationship the real gate? | Roles |
| **#18** | What is the manual reprocess procedure for failed Super Transfer loans? | Super Transfer |
| **#19** | Is the CRA app live despite being removed from INSTALLED_APPS? | Legacy |
| **#20** | What Freedom features are actively used vs the MSR coissue workflow being the primary path? | Legacy/Pricing |

---

## Appendix A: Key File Index

| Area | Path |
|------|------|
| Settings | `ebdjango/settings/shared.py`, `{dev,uat,demo,live,local}.py` |
| Root URLs | `ebdjango/urls.py` |
| API routes | `api/urls/index.py`, `api/urls/admin.py` |
| Login | `api/views/auth.py` |
| User models | `msrx/models/user.py` |
| Coissue models | `msrx/models/coissue.py` |
| Buyer models | `msrx/models/buyer.py` |
| User resolution | `base/utils/users.py` |
| Role decorators | `base/decorators/user_level_decorators.py` |
| Central orchestration | `api/api_handler.py` |
| Tape upload | `api/supporting/services/tape_upload.py` |
| MSR pricing | `api/supporting/services/msr_pricing.py`, `api/supporting/support_pricing.py` |
| MSR commit | `api/supporting/services/msr_commit.py` |
| SQS producer | `api/supporting/support_committing.py` |
| Aggregator views | `api/views/aggregator.py` |
| Super Transfer | `supertransfer/support_super_transfer.py` |
| Email | `EmailTrading/utils.py` |
| Scheduler | `api/utils/misc.py`, `api/cron_jobs.py` |
| WSGI startup | `ebdjango/wsgi.py` |
| Internal docs | `context/BACKEND_MAP.md`, `context/BACKEND_HOTSPOTS.md` |

## Appendix B: Internal Documentation Found in Repo

The repo contains prior engineering docs that complement this audit:
- `context/BACKEND_MAP.md` — entry points and module map
- `context/BACKEND_HOTSPOTS.md` — risk hotspots
- `context/DATA_DEPENDENCY_MAP.md` — data dependencies
- `context/REQUEST_FLOWS.md` — request flows
- `docs/knowledge/` — prior reverse-engineering artifacts

**Recommendation:** Cross-reference this audit with `context/BACKEND_HOTSPOTS.md` during KT for known technical debt areas.

---

*End of audit report.*
