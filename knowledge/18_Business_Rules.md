Extracted **~340 business rules** from `msrx_v2.0`, focused on domain behavior (status gates, eligibility, validation, commit/pricing constraints) — not technical plumbing.

Open the interactive inventory beside chat: [business-rules-inventory](C:\Users\AbhishekGajera\.cursor\projects\d-BLUE-WATER\canvases\business-rules-inventory.canvas.tsx)  
(It’s a live canvas: filter by module, search rules/paths, expand sections.)

### Core MSR-X tape flow
`uploaded` → approve → `approved` → price → `priced` → commit → `pre-commit` → confirm → `confirmed` → (optional) resell

### Module highlights

| Module | Rule count (approx) | Examples |
|--------|---------------------|----------|
| **API / MSR-X** | 34 | Commit only if priced/pre-commit/approved; confirm only from pre-commit; price lock window; aggregator-only auto-resell; seller must belong to aggregator on final review |
| **Freedom** | 40 | Volume caps block commit; business hours; exclusion/LLPA engines; extension only after commit; buyer must match PA |
| **Due Diligence** | 13 | Status machine; Scheduled→Closed needs PA; Funded→Purchased needs boarding |
| **SuperTransfer QC** | ~210 | Full named check catalog (dates, escrow, MERS, ARM, NFP, UW docs, etc.) |
| **Transfer** | 4 | Loan must be confirmed unless commit check disabled |
| **Second Lien / CaaS / Voxtur / CRA / Roles / …** | remainder | Schema uniqueness, AOL eligibility, income banding, aggregator-only decorators |

### Important caveat
Many **Freedom LLPA/exclusion** and **DD QC** rules are **data-driven** (DB `Rule` / `QualityControl`). Code enforces the engines; client-specific rule rows are not hard-coded. SuperTransfer QC checks are fully enumerated from `quality_functions_dict.py`.