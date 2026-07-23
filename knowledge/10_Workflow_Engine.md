Three separate engines — not one shared state machine. Freedom commit can trigger CAAS; the React Wizard talks to MSR Coissue APIs, not Freedom `WorkFlow`.

Open the full reverse-engineering artifact beside chat: [workflow-engines-reverse-engineering](C:\Users\AbhishekGajera\.cursor\projects\d-BLUE-WATER\canvases\workflow-engines-reverse-engineering.canvas.tsx) (interactive comparison, state diagrams, every table).

### Core difference

| | React Wizard | Freedom | CAAS |
|---|---|---|---|
| **Job** | MSR Coissue BestEx UI | Per-buyer pricing pipeline | Post-commit report / email / SFTP |
| **Steps live in** | Hardcoded React | `freedom_workflow` | `caas_workflow` + step configs |
| **Runtime state** | Redux `wizardStep` 0–5 | `Tape.status` + `WholeLoanPrice` | Ephemeral run + `WorkflowLog` |

### How they start
- **React:** Price Management → `showWizard` (often jumps to step 2 if tape exists).
- **Freedom:** Upload/price/reprice/… → `get_pricing_workflows` → `process_workflows`.
- **CAAS:** Freedom commit → `trigger_caas_workflows`, or cron `WorkflowJob`, or REST `caas/workflow/`.

### Transitions
- **React:** Button guards (`fileLoadSuccess`, buyers selected, duplicates check) + API success.
- **Freedom:** `for setting in workflow` → `PRICE_FUNC_MAP[setting]`; fail aborts that buyer.
- **CAAS:** Active steps `order_by(index)` → `func_map[func_name]()`; fail logs and stops.

### Permissions
- **React:** Token auth; `msrx_viewer` hides commit.
- **Freedom:** Auth + Counterparty; workflow admin = superuser.
- **CAAS:** Cascade match: user → role+platform → role → platform default → global.

### Failures
None retry or compensate. React rewinds/modals; Freedom emails and returns False; CAAS writes `WorkflowLog` and stops (already-sent email/SFTP stay sent).

### Tables
- **CAAS:** `Workflow`, `WorkflowJob`, `WorkflowStep`, CSV/SQL/Email/SFTP configs, `WorkflowLog`
- **Freedom:** `WorkFlow`, sibling `PricingUpload` (+ Tape / Price / Commit as I/O)
- **React:** no workflow tables — MSR Coissue domain entities only