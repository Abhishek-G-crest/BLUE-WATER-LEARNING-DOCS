# 23 — MSRX → Super Transfer Visual Diagrams

**Audience:** Backend developers / KT / onboarding  
**Date:** 2026-07-24  
**Source of truth:** [`22_COMPLETE_END_TO_END_WORKER_FLOW.md`](./22_COMPLETE_END_TO_END_WORKER_FLOW.md)  
**Method:** Visual learning only — **no invented architecture**

---

## About this document

| Artifact | Role |
|----------|------|
| **This Markdown (`.md`)** | Editable **Mermaid source** — edit diagrams here |
| **[`23_MSRX_SUPER_TRANSFER_VISUAL_DIAGRAMS.pdf`](./23_MSRX_SUPER_TRANSFER_VISUAL_DIAGRAMS.pdf)** | **PRIMARY deliverable** — **rendered** diagram images (open directly; no Mermaid viewer) |
| **`_diagram_assets/*.png`** | Individual rendered PNGs used inside the PDF |

~80% diagrams, ~20% short explanation. Every path below is taken from confirmed findings in the audit. Unknowns stay visibly unknown.

**PDF organization:** Part 1 System Overview → Part 2 Frontend→Backend → Part 3 Django→ST → Part 4 Worker → Part 5 Document Processing → Part 6 Data/AWS → Part 7 Example → Part 8 Failures → Part 9 KT Gaps.

---

## Legend — CONFIRMED vs UNKNOWN

| Visual / label | Meaning |
|----------------|---------|
| Solid boxes + normal arrows | **`[CONFIRMED FROM CODE]`** or **`[CONFIRMED FROM CONFIG]`** |
| Dashed / `???` / bold UNKNOWN box | **`[UNKNOWN — KT CONFIRMATION REQUIRED]`** — do not treat as implemented |
| `??? KT CONFIRMATION REQUIRED ???` | Gap that must be asked in KT — **not** labeled Lambda unless proven |

**Rule:** If a box says UNKNOWN, the audit did **not** find that component in `msrx-frontend`, `msrx_v2.0`, or `super_transfer_client`.

---

# PART 1 — SYSTEM OVERVIEW

## 1. COMPLETE END-TO-END MASTER FLOW

Confirm commit starts in the browser, passes Express → Django, may enqueue SQS, then (after an unknown enrichment step) the Super Transfer worker classifies and extracts documents and posts Due Diligence / boarding updates. Boarding Excel → buyer SFTP is a **separate** Django scheduler path, not inside the worker’s sync HTTP response. The UNKNOWN box between SQS and the worker is intentional — producer and consumer schemas do not match in these repos.

```mermaid
flowchart TD
  subgraph BROWSER["USER BROWSER"]
    U[User clicks Yes]
    R["React ConfirmCommitModalForm<br/>msrx-frontend/client<br/>confirmCommit()"]
  end

  subgraph FE["FRONTEND SERVER"]
    CSRF["csrfProtection<br/>server/index.js"]
    RT["refreshToken<br/>server/utils.js"]
    PC["postConfirmCommit<br/>server/routes/msrCoissue.js"]
  end

  subgraph DJ["DJANGO SERVER"]
    CC["ConfirmCommit.post<br/>api/views/commit.py"]
    SVC["confirm_commit<br/>msr_commit.py"]
    SQS_FN["post_loan_to_sqs<br/>support_committing.py"]
    DD_CREATE["create_commit_dd_records_and_values<br/>support_committing.py"]
  end

  subgraph PG["POSTGRESQL"]
    PG1[(Tape status confirmed<br/>+ DD rows later)]
  end

  subgraph AWS["AWS"]
    S3[(S3 supertransfer-env<br/>docs check + ST I/O)]
    SQS[SQS loansToprocess-env]
    DDB[(DynamoDB supertransfer-envDB)]
    TX[AWS Textract]
  end

  subgraph UNK["UNKNOWN COMPONENT"]
    ENRICH["??????????????????????????????<br/>??? UNKNOWN ENRICHMENT ???<br/>??? KT CONFIRMATION REQUIRED ???<br/>adds loan_id / deal_id / porfolio_id?<br/>??????????????????????????????"]
  end

  subgraph ST["SUPER TRANSFER WORKER"]
    MAIN["scripts/main.py<br/>receive_message"]
    COMMIT["commitment_check<br/>query_msrx.py"]
    GATE{"loan_id in message?"}
    PL["processLoan<br/>process_loan_handler.py"]
    SEG["segregate_documents<br/>classify_label"]
    EXT["return_ExtractFunctions<br/>extractors"]
  end

  subgraph DD["DUE DILIGENCE"]
    DDAPI["HTTP /msrx/duediligence/...<br/>send_values_to_DD"]
  end

  subgraph BOARD["BOARDING"]
    BS[Boarding staging status]
    DEL["deliver_boarding_file<br/>Django scheduler — separate path"]
    SFTP[Buyer SFTP]
  end

  U --> R
  R -->|HTTPS /msrx/confirm-commit| CSRF --> RT --> PC
  PC -->|Token + tape_id/src| CC --> SVC
  SVC --> PG1
  SVC --> S3
  SVC --> SQS_FN
  SQS_FN -->|seller-loan_id only| SQS
  SVC --> DD_CREATE
  DD_CREATE --> PG1
  SQS --> ENRICH
  ENRICH -->|full message?| MAIN
  MAIN --> COMMIT --> GATE
  GATE -->|yes| PL
  PL --> DDB
  PL --> S3
  PL --> TX
  PL --> SEG --> EXT
  EXT --> DDAPI
  PL --> BS
  BS -.->|separate Django path| DEL --> SFTP
```

**KEY TAKEAWAY:** Django enqueues only `seller-loan_id`; the worker needs `loan_id` before `processLoan`. The component that bridges that gap is **unknown** — do not invent it.

---

# PART 2 — FRONTEND TO BACKEND

## 2. FRONTEND → DJANGO (Confirm Commit Sequence)

The MSR Coissue wizard uses **direct axios**, not `apiHoc`. Express is a hand-rolled BFF: CSRF, cookie session slide, body remap (`tapeId` → `tape_id`), and `Authorization: Token`. React never holds the auth token — it lives in an httpOnly signed cookie. Confirm success opens the commit-success modal; it does **not** wait for Super Transfer.

```mermaid
sequenceDiagram
  participant User
  participant ConfirmCommitModalForm
  participant Axios
  participant Express as Express csrfProtection
  participant Refresh as refreshToken
  participant Route as postConfirmCommit
  participant View as ConfirmCommit.post
  participant Svc as confirm_commit

  User->>ConfirmCommitModalForm: clicks Yes
  ConfirmCommitModalForm->>ConfirmCommitModalForm: onYesClick → commitTimeCheck
  ConfirmCommitModalForm->>Axios: GET /msrx/check-market-hours
  Axios->>Express: csrf + cookies
  Express-->>ConfirmCommitModalForm: 200 OK
  ConfirmCommitModalForm->>ConfirmCommitModalForm: confirmCommit()
  Note over ConfirmCommitModalForm,Axios: React body: { tapeId, src }
  ConfirmCommitModalForm->>Axios: POST /msrx/confirm-commit
  Axios->>Express: csrfProtection
  Express->>Refresh: slide auth cookie
  Refresh->>Route: msrCoissue.postConfirmCommit
  Note over Route,View: Express remaps → { tape_id, src }<br/>Authorization: Token {auth.key}
  Route->>View: POST /msrx/api/confirm_commit/
  View->>Svc: confirm_commit(user, tape_id, src)
  Svc-->>View: status, details
  View-->>Route: { status, details }
  Route-->>Axios: 200 response.data
  Axios-->>ConfirmCommitModalForm: setCommitResults
  ConfirmCommitModalForm-->>User: commit-success modal
```

**KEY TAKEAWAY:** Express remaps and authenticates; Django owns commit business logic. UI success ≠ Super Transfer complete.

---

## 3. DJANGO `confirm_commit` INTERNAL FLOW

`ConfirmCommit.post` calls `confirm_commit`. After status → `confirmed` and loan loop work, **`post_loan_to_sqs` runs before `create_commit_dd_records_and_values`**. If S3 docs are missing, SQS is skipped but confirm still continues. SQS send failure does not roll back confirm — only activity log.

```mermaid
flowchart TD
  subgraph DJ["DJANGO SERVER"]
    A["ConfirmCommit.post<br/>api/views/commit.py"]
    B["confirm_commit<br/>msr_commit.py"]
    C{tape status = pre-commit?}
    D["Client_Coissue_Seller<br/>status → confirmed + save"]
    E["asset_commit_postprocess"]
    F["loop loans"]
    G["get_s3_buyer"]
    H["post_loan_to_sqs<br/>support_committing.py"]
    I{"S3 folder exists<br/>and not empty?"}
    J["NO SQS<br/>activity_log fail<br/>confirm CONTINUES"]
    K["Build seller-loan_id<br/>send_message SQS"]
    L["bulk_update delivery_month"]
    M["assign_deals_to_loans"]
    N["create_commit_dd_records_and_values<br/>⚠️ AFTER SQS"]
    O["email_commit + auto_resell_async"]
    P["HTTP { status, details }"]
  end

  subgraph AWS["AWS"]
    S3[(S3 SuperTransfer/s/b/l/)]
    SQS[SQS loansToprocess-env]
  end

  A --> B --> C
  C -->|no| FAIL[return failure]
  C -->|yes| D --> E --> F --> G --> H
  H --> I
  I -->|missing| J
  I -->|exists| K
  K --> S3
  K --> SQS
  J --> L
  K --> L
  L --> M --> N --> O --> P
```

**KEY TAKEAWAY:** **SQS is sent before DD `loan_id` rows are created.** If enrichment needs that PK, this ordering is a race risk.

---

# PART 3 — DJANGO TO SUPER TRANSFER

## 4. `seller-loan_id` CREATION

Format is `{seller_id}-{buyer_id}_{loan_number}` — verified in `post_loan_to_sqs` and worker parsers (`split("-")` then `split("_")`). Same composite string keys S3 folders, SQS messages, DynamoDB, and local worker dirs. It is **not** the Due Diligence integer `loan_id`.

```mermaid
flowchart LR
  subgraph INPUTS["INPUTS — example"]
    S["seller_id = 117<br/>MSRX user PK"]
    B["buyer_id = 42<br/>commitment / aggregator / S3"]
    L["loan_number = 2208066387<br/>tape_loan_id"]
  end

  COMBINE["combine → seller-loan_id"]
  SL["117-42_2208066387"]

  subgraph USES["WHERE USED"]
    S3U["S3 path<br/>SuperTransfer/117/42/2208066387/"]
    SQSU["SQS MessageBody<br/>only field from Django"]
    DDBU["DynamoDB PK"]
    STU["ST local folder / message id"]
    PGU["Postgres parse<br/>seller + loan for commitment_check"]
  end

  subgraph NOTSAME["NOT THE SAME"]
    SL2["seller-loan_id<br/>composite system id"]
    LID["loan_id<br/>DD duediligence_loan PK"]
  end

  S --> COMBINE
  B --> COMBINE
  L --> COMBINE
  COMBINE --> SL
  SL --> S3U
  SL --> SQSU
  SL --> DDBU
  SL --> STU
  SL --> PGU
  SL2 -.->|≠| LID
```

**KEY TAKEAWAY:** `117-42_2208066387` is the cross-system identity. DD `loan_id` is a different integer PK required by the worker gate.

---

## 5. PRODUCER / CONSUMER GAP

Django’s producer sends **only** `seller-loan_id`. The worker’s `main.py` requires `'loan_id' in res` before calling `processLoan`. No enrichment Lambda (or other bridge) exists in the three audited repos. `STLoanLookupView`’s docstring mentions Lambda — comment only; worker does not call that view.

```mermaid
flowchart TD
  subgraph LEFT["DJANGO PRODUCER — msrx_v2.0"]
    P["post_loan_to_sqs<br/>support_committing.py"]
    MSG1["sends ONLY one field:<br/>seller-loan_id = 117-42_2208066387"]
  end

  subgraph AWS["AWS"]
    Q["SQS loansToprocess-ENV"]
  end

  subgraph GAP["BIG UNKNOWN — DO NOT LABEL AS LAMBDA"]
    U["?????????????????????????????????????<br/>??? UNKNOWN ENRICHMENT COMPONENT ???<br/>??? KT CONFIRMATION REQUIRED ???<br/>?????????????????????????????????????"]
  end

  subgraph RIGHT["SUPER TRANSFER CONSUMER"]
    NEED["Worker needs:<br/>seller-loan_id + loan_id<br/>+ deal_id + porfolio_id …"]
    MAIN["scripts/main.py"]
    IF{"loan_id key present in message?"}
    PL["processLoan(...)"]
    SKIP["skip processLoan<br/>DELETE message anyway"]
  end

  NOTE["NOTE: STLoanLookupView comment says<br/>used by Lambda — comment only;<br/>Lambda NOT found in audited repos"]

  P --> MSG1 --> Q --> U --> NEED --> MAIN --> IF
  IF -->|yes| PL
  IF -->|no| SKIP
  NOTE -.-> U
```

**KEY TAKEAWAY:** Schema mismatch is proven. What fills `loan_id` in production is a **KT question** — not a silent Lambda assumption.

---

# PART 4 — SUPER TRANSFER WORKER

## 6. WORKER STARTUP

CodeDeploy installs to `/home/ec2-user/super_transfer_client/`. `start_cron.sh` installs a per-minute crontab that runs `flock` then `python3.12 scripts/main.py`. `flock -w 1` ensures a single overlapping worker process on the machine. `ensure_model_context` loads secrets, AWS clients, and ML pickles once at import; `main()` loops while `process_flag()` is true.

```mermaid
flowchart TD
  subgraph DEPLOY["DEPLOY — CONFIRMED FROM CONFIG"]
    CD[AWS CodeDeploy]
    AS["appspec.yml<br/>→ /home/ec2-user/super_transfer_client/"]
    SC["scripts/start_cron.sh"]
    CR["cron: * * * * *"]
  end

  subgraph LOCK["SINGLE INSTANCE"]
    FL["flock -w 1<br/>PURPOSE: prevent overlapping<br/>worker instances on same host"]
  end

  subgraph RUNTIME["SUPER TRANSFER WORKER"]
    PY["python3.12 scripts/main.py"]
    IMP["import helper_functions"]
    EMC["ensure_model_context()"]
    CFG[Secrets / env]
    AWSCLI[S3 + DynamoDB + SQS clients]
    ML["pickle.load NB + TF-IDF + JSON maps"]
    MN["main()"]
    PF{"process_flag()<br/>DynamoDB deploymentDB"}
    POLL["poll: missing-file queue<br/>then loan queue"]
  end

  CD --> AS --> SC --> CR --> FL --> PY --> IMP --> EMC
  EMC --> CFG --> AWSCLI --> ML
  PY --> MN --> PF
  PF -->|true| POLL
  PF -->|false| STOP[exit loop]
```

**KEY TAKEAWAY:** Worker is cron + flock, not systemd/supervisor (absent in repo). Models load at startup — not trained per loan.

---

## 7. SQS POLLING / DECISION TREE

`main.py` long-polls (`WaitTimeSeconds=20`, `MaxNumberOfMessages=1`). Malformed JSON does **not** delete (visibility retry). Duplicate `current_processing`, failed `commitment_check`, missing `loan_id`, and completed `processLoan` all **delete** the message. Delete-on-skip is **confirmed from code**; whether that is intentional product design needs **KT**.

```mermaid
flowchart TD
  R["receive_message<br/>loan queue"]
  J{JSON parse OK?}
  D1["NO delete<br/>sleep 120 / visibility retry<br/>CONFIRMED FROM CODE"]
  DUP{"seller-loan_id ==<br/>current_processing?"}
  DEL_DUP["delete_message + sleep 2<br/>CONFIRMED FROM CODE"]
  CC["commitment_check<br/>Postgres"]
  CF{commit_flag?}
  LID{"loan_id in body?"}
  PL["processLoan + heartbeat"]
  DEL["delete_message ALWAYS<br/>after this branch"]

  MARK["⚠️ DELETE-ON-SKIP<br/>CONFIRMED FROM CODE<br/>KT for DESIGN INTENT"]

  R --> J
  J -->|Exception| D1
  J -->|OK| DUP
  DUP -->|yes| DEL_DUP
  DUP -->|no| CC
  CC --> CF
  CF -->|no| DEL
  CF -->|yes| LID
  LID -->|no| DEL
  LID -->|yes| PL --> DEL
  DEL -.-> MARK
  DEL_DUP -.-> MARK
```

**KEY TAKEAWAY:** Missing `loan_id` or failed commit check → **no processLoan, message still deleted** — high data-loss risk until KT confirms intent / recovery.

---

## 8. `processLoan` INTERNAL PIPELINE

Real order from `process_loan_handler.processLoan`: DynamoDB → S3 download → blob → segregate → extract → DD → status → DDB update → S3 outputs → notifications. Exceptions set status `"Failed"` and are **not** re-raised; outer `main.py` still deletes SQS. `finally` uploads metadata/logs and removes the local folder.

```mermaid
flowchart TD
  subgraph ST["SUPER TRANSFER — processLoan"]
    A["DynamoDB query by seller-loan_id"]
    B[Resolve S3 folder from DDB]
    C[Create local folder + start log]
    D["Boarding staging = In Process"]
    E[emit started]
    F["build_processing_context"]
    G[List + download S3 PDFs]
    H[Merge PDFs → blob / JSON sidecar]
    I["segregate_documents OR zip_to_final_dict"]
    J[Optional SFTP blob upload]
    K[Split pages → per-doc PDFs]
    L["Threaded return_ExtractFunctions"]
    M[Post-extract rechecks / signatures]
    N["makeOutputFile + HOEPA"]
    O[Filename mapping → S3]
    P[DD document initialization]
    Q["prepare_outputdict_and_values<br/>→ send_values_to_DD"]
    R["status Processed + emit completed"]
    S[Missing files + extracted fields APIs]
    T["DynamoDB update_item"]
    U[Upload Extracted_Fields.json / CSV / PDFs]
    V[Stacked zip / bookmarked PDF]
    W[Notification SQS + optional Bedrock SQS]
    X["except → status Failed"]
    Y["finally → metadata/log upload + rmtree"]
  end

  OUTER["outer main.py:<br/>DELETE SQS message anyway"]

  A-->B-->C-->D-->E-->F-->G-->H-->I-->J-->K-->L-->M-->N-->O-->P-->Q-->R-->S-->T-->U-->V-->W
  A -.-> X
  X --> Y
  W --> Y
  Y --> OUTER
  X --> OUTER
```

**KEY TAKEAWAY:** Failures mark Failed and still ack SQS — no automatic redrive proven in application code.

---

# PART 5 — DOCUMENT PROCESSING

## 9. CLASSIFICATION — OFFLINE TRAINING vs RUNTIME

Runtime OCR for classification uses **AWS Textract** `detect_document_text`, then TF-IDF + Naive Bayes pickles via `predict_label` / `predict_proba`. Confidence ≤ 0.7 → `"Misc"`. Training is **not** in the worker — pickles are loaded artifacts. **Zero model training per loan.**

```mermaid
flowchart TD
  subgraph OFFLINE["OFFLINE TRAINING — NOT in worker runtime"]
    TD[training data] --> FIT[TF-IDF fit]
    FIT --> TR[Naive Bayes train]
    TR --> PK[".pkl files saved"]
  end

  subgraph RUNTIME["RUNTIME WORKER — inference only"]
    SRC[Source PDF page]
    TX["AWS Textract<br/>detect_document_text"]
    OCR[OCR text → DataFrame Text]
    TF["tf_idf.transform<br/>tf_idf.pkl"]
    NB["naive_bayes.predict_proba<br/>naive_bayes_classifier.pkl"]
    CONF{confidence > 0.7?}
    LAB[class_names label]
    MISC[Misc]
    SEG[→ segregation]
  end

  BIG["★ NO MODEL TRAINING PER LOAN ★<br/>100 loans today → 0 trains"]

  SRC --> TX --> OCR --> TF --> NB --> CONF
  CONF -->|yes| LAB --> SEG
  CONF -->|no| MISC --> SEG
  PK -.->|deploy / load only| TF
  PK -.-> NB
  BIG -.-> RUNTIME
```

**KEY TAKEAWAY:** Worker loads and predicts. Training pipeline location is outside this runtime path (KT if needed).

---

## 10. SEGREGATION (ILLUSTRATIVE EXAMPLE)

`segregate_documents` groups classified pages and splits the blob into per-type PDFs for extraction and S3 upload. Alternate path: classification JSON/txt sidecar → `zip_to_final_dict` skips full re-classification. Page labels below are **illustrative only**.

```mermaid
flowchart TD
  NOTE["★ ILLUSTRATIVE EXAMPLE ★<br/>Not a claim of exact production pages"]

  BLOB["Blob PDF<br/>merged loan documents"]

  P1["Page 1 → Note"]
  P2["Page 2 → Note"]
  P3["Page 3 → Credit Report"]
  P4["Page 4 → Credit Report"]
  P5["Page 5 → Security Instrument"]

  GRP["group consecutive / related<br/>classified pages<br/>segregate_documents"]

  O1[Note.pdf]
  O2[Credit_Report.pdf]
  O3[Security_Instrument.pdf]

  OUT["S3 upload + extraction threads"]

  NOTE --> BLOB
  BLOB --> P1 & P2 & P3 & P4 & P5
  P1 & P2 & P3 & P4 & P5 --> GRP
  GRP --> O1 & O2 & O3 --> OUT
```

**KEY TAKEAWAY:** Segregation turns page labels into document-level PDFs that drive which extractors run.

---

## 11. EXTRACTION via `return_ExtractFunctions`

Each segregated label selects a confirmed extractor. Extractors use Textract / regex / parsers, then recheck/post-process, then `prepare_outputdict_and_values` → `send_values_to_DD`. Fields exist only when that document type was classified and its extractor ran.

```mermaid
flowchart TD
  subgraph ST["SUPER TRANSFER"]
    DOC[Segregated document PDF]
    TYP[document type label]
    MAP["return_ExtractFunctions()"]
    N["Note → note()"]
    CD["Closing_Disclosure → extractCD()"]
    CR["Credit_Report → CreditReport()"]
    SI["Security_Instrument → extractDot()"]
    LA["Loan_Application-New_Format → loanAppNew()"]
    MORE["… Appraisal, Amortization,<br/>Escrow, Title, DU/LPA, W2, Paystub, …"]
    TX[Textract / regex / parser]
    FD[extracted field dict]
    RC[recheck / post-processing]
    SEND["send_values_to_DD"]
  end

  subgraph DD["DUE DILIGENCE"]
    API[Django DD HTTP APIs]
  end

  DOC --> TYP --> MAP
  MAP --> N & CD & CR & SI & LA & MORE
  N & CD & CR & SI & LA & MORE --> TX --> FD --> RC --> SEND --> API
```

**KEY TAKEAWAY:** Extraction is label-driven and partial — no universal field set for every loan.

---

# PART 6 — DATA & AWS

## 12. DATA STORE INTERACTION (Worker-Centered)

The worker talks to Postgres directly for `commitment_check` (and boarding staging merge SQL), to DynamoDB for loan state, to S3 for documents/outputs, to SQS for jobs/notifications, and to Django HTTP for Due Diligence values. Initial DynamoDB `put_item` is **not** in these repos’ runtime paths → KT.

```mermaid
flowchart TD
  subgraph STORES["DATA STORES"]
    PG[(PostgreSQL<br/>commitment_check MSRX tables<br/>boarding staging merge)]
    S3[(S3<br/>input PDFs / segregated / JSON / CSV / logs)]
    DDB[(DynamoDB<br/>query + update_item by seller-loan_id)]
    SQS[(SQS<br/>job trigger + notification queues)]
  end

  subgraph ST["SUPER TRANSFER WORKER"]
    W[scripts/main.py + processLoan]
  end

  subgraph DD["VIA DJANGO HTTP"]
    API[Due Diligence / Super Transfer APIs]
    PG2[(PostgreSQL DD data<br/>behind ORM)]
  end

  PG <-->|psycopg2 commitment_check| W
  S3 <-->|download + upload| W
  DDB <-->|query / update_item<br/>NO runtime put_item found| W
  SQS <-->|receive / delete / notify| W
  W -->|send_values_to_DD etc.| API --> PG2
```

**KEY TAKEAWAY:** Worker is the hub for ST I/O; who **creates** the first DynamoDB item is still unknown.

---

# PART 7 — COMPLETE EXAMPLE

## 13. ONE-LOAN EXAMPLE — `117` / `42` / `2208066387`

Easiest walkthrough for a new developer: same composite id from confirm through S3/SQS into the worker. Enrichment between SQS and `processLoan` remains unknown. Trader already saw commit-success while ST runs asynchronously.

```mermaid
flowchart TD
  U["User confirms tape"]
  D["Django confirm_commit<br/>status = confirmed"]
  S3["S3 check:<br/>SuperTransfer/117/42/2208066387/"]
  Q["SQS message body:<br/>seller-loan_id = 117-42_2208066387"]
  UNK["??? UNKNOWN enrichment ???<br/>??? KT CONFIRMATION REQUIRED ???"]
  W["Worker main.py"]
  CC["commitment_check Postgres"]
  PL["processLoan"]
  DOC["Download / blob / classify / segregate"]
  EXT["Extract → send_values_to_DD"]
  DD["Due Diligence + boarding staging"]
  BR["Boarding file / SFTP<br/>separate Django path"]

  U --> D --> S3 -->|docs exist| Q --> UNK --> W --> CC --> PL --> DOC --> EXT --> DD
  DD -.-> BR
```

**KEY TAKEAWAY:** One composite id ties the loan across systems; async ST work continues after the trader’s success modal.

---

# PART 8 — FAILURE FLOW

## 14. FAILURE FLOW (Confirmed Behavior Only)

Only audit-confirmed outcomes. DLQ / redrive / ops recovery for delete-on-skip paths are **unknown**. Docs missing or SQS send fail → confirm can still succeed without enqueue.

```mermaid
flowchart TD
  F1["S3 docs missing at confirm"] --> A1["NO SQS<br/>confirm STILL succeeds<br/>processLoan N/A"]
  F2["SQS send exception"] --> A2["post_loan_to_sqs False<br/>confirm continues<br/>retry UNKNOWN"]
  F3["Malformed SQS JSON"] --> A3["NO delete<br/>sleep 120 / visibility retry<br/>DLQ UNKNOWN"]
  F4["commitment_check false"] --> A4["NO processLoan<br/>DELETE message<br/>retry NO — KT intent"]
  F5["loan_id missing"] --> A5["NO processLoan<br/>DELETE message<br/>HIGH LOSS RISK — KT"]
  F6["DynamoDB item missing"] --> A6["processLoan → Failed<br/>DELETE anyway"]
  F7["OCR / classify / extract fail"] --> A7["status Failed<br/>DELETE anyway"]
  F8["DD API / processing exception"] --> A8["status Failed<br/>DELETE anyway"]
  F9["Duplicate current_processing"] --> A9["DELETE + sleep 2<br/>NO processLoan"]

  KT["DLQ / redrive / replay SOP<br/>??? UNKNOWN — KT ???"]
  A3 -.-> KT
  A4 -.-> KT
  A5 -.-> KT
```

**KEY TAKEAWAY:** Worst silent losses: skip enqueue at confirm, or delete-on-skip when `loan_id` / commit check fails — ask KT before operating incidents.

---

## 15. HIGH-LEVEL SYSTEM MAP (KT / Onboarding)

One-screen map of major boundaries only — no function overload. Use this first for architecture, then drill into diagrams 1–14.

```mermaid
flowchart TD
  subgraph BROWSER["USER BROWSER"]
    R[React SPA]
  end

  subgraph FE["FRONTEND SERVER"]
    E[Express BFF]
  end

  subgraph DJ["DJANGO SERVER"]
    D[Django API]
  end

  subgraph DATA["DATABASE"]
    PG[(PostgreSQL)]
  end

  subgraph AWS["AWS"]
    S3[(S3)]
    SQS[SQS]
    DDB[(DynamoDB)]
  end

  subgraph UNK["UNKNOWN"]
    U["??? ENRICHMENT ???<br/>KT REQUIRED"]
  end

  subgraph ST["SUPER TRANSFER"]
    W[Worker]
  end

  subgraph DD["DUE DILIGENCE"]
    DD1[DD via Django APIs]
  end

  subgraph BOARD["BOARDING"]
    B[Boarding staging]
    SFTP[Buyer SFTP]
  end

  R --> E --> D
  D --> PG
  D --> S3
  D --> SQS
  SQS --> U --> W
  W <--> S3
  W <--> DDB
  W <--> PG
  W --> DD1
  W --> B
  B -.-> SFTP
```

**KEY TAKEAWAY:** Sync path ends at Django HTTP response; async path is SQS → unknown enrichment → worker → DD/boarding → (separate) SFTP.

---

# PART 9 — KT GAPS

See Diagram 5 (producer/consumer gap), Diagram 14 (failures), and audit §32. Unresolved path remains:

```
Django → SQS → ??? UNKNOWN ENRICHMENT COMPONENT ??? → Super Transfer Worker
```

Do **not** label the gap as Lambda unless KT confirms a deployed component. `STLoanLookupView` only has a comment.

---

# HOW TO READ THESE DIAGRAMS

1. **Start with Diagram 15** for architecture — major system boundaries only.  
2. **Read Diagrams 2–3** for React → Express → Django confirm commit.  
3. **Read Diagrams 4–5** for `seller-loan_id` and the SQS producer/consumer gap.  
4. **Read Diagrams 6–8** for worker startup, SQS decisions, and `processLoan`.  
5. **Read Diagrams 9–11** for classification, segregation, and extraction.  
6. **Read Diagram 12** for databases / AWS interactions centered on the worker.  
7. **Read Diagram 13** for a complete one-loan example (`117-42_2208066387`).  
8. **Read Diagram 14** for confirmed failure behavior and KT gaps.  

Treat every `??? UNKNOWN ???` box as a **question to ask**, not as a finished connector. For prose detail and evidence tables, use [`22_COMPLETE_END_TO_END_WORKER_FLOW.md`](./22_COMPLETE_END_TO_END_WORKER_FLOW.md).

---

*End of visual diagram source. PDF with rendered diagrams is generated separately from this Markdown.*
