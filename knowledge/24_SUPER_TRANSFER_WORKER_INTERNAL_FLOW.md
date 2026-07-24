# 24 — Super Transfer Worker Internal Flow

**Audience:** Backend developers / KT — deep worker internals  
**Date:** 2026-07-24  
**Source of truth:** [`22_COMPLETE_END_TO_END_WORKER_FLOW.md`](./22_COMPLETE_END_TO_END_WORKER_FLOW.md) + `super_transfer_client` code  
**Companion (system-level):** [`23_MSRX_SUPER_TRANSFER_VISUAL_DIAGRAMS.md`](./23_MSRX_SUPER_TRANSFER_VISUAL_DIAGRAMS.md) / architecture PDF  
**Method:** Worker-only visual learning — **no invented architecture**

---

## About this document

This PDF explains the Super Transfer worker **from job receipt to cleanup**. It does **not** re-audit frontend/Django confirm-commit (see document 23).

| Label | Meaning |
|-------|---------|
| **`[CONFIRMED FROM CODE]`** | Exact file/function/behavior in `super_transfer_client` (or proven worker DB/API calls) |
| **`[CONFIRMED FROM CONFIG]`** | appspec / cron / deploy scripts |
| **`[UNKNOWN — KT CONFIRMATION REQUIRED]`** | Not proven in audited repos — do not invent |

---

## Legend — CONFIRMED vs UNKNOWN

| Visual / label | Meaning |
|----------------|---------|
| Solid boxes + normal arrows | **CONFIRMED FROM CODE** or **CONFIRMED FROM CONFIG** |
| Dashed / `???` / UNKNOWN box | **UNKNOWN — KT CONFIRMATION REQUIRED** |
| `.pkl` artifacts | **Loaded at startup** — inference only — **NO training per loan** |

---

## 1. WORKER DEPLOYMENT / STARTUP

CodeDeploy installs the repo to `/home/ec2-user/super_transfer_client/`. After install, `start_cron.sh` installs a crontab. Exact production AMI / ASG / hostname are not in repo.

```mermaid
flowchart TD
  subgraph DEPLOY["DEPLOY — CONFIRMED FROM CONFIG"]
    CD[AWS CodeDeploy]
    AS["appspec.yml destination<br/>/home/ec2-user/super_transfer_client/"]
    SC["scripts/start_cron.sh"]
  end

  subgraph HOST["EC2 WORKER HOST"]
    CR["crontab entry installed"]
    UNKHOST["Exact AMI / ASG / hostname<br/>??? UNKNOWN — KT ???"]
  end

  subgraph ENTRY["PROCESS ENTRY — CONFIRMED FROM CODE"]
    PY["python3.12 scripts/main.py"]
    IMP["import helper_functions"]
    EMC["ensure_model_context()"]
  end

  CD --> AS --> SC --> CR --> PY --> IMP --> EMC
  UNKHOST -.-> HOST
```

**KEY TAKEAWAY:** Worker is CodeDeploy + cron entrypoint — not systemd/supervisor in this repo. `[CONFIRMED FROM CONFIG]`

---

## 2. CRON + flock EXECUTION

Every minute cron tries to start the worker. `flock -w 1` ensures only one overlapping `main.py` runs on the host. Long-running work keeps the flock held.

```mermaid
flowchart TD
  CRON["cron: * * * * *<br/>CONFIRMED FROM CONFIG"]
  FL["flock -w 1<br/>PURPOSE: single worker instance<br/>CONFIRMED FROM CONFIG"]
  PY["python3.12 scripts/main.py"]
  HOLD{"flock acquired?"}
  RUN["main() long-poll loop runs"]
  SKIP["exit immediately<br/>another instance holds lock"]

  CRON --> FL --> HOLD
  HOLD -->|yes| PY --> RUN
  HOLD -->|no within 1s| SKIP
```

**KEY TAKEAWAY:** Concurrency model = one process per host via flock; messages processed sequentially inside that process. `[CONFIRMED FROM CODE]` + `[CONFIRMED FROM CONFIG]`

---

## 3. main.py PROCESSING LOOP

On import, models/secrets/AWS clients load once. `main()` regenerates local loan dirs, then loops while DynamoDB deployment `process_flag` is true. Missing-file queue is polled before the loan queue.

```mermaid
flowchart TD
  START["scripts/main.py module load"]
  EMC["ensure_model_context()<br/>Secrets + AWS clients<br/>pickle.load NB + TF-IDF + JSON maps"]
  MN["main()"]
  REGEN["regenerate_local_loan_directory"]
  PF{"process_flag()<br/>DynamoDB supertransfer-deploymentDB"}
  MF["receive_message<br/>missing-file queue first"]
  LQ["else receive_message<br/>loan queue"]
  HANDLE["handle message body"]
  STOP["exit loop"]

  START --> EMC --> MN --> REGEN --> PF
  PF -->|true| MF
  MF -->|no message| LQ
  MF -->|message| HANDLE --> PF
  LQ -->|message| HANDLE
  LQ -->|none| PF
  PF -->|false| STOP
```

**KEY TAKEAWAY:** Models load at import — not per loan. Loop gated by deployment DynamoDB flag. `[CONFIRMED FROM CODE]`

---

## 4. SQS POLLING DECISION TREE

Long-poll: `WaitTimeSeconds=20`, `MaxNumberOfMessages=1`. Visibility starts at 1200s; heartbeat during `processLoan` extends to 3600s. Malformed JSON does **not** delete. Several skip paths **do** delete.

```mermaid
flowchart TD
  R["receive_message<br/>loan queue"]
  J{JSON parse OK?}
  D1["NO delete<br/>sleep 120 / visibility retry<br/>CONFIRMED FROM CODE"]
  DUP{"seller-loan-id ==<br/>current_processing?"}
  DEL_DUP["delete_message + sleep 2<br/>CONFIRMED FROM CODE"]
  CC["commitment_check<br/>Postgres"]
  CF{commit_flag?}
  LID{"loan_id in body?"}
  PL["processLoan + heartbeat"]
  DEL["delete_message ALWAYS<br/>after this branch"]

  MARK["⚠️ DELETE-ON-SKIP<br/>CONFIRMED FROM CODE<br/>DESIGN INTENT — KT"]

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

**KEY TAKEAWAY:** Missing `loan_id` or failed commit check → no `processLoan`, message still deleted. `[CONFIRMED FROM CODE]`

---

## 5. commitment_check

Direct Postgres via `psycopg2` in `base/workflows/query_msrx.py`. Parses `seller-loan_id` → seller + loan_number. Optional seller setting `super_transfer_commit_check` requires coissue tape status `confirmed`.

```mermaid
flowchart TD
  IN["SQS body<br/>seller-loan-id"]
  PARSE["Parse:<br/>seller_id = split('-')[0]<br/>loan_number = split('_')[1]<br/>CONFIRMED FROM CODE"]
  PG[(PostgreSQL MSRX)]
  U["msrx_msrx_user<br/>user_details.transfer_settings<br/>.super_transfer_commit_check"]
  NEED{"check required<br/>== true?"}
  JOIN["Join coissue_tape + seller<br/>status = confirmed?"]
  OK["return flag=True<br/>+ coissue_loan_id"]
  BAD["return flag=False"]
  SKIP["main.py: skip processLoan<br/>DELETE message anyway"]

  IN --> PARSE --> PG --> U --> NEED
  NEED -->|no| OK
  NEED -->|yes| JOIN
  JOIN -->|yes| OK
  JOIN -->|no| BAD --> SKIP
```

**KEY TAKEAWAY:** Commit gate is Postgres, not DynamoDB. False → skip + delete. Ops recovery: `[UNKNOWN — KT CONFIRMATION REQUIRED]`

---

## 6. loan_id GATE

Django producer sends only `seller-loan-id`. Worker requires `'loan_id' in res` before `processLoan`. Enrichment component is **not** in audited repos — do **not** label as Lambda.

```mermaid
flowchart TD
  MSG["SQS message after parse"]
  HAS{"'loan_id' in res?<br/>main.py CONFIRMED FROM CODE"}
  PL["processLoan(res, lock)"]
  SKIP["skip processLoan<br/>delete_message anyway"]

  subgraph GAP["BIG UNKNOWN — DO NOT LABEL AS LAMBDA"]
    U["?????????????????????????????<br/>??? UNKNOWN ENRICHMENT ???<br/>??? KT CONFIRMATION REQUIRED ???<br/>Who adds loan_id / deal_id / porfolio_id?<br/>?????????????????????????????"]
  end

  NOTE["NOTE: DynamoDB may also hold loan_id<br/>inside processLoan initialize_portfolio<br/>but unreachable if this gate fails"]

  U -.-> MSG
  MSG --> HAS
  HAS -->|yes| PL
  HAS -->|no| SKIP
  NOTE -.-> U
```

**KEY TAKEAWAY:** Schema mismatch is proven. What fills `loan_id` in production is a **KT question**. `[CONFIRMED FROM CODE]` gate + `[UNKNOWN]` enrichment

---

## 7. processLoan COMPLETE INTERNAL PIPELINE

Real order from `scripts/process_loan_handler.py` · `processLoan(res, lock)`. Exceptions set status `"Failed"` and are **not** re-raised; outer `main.py` still deletes SQS.

```mermaid
flowchart TD
  subgraph ST["SUPER TRANSFER — processLoan"]
    A["1 DynamoDB query by seller-loan_id"]
    B["2 Resolve S3 folder from DDB"]
    C["3 Local folder + start log"]
    D["4 Boarding staging = In Process"]
    E["5 emit started"]
    F["6 build_processing_context"]
    G["7 List + download S3 PDFs"]
    H["8 Merge PDFs → blob / JSON sidecar"]
    I["9 segregate_documents OR zip_to_final_dict"]
    J["10 Optional SFTP blob upload"]
    K["11 Split pages → per-doc PDFs"]
    L["12 Threaded return_ExtractFunctions"]
    M["13 Post-extract rechecks / signatures"]
    N["14 makeOutputFile + HOEPA"]
    O["15 Filename mapping → S3"]
    P["16 DD document initialization"]
    Q["17 prepare_outputdict → send_values_to_DD"]
    R["18 status Processed + emit completed"]
    S["19 Missing files + extracted fields APIs"]
    T["20 DynamoDB update_item"]
    U["21 Upload Extracted_Fields.json / CSV / PDFs"]
    V["22 Stacked zip / bookmarked PDF"]
    W["23 Notification SQS + optional Bedrock"]
    X["except → status Failed"]
    Y["finally → metadata/log + rmtree"]
  end

  OUTER["outer main.py:<br/>DELETE SQS message anyway"]

  A-->B-->C-->D-->E-->F-->G-->H-->I-->J-->K-->L-->M-->N-->O-->P-->Q-->R-->S-->T-->U-->V-->W
  A -.-> X
  X --> Y
  W --> Y
  Y --> OUTER
  X --> OUTER
```

**KEY TAKEAWAY:** Full pipeline is sync inside one message handler; failures still ack SQS. `[CONFIRMED FROM CODE]`

---

## 8. S3 DOCUMENT PROCESSING

S3 prefix comes from DynamoDB fields `sellerID`, `Buyer`, `LoanNum` — not invented paths. Who uploaded the source PDFs originally is unknown.

```mermaid
flowchart TD
  DDB[(DynamoDB item<br/>sellerID / Buyer / LoanNum)]
  S3[(S3 SuperTransfer/s/b/loan/)]
  LIST["list_of_uploaded_files"]
  DL["download_object_files"]
  LOCAL["local_loan_files/{seller-loan-id}/"]
  MERGE["Merge PDFs → blob<br/>or use classification JSON sidecar"]
  UNK["Who uploaded source docs?<br/>??? UNKNOWN — KT ???"]

  DDB --> S3 --> LIST --> DL --> LOCAL --> MERGE
  UNK -.-> S3
```

**KEY TAKEAWAY:** Worker is a consumer of S3 loan folders keyed by DDB metadata. Upload provenance: KT. `[CONFIRMED FROM CODE]`

---

## 9. CLASSIFICATION RUNTIME

Runtime classification: page → Textract OCR text → TF-IDF transform → Naive Bayes `predict_proba` → label or `"Misc"` if confidence ≤ 0.7. **No training in this path.**

```mermaid
flowchart TD
  subgraph RUNTIME["RUNTIME — INFERENCE ONLY"]
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

  BIG["★ NO MODEL TRAINING PER LOAN ★"]

  SRC --> TX --> OCR --> TF --> NB --> CONF
  CONF -->|yes| LAB --> SEG
  CONF -->|no| MISC --> SEG
  BIG -.-> RUNTIME
```

**KEY TAKEAWAY:** Classification is inference against loaded pickles. `[CONFIRMED FROM CODE]`

---

## 10. TF-IDF + Naive Bayes MODEL USAGE

Artifacts loaded in `ensure_model_context` / `get_main_model`: `naive_bayes_classifier.pkl`, `tf_idf.pkl`, plus JSON maps. Optional buyer-specific model from S3. Offline training location is outside worker runtime.

```mermaid
flowchart TD
  subgraph OFFLINE["OFFLINE TRAINING — NOT in worker"]
    TD[training data] --> FIT[TF-IDF fit]
    FIT --> TR[Naive Bayes train]
    TR --> PK[".pkl files saved"]
  end

  subgraph LOAD["WORKER LOAD — CONFIRMED FROM CODE"]
    EMC["ensure_model_context / get_main_model"]
    NB["naive_bayes_classifier.pkl"]
    TF["tf_idf.pkl"]
    JT["label_tokenizer.json"]
    PM["page_number_mappings.json"]
    BUY["optional customized_model/{branch}/{buyer}/"]
  end

  subgraph USE["PER-PAGE INFERENCE"]
    TRF["tf_idf.transform"]
    PR["predict_proba"]
    OUT[label + confidence]
  end

  PK -.->|deploy / load only| EMC
  EMC --> NB & TF & JT & PM
  BUY -.-> EMC
  TF --> TRF --> PR
  NB --> PR --> OUT
```

**KEY TAKEAWAY:** 100 loans today → **0 trains**. Load ≠ train. `[CONFIRMED FROM CODE]`

---

## 11. AWS TEXTRACT USAGE

Textract is used at **runtime** for classification OCR and for many field extractors. Tesseract appears in some extractors (e.g. credit report page numbers). Training-data OCR pipeline location is unknown.

```mermaid
flowchart TD
  PAGE[PDF page / document]
  DET["Textract detect_document_text<br/>classification OCR<br/>CONFIRMED FROM CODE"]
  AN["Textract analyze_document<br/>forms / queries / analyze_id<br/>field extraction<br/>CONFIRMED FROM CODE"]
  TES["Tesseract pytesseract<br/>secondary — some extractors<br/>CONFIRMED FROM CODE"]
  CLS[Classification Text column]
  FLD[Extractor field dict]

  PAGE --> DET --> CLS
  PAGE --> AN --> FLD
  PAGE --> TES --> FLD

  UNK["Training OCR pipeline location<br/>??? UNKNOWN — KT ???"]
  UNK -.-> DET
```

**KEY TAKEAWAY:** Textract = runtime OCR/extraction service, not the training loop. `[CONFIRMED FROM CODE]`

---

## 12. DOCUMENT SEGREGATION

`segregate_documents` groups classified pages and splits the blob into per-type PDFs. Alternate: JSON/txt sidecar → `zip_to_final_dict` skips full re-classification. Page labels below are illustrative.

```mermaid
flowchart TD
  NOTE["★ ILLUSTRATIVE PAGE LABELS ★"]
  BLOB[Blob PDF]
  P1["Page → Note"]
  P2["Page → Note"]
  P3["Page → Credit Report"]
  P4["Page → Security Instrument"]
  GRP["segregate_documents<br/>group + split"]
  O1[Note.pdf]
  O2[Credit_Report.pdf]
  O3[Security_Instrument.pdf]
  OUT[S3 upload + extraction threads]

  ALT["Alternate: zip_to_final_dict<br/>if classification sidecar exists"]

  NOTE --> BLOB
  BLOB --> P1 & P2 & P3 & P4 --> GRP
  GRP --> O1 & O2 & O3 --> OUT
  ALT -.-> GRP
```

**KEY TAKEAWAY:** Segregation turns page labels into document PDFs that drive extractors. `[CONFIRMED FROM CODE]`

---

## 13. return_ExtractFunctions EXTRACTION ROUTING

Each segregated label selects a confirmed extractor. Fields exist only when that document type was classified and its extractor ran.

```mermaid
flowchart TD
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
  SEND["prepare_outputdict_and_values<br/>→ send_values_to_DD"]

  DOC --> TYP --> MAP
  MAP --> N & CD & CR & SI & LA & MORE
  N & CD & CR & SI & LA & MORE --> TX --> FD --> RC --> SEND
```

**KEY TAKEAWAY:** Extraction is label-driven and partial — not a universal field set. `[CONFIRMED FROM CODE]`

---

## 14. DUE DILIGENCE COMMUNICATION

Worker posts to Django HTTP Due Diligence / Super Transfer APIs (Api-Key). DD Postgres is behind Django ORM — worker does not write DD tables via raw SQL.

```mermaid
flowchart TD
  W[processLoan]
  INIT["DD document initialization APIs"]
  SEND["send_values_to_DD"]
  MISS["missing files / extracted fields APIs"]
  DJ["Django HTTP<br/>/msrx/duediligence/...<br/>/msrx/supertransfer/..."]
  PG[(PostgreSQL DD data<br/>via ORM)]

  W --> INIT --> DJ
  W --> SEND --> DJ
  W --> MISS --> DJ
  DJ --> PG
```

**KEY TAKEAWAY:** DD updates are HTTP API writes, not direct worker SQL into DD tables. `[CONFIRMED FROM CODE]`

---

## 15. DYNAMODB INTERACTION

Worker **queries** and **updates** by `seller-loan_id`. No runtime `put_item` found. Initial item creator is unknown. Deployment table uses PK `env` for `process_flag`.

```mermaid
flowchart TD
  SQS[SQS seller-loan-id]
  Q["table.query<br/>KeyCondition seller-loan-id<br/>MUST exist"]
  META["Read LoanNum / sellerID / Buyer<br/>+ loan_id / deal_id / porfolio_id if present"]
  PROC[processLoan work]
  UP["table.update_item<br/>Files / Extracted_Fields / loan_Status / …"]
  CREATE["Initial put_item creator<br/>?????????????????<br/>??? UNKNOWN — KT ???<br/>?????????????????"]

  DEP["supertransfer-deploymentDB<br/>query env → process_flag"]

  CREATE -.-> Q
  SQS --> Q --> META --> PROC --> UP
  DEP -.->|startup loop gate| SQS
```

**KEY TAKEAWAY:** Worker assumes DDB item already exists; it does not create it. `[CONFIRMED FROM CODE]` + `[UNKNOWN]` creator

---

## 16. POSTGRESQL INTERACTION

Worker uses direct `psycopg2` for commitment check and boarding-staging merge lookups. DD business data goes through Django HTTP.

```mermaid
flowchart TD
  W[Worker]

  subgraph DIRECT["DIRECT psycopg2 — CONFIRMED FROM CODE"]
    CC["commitment_check<br/>msrx_msrx_user<br/>msrx_client_coissue_tape<br/>msrx_client_coissue_seller"]
    BS["boarding staging merge SQL<br/>msrx_boarding_staging"]
  end

  subgraph VIAAPI["VIA DJANGO HTTP"]
    DD[Due Diligence / ST APIs]
  end

  PG[(PostgreSQL MSRX DB)]

  W --> CC --> PG
  W --> BS --> PG
  W --> DD --> PG
```

**KEY TAKEAWAY:** Only commit/boarding SQL is direct; DD entity writes are API-mediated. `[CONFIRMED FROM CODE]`

---

## 17. WORKER FAILURE PATHS

Only audit-confirmed outcomes. DLQ / redrive / ops replay for delete-on-skip are unknown.

```mermaid
flowchart TD
  F1["Malformed SQS JSON"] --> A1["NO delete<br/>sleep 120 / visibility retry"]
  F2["Duplicate current_processing"] --> A2["DELETE + sleep 2<br/>NO processLoan"]
  F3["commitment_check false"] --> A3["NO processLoan<br/>DELETE message"]
  F4["loan_id missing"] --> A4["NO processLoan<br/>DELETE — HIGH LOSS RISK"]
  F5["DynamoDB item missing"] --> A5["processLoan → Failed<br/>DELETE anyway"]
  F6["S3 docs empty / OCR fail"] --> A6["status Failed<br/>DELETE anyway"]
  F7["Extractor / DD API exception"] --> A7["status Failed<br/>DELETE anyway"]

  KT["DLQ / redrive / replay SOP<br/>??? UNKNOWN — KT ???"]
  A1 -.-> KT
  A3 -.-> KT
  A4 -.-> KT
```

**KEY TAKEAWAY:** Worst silent losses: delete-on-skip when `loan_id` / commit check fails. `[CONFIRMED FROM CODE]`

---

## 18. SQS DELETION / RETRY BEHAVIOR

```mermaid
flowchart TD
  subgraph DELETE_YES["DELETE MESSAGE — CONFIRMED"]
    D1[Duplicate current_processing]
    D2[commitment_check false]
    D3[loan_id missing]
    D4[processLoan success]
    D5[processLoan Failed exception path]
  end

  subgraph DELETE_NO["NO DELETE — CONFIRMED"]
    N1[Malformed JSON<br/>visibility timeout retry]
  end

  subgraph UNKNOWN_OPS["UNKNOWN — KT"]
    U1[DLQ configuration]
    U2[Redrive policy]
    U3[Ops replay SOP for delete-on-skip]
  end

  D1 & D2 & D3 & D4 & D5 --> DEL[delete_message]
  N1 --> VIS[visibility / sleep 120]
  DEL -.-> U1
  DEL -.-> U2
  DEL -.-> U3
```

**KEY TAKEAWAY:** Visibility retry only for bad JSON. Most business skips permanently ack. `[CONFIRMED FROM CODE]`

---

## 19. WORKER CLEANUP / FINALIZATION

`processLoan` `finally` uploads metadata/logs and removes the local folder. Outer `main.py` deletes SQS after the handler returns (success or Failed).

```mermaid
flowchart TD
  DONE["processLoan try path ends<br/>Processed OR Failed"]
  FIN["finally block"]
  META["Upload metadata / log to S3"]
  RM["rmtree local_loan_files/{seller-loan-id}"]
  RET["return to main.py"]
  DEL["delete_message SQS"]
  LOOP["continue process_flag loop"]

  DONE --> FIN --> META --> RM --> RET --> DEL --> LOOP
```

**KEY TAKEAWAY:** Local cleanup always runs; SQS delete is outside `processLoan` in `main.py`. `[CONFIRMED FROM CODE]`

---

## 20. ONE-LOAN WORKER EXAMPLE — `117-42_2208066387`

Example IDs: seller `117`, buyer `42`, loan `2208066387`. Enrichment between SQS receive and `loan_id` gate remains unknown.

```mermaid
flowchart TD
  Q["SQS receives<br/>seller-loan-id = 117-42_2208066387<br/>+ loan_id ?"]
  UNK["??? UNKNOWN enrichment ???<br/>??? KT CONFIRMATION REQUIRED ???"]
  MAIN["scripts/main.py"]
  CC["commitment_check Postgres"]
  GATE{"loan_id present?"}
  PL["processLoan"]
  DDB["DynamoDB query 117-42_2208066387"]
  S3["S3 SuperTransfer/117/42/2208066387/"]
  CLS["Textract → TF-IDF → NB → labels"]
  SEG["segregate → per-doc PDFs"]
  EXT["return_ExtractFunctions → fields"]
  DD["send_values_to_DD"]
  UP["DDB update_item + S3 outputs"]
  CLN["finally cleanup + SQS delete"]

  UNK -.-> Q
  Q --> MAIN --> CC --> GATE
  GATE -->|yes| PL --> DDB --> S3 --> CLS --> SEG --> EXT --> DD --> UP --> CLN
  GATE -->|no| SKIP["skip + DELETE"]
```

**KEY TAKEAWAY:** One composite id keys worker local/S3/DDB paths; `loan_id` is a separate DD PK required by the gate. `[CONFIRMED FROM CODE]`

---

# HOW TO READ THESE DIAGRAMS

1. **Start with Diagrams 1–3** — deploy, flock, main loop.  
2. **Read Diagrams 4–6** — SQS decisions, commitment_check, loan_id gate (+ UNKNOWN enrichment).  
3. **Read Diagram 7** — full `processLoan` order.  
4. **Read Diagrams 8–13** — S3, classification, pickles, Textract, segregation, extractors.  
5. **Read Diagrams 14–16** — DD HTTP, DynamoDB, Postgres.  
6. **Read Diagrams 17–19** — failures, delete/retry, cleanup.  
7. **Read Diagram 20** — one-loan walkthrough `117-42_2208066387`.  

Treat every `??? UNKNOWN ???` box as a **KT question**, not an implemented connector.

For system-level MSRX → SQS → Worker boundaries, use document **23** (architecture / visual diagrams PDF).

---

*End of worker-internal diagram source. PDF with rendered diagrams is generated separately — does not overwrite document 23.*
