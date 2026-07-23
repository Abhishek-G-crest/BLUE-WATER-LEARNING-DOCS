There are **two pricing engines**, not one. Full navigable breakdown with every formula is in the canvas: **Pricing Engine Reverse Engineering**.

---

## Universal stack

```
Input → Validation → Business Rules → Calculation → DB/JSON Lookups → Output
```

| Engine | Domain | Orchestrator |
|--------|--------|--------------|
| **Freedom** | Whole-loan / correspondent | `price_via_workflow` + `PRICE_FUNC_MAP` |
| **MSRX** | Coissue MSR (grid + DPX) | `asset_price_v3` |

---

## Engine A — Freedom whole-loan

**Entry:** `POST price-tape/` → `validate_tape` → `get_pricing_workflows` → `process_workflows` → `price_via_workflow`

**Default workflow:**
`SETTLEMENTDATES → BASERATESHEET → EXCLUSIONS → RATESHEETLLPA → MARGIN → GENERICTOTAL → EXTENSIONS`

### Core formulas

**Base price** — first matching `Rule` → `wl_price = Rule.adj` (`base/base_ratesheet.py`)

**LLPA** (`rules/rules.py`):
```
adj = Rule.adj  (+ waiver adj if hp/hr waiver)
llpa_total += adj
# then: ratesheet_controls = clamp(llpa_total, ratesheet_cap, ratesheet_floor)
```

**Margin** (`seller_specific/margin.py`):
```
margin = point_margin + (dollar_margin / t_loan_balance) × 100
```

**MA/SRP** (`base/ma.py` + `subsidy.py`):
```
type_rate_key = F|G + 15|30 + note_rate
srp = ma_srp + subsidy_adj   # govt floored at 0
```

**Desk incentive** (`desk_incentive.py`):
```
desk_incentive = (rs_mult − bid_mult − expense_mult) × service_rate
```

**Generic total** (`total_generic.py`):
```
asset = wl_price + bubd_adj + ratesheet_controls + desk_incentive
      + margin + realtime_llpa + ma_adj + spec_payup
gross = asset + msr_or_srp()
total = total_controls(gross)
```

**Freedom total** uses `asset + srp` (no margin/realtime in asset). Agency totals add `base_price + spec_payup×passthrough + LLPA + margin + MSR`.

**EFC:** `efc_mult = selected_perdiem / service_rate`; month price selected by turn-time vs fund dates.

**Providers:** FNMA/Freddie cash APIs, Refinitiv RICS, Bloomberg TBA helper, `YearlyLLPA` for agency LLPAs.

---

## Engine B — MSRX coissue / DPX

**Entry:** `POST /pricing/` → `msr_pricing` → `pricing_pre_check` → `asset_price_v3`

### Grid formula (`general_grid.py`)
```
price = (base × (1 + Σ multipliers) + Σ level) × (1 + Σ overall) × Π dm
total = price_base + price_excess + price_incentive
multiple = total / service_rate
```
Conv produces `price_ss/sa/aa`; govt produces `price_ss`.

### Buyer SRP (`SRP.py`) — same economics, buyer-specific adjustor maps:
```
base_price_ss = (base_mult × base_sr) × (1 + Σ adj + remit)
price_ss = base_price_ss + excess_price
```
Providers: 53, Planet, Lakeview, Pingora, CMC, BSI, Seneca, MrCooper, Roundpoint, Balbec, …

### DPX middleware (`support_middleware.py`)
1. Normalize features → interpolate/predict base multiple  
2. Level-2: term, state/escrow, remit  
3. Excess strip  
4. `price = multiple × service_rate` (+ JSON overlays)  
5. Newer InterpretableDPX: `final = predict(base)×base_sf + predict(excess)×excess_sf`

### Margin overlay (bps)
```
margin = margins[buyer] / 100
price_* = price_* − margin
multiple_* = price_* / service_rate
```

---

## Where formulas live

| Kind | Location |
|------|----------|
| Algebra | Python (`total_*`, `desk_incentive`, `general_grid`, `SRP_*`, DPX) |
| LLPA / base values | DB `Rule.adj` under `Step` → sheets |
| MA/SRP sheets | DB `MaSheet`, `Subsidy` |
| Grid / SRP adjustors | JSON on `Client_Coissue_Buyer` |
| DPX models | JSON/pickle on `Client_Coissue_Buyer_Middleware` |
| Workflow order | DB `WorkFlow.step` (defaults in `upload.py`) |
| Schema docs | `Doc/json_config.md`, `Doc/DPX_Term.json` |

Open the canvas for every total variant, every `PRICE_FUNC_MAP` step, every SRP provider, and the full file list under `freedom/supporting/pricing/` and `api/supporting/`.


BLUE-WATER Pricing Engine
Complete reverse engineering of both engines: Freedom whole-loan rules workflow and MSRX coissue grid + DPX middleware.

Freedom
Whole-loan engine
MSRX
Coissue / MSR engine
~45
PRICE_FUNC_MAP steps
11+
Buyer SRP providers
Universal pipeline
Every price path follows the same conceptual stack: Input → Validation → Business Rules → Calculation → Database/JSON Lookups → Output.
Stage	What happens
1. Input	Loan tape / API payload / buyer IDs
2. Validation	Field enums, mandatory fields, pre-checks
3. Business rules	Exclusions, eligibility, agency remit gates
4. Calculation	Workflow steps or grid/DPX math
5. DB / JSON lookups	Rules, MA sheet, adjustors, DPX models
6. Output	loan_price JSON or Client_Coissue_Tape.price
Engine A — Freedom (Whole Loan)
Entry: POST freedom/price-tape/ → validate_tape → get_pricing_workflows → process_workflows → price_via_workflow (PRICE_FUNC_MAP).


Pipeline detail
Tape upload → tapecrack + validate_tape → price_setup(DEFAULT_LOAN_PRICE) → WorkFlow.step order from DB (or DEFAULT_PRICING) → for each step: PRICE_FUNC_MAP[step](loans, model, …) → WholeLoanPrice.price = JSON(loan_price)
Default workflow

SETTLEMENTDATES → BASERATESHEET → EXCLUSIONS → RATESHEETLLPA → MARGIN → GENERICTOTAL → EXTENSIONS
Freddie default

FREDDIECASH → AGENCYLLPA → MARGIN → AGENCYTOTAL

Core formulas
Cap / floor control
controls(total, cap, floor) = max(min(total, cap), floor) # if both set min(total, cap) # cap only max(total, floor) # floor only ratesheet_controls = controls(llpa_total, ratesheet_cap, ratesheet_floor) total_controls = controls(gross_or_msr_total, total_cap, total_floor)
File: freedom/supporting/pricing/controls/price_controls_apply.py

LLPA (ratesheet)
For each matching Rule (case=0): if hp_waiver and hp_waiver_adj: adj = hp_waiver_adj + Rule.adj elif hr_waiver and hr_waiver_adj: adj = hr_waiver_adj + Rule.adj else: adj = Rule.adj llpa_total += adj # loan_exclude or adj falsy → exclusion, llpa_total = 0 Base ratesheet (non-additive): first matching Rule → wl_price = Rule.adj no match → base_exclusion
Files: rules/rules.py, llpas/ratesheet.py, base/base_ratesheet.py

Margin
margin = point_margin + (dollar_margin / t_loan_balance) × 100 resell_margin = resell_point + (resell_dollar / t_loan_balance) × 100 # layers: seller + investor; resell when correspondent chain differs # metaproduct_margin overrides when set
File: seller_specific/margin.py · Table: Margin

MA / SRP (Freedom)
type_rate_key = agencyLetter + term15or30 + note_rate # F/G + 15|30 + rate e.g. F304.25 From MaSheet row: srp, ma_srp, bubd_adj, ma_adj, coupon, mbs_price→wl_price, payup_adj After subsidy: srp = ma_srp + subsidy_adj # govt: srp = max(srp, 0) msr_or_srp = msr_total if present else srp (else 0)
Files: base/ma.py, price_adjustments/subsidy.py, controls/msr_or_srp.py

Desk incentive (Freedom)
npt_mult = npt_total / (−service_rate) # 30yr: npt_total includes spec_payup bid_mult = start_mult + npt_mult # capped by strip_cap (±), then spec_cap rs_mult = (rs_npt_total + (ma_srp + subsidy_adj)) / service_rate × (−1) # govt: di_ma_srp = max(0, ma_srp+subsidy) efc effect: bid_mult += (−efc_mult) desk_incentive = (rs_mult − bid_mult − expense_mult) × service_rate # VA cashout LTV>90: bid_mult = llpa_total/(−sr); desk_inc = −expense×sr
File: price_adjustments/desk_incentive.py

EFC (expected funding cost / carry)
monthN_efc_perdiem_calc = min(monthN_efc_max, per_diem × fund_diff_days) monthN_efc_price = monthN_price + monthN_efc_perdiem_calc # select month0 vs month1 by product/term/turn_time rules efc_mult = selected_mo_efc_perdiem / service_rate wl_price = selected_mo_price
File: base/efc.py · Tables: EFC, SettlementDate, SifmaSettlementDates

Total-price variants
total/total_generic.py
asset = wl_price + bubd_adj + ratesheet_controls(llpa) + desk_incentive + margin + realtime_llpa + ma_adj + spec_payup gross = asset + msr_or_srp() total = total_controls(gross)
total/total_freedom.py
asset = wl_price + bubd_adj + ratesheet_controls(llpa) + desk_incentive gross = asset + srp total = total_controls(gross)
total/total_msr.py
gross = wl_price + ratesheet_controls(llpa) + margin total = total_controls(gross) → msr_total
total/total_agency.py, total_fnma.py
asset = base_price + spec_payup×passthrough + ratesheet_controls(llpa) + margin + resell_margin gross = asset + msr_or_srp_for_note_rate total = clamp(gross, total_floor, total_cap)
total/total_investor.py
total = total_controls(wl_price + ratesheet_controls(llpa) + margin) basis_diff = total − cost_basis
total/total_ares.py
asset = wl_price + ratesheet_controls(llpa) + margin total = total_controls(asset)
total/total_village.py
asset = wl_price + realtime_llpa + margin + ma_adj gross = asset + msr_or_srp() total = total_controls(gross)

Workflow steps (PRICE_FUNC_MAP)
Engine B — MSRX Coissue / DPX
Entry: POST /pricing/ → msr_pricing → pricing_pre_check → asset_price_v3 (grid then middleware) → margin overlay → Client_Coissue_Tape.price


Grid formula (general_grid)
Base_price_formula = [base, [multipliers], [level_adds], [overall_mults], [dm…]] Excess_price_formula = same shape price_base = (base × (1 + Σ multipliers) + Σ level) × (1 + Σ overall) × Π dm_i # govt only (elem[4]) price_excess = same pattern on excess strip total_price = price_base + price_excess + price_incentive multiple = total_price / service_rate Conv remits: price_ss, price_sa, price_aa (each remit re-run) Govt: price_ss only Optional adj_cap / adj_floor clip final price_*
File: api/supporting/general_grid.py · Config JSON: Client_Coissue_Buyer.adjustors / grid_info · Schema: Doc/json_config.md


Buyer-specific SRP (legacy grid path)
moneyness = (note_rate − buyer_par) × 100 excess_sr = max(0, service_rate − 0.25) # conv typical base_sr = service_rate − excess_sr base_price_unadj = base_mult_unadj × base_sr excess_price_unadj = excess_mult_unadj × excess_sr adj_base_total = 1 + Σ base adjustors (rate, fico, ltv, bal, state…) adj_excess_total = 1 + Σ excess rate adjustors base_price_ss = base_price_unadj × (adj_base_total + remit_ss) # similarly sa/aa excess_price = excess_price_unadj × adj_excess_total price_ss = base_price_ss + excess_price multiple_ss = price_ss / service_rate
Providers (api/supporting/SRP.py)

Function	Buyer
SRP_Search_Conv / Govt	Generic dispatcher
SRP_Search_*_53	Buyer 53
SRP_Search_*_Planet	Planet
SRP_Search_Govt_Lakeview	Lakeview
SRP_Search_Conv_Pingora	Pingora
SRP_Search_Conv_CMC	CMC
SRP_Search_Conv_BSI	BSI
SRP_Search_Conv_Seneca	Seneca
SRP_Search_*_MrCooper	Mr Cooper
SRP_Search_Conv_Roundpoint	Roundpoint
SRP_Search_Govt_Balbec	Balbec

DPX middleware formulas
Classic Varde / RBF interpolation
moneyness = note_rate − primary_rate normalize each feature x_i to [0,1] via model input_factor ranges p1, p4, p16 = component{1,2,3}.predict(coords) p_base = min(p4,p16) if same direction as p1 else p1 level2: p += term_adj×p_base; p += state_escrow×p_base base_multiple_remit = p × (1 + remit_model.predict) excess strip similarly; price = multiple × service_rate strips + JSON price_adjustor / state / multiple_cap overlays
File: api/supporting/support_middleware.py · middleware_interpolation_conv / _govt / _linearRBF / _gradient_boosting

Interpretable DPX (newer)
base_price = base_model.predict(features) × base_service_rate excess_price = excess_model.predict(features) × excess_service_rate final_price = base_price + excess_price + price_incentive # remit variants → price_ss / price_sa / price_aa # then level/price_adjustor overlays scaled by service_rate
Train: middleware/utils/interpretable_dpx/ · Runtime predict in support_middleware.py · Stored: Client_Coissue_Buyer_Middleware.adjustors

Aggregator margin overlay (bps)
margin = user_details.margins[buyer_id].margin / 100 # 1 bp → 0.01 price_*_wo_margin = price_* price_* = price_* − margin multiple_* = price_* / service_rate
File: api/supporting/support_pricing.py · asset_price_v3

Database & JSON storage
Store	Purpose
BaseRateSheet / RateSheet + Step + Rule	Base price & LLPA grids (Freedom)
MaSheet	SRP, BUBD, coupon, MBS price
Subsidy / StateAssignment / EFC	Subsidy, state, carry
PriceControls / GlobalExclusion	Caps/floors & kicks
RealTimeLLPA / Spec / StartMult / StripCap	Specialty matrices
Margin	Point & dollar margins
WorkFlow / PricingModel / PricingUpload	Step order & artifact bundle
Mappings (JSON)	llpa_dict_map, npts, rt matrix maps
YearlyLLPA (analytics)	Agency cash LLPAs
WholeLoanPrice	Persisted Freedom loan_price JSON
Client_Coissue_Buyer.adjustors / grid_info	Grid + SRP JSON
Client_Coissue_Buyer_Middleware.adjustors	DPX model JSON
Client_Coissue_Buyer_Par	Par rates
Client_Coissue_Tape.price	Persisted coissue prices
MSRX JSON schema documented in msrx_v2.0/Doc/json_config.md and Doc/DPX_Term.json (term buckets + sample adjustors).

Providers & external systems
Freedom providers
FNMA cash window API — fnma_contract_price / fnma_api

Freddie cash — freddie_contract_price

Refinitiv RICS — process_rics (live MBS)

Bloomberg TBA helper — Bloomberg/GetTBAPrice.py

YearlyLLPA (analytics DB) — agency LLPA

MSRX providers
Grid JSON per buyer (general_grid + SRP_*)

DPX middleware models (pickle / InterpretableDPX JSON)

Par tables — Client_Coissue_Buyer_Par

S3 model download for classic DPX pickles

Key files (every path involved)

Freedom whole-loan
Entry / orchestration

freedom/views/pricing.py, reprice.py, best_efforts.py, pre_close.py · caas/views/loan_builder/price_single.py · freedom/supporting/globals/upload.py · freedom/supporting/pricing/process/price.py · multi_workflow.py · setup/price_setup.py · get_pricing_workflows.py · pre_check.py

Base / LLPA / MA

base/base_ratesheet.py · base/ma.py · base/efc.py · base/rics.py · llpas/ratesheet.py · realtime.py · npt.py · spec.py · strip_cap.py · start_mult.py · rules/rules.py · agency/*

Adjustments / totals / controls

seller_specific/margin.py · price_adjustments/desk_incentive.py · subsidy.py · best_efforts.py · mandatory.py · extension.py · controls/price_controls*.py · exclusions.py · msr_or_srp.py · volume_caps.py · total/total_*.py · msrx/msrx.py

Models

freedom/models/pricing.py · rules_based.py · config.py · users.py (Margin) · msr.py


MSRX coissue / DPX
api/views/pricing.py · api/supporting/services/msr_pricing.py · support_pricing.py (asset_price_v3) · general_grid.py · SRP.py · support_middleware.py · support_middleware_audit_ready.py · support_par.py · static_pricing_helper.py · support_varde_pricing.py · freedom_grid_converter.py · planet_grid_converter.py · Grid_Converter.py · govt_grid_template.json

middleware/views.py · urls.py · utils/interpretable_dpx/* · utils/DPX_Model_Fit/* · utils/SPF_Generation/* · utils/msrx_polyassumption/*.json · Doc/json_config.md · Doc/DPX_Term.json

Formula storage rule of thumb
Algebra lives in Python. Numeric grids, Rule.adj values, MA/SRP sheets, buyer adjustors, and DPX model coefficients live in DB tables and JSON fields. Workflow order is WorkFlow.step (DB) with defaults in upload.py.