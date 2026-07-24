# Super Transfer Client — Deployment & Architecture Investigation

This report is based **only on repository evidence** in `d:\BLUE-WATER`, with emphasis on `super_transfer_client/`. Where the handover meeting mentioned things not present in the repo, those gaps are called out explicitly.

---

## 1. Application Entry Points

| FILE | PATH | FUNCTION/CLASS | PURPOSE | HOW STARTED | LONG-RUNNING? | EVIDENCE |
|------|------|----------------|---------|-------------|---------------|----------|
| **Main worker** | `super_transfer_client/scripts/main.py` | `main()` | SQS poll loop for loan + missing-file jobs | EC2 crontab (`flock` + `python3.12`) or manual `python3 scripts/main.py` | **Yes** | `while process_flag():` + `sqs.receive_message(...)` |
| Loan processor | `scripts/process_loan_handler.py` | `processLoan(res, lock)` | Full loan pipeline: S3 download → classify → extract → API/DB updates | Called from `main.py` | No (per-message) | `main.py:110` |
| Missing-file processor | `scripts/process_file_handler.py` | `processFile(res, lock)` | Process one uploaded missing document for an existing loan | Called from `main.py` | No (per-message) | `main.py:69` |
| AWS/ML bootstrap | `scripts/helper_functions.py` | `ensure_model_context()` | Loads boto3 clients, pickles, NLTK at import time | Imported by handlers | N/A (module init) | `helper_functions.py:182` `ensure_model_context()` |
| Model deploy hook | `scripts/upload_model.py` | `if __name__ == "__main__"` | Upload TF-IDF/NB model artifacts to S3 on deploy | CodeDeploy `ApplicationStart` hook | One-time | `appspec.yml:18-20` |
| Cron enable/disable | `scripts/start_cron.sh`, `stop_cron.sh` | shell | Register/remove crontab line; kill python on stop | CodeDeploy `AfterInstall` / `BeforeInstall` | N/A | `appspec.yml:11-16` |
| Workspace reset | `scripts/clean_workspace.sh` | shell | Git reset, pyc cleanup during deploy | CodeDeploy hooks | One-time | `appspec.yml:8-15` |
| Deployment gate | `base/workflows/process_flag.py` | `process_flag()` | Reads DynamoDB flag; worker exits when false | Called from `main.py` loop condition | N/A | `main.py:48` |
| Manual dev tool | `scripts/Manual_Loan_Process.ipynb` | notebook cells | Manually invoke `processLoan` / `processFile` | Jupyter, manual | No | notebook cells |
| Per-doc extract CLIs | `scripts/extract*.py` (30+ files) | various `if __name__ == "__main__"` | Standalone extraction testing | Manual `python extractX.py` | No | grep across `scripts/` |
| Segregation test | `base/workflows/doc_seg.py` | `if __name__ == "__main__"` | Test JSON→page mapping | Manual | No | `doc_seg.py:103` |

**SQS producer (not the worker — lives in sibling `msrx_v2.0`):**

| FILE | FUNCTION | PURPOSE |
|------|----------|---------|
| `msrx_v2.0/api/supporting/support_committing.py` | `post_loan_to_sqs()` | Enqueue loan after commit if S3 folder has files |

### Main Super Transfer worker

**`super_transfer_client/scripts/main.py` → `main()`** is the primary long-running worker. It is invoked at module load (`main()` on line 140, not guarded by `if __name__ == "__main__"`).

---

## 2. How the Worker Stays Running

```
EC2 crontab (* * * * *)
    ↓
flock /home/ec2-user/super_transfer_client/cron.lock
    ↓
python3.12 /home/ec2-user/super_transfer_client/scripts/main.py
    ↓
main() starts
    ↓
ensure_model_context() [import side-effect in helper_functions]
    ↓
while process_flag():          ← DynamoDB gate; exits during deploy
    ↓
sqs.receive_message(missing_file_queue)   [20s long poll, visibility 1200s]
    ↓ (if no message)
sqs.receive_message(loan_queue)           [20s long poll, visibility 1200s]
    ↓ (if no messages)
sleep(5), regenerate local dirs, repeat
```

**Stay-alive mechanisms (confirmed):**

1. **Inner loop:** `while process_flag():` in `main.py:48`
2. **Long polling:** `WaitTimeSeconds=20` on both queues
3. **Idle backoff:** `time.sleep(5)` when queues are empty (`main.py:131`)
4. **Error backoff:** `time.sleep(120)` on uncaught loop exceptions (`main.py:136`)
5. **Cron watchdog:** crontab runs every minute; `flock` ensures only one instance (`start_cron.sh:7-14`)
6. **Visibility heartbeat:** background thread extends visibility to 3600s every 600s during loan processing (`main.py:22-33`, `104-113`)

**Not found:** systemd, supervisor, Docker restart policy, PM2, nohup/screen/tmux in repo.

---

## 3. How SQS Is Used

### Where the client is created

```23:37:super_transfer_client/base/workflows/runtime.py
def initialize_aws_variables():
    ...
    sqs = client("sqs", region_name=config.region_name)
    queue_url = env_variables.get_sqs_loan_queue_url()
    missing_file_queue_url = env_variables.get_missing_file_sqs_queue_url()
    bedrock_queue_url = env_variables.get_sqs_bedrock_queue_url()
```

Called once at startup via `ensure_model_context()` in `helper_functions.py:151`.

### Queue URL source

From AWS Secrets Manager secret `SUPER_TRANSFER_AWS_VARIABLES`, keyed by active git branch (`Dev`/`UAT`/`Demo`/`Live`):

```119:121:super_transfer_client/scripts/env_variables.py
sqs_loan_queue_url = st_variables_secret.get(f"sqs_loan_queue_url_{git_branch.lower()}", "")
missing_file_sqs_queue_url = st_variables_secret.get(f"missing_file_sqs_queue_url_{git_branch.lower()}", "")
sqs_bedrock_queue_url = st_variables_secret.get(f"sqs_bedrock_queue_url_{git_branch.lower()}", "")
```

Notifications queue is **hardcoded** (not from secret):

```265:267:super_transfer_client/scripts/env_variables.py
base_url = "https://sqs.us-east-1.amazonaws.com/634018989711/supertransfer-notifications-"
return base_url + git_branch.lower()
```

Django producer uses a **different naming pattern**:

```180:181:msrx_v2.0/api/supporting/support_committing.py
QueueUrl=f"https://sqs.us-east-1.amazonaws.com/{get_env_var('AWS_ACCOUNT_ID')}/loansToprocess-{os.environ['MSRX_ENV'].lower()}",
MessageBody=json.dumps({"seller-loan_id": f"{seller_id}-{buyer_id}_{loan_number}"}),
```

| Queue | Role in ST client | Producer in repo? |
|-------|-------------------|-------------------|
| Loan queue (`sqs_loan_queue_url_{env}` / `loansToprocess-{env}`) | Consumed | **Yes** — `post_loan_to_sqs` |
| Missing-file queue | Consumed (priority) | **Not found** in this monorepo |
| Bedrock queue | Produced after extraction | Consumer **not found** |
| Notifications queue | Produced on loan complete | Consumer **not found** |

### Authentication

**Super Transfer client:** `boto3.client("sqs", region_name=...)` with **no explicit credentials** → boto3 default credential chain (typically **EC2 instance IAM role**). Same pattern for `boto3.Session()` in Secrets Manager access (`base/utils/aws.py:14`).

**Django producer:** explicit `AWS_ACCESS_KEY` / `AWS_SECRET_KEY` from env (`support_committing.py:175-177`).

No `AWS_PROFILE`, no hardcoded keys in ST client code. `scripts/awsCredentials.py` is **gitignored** (`.gitignore:130`) — may exist on servers for local dev; not in repo.

### Message formats (typed in repo)

```14:29:super_transfer_client/base/types/misc.py
MissingFileResponseBody = TypedDict(..., {
    "seller-loan_id": str,
    "File": str,
    "id": int,
    "name": str,
})

LoanResponseBody = TypedDict(..., {
    "seller-loan_id": str,
    "porfolio_id": str,
    "deal_id": str,
    "loan_id": int,
    ...
})
```

### Receive / parse / dispatch / delete

| Step | Location |
|------|----------|
| Receive | `main.py:51-58` (missing), `79-86` (loan) |
| Parse | `json.loads(message['Body'])` → `res` |
| Loan dispatch | `commitment_check(res)` → if `commit_flag` and `'loan_id' in res` → `processLoan(res, lock)` |
| Missing-file dispatch | `processFile(res, lock)` |
| Delete | `delete_queue_message()` in `helper_functions.py:2591-2599` |

### Failure / retry / DLQ

| Scenario | Behavior (code-proven) |
|----------|------------------------|
| Processing exception in loop | Message **not deleted**; loop sleeps 120s; SQS redelivers after visibility timeout |
| `commitment_check` returns False | `processLoan` skipped; message **still deleted** (`main.py:115`) |
| `commit_flag` True but no `loan_id` in message | `processLoan` skipped; message **still deleted** |
| Duplicate in-flight guard | In-memory `current_processing` string; not durable across restarts |
| DLQ | **Not found** in repository code |

**Important repo mismatch:** Django's `post_loan_to_sqs` sends only `{"seller-loan_id": "..."}`, but `main.py:100` gates `processLoan` on `'loan_id' in res.keys()`. The full message shape (with `loan_id`, `deal_id`, etc.) appears in `Manual_Loan_Process.ipynb` but not in the Django producer found in this repo. **Cannot determine** how production messages get `loan_id` without code outside this repo.

---

## 4. SQS → Processing Trace (one loan message)

```
SQS loan queue
  ↓ main.py:main() — sqs.receive_message(QueueUrl=queue_url, WaitTimeSeconds=20, VisibilityTimeout=1200)
  ↓ main.py — res = json.loads(message['Body'])
  ↓ base/workflows/query_msrx.py:commitment_check(res)
      • Direct PostgreSQL via psycopg2
      • Returns (commit_flag: bool, coissue_id)
  ↓ [if commit_flag and 'loan_id' in res]
  ↓ process_loan_handler.py:processLoan(res, lock)
      ↓ table.query(Key="seller-loan_id") — DynamoDB loan metadata
      ↓ build_processing_context(res, result, msrx_api_key) — MSRX REST APIs for DD config
      ↓ helper_functions.py:list_of_uploaded_files(s3_folder, bucket)
      ↓ helper_functions.py:download_object_files() — S3 → local_loan_files/{seller-loan_id}/
      ↓ [if .json/.txt sidecars present]
          base/workflows/doc_seg.py:get_pdf_json_zip() → zip_to_final_dict()
        [else]
          helper_functions.py:segregate_documents() — Textract OCR + TF-IDF + Naive Bayes
      ↓ [physical PDF split] PdfReader/PdfWriter per docToPages
      ↓ [parallel threads] extract*.py functions per docToLabel (e.g. extractCD, extractNote)
      ↓ helper_functions.py:prepare_outputdict_and_values()
          → send_values_to_DD() → post_values() → MSRX PATCH/POST /stloanvalues/
          → send_extracted_fields() → MSRX PATCH /supertransfer/ec_exceptions/
      ↓ update_loan_status() → MSRX PATCH /stloans/
      ↓ update_table() → DynamoDB update_item
      ↓ upload_file_to_s3() / upload_pdf_files_to_s3() → S3 processed artifacts
      ↓ sqs.send_message(notifications_queue) + optional bedrock_queue
  ↓ main.py:delete_queue_message(sqs, receipt_handle, ...)
```

**Cannot be proven from repo:** missing-file queue producer; how `loan_id` gets into SQS body in production.

---

## 5. How S3 Is Used

### Client initialization

```25:27:super_transfer_client/base/workflows/runtime.py
s3_client = client("s3", region_name=config.region_name)
bucket = s3.Bucket(env_variables.get_s3_bucket())
```

Bucket name from Secrets Manager: `s3_bucket_{env}`.

Django uses `supertransfer-{MSRX_ENV}` (`support_committing.py:169`) — likely the same bucket with env-specific naming.

### Key layout

```
SuperTransfer/{sellerID}/{Buyer}/{LoanNum}/     ← input PDFs + outputs
SuperTransfer/{sellerID}/{Buyer}/{LoanNum}/stacked_zip/
SuperTransfer/{sellerID}/{Buyer}/{LoanNum}/stacked_bookmarked_pdf/
{git_branch}/{s3_folder}/                       ← metadata bucket (Textract cache)
{sftp_path}/{Loan_num}/                         ← optional SFTP mirror bucket (sftp.bluewater.com)
```

### In the processing flow

| Phase | Function | Operation |
|-------|----------|-----------|
| List inputs | `list_of_uploaded_files()` | `bucket.objects.filter(Prefix=s3_folder)` |
| Download | `download_file_from_S3()` | `bucket.download_file(key, local_path)` |
| Upload results | `upload_file_to_s3()`, `upload_pdf_files_to_s3()` | `s3_client.upload_file(...)` |
| Missing file | `process_file_handler.py:96` | `bucket.download_file(documentName, ...)` |
| Metadata | `upload_metadata_files_to_s3()` | Textract JSON cache back to S3 |

Local temp storage: `super_transfer_client/local_loan_files/` (gitignored), wiped/recreated by `regenerate_local_loan_directory()`.

---

## 6. OCR Sidecar Files

### What the repo expects

Sidecars are **peer files** to PDFs in the loan S3 folder, with matching basename:

```75:88:super_transfer_client/base/workflows/doc_seg.py
for pdf_file in pdf_files:
    base_file_name = pdf_file[:-4]
    if f"{base_file_name}.txt" in json_files:
        ... json.load(...)
    elif f"{base_file_name}.json" in json_files:
        ... json.load(...)
    else:
        print("JSON file not found for pdf:", pdf_file)
        continue
```

Expected JSON shape:

```json
{
  "Documents": [
    {"DocId": "...", "PageCount": 5},
    ...
  ]
}
```

`__split__` pattern: **not found** in `super_transfer_client`.

### When sidecars exist vs missing

| Condition | Path |
|-----------|------|
| `.json`/`.txt` sidecar present | `get_pdf_json_zip()` → `zip_to_final_dict()` — pre-segmented page ranges (currently labels as `Closing_Disclosure`) |
| Sidecar absent | `segregate_documents()` — **blob ML path**: PDF→images→AWS Textract→TF-IDF→Naive Bayes |

### What this repo generates vs consumes

| Artifact | Generated here? | Consumed here? |
|----------|-----------------|----------------|
| Upstream `.json`/`.txt` sidecars (Documents/PageCount) | **No** | **Yes** — if present in S3 download |
| Page-level `.csv` (`{blob}.csv`) | **Yes** — during `segregate_documents()` | Yes — extraction threads read it |
| Textract metadata JSON in `meta_data/` | **Yes** — `textract.py` caches responses | Yes — extraction scripts |
| Split PDFs per document type | **Yes** — `PdfWriter` in `process_loan_handler.py:236-248` | Uploaded back to S3 |

Classification OCR for the ML path uses **AWS Textract** (`detect_document_text_response`), not Tesseract. Tesseract (`pytesseract`) is used in some extraction scripts and page-number helpers.

---

## 7. Classification / Segregation / Extraction

### Model loading (at worker startup)

```153:171:super_transfer_client/scripts/helper_functions.py
naive_bayes_classifier = pickle.load(.../"naive_bayes_classifier.pkl")
tf_idf = pickle.load(.../"tf_idf.pkl")
label_tokenizer = json.load(.../"label_tokenizer.json")
```

Artifacts live in `supporting_files/document_recognition_model/main/`. CodeDeploy runs `upload_model.py` to sync models to S3.

### Classification pipeline (no sidecar path)

```
segregate_documents(docpath, documentName, pdf_to_pages, buyer_name)
  → create_df() — PDF→images→Textract per page→CSV
  → predict_label() per page:
      clean_text → NLTK tokenize/lemmatize → tf_idf.transform() → naive_bayes.predict_proba()
      confidence > 0.7 → label; else "Misc"
  → first_pass() / doc_versioning — group pages into document types
  → docToLabel, docToPages — page ranges per segregated PDF filename
```

Optional buyer-specific model from S3 (`download_model_from_s3`) when `check_model_present(buyer_name)` is true.

### Extraction

`return_ExtractFunctions()` maps label strings → `extract*.py` callables. Each runs in a **Thread** (`process_loan_handler.py:279-298`). Results accumulate in shared `fields` dict under a `threading.Lock`.

### Results persistence

`prepare_outputdict_and_values()` → `send_values_to_DD()` → MSRX Due Diligence values API (`/msrx/duediligence/stloanvalues/`).

---

## 8. Actual Deployment Method

| Mechanism | Status | Evidence |
|-----------|--------|----------|
| **AWS CodeDeploy** | **CONFIRMED** | `super_transfer_client/appspec.yml` |
| **EC2 direct Python** | **CONFIRMED** | `destination: /home/ec2-user/super_transfer_client/`, `python3.12` in `start_cron.sh` |
| **EC2 crontab + flock** | **CONFIRMED** | `start_cron.sh`, `README.md` |
| **DynamoDB deploy gate** | **CONFIRMED** | `process_flag.py` → table `supertransfer-deploymentDB` |
| Docker / K8s / ECS / EKS | **NOT FOUND** in `super_transfer_client` |
| systemd / supervisor / PM2 | **NOT FOUND** |
| Terraform / CloudFormation | **NOT FOUND** in `super_transfer_client` |
| GitHub Actions deploy to EC2 | **NOT FOUND** — only PR patch workflow (`.github/workflows/patch.yml`) |

### How Super Transfer runs on EC2 (repo-supported)

```
EC2 instance (/home/ec2-user/)
    ↓
AWS CodeDeploy deploys repo → /home/ec2-user/super_transfer_client/
    ↓
BeforeInstall: stop_cron.sh (comment crontab, pkill python3, rm flock)
    ↓
AfterInstall: start_cron.sh (register crontab, chmod 777)
    ↓
ApplicationStart: upload_model.py (sync ML artifacts)
    ↓
crontab every minute:
  flock cron.lock env TESSDATA_PREFIX=... python3.12 scripts/main.py >> DO_NOT_DELETE_THIS.txt
    ↓
main.py polls SQS until process_flag=false (deploy window)
```

**LIKELY (not directly in repo):** EC2 instance has IAM role, `config.py` (gitignored), Python 3.12, poppler, Tesseract tessdata, possibly GPU (README mentions `nvidia-smi` during deploy).

---

## 9. Dependency / Environment Setup

Evidence-based fresh-server prep:

```
1. Clone super_transfer_client to /home/ec2-user/super_transfer_client/
2. git checkout Dev|UAT|Demo|Live  ← branch selects environment via get_active_git_branch()
3. Create config.py (GITIGNORED — not in repo; must contain account_id at minimum)
4. cd scripts && sudo pip3 install -r requirements.txt
5. yum install poppler-utils  (README.md)
6. Ensure TESSDATA_PREFIX=/usr/local/share/tessdata (set in cron)
7. EC2 IAM role: S3, SQS, DynamoDB, Secrets Manager, Textract
8. CodeDeploy agent registers hooks from appspec.yml
9. Crontab installed by start_cron.sh OR manual per README.md
10. Worker starts: python3.12 scripts/main.py
```

**Secrets loaded at runtime** (not env files in repo):

| Secret | Contents |
|--------|----------|
| `API_KEYS` | `MSRX_API_KEY_{ENV}` |
| `msrx-urls` | MSRX base URLs, DB host/password per env |
| `SUPER_TRANSFER_AWS_VARIABLES` | S3 bucket, DynamoDB table, SQS URLs |
| `NotificationEmail` | Deploy-ready email credentials |

**DB config** (for direct PostgreSQL in `query_msrx.py`):

```61:66:super_transfer_client/scripts/env_variables.py
db_name_mapping = {
    'Dev':  'msrx_internal_dev',
    'UAT':  'msrx_uat_new',
    ...
}
```

---

## 10. Cron Jobs (separate from SQS worker)

### `phagevolve_ingestion.py`

**`phagevolve_ingestion.py` is not present in this repository.**

### FLOW A — CRON / SCHEDULED (Super Transfer EC2)

```
EC2 crontab (* * * * *)
  ↓ flock /home/ec2-user/super_transfer_client/cron.lock
  ↓ TESSDATA_PREFIX=/usr/local/share/tessdata python3.12 scripts/main.py
  ↓ (if previous instance still running, flock skips — no duplicate)
```

Deploy lifecycle (not periodic cron):

```
CodeDeploy BeforeInstall → stop_cron.sh (disable cron, kill python3)
CodeDeploy AfterInstall  → start_cron.sh (enable cron)
CodeDeploy ApplicationStart → upload_model.py
```

### FLOW A — CRON / SCHEDULED (MSRX Django — separate from ST worker)

In `msrx_v2.0`, **APScheduler** (leader-elected) runs jobs from `api/cron_jobs.py`, including:

- `secondlien_ingest_client_files` — 06:30 US/Central — SFTP→S3 for second-lien sellers (`support_secondlien_ingestion.py`)
- Email monitors, loan delivery, FNMA pricing, CAAS workflows, etc.

These run **inside the Django app**, not on the Super Transfer EC2 worker. **No connection to ST SQS** found in code.

### FLOW B — SQS / SUPER TRANSFER WORKER

```
crontab starts main.py (long-running)
  ↓ while process_flag():
  ↓   missing-file SQS (priority)
  ↓   else loan SQS
  ↓   processFile / processLoan
  ↓   delete SQS message
  ↓   produce notifications + bedrock SQS messages
```

**Explicitly separate** — no code links `phagevolve_ingestion` or Django APScheduler jobs to the ST SQS worker.

---

## 11. EC2 / AWS Authentication

| Component | Auth method |
|-----------|-------------|
| ST worker boto3 (S3/SQS/DynamoDB/Textract/Secrets) | Default credential chain — **no explicit keys in code** → **LIKELY EC2 IAM instance role** |
| Secrets Manager | `boto3.Session().client("secretsmanager")` |
| EC2 metadata | `get_current_instance_id()` hits `169.254.169.254` (`base/utils/aws.py`) |
| Django SQS producer | Explicit `AWS_ACCESS_KEY` / `AWS_SECRET_KEY` env vars |
| Local dev override | `scripts/awsCredentials.py` — **gitignored**, contents unknown |

**Cannot determine from repo:** actual IAM policy ARNs or whether instance profiles differ per environment.

---

## 12. Database / Django / API Connection

Super Transfer uses **all three**:

| Store | How | Evidence |
|-------|-----|----------|
| **PostgreSQL (direct)** | `psycopg2` in `query_msrx.py` | `commitment_check()`, `check_loan_record_boarding_staging()` |
| **DynamoDB** | Loan processing state | `table.query()`, `update_table()` |
| **MSRX Django REST APIs** | `requests` + `Api-Key` header | URLs built in `env_variables.py` |

### Example: extraction results saved

```
extract*.py threads → fields dict
  ↓ prepare_outputdict_and_values()
  ↓ send_values_to_DD() → post_values() → POST/PATCH {msrx_base}/msrx/duediligence/stloanvalues/
  ↓ send_extracted_fields() → PATCH {msrx_base}/msrx/supertransfer/ec_exceptions/
  ↓ update_loan_status() → PATCH {msrx_base}/msrx/duediligence/stloans/?id={loan_id}
  ↓ update_table() → DynamoDB
  ↓ upload Extracted_Fields.json, split PDFs → S3
```

PostgreSQL is **not** written to directly for extraction results — only read for commit/boarding checks.

---

## 13. Error Handling

| ERROR | Caught where | Logged | SQS msg | Retry | Loan status |
|-------|--------------|--------|---------|-------|-------------|
| Invalid SQS JSON | `main.py` except | `print(e)` | **Retained** (no delete) | Yes, after 120s sleep | N/A |
| `commitment_check` fails | `main.py` (no except) | prints in `query_msrx.py` | **Deleted** | **No** | Not updated |
| No DynamoDB record | `processLoan` except | `print(e)` | **Deleted** (delete runs after try) | No | `update_loan_status(..., "Failed")` if `loan_id` in res |
| S3 download fail | Various try/except | `print` | Deleted after handler returns | No | `"Failed"` on outer except |
| OCR sidecar missing | `doc_seg.py` | `"JSON file not found for pdf"` | N/A | Falls back to `segregate_documents()` | N/A |
| Classification/segregation fail | `process_loan_handler.py:220-223` | `print` + raise | Deleted | No | `"Failed"` |
| Extraction thread fail | Per extract script | varies | Deleted | No | Partial fields may still post |
| DD API post fail | `send_values_to_DD` | `"FAILED TO POST VALUES TO DD"` | Deleted | 5 HTTP retries per batch | DynamoDB records `extracted_fields_to_DD_sent=False` |
| Deploy window | `process_flag()` false | email via SMTP | Worker stops polling | N/A | N/A |

---

## 14. Final Architecture Diagram

```
                         ┌─────────────────────────────────────┐
                         │           msrx_v2.0 (Django)         │
                         │  Commit → post_loan_to_sqs()         │
                         │  DD APIs ← ST worker callbacks       │
                         │  APScheduler crons (separate)        │
                         └──────────────┬──────────────────────┘
                                        │ SQS send (loansToprocess-{env})
                                        │ REST (Api-Key)
                                        ▼
┌──────────┐    ┌──────────┐    ┌──────────────────────────────────────────┐
│ Secrets  │    │PostgreSQL│    │              EC2 Instance                 │
│ Manager  │    │(commit   │    │  CodeDeploy → /home/ec2-user/super_...    │
└────┬─────┘    │ check)   │    │  crontab+flock → python3.12 main.py     │
     │          └────┬─────┘    │                                           │
     │               │          │  ┌─────────────────────────────────────┐ │
     ▼               ▼          │  │ Super Transfer Worker (main.py)      │ │
┌─────────┐   ┌──────────┐     │  │  poll SQS → processLoan/processFile  │ │
│   S3    │◄─►│ DynamoDB │◄────┼──│  Textract + TF-IDF/NB classify       │ │
│ buckets │   │loan state│     │  │  extract*.py threads               │ │
└─────────┘   └──────────┘     │  └─────────────────────────────────────┘ │
     ▲                          └──────────────────────────────────────────┘
     │                                         │
┌────┴────┐   ┌──────────────┐   ┌────────────┴────────┐
│ SQS     │   │ SQS notif.   │   │ SQS bedrock         │
│ loan +  │──►│ (produced)   │   │ (produced)          │
│ missing │   │ consumer ?   │   │ consumer ?          │
└─────────┘   └──────────────┘   └─────────────────────┘
```

---

## 15. Backend Developer Explanation

1. **What starts first?** CodeDeploy puts code on EC2; `start_cron.sh` registers a crontab entry. Every minute, cron tries to start `scripts/main.py` under `flock`.

2. **What keeps running?** A single `main.py` process loops until killed or `process_flag` goes false. Cron is a **watchdog** — if the process dies, the next minute's cron starts a new one (unless flock blocks because one is already running).

3. **What waits for SQS?** `main.py`'s `while process_flag()` loop with `sqs.receive_message(..., WaitTimeSeconds=20)`.

4. **When a message arrives?** Missing-file queue is checked first. Loan messages go through `commitment_check` (PostgreSQL), then `processLoan` downloads S3 files, classifies/segregates, extracts in threads, posts to MSRX APIs, updates DynamoDB, uploads to S3, sends notification/bedrock SQS messages, then deletes the SQS message.

5. **Where does S3 come in?** Input loan PDFs (and optional sidecars) live in S3. Worker downloads them, uploads processed split PDFs, CSVs, JSON, logs, and metadata back.

6. **Where does ML come in?** Pickled TF-IDF + Naive Bayes classifiers classify page text. Page text comes from AWS Textract during segregation (unless pre-built JSON sidecars skip ML).

7. **Where does extraction happen?** Per-document `extract*.py` modules, launched as threads from `process_loan_handler.py`.

8. **Where are results stored?** MSRX Due Diligence APIs (values, loan status, exceptions), DynamoDB loan record, S3 artifacts.

9. **When is SQS complete?** `delete_queue_message()` after handler returns — including when `commitment_check` fails or `processLoan` is skipped.

10. **What's separate?** Django APScheduler crons (email, second-lien SFTP ingestion, etc.), CodeDeploy lifecycle, `upload_model.py`, manual `extract*.py` CLIs, and the handover-mentioned `phagevolve_ingestion.py` (not in repo).

---

## 16. Evidence Table

| Finding | File | Function/Class | Evidence | Confidence |
|---------|------|----------------|----------|------------|
| Main SQS worker entry | `scripts/main.py` | `main()` | `while process_flag(): sqs.receive_message` | **CONFIRMED** |
| Worker started by cron | `scripts/start_cron.sh` | shell | `* * * * * flock ... python3.12 scripts/main.py` | **CONFIRMED** |
| CodeDeploy to EC2 | `appspec.yml` | hooks | `destination: /home/ec2-user/super_transfer_client/` | **CONFIRMED** |
| No Dockerfile | `super_transfer_client/` | — | glob search: 0 Dockerfiles | **CONFIRMED** |
| SQS client creation | `base/workflows/runtime.py` | `initialize_aws_variables()` | `sqs = client("sqs")` | **CONFIRMED** |
| Queue URLs from Secrets Manager | `scripts/env_variables.py` | `_ensure_env_loaded()` | `sqs_loan_queue_url_{env}` keys | **CONFIRMED** |
| Loan SQS producer | `msrx_v2.0/.../support_committing.py` | `post_loan_to_sqs()` | `send_message` to `loansToprocess-{env}` | **CONFIRMED** |
| TF-IDF + Naive Bayes classification | `scripts/helper_functions.py` | `predict_label()`, `segregate_documents()` | pickle load + `predict_proba` | **CONFIRMED** |
| OCR sidecar consumption | `base/workflows/doc_seg.py` | `get_pdf_json_zip()` | matches `.txt`/`.json` to PDF basename | **CONFIRMED** |
| ML fallback when no sidecar | `process_loan_handler.py` | `processLoan()` | `else: segregate_documents(...)` | **CONFIRMED** |
| Direct PostgreSQL | `base/workflows/query_msrx.py` | `commitment_check()` | `psycopg2.connect(...)` | **CONFIRMED** |
| Results to MSRX API | `scripts/helper_functions.py` | `post_values()`, `send_extracted_fields()` | `requests.patch/post` to DD URLs | **CONFIRMED** |
| Deploy gate | `base/workflows/process_flag.py` | `process_flag()` | DynamoDB `supertransfer-deploymentDB` | **CONFIRMED** |
| `phagevolve_ingestion.py` absent | entire repo | — | grep: no matches | **CONFIRMED** |
| Missing-file SQS producer | — | — | not found in monorepo | **CANNOT DETERMINE** |
| `loan_id` in production SQS messages | `main.py:100` vs `support_committing.py:181` | — | gate requires `loan_id`; producer sends only `seller-loan_id` | **UNCLEAR** |
| EC2 IAM role permissions | — | — | implied by credential-less boto3 | **STRONG INFERENCE** |
| DLQ configuration | — | — | no references in code | **NOT FOUND** |

---

## Five Direct Answers

**A. What exact command/file starts the Super Transfer worker?**

```bash
/usr/bin/flock -w 1 /home/ec2-user/super_transfer_client/cron.lock \
  env TESSDATA_PREFIX=/usr/local/share/tessdata \
  /usr/bin/python3.12 /home/ec2-user/super_transfer_client/scripts/main.py \
  >> /home/ec2-user/DO_NOT_DELETE_THIS.txt 2>&1
```

(from `start_cron.sh`). Manual alternative: `python3 scripts/main.py` from repo root (`README.md`).

**B. How does the worker stay alive and wait for jobs?**

A `while process_flag():` loop in `main.py` long-polls SQS (`WaitTimeSeconds=20`), sleeps 5s when idle, 120s on errors. EC2 crontab + `flock` restarts it if the process exits.

**C. Is production Docker-based?**

**No — not based on repository evidence.** No `Dockerfile`, `docker-compose`, or container orchestration in `super_transfer_client`. Deployment is **AWS CodeDeploy → EC2 filesystem + crontab + direct Python 3.12**.

**D. How does the EC2-hosted application connect to SQS and S3?**

Via `boto3` clients created in `initialize_aws_variables()` using the default AWS credential chain (no explicit keys in ST code — **likely EC2 IAM role**). Resource names/queue URLs come from AWS Secrets Manager (`SUPER_TRANSFER_AWS_VARIABLES`), keyed by git branch (`Dev`/`UAT`/`Demo`/`Live`).

**E. What is still impossible to determine from this repository alone?**

- Exact production EC2 crontab contents on running servers (only `start_cron.sh` template in repo)
- Contents of gitignored `config.py` and `scripts/awsCredentials.py`
- IAM policy documents / instance profile names
- Missing-file SQS message producer
- Bedrock and notifications SQS consumers
- DLQ configuration on AWS queues
- How production loan SQS messages get `loan_id` (Django producer in repo sends only `seller-loan_id`, but `main.py` requires `loan_id` to call `processLoan`)
- `phagevolve_ingestion.py` and its 15-minute SFTP schedule (not in repo; closest analogue is `secondlien` SFTP ingestion in Django at 06:30 CT)
- Whether multiple EC2 instances run workers (horizontal scaling implied by architecture docs but not configured in repo)