# COMPLETE DJANGO MODEL INVENTORY — msrx_v2.0

## Global
- Total model classes: **264** (262 AST + 2 inheritance-only concrete: `freedom.Loan`, `freedom.LoanSnapshot`)
- Empty apps: `middleware`, `bw_middleware` (placeholder `models.py` only)
- **Meta.db_table overrides:**
  - `base.APIActivityLog` → `api_activity_log`
  - `duediligence.ProgramDocumentTypeAlternate` → `duediligence_program_document_type_alternates`
- **proxy=True:** none | **managed=False:** none
- **Abstract bases:** freedom: BaseRateSheetBase, RateSheetBase, PriceControlsBase, GlobalExclusionBase; duediligence: BaseModel; caas: BaseLoan, BaseLoanNPI, BaseWholeLoan, BaseNQM, BaseSecondLien, BaseAllocationLoan, BaseEpicAPILoan, LoanSnapshotFields, LoanSnapshotForeignKeys, LoanSnapshot, WholeLoanFields, WholeLoanForeignKeys, WholeLoan
- Default PK for all models unless noted: implicit `id` AutoField
- Django default db_table pattern: `{app_label}_{modelname}`.lower()

## `msrx` — 56 models

### `Boarded_Tapes`
- path: `msrx/models/boarding_staging.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_boarded_tapes` | pk: `id (implicit AutoField)`
- cols (5): loan_ids, loan_count, buyer, generated_by, updated_at
- FK `buyer` → `MSRX_User` on_delete=CASCADE related_name=loans_buyer null=True
- JSON: none
- business: loan_ids, loan_count, buyer

### `LoanNumbers`
- path: `msrx/models/boarding_staging.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_loannumbers` | pk: `id (implicit AutoField)`
- cols (8): buyer_loan_number, seller_loan_number, burned, seller, buyer, datetime_assigned, change_request_reason, change_request_datetime
- FK `seller` → `MSRX_User` on_delete=CASCADE related_name=seller_of_loan null=True
- FK `buyer` → `MSRX_User` on_delete=CASCADE related_name=buyer_of_loan null=False
- JSON: none
- business: buyer_loan_number, seller_loan_number, seller, buyer

### `Boarding_Staging`
- path: `msrx/models/boarding_staging.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_boarding_staging` | pk: `id (implicit AutoField)`
- cols (1496): two_zero_three_k_indicator, ability_to_repay, ability_to_repay_flag, active_exceptions_when_checked, affordable_housing_indicator, aggregator_loan_number, ah_insurance_solicitation_allowed_flag, amount_paid_by_borrower … supplemental_data_date, msrx_coissue_loan, whole_loan, qc_loan, origination_loan_number, status
- FK `buyer` → `MSRX_User` on_delete=CASCADE related_name=loan_buyer null=True
- FK `seller` → `MSRX_User` on_delete=CASCADE related_name=loan_seller null=True
- FK `updated_by` → `MSRX_User` on_delete=CASCADE related_name=updated_by_user null=True
- FK `msrx_coissue_loan` → `Client_Coissue_Tape` on_delete=CASCADE related_name=boarding_staging null=True
- FK `whole_loan` → `Loan` on_delete=CASCADE related_name=boarding_staging null=True
- FK `qc_loan` → `QCLoan` on_delete=CASCADE related_name=boarding_staging null=True
- JSON: delivered_additional_parties_list, excess_fields
- status/choices: amortization_type, arm_ir_rounding_type, borrower_1_state_alpha_abbr, borrower_2_state_alpha_abbr, borrower_3_state_alpha_abbr, borrower_4_state_alpha_abbr, borrower_5_state_alpha_abbr, co_borrower_mailing_state, current_appraised_type, current_occupancy_status, development_type, disbursement_type_description_1, disbursement_type_description_10, disbursement_type_description_11, disbursement_type_description_12, disbursement_type_description_13, disbursement_type_description_14, disbursement_type_description_15, disbursement_type_description_16, disbursement_type_description_17, disbursement_type_description_18, disbursement_type_description_19, disbursement_type_description_2, disbursement_type_description_20, disbursement_type_description_3, disbursement_type_description_4, disbursement_type_description_5, disbursement_type_description_6, disbursement_type_description_7, disbursement_type_description_8, disbursement_type_description_9, document_type, flood_contract_type, heloc_indicator_status, loan_type, mailing_state, mers_id_status_code, mip_payment_plan_type, ownership_type, property_state_abbreviation, property_type, qualified_mortgage_type, state_high_cost_indicator, flood_pay_type_mismatch, hazard_pay_type_mismatch, interest_rate_exceeds_state_max, invalid_hazard_pay_type, lo_type_is_blank, loan_type_3_with_mi_data, mailing_state_contains_number, mailing_state_is_blank_or_not_in_zz_format, mailing_state_not_valid, property_not_in_licensed_state, property_state_is_blank_or_not_in_zz_format, property_state_is_not_valid, property_type_is_blank, property_type_is_invalid, property_type_mismatch, borrower_1_id_type_is_missing, borrower_2_id_type_is_missing, uw_missing_asset_statements, c_mailing_state_is_blank_or_not_in_zz_format, borrower_1_identification_type_1, borrower_1_identification_type_other_1, borrower_1_identification_type_2, borrower_1_identification_type_other_2, borrower_2_identification_type_1, borrower_2_identification_type_other_1, borrower_2_identification_type_2, borrower_2_identification_type_other_2, borrower_3_identification_type_1, borrower_3_identification_type_other_1, borrower_3_identification_type_2, borrower_3_identification_type_other_2, borrower_4_identification_type_1, borrower_4_identification_type_other_1, borrower_4_identification_type_2, borrower_4_identification_type_other_2, borrower_5_identification_type_1, borrower_5_identification_type_other_1, borrower_5_identification_type_2, borrower_5_identification_type_other_2, status
- business: aggregator_loan_number, boarding_file_delivered, boarding_file_delivered_at, buyer, counter_party_loan_number, document_type, first_time_homebuyer_flag, higher_priced_flag, investor_loan_number, loan_closing_date, loan_funding_date, loan_maturity_date, loan_purpose, loan_purpose_code, loan_type, original_loan_term, pending_document_upload, permanent_investor_code, pool_pmi_payee, pool_pmi_policy_no, purchase_price, rhs_loan_no, seller, seller_loan_number, seller_name, super_transfer_loan_number, universal_loan_indicator, escrowed_loan_without_escrow_balance, escrowed_loan_without_escrow_payment, loan_closing_date_is_blank, loan_closing_date_on_today_or_in_the_future, loan_has_both_escrow_balance_and_escrow_advance_balance, loan_is_greater_than_30_days_delinquent, loan_term_is_blank_or_zero, loan_type_3_with_mi_data, loan_with_a_negative_lien_amount, maturity_date_is_prior_to_transfer, new_loan_with_late_fee, newly_originated_loan_with_escrow_advance_balance, non_escrowed_loan_with_escrow_balance…

### `Exceptions_Buyer_Configs`
- path: `msrx/models/buyer.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_exceptions_buyer_configs` | pk: `id (implicit AutoField)`
- cols (5): buyer, seller, active_exceptions, all_exceptions, updated_at
- FK `buyer` → `MSRX_User` on_delete=CASCADE related_name=buyer_config_id null=True
- FK `seller` → `MSRX_User` on_delete=CASCADE related_name=seller_config_id null=True
- JSON: none
- business: buyer, seller

### `BuyerAxeManagement`
- path: `msrx/models/buyer.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_buyeraxemanagement` | pk: `id (implicit AutoField)`
- cols (4): name, buyer, created_at, updated_at
- FK `buyer` → `msrx.MSRX_User` on_delete=CASCADE related_name=None null=True
- JSON: none
- business: buyer

### `BuyerAxeDescription`
- path: `msrx/models/buyer.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_buyeraxedescription` | pk: `id (implicit AutoField)`
- cols (2): buyer_axe, description
- FK `buyer_axe` → `BuyerAxeManagement` on_delete=CASCADE related_name=None null=False
- JSON: none
- business: buyer_axe

### `Buyer_Par_History`
- path: `msrx/models/buyer.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_buyer_par_history` | pk: `id (implicit AutoField)`
- cols (21): client, par_fn40, par_fn30, par_fn25, par_fn20, par_fn15, par_fn10, par_gn40, par_gn30, par_gn25, par_gn20, par_gn15, par_gn10, par_arm_1, par_arm_3, par_arm_5, par_arm_7, par_arm_10, par_rate_formula, discretionary_spread, uploadtime
- FK `client` → `MSRX_User` on_delete=CASCADE related_name=None null=True
- JSON: par_rate_formula, discretionary_spread
- business: client

### `Client_Coissue_Seller`
- path: `msrx/models/coissue.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_client_coissue_seller` | pk: `id (implicit AutoField)`
- cols (14): client, correspondent, tape_name, uploadtime, loancount, upb, status, transfer_date, status_details, updated_at, execution, psa_deal, whole_loan_tape, pricer
- FK `client` → `MSRX_User` on_delete=CASCADE related_name=tapes_seller null=True
- FK `correspondent` → `MSRX_User` on_delete=CASCADE related_name=tapes_correspondent null=True
- FK `psa_deal` → `PSADeals` on_delete=PROTECT related_name=coissue_psa_deals null=True
- FK `whole_loan_tape` → `freedom.Tape` on_delete=PROTECT related_name=msrx_tape null=True
- FK `pricer` → `User` on_delete=SET_NULL related_name=None null=True
- JSON: status_details
- status/choices: status, status_details
- business: client, correspondent, tape_name, loancount, transfer_date, psa_deal, whole_loan_tape, pricer

### `Client_Coissue_Tape`
- path: `msrx/models/coissue.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_client_coissue_tape` | pk: `id (implicit AutoField)`
- cols (60): tape_loan_id, tapeinfo, agency, remit, service_rate, loan_type, loan_balance, orig_loan_balance … commit_cycle, enote, insurance, price_incentive, psa_deal, nmls_id
- FK `tapeinfo` → `Client_Coissue_Seller` on_delete=CASCADE related_name=view_loans null=True
- FK `transfer` → `EMResource` on_delete=CASCADE related_name=None null=True
- FK `acquisition_id` → `msrx.MSRX_User` on_delete=PROTECT related_name=None null=True
- FK `commit_cycle` → `Client_Commit_Cycle` on_delete=PROTECT related_name=loans null=True
- FK `psa_deal` → `PSADeals` on_delete=PROTECT related_name=coissue_psa_deal_loans null=True
- JSON: price, commitment
- status/choices: loan_type, title_option(choices=title_choices), state, product_type, property_type, doc_type
- business: tape_loan_id, tapeinfo, loan_type, loan_balance, orig_loan_balance, price, commitment, aggregator_loan_id, boarding_date, transfer, agg_loan_num, loan_group, agency_commit_num, agency_commit_date, agency_commit_exp, expected_price, commit_cycle, price_incentive, psa_deal

### `Client_Coissue_Seller_Resell`
- path: `msrx/models/coissue.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_client_coissue_seller_resell` | pk: `id (implicit AutoField)`
- cols (6): orig_tape_id, uploadtime, status, status_details, updated_at, pricer
- FK `orig_tape_id` → `Client_Coissue_Seller` on_delete=CASCADE related_name=seller_resell null=True
- FK `pricer` → `User` on_delete=SET_NULL related_name=None null=True
- JSON: status_details
- status/choices: status, status_details
- business: orig_tape_id, pricer

### `Client_Coissue_Tape_Resell`
- path: `msrx/models/coissue.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_client_coissue_tape_resell` | pk: `id (implicit AutoField)`
- cols (60): tape_loan_id, tapeinfo, agency, remit, service_rate, loan_type, loan_balance, orig_loan_balance … commit_cycle, enote, insurance, price_incentive, psa_deal, nmls_id
- FK `tapeinfo` → `Client_Coissue_Seller_Resell` on_delete=CASCADE related_name=tape_resell null=True
- FK `acquisition_id` → `MSRX_User` on_delete=PROTECT related_name=None null=True
- FK `real_transfer` → `EMResource` on_delete=CASCADE related_name=None null=True
- FK `commit_cycle` → `Client_Commit_Cycle` on_delete=PROTECT related_name=resell_loans null=True
- FK `psa_deal` → `PSADeals` on_delete=PROTECT related_name=coissue_psa_deal_resell_loans null=True
- JSON: price, commitment
- status/choices: loan_type, title_option(choices=title_choices), state, product_type, property_type, doc_type
- business: tape_loan_id, tapeinfo, loan_type, loan_balance, orig_loan_balance, price, commitment, aggregator_loan_id, boarding_date, agg_loan_num, loan_group, agency_commit_num, agency_commit_date, agency_commit_exp, expected_price, real_transfer, commit_cycle, price_incentive, psa_deal

### `Client_Coissue_Seller_Deleted`
- path: `msrx/models/coissue.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_client_coissue_seller_deleted` | pk: `id (implicit AutoField)`
- cols (11): client, orig_tape_id, tape_name, uploadtime, loancount, upb, status, transfer_date, status_details, updated_at, pricer
- FK `client` → `MSRX_User` on_delete=CASCADE related_name=None null=True
- FK `pricer` → `User` on_delete=SET_NULL related_name=None null=True
- JSON: status_details
- status/choices: status, status_details
- business: client, orig_tape_id, tape_name, loancount, transfer_date, pricer

### `Client_Coissue_Tape_Deleted`
- path: `msrx/models/coissue.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_client_coissue_tape_deleted` | pk: `id (implicit AutoField)`
- cols (59): tape_loan_id, tapeinfo, agency, remit, service_rate, loan_type, loan_balance, orig_loan_balance … commit_cycle, enote, insurance, price_incentive, psa_deal, nmls_id
- FK `tapeinfo` → `Client_Coissue_Seller_Deleted` on_delete=CASCADE related_name=None null=True
- FK `commit_cycle` → `Client_Commit_Cycle` on_delete=PROTECT related_name=deleted_loans null=True
- FK `psa_deal` → `PSADeals` on_delete=PROTECT related_name=coissue_psa_deal_deleted_loans null=True
- JSON: price, commitment
- status/choices: loan_type, title_option(choices=title_choices), state, product_type, property_type, doc_type
- business: tape_loan_id, tapeinfo, loan_type, loan_balance, orig_loan_balance, price, commitment, aggregator_loan_id, boarding_date, agg_loan_num, loan_group, agency_commit_num, agency_commit_date, agency_commit_exp, expected_price, commit_cycle, price_incentive, psa_deal

### `Client_Coissue_Tape_Updated`
- path: `msrx/models/coissue.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_client_coissue_tape_updated` | pk: `id (implicit AutoField)`
- cols (64): original_id, tapeinfo, tape_loan_id, agency, remit, service_rate, loan_type, loan_balance … insurance, price_incentive, psa_deal, seller_pa_summary, investor_pa_summary, nmls_id
- FK `original_id` → `Client_Coissue_Tape` on_delete=CASCADE related_name=updated_loan null=True
- FK `tapeinfo` → `Client_Coissue_Seller` on_delete=CASCADE related_name=None null=True
- FK `acquisition_id` → `MSRX_User` on_delete=PROTECT related_name=None null=True
- FK `commit_cycle` → `Client_Commit_Cycle` on_delete=PROTECT related_name=updated_loans null=True
- FK `psa_deal` → `PSADeals` on_delete=PROTECT related_name=coissue_psa_deal_updated_loans null=True
- FK `seller_pa_summary` → `commitrecon.PA_Summary` on_delete=SET_NULL related_name=seller_pa_summary null=True
- FK `investor_pa_summary` → `commitrecon.PA_Summary` on_delete=SET_NULL related_name=investor_pa_summary null=True
- JSON: price, commitment, resell_price, resell_commitment
- status/choices: loan_type, title_option(choices=title_choices), state, product_type, property_type, doc_type
- business: tapeinfo, tape_loan_id, loan_type, loan_balance, orig_loan_balance, price, commitment, resell_price, resell_commitment, aggregator_loan_id, boarding_date, agg_loan_num, loan_group, agency_commit_num, agency_commit_date, agency_commit_exp, expected_price, commit_cycle, price_incentive, psa_deal, seller_pa_summary, investor_pa_summary

### `Client_Coissue_Buyer`
- path: `msrx/models/coissue.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_client_coissue_buyer` | pk: `id (implicit AutoField)`
- cols (13): client, grid_name, grid_info, comment, counterparty, uploadtime, inuse, status, updated_at, coissue, valid_until, adjustors, s3_url
- FK `client` → `MSRX_User` on_delete=CASCADE related_name=None null=True
- JSON: grid_info, counterparty, adjustors
- status/choices: status
- business: client

### `Client_Coissue_Buyer_Criteria`
- path: `msrx/models/coissue.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_client_coissue_buyer_criteria` | pk: `id (implicit AutoField)`
- cols (7): buyer, seller, criteria, comment, inuse, uploadtime, updated_at
- FK `buyer` → `MSRX_User` on_delete=CASCADE related_name=buyer null=True
- FK `seller` → `MSRX_User` on_delete=CASCADE related_name=seller null=True
- JSON: criteria
- business: buyer, seller

### `Client_Coissue_Buyer_Middleware`
- path: `msrx/models/coissue.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_client_coissue_buyer_middleware` | pk: `id (implicit AutoField)`
- cols (28): client, conv_30_model, conv_15_model, fha_30_model, fha_15_model, va_30_model, va_15_model, usda_30_model, usda_15_model, seasoned_conv_30_model, seasoned_conv_15_model, seasoned_gnma_30_model, seasoned_gnma_15_model, model_folder, comment, adjustors, seasoned_adjustors, counterparty, uploadtime, inuse, open_to_composite_api, updated_at, coissue, valid_until, task, build_metrics, audit_ready, audit_ready_model
- FK `client` → `MSRX_User` on_delete=CASCADE related_name=None null=True
- FK `task` → `Background_Task` on_delete=PROTECT related_name=None null=True
- JSON: adjustors, seasoned_adjustors, counterparty, build_metrics, audit_ready_model
- status/choices: conv_30_model, conv_15_model, fha_30_model, fha_15_model, va_30_model, va_15_model, usda_30_model, usda_15_model, seasoned_conv_30_model, seasoned_conv_15_model, seasoned_gnma_30_model, seasoned_gnma_15_model, model_folder, audit_ready_model
- business: client

### `Client_Coissue_Buyer_Par`
- path: `msrx/models/coissue.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_client_coissue_buyer_par` | pk: `id (implicit AutoField)`
- cols (9): client, product_type, loan_type, term, par_rate_formula, comment, uploadtime, inuse, log
- FK `client` → `MSRX_User` on_delete=CASCADE related_name=None null=True
- JSON: par_rate_formula, log
- status/choices: product_type, loan_type
- business: client, loan_type

### `EmailSubject`
- path: `msrx/models/email.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_emailsubject` | pk: `id (implicit AutoField)`
- cols (2): email_type, subject
- relations: none
- JSON: none
- status/choices: email_type(choices=email_choices)

### `EmailMonitorAdminList`
- path: `msrx/models/email.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_emailmonitoradminlist` | pk: `id (implicit AutoField)`
- cols (2): name, email
- relations: none
- JSON: none

### `InternalNotificationStore`
- path: `msrx/models/email.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_internalnotificationstore` | pk: `id (implicit AutoField)`
- cols (3): job_name, email_notification, internal_emails
- relations: none
- JSON: none

### `Market`
- path: `msrx/models/market.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_market` | pk: `id (implicit AutoField)`
- cols (41): cc102_30y, cc102_15y, pss_fn30, pss_fn15, pss_gn30, pss_gn15, ussw2, ussw5 … fncr3090, fncr1510, fncr1530, fncr1590, prpy_elbow_base, uploadtime
- relations: none
- JSON: none

### `MarketTempRTO`
- path: `msrx/models/market.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_markettemprto` | pk: `id (implicit AutoField)`
- cols (55): cc102_30y, cc102_15y, cc102_30y_gn, cc102_15y_gn, cc100_30y, cc100_15y, cc100_30y_gn, cc100_15y_gn … fncr1590, fncr3010, fncr3030, fncr3060, fncr3090, uploadtime
- relations: none
- JSON: none

### `Background_Task`
- path: `msrx/models/misc.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_background_task` | pk: `id (implicit AutoField)`
- cols (4): status, details, start_date, completed_date
- relations: none
- JSON: details
- status/choices: status(choices=status_choices)

### `Client_Commit_Cycle`
- path: `msrx/models/misc.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_client_commit_cycle` | pk: `id (implicit AutoField)`
- cols (11): start_date, end_date, loan_count_cap, upb_cap, priced_count, priced_upb, committed_count, committed_upb, cap, buyer, seller
- FK `buyer` → `MSRX_User` on_delete=CASCADE related_name=list_buyers null=True
- FK `seller` → `MSRX_User` on_delete=CASCADE related_name=list_sellers null=True
- JSON: none
- business: loan_count_cap, priced_count, priced_upb, committed_count, committed_upb, buyer, seller

### `OneTimePasscode`
- path: `msrx/models/misc.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_onetimepasscode` | pk: `id (implicit AutoField)`
- cols (3): client, passcode, updated_at
- FK `client` → `User` on_delete=CASCADE related_name=None null=True
- JSON: none
- business: client

### `SifmaSettlementDates`
- path: `msrx/models/misc.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_sifmasettlementdates` | pk: `id (implicit AutoField)`
- cols (6): settlement_month, date_type, class_a, class_b, class_c, class_d
- relations: none
- JSON: none
- status/choices: date_type(choices=SifmaSettlementDateType.choices)

### `LeaderElection`
- path: `msrx/models/misc.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_leaderelection` | pk: `id (implicit AutoField)`
- cols (3): instance_id, last_updated_time, is_leader
- relations: none
- JSON: none

### `SFTPConfig`
- path: `msrx/models/misc.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_sftpconfig` | pk: `id (implicit AutoField)`
- cols (11): msrx_user, path, path_backup, username, password, openssh, app_label, display_name, port, create_time, last_updated_time
- FK `msrx_user` → `msrx.MSRX_User` on_delete=CASCADE related_name=None null=True
- JSON: none

### `EnvironmentVariable`
- path: `msrx/models/misc.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_environmentvariable` | pk: `id (implicit AutoField)`
- cols (7): key, settings_key, value, created_at, updated_at, description, active
- relations: none
- JSON: none

### `SingleFamilyCode`
- path: `msrx/models/misc.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_singlefamilycode` | pk: `id (implicit AutoField)`
- cols (6): code, description, details, agency, type, delivery_type
- relations: none
- JSON: none
- status/choices: type, delivery_type

### `PlatformConfiguration`
- path: `msrx/models/platform.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_platformconfiguration` | pk: `id (implicit AutoField)`
- cols (15): hostname, company_name, company_website, portal_name, site_header, support_email, click_wrap, mfa, updated_at, email_monitor_inbox, whole_loan_inbox, epic_user_alias, logo, header_logo, sidepanel_logo
- FK `email_monitor_inbox` → `MonitoredMailbox` on_delete=SET_NULL related_name=platform_config null=True
- FK `whole_loan_inbox` → `MonitoredMailbox` on_delete=SET_NULL related_name=wl_platform_config null=True
- JSON: none
- business: whole_loan_inbox

### `SidePanels`
- path: `msrx/models/platform.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_sidepanels` | pk: `id (implicit AutoField)`
- cols (8): updated_at, created_at, user_role, aggregator_flag, aggregator_seller_flag, side_panel_name, side_panel_items, platformconfig
- FK `platformconfig` → `PlatformConfiguration` on_delete=CASCADE related_name=side_panels null=True
- JSON: side_panel_items
- status/choices: user_role(choices=user_role_choices)
- business: aggregator_flag, aggregator_seller_flag

### `FrontendComponents`
- path: `msrx/models/platform.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_frontendcomponents` | pk: `id (implicit AutoField)`
- cols (2): component_name, elements
- relations: none
- JSON: none

### `FrontendComponentConfigs`
- path: `msrx/models/platform.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_frontendcomponentconfigs` | pk: `id (implicit AutoField)`
- cols (5): component, platform, msrx_user, auth_user, active_elements
- FK `component` → `FrontendComponents` on_delete=CASCADE related_name=None null=False
- FK `platform` → `PlatformConfiguration` on_delete=CASCADE related_name=None null=True
- FK `msrx_user` → `MSRX_User` on_delete=CASCADE related_name=None null=True
- FK `auth_user` → `User` on_delete=CASCADE related_name=None null=True
- JSON: none

### `PSADeals`
- path: `msrx/models/psa.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_psadeals` | pk: `id (implicit AutoField)`
- cols (15): date, deal_name, settlement_date, sale_date, servicing_transfer_date, notes, temporary, active_dates, holdbacks, loi_pdf_path, psa_pdf_path, seller, buyer, platform, inuse
- FK `seller` → `MSRX_User` on_delete=CASCADE related_name=seller_deals null=True
- FK `buyer` → `MSRX_User` on_delete=CASCADE related_name=buyer_deals null=True
- FK `platform` → `PlatformConfiguration` on_delete=CASCADE related_name=None null=True
- JSON: holdbacks, loi_pdf_path, psa_pdf_path
- business: deal_name, servicing_transfer_date, seller, buyer

### `PSATerms`
- path: `msrx/models/psa.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_psaterms` | pk: `id (implicit AutoField)`
- cols (9): cost_fee_name, amount, type, paid_by, occurence, recipient, used, deal, adjustments
- FK `deal` → `PSADeals` on_delete=CASCADE related_name=payer_psa_terms null=True
- JSON: adjustments
- status/choices: type(choices=type_choices), paid_by(choices=paid_by_choices), occurence(choices=occurence_choices), recipient(choices=paid_by_choices)
- business: deal

### `Client_Seasoned_Committable_Summary`
- path: `msrx/models/seasoned.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_client_seasoned_committable_summary` | pk: `id (implicit AutoField)`
- cols (14): wala, wam, wac, age, fico, ltv, price, serv_fee, note_rate, mult, market_value, avg_upb, loancount, upb
- relations: none
- JSON: none
- business: price, loancount

### `Client_Seasoned_Eligible_Summary`
- path: `msrx/models/seasoned.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_client_seasoned_eligible_summary` | pk: `id (implicit AutoField)`
- cols (14): wala, wam, wac, age, fico, ltv, price, serv_fee, note_rate, mult, market_value, avg_upb, upb, loancount
- relations: none
- JSON: none
- business: price, loancount

### `Client_Seasoned_Seller`
- path: `msrx/models/seasoned.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_client_seasoned_seller` | pk: `id (implicit AutoField)`
- cols (28): client, committable, eligible, tape_name, uploadtime, loancount, upb, status, transfer_date, status_details, updated_at, execution, wala, wam, wac, age, fico, ltv, price, serv_fee, note_rate, mult, market_value, avg_upb, eligible_summary, committable_summary, psa_deal, pricer
- FK `client` → `MSRX_User` on_delete=CASCADE related_name=None null=True
- FK `committable` → `self` on_delete=CASCADE related_name=committable_original_tape null=True
- FK `eligible` → `self` on_delete=CASCADE related_name=eligible_original_tape null=True
- FK `eligible_summary` → `Client_Seasoned_Eligible_Summary` on_delete=CASCADE related_name=tape_from_eligible null=True
- FK `committable_summary` → `Client_Seasoned_Committable_Summary` on_delete=CASCADE related_name=tape_from_committable null=True
- FK `psa_deal` → `PSADeals` on_delete=PROTECT related_name=seasoned_psa_deals null=True
- FK `pricer` → `User` on_delete=SET_NULL related_name=None null=True
- JSON: status_details
- status/choices: status, status_details
- business: client, committable, tape_name, loancount, transfer_date, price, committable_summary, psa_deal, pricer

### `Client_Seasoned_Tape`
- path: `msrx/models/seasoned.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_client_seasoned_tape` | pk: `id (implicit AutoField)`
- cols (60): tape_loan_id, tapeinfo, agency, remit, service_rate, loan_type, loan_balance, orig_loan_balance … commit_cycle, pool_id, shock_scenarios, insurance, enote, price_incentive
- FK `tapeinfo` → `Client_Seasoned_Seller` on_delete=CASCADE related_name=None null=True
- FK `transfer` → `EMResource` on_delete=CASCADE related_name=None null=True
- FK `commit_cycle` → `Client_Commit_Cycle` on_delete=SET_NULL related_name=list_commit_cycle null=True
- JSON: price, commitment, shock_scenarios
- status/choices: loan_type, title_option(choices=title_choices), state, product_type, property_type, doc_type
- business: tape_loan_id, tapeinfo, loan_type, loan_balance, orig_loan_balance, price, commitment, aggregator_loan_id, boarding_date, transfer, agg_loan_num, loan_group, agency_commit_num, agency_commit_date, agency_commit_exp, expected_price, commit_cycle, pool_id, price_incentive

### `Client_Seasoned_Seller_Resell`
- path: `msrx/models/seasoned.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_client_seasoned_seller_resell` | pk: `id (implicit AutoField)`
- cols (6): orig_tape_id, uploadtime, status, status_details, updated_at, pricer
- FK `orig_tape_id` → `Client_Seasoned_Seller` on_delete=CASCADE related_name=None null=True
- FK `pricer` → `User` on_delete=SET_NULL related_name=None null=True
- JSON: status_details
- status/choices: status, status_details
- business: orig_tape_id, pricer

### `Client_Seasoned_Tape_Resell`
- path: `msrx/models/seasoned.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_client_seasoned_tape_resell` | pk: `id (implicit AutoField)`
- cols (58): tape_loan_id, tapeinfo, agency, remit, service_rate, loan_type, loan_balance, orig_loan_balance … delinquency, forbearance, commit_cycle, insurance, enote, price_incentive
- FK `tapeinfo` → `Client_Seasoned_Seller_Resell` on_delete=CASCADE related_name=None null=True
- FK `transfer` → `EMResource` on_delete=CASCADE related_name=None null=True
- FK `commit_cycle` → `Client_Commit_Cycle` on_delete=PROTECT related_name=seasoned_resell_loans null=True
- JSON: price, commitment
- status/choices: loan_type, title_option(choices=title_choices), state, product_type, property_type, doc_type
- business: tape_loan_id, tapeinfo, loan_type, loan_balance, orig_loan_balance, price, commitment, aggregator_loan_id, boarding_date, transfer, agg_loan_num, loan_group, agency_commit_num, agency_commit_date, agency_commit_exp, expected_price, commit_cycle, price_incentive

### `Client_Seasoned_Seller_Deleted`
- path: `msrx/models/seasoned.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_client_seasoned_seller_deleted` | pk: `id (implicit AutoField)`
- cols (23): client, tape_name, uploadtime, loancount, upb, status, transfer_date, status_details, updated_at, execution, wala, wam, wac, age, fico, ltv, price, serv_fee, note_rate, mult, market_value, avg_upb, pricer
- FK `client` → `MSRX_User` on_delete=CASCADE related_name=None null=True
- FK `pricer` → `User` on_delete=SET_NULL related_name=None null=True
- JSON: status_details
- status/choices: status, status_details
- business: client, tape_name, loancount, transfer_date, price, pricer

### `Client_Seasoned_Tape_Deleted`
- path: `msrx/models/seasoned.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_client_seasoned_tape_deleted` | pk: `id (implicit AutoField)`
- cols (60): tape_loan_id, tapeinfo, agency, remit, service_rate, loan_type, loan_balance, orig_loan_balance … commit_cycle, pool_id, shock_scenarios, insurance, enote, price_incentive
- FK `tapeinfo` → `Client_Seasoned_Seller_Deleted` on_delete=CASCADE related_name=None null=True
- FK `transfer` → `EMResource` on_delete=CASCADE related_name=None null=True
- FK `commit_cycle` → `Client_Commit_Cycle` on_delete=PROTECT related_name=seasoned_deleted_loans null=True
- JSON: price, commitment, shock_scenarios
- status/choices: loan_type, title_option(choices=title_choices), state, product_type, property_type, doc_type
- business: tape_loan_id, tapeinfo, loan_type, loan_balance, orig_loan_balance, price, commitment, aggregator_loan_id, boarding_date, transfer, agg_loan_num, loan_group, agency_commit_num, agency_commit_date, agency_commit_exp, expected_price, commit_cycle, pool_id, price_incentive

### `PriceTestTape`
- path: `msrx/models/test_price.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_pricetesttape` | pk: `id (implicit AutoField)`
- cols (10): client, tape_name, uploadtime, loancount, upb, status, transfer_date, status_details, updated_at, execution
- FK `client` → `MSRX_User` on_delete=CASCADE related_name=None null=True
- JSON: status_details
- status/choices: status, status_details
- business: client, tape_name, loancount, transfer_date

### `PriceTestLoan`
- path: `msrx/models/test_price.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_pricetestloan` | pk: `id (implicit AutoField)`
- cols (54): tape_loan_id, tape, agency, remit, service_rate, loan_type, loan_balance, orig_loan_balance … delivery_month, expected_price, insurance, enote, price_incentive, nmls_id
- FK `tape` → `PriceTestTape` on_delete=CASCADE related_name=None null=True
- JSON: price, commitment
- status/choices: loan_type, title_option(choices=title_choices), state, product_type, property_type, doc_type
- business: tape_loan_id, tape, loan_type, loan_balance, orig_loan_balance, price, commitment, aggregator_loan_id, boarding_date, loan_group, agency_commit_num, agency_commit_date, agency_commit_exp, expected_price, price_incentive

### `TestPricing`
- path: `msrx/models/test_price.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_testpricing` | pk: `id (implicit AutoField)`
- cols (7): model, loan, tape, exclusion, par, pricing_data, timestamp
- FK `model` → `Client_Coissue_Buyer` on_delete=CASCADE related_name=test_price_grid null=True
- FK `loan` → `PriceTestLoan` on_delete=CASCADE related_name=test_price null=True
- FK `tape` → `PriceTestTape` on_delete=CASCADE related_name=test_price_tape null=True
- JSON: pricing_data
- status/choices: model
- business: loan, tape

### `User_Activity_Log`
- path: `msrx/models/user.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_user_activity_log` | pk: `id (implicit AutoField)`
- cols (8): user, updated_at, activity_method, activity_name, parameters, success, message, other
- FK `user` → `User` on_delete=CASCADE related_name=None null=True
- JSON: other

### `MSRX_User`
- path: `msrx/models/user.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_msrx_user` | pk: `id (implicit AutoField)`
- cols (65): user, client_name, user_role, counterparty, user_details, valuation_assumptions, additional_emails, last_password_change … correspondent, srp_provider, platform, qc_company, has_epic_api_access, wl_ratesheet_check
- O2O `user` → `User` on_delete=CASCADE related_name=None null=True
- FK `haf` → `freedom.HedgeAdvisoryFund` on_delete=CASCADE related_name=sellers null=True
- FK `branch` → `freedom.Branch` on_delete=CASCADE related_name=related_agg_seller null=True
- FK `price_class` → `freedom.PriceClass` on_delete=CASCADE related_name=None null=True
- M2M `linked_buyers` → `self` on_delete=None related_name=root_buyer null=None
- M2M `aggregated_buyers` → `self` on_delete=None related_name=root_aggregator null=None
- FK `correspondent` → `self` on_delete=CASCADE related_name=investors null=True
- FK `srp_provider` → `self` on_delete=CASCADE related_name=srp_recipients null=True
- FK `platform` → `PlatformConfiguration` on_delete=CASCADE related_name=None null=True
- FK `qc_company` → `duediligence.Company` on_delete=CASCADE related_name=qc_users null=True
- JSON: counterparty, user_details, valuation_assumptions, side_panel_items
- status/choices: fnma_execution_type(choices=FNMA_EXECUTION_TYPE_CHOICES), fhlmc_execution_type(choices=FHLMC_EXECUTION_TYPE_CHOICES)
- business: client_name, fnma_commitment_period, fhlmc_commitment_period, aggregator_flag, aggregator_seller_flag, correspondent_buyer_flag, selleracqidprefix, boardingfee, fnmasellernumber, fhlmcsellernumber, price_class, investor_number, wl_commit_duplicate_id_check, wl_investor_active, linked_buyers, aggregated_buyers, correspondent

### `MSRX_User_additional`
- path: `msrx/models/user.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_msrx_user_additional` | pk: `id (implicit AutoField)`
- cols (2): django_user, msrx_user
- FK `django_user` → `User` on_delete=CASCADE related_name=linked_agg null=True
- FK `msrx_user` → `MSRX_User` on_delete=CASCADE related_name=linked_auth_users null=True
- JSON: none

### `Client_Aggregator_Seller`
- path: `msrx/models/user.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_client_aggregator_seller` | pk: `id (implicit AutoField)`
- cols (10): user, seller_code, loan_origination_system, pricing_engine, hedge_advisor, subservicer, fnma_seller_servicer_number, fhlmc_seller_servicer_number, gnma_seller_servicer_number, aggregator
- O2O `user` → `MSRX_User` on_delete=CASCADE related_name=aggregator_seller null=True
- FK `aggregator` → `MSRX_User` on_delete=CASCADE related_name=agg_sellers null=True
- JSON: none
- business: seller_code, loan_origination_system, fnma_seller_servicer_number, fhlmc_seller_servicer_number, gnma_seller_servicer_number, aggregator

### `Client_Aggregator_Seller_Login`
- path: `msrx/models/user.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_client_aggregator_seller_login` | pk: `id (implicit AutoField)`
- cols (9): seller, user, phone_number, access_view, access_pricing, access_commit, access_exception, last_password_change, reset_link_last_sent
- FK `seller` → `Client_Aggregator_Seller` on_delete=CASCADE related_name=None null=True
- O2O `user` → `User` on_delete=CASCADE related_name=None null=True
- JSON: none
- business: seller, access_commit

### `AggregatorStore`
- path: `msrx/models/user.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_aggregatorstore` | pk: `id (implicit AutoField)`
- cols (7): aggregator, doc_name, doc_type, file, created_at, updated_at, sellers
- FK `aggregator` → `msrx.MSRX_User` on_delete=CASCADE related_name=None null=False
- M2M `sellers` → `Client_Aggregator_Seller` on_delete=None related_name=aggregator_store_seller null=None
- JSON: file
- status/choices: doc_type
- business: aggregator, sellers

### `Linked_Buyers`
- path: `msrx/models/user.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_linked_buyers` | pk: `id (implicit AutoField)`
- cols (3): root, linked, aggregator
- FK `root` → `MSRX_User` on_delete=CASCADE related_name=buyer_root null=True
- FK `linked` → `MSRX_User` on_delete=CASCADE related_name=buyer_linked null=True
- FK `aggregator` → `MSRX_User` on_delete=CASCADE related_name=aggregator_root null=True
- JSON: none
- business: aggregator

### `whole_loan_tape`
- path: `msrx/models/whole_loan.py` | bases: `['models.Model']` | label: `msrx` | table: `msrx_whole_loan_tape` | pk: `id (implicit AutoField)`
- cols (63): tapeinfo, tape_loan_id, agency, remit, service_rate, loan_type, loan_balance, note_rate … note_date, doc_type, delivery_month, expected_price, sfc_fnma, ifi_fhlmc
- FK `tapeinfo` → `Client_Coissue_Seller` on_delete=CASCADE related_name=wl_tape null=True
- JSON: price, commitment, resell_price, resell_commitment
- status/choices: loan_type, state, underwriting_risk_asscess_type, product_type, property_type, doc_type
- business: tapeinfo, tape_loan_id, loan_type, loan_balance, price, commitment, resell_price, resell_commitment, aggregator_loan_id, boarding_date, agg_loan_num, loan_group, agency_commit_num, agency_commit_date, agency_commit_exp, expected_price

## `freedom` — 67 models

### `PricingModel`
- path: `freedom/models/base.py` | bases: `['Model']` | label: `freedom` | table: `freedom_pricingmodel` | pk: `id (implicit AutoField)`
- cols (4): client, inuse, uploadtime, name
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=None null=True
- JSON: none
- business: client

### `BaseRateSheetBase` **[ABSTRACT]**
- path: `freedom/models/base.py` | bases: `['Model']` | label: `freedom` | table: `freedom_baseratesheetbase` | pk: `id (implicit AutoField)`
- cols (3): name, inuse, uploadtime
- relations: none
- JSON: none

### `RateSheetBase` **[ABSTRACT]**
- path: `freedom/models/base.py` | bases: `['Model']` | label: `freedom` | table: `freedom_ratesheetbase` | pk: `id (implicit AutoField)`
- cols (3): name, inuse, uploadtime
- relations: none
- JSON: none

### `PriceControlsBase` **[ABSTRACT]**
- path: `freedom/models/base.py` | bases: `['Model']` | label: `freedom` | table: `freedom_pricecontrolsbase` | pk: `id (implicit AutoField)`
- cols (3): name, inuse, uploadtime
- relations: none
- JSON: none

### `GlobalExclusionBase` **[ABSTRACT]**
- path: `freedom/models/base.py` | bases: `['Model']` | label: `freedom` | table: `freedom_globalexclusionbase` | pk: `id (implicit AutoField)`
- cols (3): name, inuse, uploadtime
- relations: none
- JSON: none

### `WorkFlow`
- path: `freedom/models/config.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_workflow` | pk: `id (implicit AutoField)`
- cols (4): client, index, inuse, step
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=None null=False
- JSON: none
- status/choices: step(choices=<ListComp>)
- business: client

### `PricingUpload`
- path: `freedom/models/config.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_pricingupload` | pk: `id (implicit AutoField)`
- cols (4): client, index, inuse, step
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=None null=False
- JSON: none
- status/choices: step(choices=<ListComp>)
- business: client

### `CostBasis`
- path: `freedom/models/cost_basis.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_costbasis` | pk: `id (implicit AutoField)`
- cols (6): selected, allocated, investor, buyer, loan, target_margin
- FK `investor` → `MSRX_User` on_delete=CASCADE related_name=investor_costbases null=True
- FK `buyer` → `MSRX_User` on_delete=CASCADE related_name=buyer_costbases null=True
- FK `loan` → `Loan` on_delete=CASCADE related_name=costbases null=True
- JSON: none
- business: investor, buyer, loan

### `CRAInfo`
- path: `freedom/models/cra.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_crainfo` | pk: `id (implicit AutoField)`
- cols (28): loan, success, failure_response, request_transaction_id, transaction_datetime, address_line_text, census_tract_id, city_name, core_based_statistical_area_code, county_name, disaster_area_census_tract_ind, fips_county_code, fips_state_numeric_code, high_cost_area_ind, high_needs_rural_region_eligiblity_and_qualified_ind, low_income_census_tract_ind, minority_pop_census_tract_ind, minority_pop_census_tract_percent, postal_code, rural_area_ind, state_code, ami_effective_date, eighty_percent_hud_median_income_amt, fifty_percent_hud_median_income_amt, home_possible_income_limit_amt, hundred_and_twenty_percent_hud_median_income_amt, hundred_percent_hud_median_income_amt, refi_possible_income_limit_amt
- FK `loan` → `Loan` on_delete=CASCADE related_name=cra_info null=False
- JSON: failure_response
- status/choices: fips_state_numeric_code, state_code
- business: loan

### `FieldEnumConfig`
- path: `freedom/models/field_enum.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_fieldenumconfig` | pk: `id (implicit AutoField)`
- cols (4): user, platform, user_role, active
- FK `user` → `msrx.MSRX_User` on_delete=CASCADE related_name=wl_field_enum_config null=True
- FK `platform` → `msrx.PlatformConfiguration` on_delete=CASCADE related_name=wl_field_enum_config null=True
- JSON: none

### `FieldEnumFunction`
- path: `freedom/models/field_enum.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_fieldenumfunction` | pk: `id (implicit AutoField)`
- cols (4): field, function, order, config
- FK `config` → `FieldEnumConfig` on_delete=CASCADE related_name=func null=True
- JSON: none

### `FnmaUpdateSettings`
- path: `freedom/models/fnma_update_settings.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_fnmaupdatesettings` | pk: `id (implicit AutoField)`
- cols (7): client, update_interval_hours, last_update_utc, rate_sheet_api_key, inuse, fnma_client_id, fnma_client_secret
- O2O `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=fnma_update_settings null=False
- JSON: none
- business: client, fnma_client_id, fnma_client_secret

### `IncomingMappingField`
- path: `freedom/models/incoming_mapping.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_incomingmappingfield` | pk: `id (implicit AutoField)`
- cols (8): fl_field, use_match, py_type, threshold, client, source, qc_field, inherit_enums_from
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=wl_incoming_mapping_fields null=True
- FK `qc_field` → `Field` on_delete=CASCADE related_name=maps_to_wl_fields null=True
- FK `inherit_enums_from` → `self` on_delete=SET_NULL related_name=inherited_by null=True
- JSON: none
- status/choices: py_type
- business: client

### `IncomingMappingValue`
- path: `freedom/models/incoming_mapping.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_incomingmappingvalue` | pk: `id (implicit AutoField)`
- cols (4): enum, official, change_to, field
- FK `change_to` → `self` on_delete=SET_NULL related_name=change_from null=True
- FK `field` → `IncomingMappingField` on_delete=CASCADE related_name=values null=True
- JSON: none

### `IncomingMappingRule`
- path: `freedom/models/incoming_mapping.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_incomingmappingrule` | pk: `id (implicit AutoField)`
- cols (2): enum, field
- FK `field` → `IncomingMappingField` on_delete=CASCADE related_name=multi_input_rules null=True
- JSON: none

### `IncomingMappingParams`
- path: `freedom/models/incoming_mapping.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_incomingmappingparams` | pk: `id (implicit AutoField)`
- cols (3): output, input_field, input_value
- FK `output` → `IncomingMappingRule` on_delete=CASCADE related_name=inputs null=True
- FK `input_field` → `IncomingMappingField` on_delete=CASCADE related_name=multi_input_params null=True
- FK `input_value` → `IncomingMappingValue` on_delete=CASCADE related_name=multi_input_params null=True
- JSON: none

### `Log`
- path: `freedom/models/logs.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_log` | pk: `id (implicit AutoField)`
- cols (11): auth, client, time, method, route, success, message, details, body, response, info
- FK `auth` → `User` on_delete=PROTECT related_name=None null=True
- FK `client` → `msrx.MSRX_User` on_delete=PROTECT related_name=None null=True
- JSON: info
- business: client

### `EpicRecord`
- path: `freedom/models/logs.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_epicrecord` | pk: `id (implicit AutoField)`
- cols (14): auth, client, time, method, epic_route, success, body, error, response, alias_user, info, epic_loan_key, change_success, status_code
- FK `auth` → `User` on_delete=PROTECT related_name=None null=True
- FK `client` → `msrx.MSRX_User` on_delete=PROTECT related_name=None null=True
- JSON: body, info, change_success
- status/choices: status_code
- business: client, epic_loan_key

### `MSRBaseRateSheet`
- path: `freedom/models/msr.py` | bases: `['BaseRateSheetBase']` | label: `freedom` | table: `freedom_msrbaseratesheet` | pk: `id (implicit AutoField)`
- cols (2): client, pricing_model
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=msr_base_rate_sheet null=True
- FK `pricing_model` → `PricingModel` on_delete=CASCADE related_name=msr_base_rate_sheet null=True
- JSON: none
- status/choices: pricing_model
- business: client

### `MSRRateSheet`
- path: `freedom/models/msr.py` | bases: `['RateSheetBase']` | label: `freedom` | table: `freedom_msrratesheet` | pk: `id (implicit AutoField)`
- cols (2): client, pricing_model
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=msr_uploaded_rate_sheets null=True
- FK `pricing_model` → `PricingModel` on_delete=CASCADE related_name=msr_rate_sheet null=True
- JSON: none
- status/choices: pricing_model
- business: client

### `MSRPriceControls`
- path: `freedom/models/msr.py` | bases: `['PriceControlsBase']` | label: `freedom` | table: `freedom_msrpricecontrols` | pk: `id (implicit AutoField)`
- cols (2): client, pricing_model
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=msr_price_controls null=True
- FK `pricing_model` → `PricingModel` on_delete=CASCADE related_name=msr_price_controls null=True
- JSON: none
- status/choices: pricing_model
- business: client

### `MSRGlobalExclusion`
- path: `freedom/models/msr.py` | bases: `['GlobalExclusionBase']` | label: `freedom` | table: `freedom_msrglobalexclusion` | pk: `id (implicit AutoField)`
- cols (2): client, pricing_model
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=msr_global_exclusions null=True
- FK `pricing_model` → `PricingModel` on_delete=CASCADE related_name=msr_global_exclusions null=True
- JSON: none
- status/choices: pricing_model
- business: client

### `Counterparty`
- path: `freedom/models/msrx.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_counterparty` | pk: `id (implicit AutoField)`
- cols (3): seller, correspondent, buyer
- FK `seller` → `msrx.MSRX_User` on_delete=PROTECT related_name=sellers null=True
- FK `correspondent` → `msrx.MSRX_User` on_delete=PROTECT related_name=correspondents null=True
- FK `buyer` → `msrx.MSRX_User` on_delete=PROTECT related_name=buyers null=True
- JSON: none
- business: seller, correspondent, buyer

### `OptimizationEvent`
- path: `freedom/models/optimization.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_optimizationevent` | pk: `id (implicit AutoField)`
- cols (8): client, tape, success, status, processing, progress, timestamp, updated
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=optimizationevents null=False
- FK `tape` → `Tape` on_delete=CASCADE related_name=optimizationevent null=False
- JSON: none
- status/choices: status(choices=OPTIMIZATION_STATUS_CHOICES)
- business: client, tape

### `PoolSnapshot`
- path: `freedom/models/optimization.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_poolsnapshot` | pk: `id (implicit AutoField)`
- cols (4): timestamp, upb_cap, price_cap, constraints
- relations: none
- JSON: constraints
- business: price_cap

### `OptimizationSnapshot`
- path: `freedom/models/optimization.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_optimizationsnapshot` | pk: `id (implicit AutoField)`
- cols (6): optimizationevent, loan, pool, pool_snapshot, allocated, allocated_elsewhere
- FK `optimizationevent` → `OptimizationEvent` on_delete=CASCADE related_name=optimization_snapshot null=False
- FK `loan` → `Loan` on_delete=CASCADE related_name=optimization_snapshot null=False
- FK `pool` → `Pool` on_delete=CASCADE related_name=optimization_snapshot null=False
- FK `pool_snapshot` → `PoolSnapshot` on_delete=CASCADE related_name=optimization_snapshot null=False
- JSON: none
- business: loan, pool, pool_snapshot

### `OptimizationError`
- path: `freedom/models/optimization.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_optimizationerror` | pk: `id (implicit AutoField)`
- cols (8): optimization, status, message, error_type, error_text, error_file, error_line, timestamp
- FK `optimization` → `OptimizationEvent` on_delete=CASCADE related_name=errors null=False
- JSON: none
- status/choices: status(choices=OPTIMIZATION_STATUS_CHOICES), error_type

### `ShockSnapshot`
- path: `freedom/models/optimization.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_shocksnapshot` | pk: `id (implicit AutoField)`
- cols (5): optimizationevent, loan, pool, pool_snapshot, shock_amount
- FK `optimizationevent` → `OptimizationEvent` on_delete=CASCADE related_name=shock_snapshot null=False
- FK `loan` → `Loan` on_delete=CASCADE related_name=shock_snapshot null=False
- FK `pool` → `Pool` on_delete=CASCADE related_name=shock_snapshot null=False
- FK `pool_snapshot` → `PoolSnapshot` on_delete=CASCADE related_name=shock_snapshot null=False
- JSON: none
- business: loan, pool, pool_snapshot

### `Pool`
- path: `freedom/models/pools.py` | bases: `['Model']` | label: `freedom` | table: `freedom_pool` | pk: `id (implicit AutoField)`
- cols (9): client, investor, start, end, type, allocated, upb_cap, active, price_cap
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=corr_pools null=False
- FK `investor` → `msrx.MSRX_User` on_delete=CASCADE related_name=investor_pools null=False
- JSON: none
- status/choices: type
- business: client, investor, price_cap

### `Constraint`
- path: `freedom/models/pools.py` | bases: `['Model']` | label: `freedom` | table: `freedom_constraint` | pk: `id (implicit AutoField)`
- cols (2): pool, constraint_string
- FK `pool` → `Pool` on_delete=CASCADE related_name=constraints null=False
- JSON: none
- business: pool

### `BulkBidData`
- path: `freedom/models/pricing.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_bulkbiddata` | pk: `id (implicit AutoField)`
- cols (5): client, file_name, inuse, uploadtime, pricing_model
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=None null=True
- FK `pricing_model` → `PricingModel` on_delete=CASCADE related_name=bulk_bid_data null=True
- JSON: none
- status/choices: pricing_model
- business: client

### `MaSheet`
- path: `freedom/models/pricing.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_masheet` | pk: `id (implicit AutoField)`
- cols (14): client, bulk_bid_data, type_rate_key, product_key, coupon, rate, bubd_adj, srp, ma, payup_term, payup_adj, nr_on_rate_sheet, mbs_price, inuse
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=masheets null=True
- FK `bulk_bid_data` → `BulkBidData` on_delete=CASCADE related_name=ma_sheet null=True
- JSON: none
- status/choices: type_rate_key, product_key(choices=<ListComp>)
- business: client, mbs_price

### `Subsidy`
- path: `freedom/models/pricing.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_subsidy` | pk: `id (implicit AutoField)`
- cols (7): client, bulk_bid_data, price_class, sub_code, prod, adjustor, inuse
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=subsidies null=True
- FK `bulk_bid_data` → `BulkBidData` on_delete=CASCADE related_name=subsidy_sheet null=True
- FK `price_class` → `PriceClass` on_delete=CASCADE related_name=subsidy_sheet null=False
- JSON: none
- business: client, price_class

### `RateSheet`
- path: `freedom/models/pricing.py` | bases: `['RateSheetBase']` | label: `freedom` | table: `freedom_ratesheet` | pk: `id (implicit AutoField)`
- cols (2): client, pricing_model
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=uploaded_rate_sheets null=True
- FK `pricing_model` → `PricingModel` on_delete=CASCADE related_name=rate_sheet null=True
- JSON: none
- status/choices: pricing_model
- business: client

### `BaseRateSheet`
- path: `freedom/models/pricing.py` | bases: `['RateSheetBase']` | label: `freedom` | table: `freedom_baseratesheet` | pk: `id (implicit AutoField)`
- cols (2): client, pricing_model
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=base_rate_sheet null=True
- FK `pricing_model` → `PricingModel` on_delete=CASCADE related_name=base_rate_sheet null=True
- JSON: none
- status/choices: pricing_model
- business: client

### `StateAssignment`
- path: `freedom/models/pricing.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_stateassignment` | pk: `id (implicit AutoField)`
- cols (12): bulk_bid_data, client, state, product, units_1, units_2, units_3, units_4, group, judicial, judicial_level, inuse
- FK `bulk_bid_data` → `BulkBidData` on_delete=CASCADE related_name=state_assignment_sheet null=True
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=state_assignments null=True
- JSON: none
- status/choices: state
- business: client

### `SettlementDate`
- path: `freedom/models/pricing.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_settlementdate` | pk: `id (implicit AutoField)`
- cols (9): client, del_month, year, product, term, efc_date, lastdatetodeliver, lastdatetofund_clear, settlementdate
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=settlement_dates null=False
- JSON: none
- business: client

### `RealTimeLLPA`
- path: `freedom/models/pricing.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_realtimellpa` | pk: `id (implicit AutoField)`
- cols (5): client, name, inuse, uploadtime, pricing_model
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=realtime_llpas null=False
- FK `pricing_model` → `PricingModel` on_delete=CASCADE related_name=realtime_llpa null=True
- JSON: none
- status/choices: pricing_model
- business: client

### `Spec`
- path: `freedom/models/pricing.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_spec` | pk: `id (implicit AutoField)`
- cols (5): client, name, inuse, uploadtime, pricing_model
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=specs null=False
- FK `pricing_model` → `PricingModel` on_delete=CASCADE related_name=spec null=True
- JSON: none
- status/choices: pricing_model
- business: client

### `StartMult`
- path: `freedom/models/pricing.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_startmult` | pk: `id (implicit AutoField)`
- cols (5): client, name, inuse, uploadtime, pricing_model
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=start_mults null=False
- FK `pricing_model` → `PricingModel` on_delete=CASCADE related_name=start_mult null=True
- JSON: none
- status/choices: pricing_model
- business: client

### `StripCap`
- path: `freedom/models/pricing.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_stripcap` | pk: `id (implicit AutoField)`
- cols (5): client, name, inuse, uploadtime, pricing_model
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=strip_caps null=False
- FK `pricing_model` → `PricingModel` on_delete=CASCADE related_name=strip_cap null=True
- JSON: none
- status/choices: pricing_model
- business: client

### `EFC`
- path: `freedom/models/pricing.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_efc` | pk: `id (implicit AutoField)`
- cols (8): client, settlement_month, coupon, per_diem, max_efc, max_efc_days, inuse, pricing_model
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=efcs null=False
- FK `pricing_model` → `PricingModel` on_delete=CASCADE related_name=efc null=True
- JSON: none
- status/choices: pricing_model
- business: client

### `RICCode`
- path: `freedom/models/pricing.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_riccode` | pk: `id (implicit AutoField)`
- cols (8): security, product_type, term, coupon, month0_code, month1_code, month2_code, client
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=ric_codes null=True
- JSON: none
- status/choices: product_type
- business: client

### `Override`
- path: `freedom/models/pricing.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_override` | pk: `id (implicit AutoField)`
- cols (7): client, product, term, coupon, c_override, spread, security
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=coup_overs null=False
- JSON: none
- business: client

### `DealerBroker`
- path: `freedom/models/pricing.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_dealerbroker` | pk: `id (implicit AutoField)`
- cols (2): name, correspondent
- FK `correspondent` → `msrx.MSRX_User` on_delete=CASCADE related_name=dealerbroker null=False
- JSON: none
- business: correspondent

### `AOTInformation`
- path: `freedom/models/pricing.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_aotinformation` | pk: `id (implicit AutoField)`
- cols (14): product_code, product_type, agency, term, coupon, assigned_amt, orig_trade_amt, security_price, trade_date, settlement_month, inuse, dealer, tape, pricing_owner
- FK `dealer` → `DealerBroker` on_delete=SET_NULL related_name=aot_information null=True
- FK `tape` → `freedom.Tape` on_delete=CASCADE related_name=aot_information null=False
- FK `pricing_owner` → `msrx.MSRX_User` on_delete=CASCADE related_name=aot_information null=False
- JSON: none
- status/choices: product_code(choices=<ListComp>), product_type
- business: security_price, dealer, tape

### `PriceControls`
- path: `freedom/models/pricing.py` | bases: `['PriceControlsBase']` | label: `freedom` | table: `freedom_pricecontrols` | pk: `id (implicit AutoField)`
- cols (2): client, pricing_model
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=price_controls null=True
- FK `pricing_model` → `PricingModel` on_delete=CASCADE related_name=price_controls null=True
- JSON: none
- status/choices: pricing_model
- business: client

### `RefinitivCreds`
- path: `freedom/models/refinitiv.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_refinitivcreds` | pk: `id (implicit AutoField)`
- cols (4): username, clientid, password_env, user
- FK `user` → `msrx.MSRX_User` on_delete=CASCADE related_name=refinitiv_creds null=True
- JSON: none
- business: clientid

### `Report`
- path: `freedom/models/reports.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_report` | pk: `id (implicit AutoField)`
- cols (5): report_type, user, platform, user_role, active
- FK `user` → `msrx.MSRX_User` on_delete=CASCADE related_name=wl_reports null=True
- FK `platform` → `msrx.PlatformConfiguration` on_delete=CASCADE related_name=wl_reports null=True
- JSON: none
- status/choices: report_type

### `ReportSheet`
- path: `freedom/models/reports.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_reportsheet` | pk: `id (implicit AutoField)`
- cols (4): report, name, index, function
- FK `report` → `Report` on_delete=CASCADE related_name=report_sheets null=True
- JSON: none

### `Step`
- path: `freedom/models/rules_based.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_step` | pk: `id (implicit AutoField)`
- cols (14): rate_sheet, base_rate_sheet, real_time_llpa, spec, start_mult, strip_cap, agency_llpa, description, global_exclusion, price_controls, msr_rate_sheet, msr_base_rate_sheet, msr_global_exclusion, msr_price_controls
- FK `rate_sheet` → `RateSheet` on_delete=CASCADE related_name=steps null=True
- FK `base_rate_sheet` → `BaseRateSheet` on_delete=CASCADE related_name=steps null=True
- FK `real_time_llpa` → `RealTimeLLPA` on_delete=CASCADE related_name=steps null=True
- FK `spec` → `Spec` on_delete=CASCADE related_name=steps null=True
- FK `start_mult` → `StartMult` on_delete=CASCADE related_name=steps null=True
- FK `strip_cap` → `StripCap` on_delete=CASCADE related_name=steps null=True
- FK `agency_llpa` → `analytics.YearlyLLPA` on_delete=CASCADE related_name=steps null=True
- FK `global_exclusion` → `freedom.GlobalExclusion` on_delete=CASCADE related_name=steps null=True
- FK `price_controls` → `freedom.PriceControls` on_delete=CASCADE related_name=steps null=True
- FK `msr_rate_sheet` → `MSRRateSheet` on_delete=CASCADE related_name=steps null=True
- FK `msr_base_rate_sheet` → `MSRBaseRateSheet` on_delete=CASCADE related_name=steps null=True
- FK `msr_global_exclusion` → `freedom.MSRGlobalExclusion` on_delete=CASCADE related_name=steps null=True
- FK `msr_price_controls` → `freedom.MSRPriceControls` on_delete=CASCADE related_name=steps null=True
- JSON: none
- business: price_controls, msr_price_controls

### `Rule`
- path: `freedom/models/rules_based.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_rule` | pk: `id (implicit AutoField)`
- cols (159): step, exclusion, client, adj, adj_type, all_loans, control_category, uploaded_adj … x60x24_u, x90x12_l, x90x12_u, x90x24_l, x90x24_u, piggyback
- FK `step` → `Step` on_delete=CASCADE related_name=rules null=True
- FK `exclusion` → `freedom.GlobalExclusion` on_delete=CASCADE related_name=rule null=True
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=rule null=True
- JSON: rule_exclude
- status/choices: adj_type, doc_type, loan_type, product_type, property_type, state, state_group, amortization_type(choices=<ListComp>), arm_index(choices=<ListComp>), arm_type, bankruptcy_status, broker_compensation_type(choices=<ListComp>), citizenship(choices=<ListComp>), foreclosure_status, income_type(choices=<ListComp>), income_type_term_l, income_type_term_u, prepayment_type
- business: client, all_loans, loan_balance_l, loan_balance_u, loan_exclude, loan_group, loan_type, t_loan_balance, t_loan_balance_l, t_loan_balance_u, arm_life_of_loan_max_rate_l, arm_life_of_loan_max_rate_u, arm_life_of_loan_min_rate_l, arm_life_of_loan_min_rate_u

### `Mappings`
- path: `freedom/models/rules_based.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_mappings` | pk: `id (implicit AutoField)`
- cols (13): rule_storage, llpa_dict_map, npts, rt_llpa_matrix_map, sc_map, sm_map, sp_map, rt_container_args, sc_container_args, sm_container_args, sp_container_args, updated_at, updated_by
- FK `updated_by` → `User` on_delete=CASCADE related_name=None null=True
- JSON: rule_storage, llpa_dict_map, npts, rt_llpa_matrix_map, sc_map, sm_map, sp_map, rt_container_args, sc_container_args, sm_container_args, sp_container_args

### `GlobalExclusion`
- path: `freedom/models/rules_based.py` | bases: `['GlobalExclusionBase']` | label: `freedom` | table: `freedom_globalexclusion` | pk: `id (implicit AutoField)`
- cols (2): client, pricing_model
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=global_exclusions null=True
- FK `pricing_model` → `PricingModel` on_delete=CASCADE related_name=global_exclusions null=True
- JSON: none
- status/choices: pricing_model
- business: client

### `Tape`
- path: `freedom/models/tapes.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_tape` | pk: `id (implicit AutoField)`
- cols (27): client, root, correspondent, tape_name, uploadtime, loancount, upb, status, transfer_date, status_details, updated_at, execution, haf, branch, fnma_agency_cash_succ, fhlmc_agency_cash_succ, time_last_sent, times_bidtape_sent, winner, latest_pricer, pricing_tape_s3, commit_tape_s3, genesis, allocation_status, allocatable, deleted, saved_scenario
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=seller_tapes null=True
- FK `root` → `self` on_delete=CASCADE related_name=leaf_tapes null=True
- FK `correspondent` → `msrx.MSRX_User` on_delete=CASCADE related_name=correspondent_tapes null=True
- FK `haf` → `HedgeAdvisoryFund` on_delete=CASCADE related_name=None null=True
- FK `branch` → `Branch` on_delete=CASCADE related_name=None null=True
- FK `winner` → `msrx.MSRX_User` on_delete=CASCADE related_name=won_tapes null=True
- FK `latest_pricer` → `User` on_delete=SET_NULL related_name=None null=True
- JSON: status_details, pricing_tape_s3, commit_tape_s3
- status/choices: status, status_details, allocation_status
- business: client, correspondent, tape_name, loancount, transfer_date, times_bidtape_sent, latest_pricer, pricing_tape_s3, commit_tape_s3

### `TapeDeleteLog`
- path: `freedom/models/tapes.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_tapedeletelog` | pk: `id (implicit AutoField)`
- cols (3): deleted_at, deleted_by, tape
- FK `deleted_by` → `User` on_delete=CASCADE related_name=deleted_tape_history null=False
- FK `tape` → `Tape` on_delete=CASCADE related_name=delete_log null=False
- JSON: none
- business: tape

### `WholeLoanPrice`
- path: `freedom/models/tapes.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_wholeloanprice` | pk: `id (implicit AutoField)`
- cols (17): loan, optimizationevent, buyer, price, msr, msr_total, asset_total, total_price, selected, type, price_chain, timestamp, pricer, pricing_model, loan_snapshot, optimal, exclusion
- FK `loan` → `Loan` on_delete=CASCADE related_name=wl_price null=False
- FK `optimizationevent` → `freedom.OptimizationEvent` on_delete=CASCADE related_name=wl_prices null=True
- FK `buyer` → `msrx.MSRX_User` on_delete=CASCADE related_name=None null=False
- FK `pricer` → `User` on_delete=SET_NULL related_name=None null=True
- FK `pricing_model` → `PricingModel` on_delete=SET_NULL related_name=whole_loan_prices null=True
- FK `loan_snapshot` → `LoanSnapshot` on_delete=SET_NULL related_name=whole_loan_prices null=True
- JSON: price, msr
- status/choices: type(choices=<ListComp>), pricing_model
- business: loan, buyer, price, total_price, price_chain, pricer, loan_snapshot

### `WholeLoanCommit`
- path: `freedom/models/tapes.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_wholeloancommit` | pk: `id (implicit AutoField)`
- cols (18): loan, buyer, commit, msr_commit, purchase, msr_purchase, msr_total, asset_total, total_price, type, commit_chain, timestamp, pricer, pricing_model, loan_snapshot, deal_chain, psa_deals, commit_timestamp
- FK `loan` → `Loan` on_delete=CASCADE related_name=wl_commit null=False
- FK `buyer` → `msrx.MSRX_User` on_delete=CASCADE related_name=None null=False
- FK `pricer` → `User` on_delete=SET_NULL related_name=None null=True
- FK `pricing_model` → `PricingModel` on_delete=SET_NULL related_name=whole_loan_commits null=True
- FK `loan_snapshot` → `LoanSnapshot` on_delete=SET_NULL related_name=whole_loan_commits null=True
- M2M `psa_deals` → `msrx.PSADeals` on_delete=None related_name=wl_commits null=None
- JSON: commit, msr_commit, purchase, msr_purchase
- status/choices: type(choices=<ListComp>), pricing_model
- business: loan, buyer, commit, msr_commit, total_price, commit_chain, pricer, loan_snapshot, deal_chain, psa_deals, commit_timestamp

### `MassUploadFileTracker`
- path: `freedom/models/tapes.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_massuploadfiletracker` | pk: `id (implicit AutoField)`
- cols (3): uploadtime, s3_path, uploader
- FK `uploader` → `msrx.MSRX_User` on_delete=CASCADE related_name=None null=False
- JSON: s3_path

### `MetaProductMap`
- path: `freedom/models/tapes.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_metaproductmap` | pk: `id (implicit AutoField)`
- cols (9): updated_at, created_at, client_alias, bw_product_name, client, spread, product_code, field_map, inuse
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=None null=False
- JSON: field_map
- business: client_alias, client

### `MetaProductPriceHistory`
- path: `freedom/models/tapes.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_metaproductpricehistory` | pk: `id (implicit AutoField)`
- cols (9): priced_date, product_code, product_name, pricing_response, fnma_contract_period, rate_increment, request_id, commitment_level, client
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=None null=False
- JSON: pricing_response
- business: priced_date, commitment_level, client

### `HedgeAdvisoryFund`
- path: `freedom/models/users.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_hedgeadvisoryfund` | pk: `id (implicit AutoField)`
- cols (9): aggregator, name, download_map, tape_crack, manager_name, address, phone_number, email, pricing_emails
- FK `aggregator` → `msrx.MSRX_User` on_delete=CASCADE related_name=owned_hafs null=True
- JSON: download_map, tape_crack, pricing_emails
- business: aggregator, tape_crack

### `Branch`
- path: `freedom/models/users.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_branch` | pk: `id (implicit AutoField)`
- cols (7): aggregator, name, code, manager_name, address, phone_number, email
- FK `aggregator` → `msrx.MSRX_User` on_delete=CASCADE related_name=owned_branches null=True
- JSON: none
- business: aggregator

### `PriceClass`
- path: `freedom/models/users.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_priceclass` | pk: `id (implicit AutoField)`
- cols (4): aggregator, branch, rate_sheet, code
- FK `aggregator` → `msrx.MSRX_User` on_delete=CASCADE related_name=owned_priceclasses null=True
- FK `branch` → `Branch` on_delete=CASCADE related_name=ratesheets null=False
- FK `rate_sheet` → `freedom.RateSheet` on_delete=CASCADE related_name=price_class null=True
- JSON: none
- business: aggregator
- unique_together: ("code", "branch")

### `Margin`
- path: `freedom/models/users.py` | bases: `['models.Model']` | label: `freedom` | table: `freedom_margin` | pk: `id (implicit AutoField)`
- cols (8): correspondent, seller, linked_seller, investor, point_margin, point_margin_inuse, dollar_margin, dollar_margin_inuse
- FK `correspondent` → `msrx.MSRX_User` on_delete=CASCADE related_name=correspondent_margin null=True
- FK `seller` → `msrx.MSRX_User` on_delete=CASCADE related_name=seller_margin null=True
- FK `linked_seller` → `msrx.MSRX_User` on_delete=CASCADE related_name=linked_seller_margin null=True
- FK `investor` → `msrx.MSRX_User` on_delete=CASCADE related_name=investor null=True
- JSON: none
- business: correspondent, seller, linked_seller, investor

### `Loan`
- path: `freedom/models/tapes.py` | bases: `['WholeLoan']` | label: `freedom` | table: `freedom_loan` | pk: `id (implicit)`
- note: concrete; fields from abstract parents
- cols (100): inherits caas.WholeLoan abstract fields (~100+) … inherits caas.WholeLoan abstract fields (~100+)
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=None null=True
- FK `tape` → `freedom.Tape` on_delete=CASCADE related_name=loans null=True
- FK `aot` → `freedom.AOTInformation` on_delete=SET_NULL related_name=loans null=True
- FK `selected_wl_resell_price` → `freedom.WholeLoanPrice` on_delete=CASCADE related_name=priced_loan null=True
- FK `allocated_pool` → `freedom.Pool` on_delete=PROTECT related_name=allocated_loans null=True
- FK `meta_product` → `freedom.MetaProductMap` on_delete=SET_NULL related_name=loans null=True
- JSON: msr_price, extension_policy
- status/choices: origination_status, lock_status, loan_pipeline_status, buydown
- business: client, tape, commitment_number

### `LoanSnapshot`
- path: `freedom/models/tapes.py` | bases: `['caas.LoanSnapshot']` | label: `freedom` | table: `freedom_loansnapshot` | pk: `id (implicit)`
- note: concrete; fields from abstract parents
- cols (100): snapshot_timestamp + WholeLoan fields … snapshot_timestamp + WholeLoan fields
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=None null=True
- FK `tape` → `freedom.Tape` on_delete=CASCADE related_name=loan_snapshots null=True
- FK `aot` → `freedom.AOTInformation` on_delete=SET_NULL related_name=loan_snapshots null=True
- FK `selected_wl_resell_price` → `freedom.WholeLoanPrice` on_delete=CASCADE related_name=priced_loan_snapshot null=True
- FK `allocated_pool` → `freedom.Pool` on_delete=PROTECT related_name=allocated_loan_snapshots null=True
- FK `meta_product` → `freedom.MetaProductMap` on_delete=SET_NULL related_name=loan_snapshots null=True
- FK `loan` → `freedom.Loan` on_delete=CASCADE related_name=loan_snapshots null=True
- JSON: msr_price, extension_policy
- status/choices: origination_status, lock_status
- business: client, tape, loan

## `duediligence` — 44 models

### `BaseModel` **[ABSTRACT]**
- path: `duediligence/models/basemodel.py` | bases: `['models.Model']` | label: `duediligence` | table: `duediligence_basemodel` | pk: `id (implicit AutoField)`
- cols (2): created_at, updated_at
- relations: none
- JSON: none

### `BoardingFileConfig`
- path: `duediligence/models/boardingfile.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_boardingfileconfig` | pk: `id (implicit AutoField)`
- cols (5): deal, active, boarding_file_function, sftp_configs, email_recipients
- FK `deal` → `duediligence.Deal` on_delete=CASCADE related_name=boarding_file_configs null=True
- M2M `sftp_configs` → `msrx.SFTPConfig` on_delete=None related_name=boarding_file_configs null=None
- JSON: email_recipients
- business: deal, boarding_file_function
- unique_together: ("deal",)

### `BoardingFileConfigSFTPConfig`
- path: `duediligence/models/boardingfile.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_boardingfileconfigsftpconfig` | pk: `id (implicit AutoField)`
- cols (3): boarding_file_config, sftp_config, sftp_dir
- FK `boarding_file_config` → `duediligence.BoardingFileConfig` on_delete=CASCADE related_name=sftp_config_mappings null=False
- FK `sftp_config` → `msrx.SFTPConfig` on_delete=CASCADE related_name=boarding_file_mappings null=False
- JSON: none
- business: boarding_file_config
- unique_together: ("boarding_file_config", "sftp_config")

### `BoardingFileDeliveryStatus`
- path: `duediligence/models/boardingfile.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_boardingfiledeliverystatus` | pk: `id (implicit AutoField)`
- cols (6): loan, sftp_config, email_recipients, success, timestamp, message
- FK `loan` → `duediligence.Loan` on_delete=CASCADE related_name=boarding_file_delivery_statuses null=False
- FK `sftp_config` → `msrx.SFTPConfig` on_delete=CASCADE related_name=boarding_file_delivery_statuses null=True
- JSON: email_recipients
- business: loan

### `QCRuleDocsFields`
- path: `duediligence/models/checks.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_qcruledocsfields` | pk: `id (implicit AutoField)`
- cols (3): rule, field, doc_type
- FK `rule` → `duediligence.QCRule` on_delete=CASCADE related_name=docs_fields null=False
- FK `field` → `duediligence.Field` on_delete=CASCADE related_name=docs_fields null=False
- FK `doc_type` → `duediligence.DocumentType` on_delete=CASCADE related_name=docs_fields null=False
- JSON: none
- status/choices: doc_type

### `QCRule`
- path: `duediligence/models/checks.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_qcrule` | pk: `id (implicit AutoField)`
- cols (12): name, description, is_prebuilt, arguments, category, material, seller, commentable, auto_clear_by_comment, active, programs, company
- M2M `category` → `duediligence.QCCategory` on_delete=None related_name=qcrules null=None
- FK `seller` → `msrx.MSRX_User` on_delete=CASCADE related_name=qcrules null=True
- M2M `programs` → `duediligence.Program` on_delete=None related_name=qcrules null=None
- FK `company` → `duediligence.Company` on_delete=CASCADE related_name=qcrules null=True
- JSON: arguments
- business: seller
- unique_together: ['name', 'company']

### `QualityControl`
- path: `duediligence/models/checks.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_qualitycontrol` | pk: `id (implicit AutoField)`
- cols (3): triggered, rule, loan
- FK `rule` → `duediligence.QCRule` on_delete=CASCADE related_name=quality_controls null=False
- FK `loan` → `duediligence.Loan` on_delete=CASCADE related_name=quality_controls null=False
- JSON: none
- business: loan

### `UserDefinedList`
- path: `duediligence/models/checks.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_userdefinedlist` | pk: `id (implicit AutoField)`
- cols (5): name, values, rules, buyer, company
- M2M `rules` → `duediligence.QCRule` on_delete=None related_name=enums null=None
- FK `buyer` → `msrx.MSRX_User` on_delete=CASCADE related_name=enums null=True
- FK `company` → `duediligence.Company` on_delete=CASCADE related_name=userdefined_lists null=True
- JSON: none
- business: buyer

### `UserDefinedVariable`
- path: `duediligence/models/checks.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_userdefinedvariable` | pk: `id (implicit AutoField)`
- cols (5): name, value, rules, buyer, company
- M2M `rules` → `duediligence.QCRule` on_delete=None related_name=variables null=None
- FK `buyer` → `msrx.MSRX_User` on_delete=CASCADE related_name=variables null=True
- FK `company` → `duediligence.Company` on_delete=CASCADE related_name=userdefined_variables null=True
- JSON: none
- business: buyer

### `UserDefinedDict`
- path: `duediligence/models/checks.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_userdefineddict` | pk: `id (implicit AutoField)`
- cols (5): name, values, rules, buyer, company
- M2M `rules` → `duediligence.QCRule` on_delete=None related_name=user_defined_unordered_dicts null=None
- FK `buyer` → `msrx.MSRX_User` on_delete=CASCADE related_name=user_defined_unordered_dicts null=True
- FK `company` → `duediligence.Company` on_delete=CASCADE related_name=userdefined_dicts null=True
- JSON: values
- business: buyer

### `ArgumentTemplate`
- path: `duediligence/models/checks.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_argumenttemplate` | pk: `id (implicit AutoField)`
- cols (8): logic_key, rule_format, obj_count, list_count, udict_count, description, name, frequency
- relations: none
- JSON: rule_format

### `QCCategory`
- path: `duediligence/models/checks.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_qccategory` | pk: `id (implicit AutoField)`
- cols (3): name, qc_company, description
- FK `qc_company` → `duediligence.Company` on_delete=CASCADE related_name=category null=True
- JSON: none

### `QCOperation`
- path: `duediligence/models/checks.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_qcoperation` | pk: `id (implicit AutoField)`
- cols (6): operation, name, arguments, list_only, input_only, delta_required
- relations: none
- JSON: none

### `Ratings`
- path: `duediligence/models/checks.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_ratings` | pk: `id (implicit AutoField)`
- cols (2): loan_score_card, deal_score_card
- relations: none
- JSON: loan_score_card, deal_score_card
- business: loan_score_card, deal_score_card

### `Comment`
- path: `duediligence/models/comments.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_comment` | pk: `id (implicit AutoField)`
- cols (5): author, body, rule, clears_rule, loan
- FK `author` → `msrx.MSRX_User` on_delete=CASCADE related_name=comments null=False
- FK `rule` → `duediligence.QCRule` on_delete=CASCADE related_name=comments null=False
- FK `loan` → `duediligence.Loan` on_delete=CASCADE related_name=comments null=False
- JSON: none
- business: loan

### `FieldEnums`
- path: `duediligence/models/data.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_fieldenums` | pk: `id (implicit AutoField)`
- cols (3): name, values, company
- FK `company` → `duediligence.Company` on_delete=CASCADE related_name=field_enums null=True
- JSON: none

### `Field`
- path: `duediligence/models/data.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_field` | pk: `id (implicit AutoField)`
- cols (11): company, name, pretty_name, type, description, document_types, locked, reason_locked, enums, bw_field, calc_field
- FK `company` → `duediligence.Company` on_delete=CASCADE related_name=fields null=True
- M2M `document_types` → `duediligence.DocumentType` on_delete=None related_name=fields null=None
- FK `enums` → `duediligence.FieldEnums` on_delete=SET_NULL related_name=fields null=True
- FK `bw_field` → `self` on_delete=SET_NULL related_name=client_fields null=True
- FK `calc_field` → `duediligence.CalculatedField` on_delete=SET_NULL related_name=field null=True
- JSON: none
- status/choices: type(choices=TYPE_CHOICES), document_types
- business: document_types
- indexes: ['models.Index']

### `FieldOrdering`
- path: `duediligence/models/data.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_fieldordering` | pk: `id (implicit AutoField)`
- cols (3): field, document_type, order
- FK `field` → `duediligence.Field` on_delete=CASCADE related_name=ordering null=False
- FK `document_type` → `duediligence.DocumentType` on_delete=CASCADE related_name=doc_field_ordering null=False
- JSON: none
- status/choices: document_type
- business: document_type

### `Value`
- path: `duediligence/models/data.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_value` | pk: `id (implicit AutoField)`
- cols (9): loan, extracted, confirmed, is_confirmed, source, field, document, calc_success, calc_error
- FK `loan` → `duediligence.Loan` on_delete=CASCADE related_name=values null=False
- FK `field` → `duediligence.Field` on_delete=SET_NULL related_name=values null=True
- FK `document` → `duediligence.Document` on_delete=SET_NULL related_name=values null=True
- JSON: none
- business: loan, document

### `CalculatedField`
- path: `duediligence/models/data.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_calculatedfield` | pk: `id (implicit AutoField)`
- cols (5): arguments, active, adjustment, adjustment_method, adjustment_places
- relations: none
- JSON: arguments

### `CalculatedFieldComp`
- path: `duediligence/models/data.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_calculatedfieldcomp` | pk: `id (implicit AutoField)`
- cols (3): calculated_field, field, doc_type
- FK `calculated_field` → `duediligence.CalculatedField` on_delete=CASCADE related_name=calculated_field_comp null=False
- FK `field` → `duediligence.Field` on_delete=CASCADE related_name=calculated_field_comp null=False
- FK `doc_type` → `duediligence.DocumentType` on_delete=CASCADE related_name=calculated_field_comp null=False
- JSON: none
- status/choices: doc_type
- unique_together: ["calculated_field", "field", "doc_type"]

### `LoanDeliveryConfig`
- path: `duediligence/models/delivery.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_loandeliveryconfig` | pk: `id (implicit AutoField)`
- cols (3): deal, active, sftp_configs
- FK `deal` → `duediligence.Deal` on_delete=CASCADE related_name=loan_delivery_configs null=True
- M2M `sftp_configs` → `msrx.SFTPConfig` on_delete=None related_name=loan_delivery_configs null=None
- JSON: none
- business: deal
- unique_together: ("deal",)

### `LoanDeliveryConfigSFTPConfig`
- path: `duediligence/models/delivery.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_loandeliveryconfigsftpconfig` | pk: `id (implicit AutoField)`
- cols (3): loan_delivery_config, sftp_config, sftp_dir
- FK `loan_delivery_config` → `duediligence.LoanDeliveryConfig` on_delete=CASCADE related_name=sftp_config_mappings null=False
- FK `sftp_config` → `msrx.SFTPConfig` on_delete=CASCADE related_name=loan_delivery_mappings null=False
- JSON: none
- business: loan_delivery_config
- unique_together: ("loan_delivery_config", "sftp_config")

### `LoanDeliveryStatus`
- path: `duediligence/models/delivery.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_loandeliverystatus` | pk: `id (implicit AutoField)`
- cols (5): loan, sftp_config, success, timestamp, message
- FK `loan` → `duediligence.Loan` on_delete=CASCADE related_name=delivery_statuses null=False
- FK `sftp_config` → `msrx.SFTPConfig` on_delete=CASCADE related_name=delivery_statuses null=False
- JSON: none
- business: loan

### `DocumentType`
- path: `duediligence/models/documents.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_documenttype` | pk: `id (implicit AutoField)`
- cols (6): company, name, description, bw_doc_type, ordering, generated
- FK `company` → `duediligence.Company` on_delete=CASCADE related_name=document_types null=True
- FK `bw_doc_type` → `self` on_delete=SET_NULL related_name=client_doc_types null=True
- JSON: none
- status/choices: bw_doc_type
- UniqueConstraint: [('["name", "company"]', 'Chosen name for document type already taken')]
- indexes: ['["name"]']

### `DocumentGenerations`
- path: `duediligence/models/documents.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_documentgenerations` | pk: `id (implicit AutoField)`
- cols (6): final_version, field, parent_document_type, document_type, most_recent, confirmed
- FK `field` → `duediligence.Field` on_delete=CASCADE related_name=None null=False
- FK `parent_document_type` → `duediligence.DocumentType` on_delete=CASCADE related_name=document_generations null=False
- FK `document_type` → `duediligence.DocumentType` on_delete=CASCADE related_name=document_selection null=False
- JSON: none
- status/choices: parent_document_type, document_type
- business: parent_document_type, document_type

### `Document`
- path: `duediligence/models/documents.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_document` | pk: `id (implicit AutoField)`
- cols (7): type, blob_file_name, file_name, pages, loan, version, final_version
- FK `type` → `duediligence.DocumentType` on_delete=CASCADE related_name=None null=False
- FK `loan` → `duediligence.Loan` on_delete=CASCADE related_name=documents null=False
- JSON: none
- status/choices: type
- business: loan

### `DocumentPriority`
- path: `duediligence/models/documents.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_documentpriority` | pk: `id (implicit AutoField)`
- cols (3): field, document_type, rank
- FK `field` → `duediligence.Field` on_delete=CASCADE related_name=document_priorities null=False
- FK `document_type` → `duediligence.DocumentType` on_delete=CASCADE related_name=priorities null=False
- JSON: none
- status/choices: document_type
- business: document_type

### `DocumentPrioritySnapshot`
- path: `duediligence/models/documents.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_documentprioritysnapshot` | pk: `id (implicit AutoField)`
- cols (2): company, priorities
- FK `company` → `duediligence.Company` on_delete=CASCADE related_name=doc_priority_snapshot null=True
- JSON: priorities

### `File`
- path: `duediligence/models/files.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_file` | pk: `id (implicit AutoField)`
- cols (3): loan, name, status
- FK `loan` → `duediligence.Loan` on_delete=CASCADE related_name=files null=False
- JSON: none
- status/choices: status
- business: loan

### `Rating`
- path: `duediligence/models/gradings.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_rating` | pk: `id (implicit AutoField)`
- cols (3): grade, agency, deal
- FK `deal` → `duediligence.Deal` on_delete=CASCADE related_name=ratings null=False
- JSON: none
- business: deal

### `Portfolio`
- path: `duediligence/models/groupings.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_portfolio` | pk: `id (implicit AutoField)`
- cols (4): name, owner, active, company
- FK `owner` → `msrx.MSRX_User` on_delete=CASCADE related_name=portfolio null=False
- FK `company` → `duediligence.Company` on_delete=SET_NULL related_name=portfolios null=True
- JSON: none

### `Deal`
- path: `duediligence/models/groupings.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_deal` | pk: `id (implicit AutoField)`
- cols (11): name, portfolio, seller, program, sftp_established, active, company, cleared, sftp_path, input_sftp_path, is_flat_upload
- FK `portfolio` → `duediligence.Portfolio` on_delete=SET_NULL related_name=deals null=True
- FK `seller` → `msrx.MSRX_User` on_delete=SET_NULL related_name=deals null=True
- FK `program` → `duediligence.Program` on_delete=SET_NULL related_name=deals null=True
- FK `company` → `duediligence.Company` on_delete=SET_NULL related_name=deals null=True
- JSON: none
- business: seller

### `Company`
- path: `duediligence/models/groupings.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_company` | pk: `id (implicit AutoField)`
- cols (10): name, description, ratings, custom_doc_ordering, custom_field_ordering, enable_stacked_bookmarks, enable_stacked_zips, enable_validations, skip_bs_table, use_borrower_note_order
- FK `ratings` → `duediligence.Ratings` on_delete=CASCADE related_name=company null=True
- JSON: none

### `ClientCompanies`
- path: `duediligence/models/groupings.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_clientcompanies` | pk: `id (implicit AutoField)`
- cols (2): buyer, seller
- FK `buyer` → `duediligence.Company` on_delete=CASCADE related_name=buyers null=False
- FK `seller` → `duediligence.Company` on_delete=CASCADE related_name=sellers null=False
- JSON: none
- business: buyer, seller

### `Loan`
- path: `duediligence/models/loan.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_loan` | pk: `id (implicit AutoField)`
- cols (13): deal, program, post_close_program, loan_number, status, cleared, all_documents_received, post_close, close_date, closing_docs_s3_path, active, msrx_coissue_loan, whole_loan
- FK `deal` → `duediligence.Deal` on_delete=SET_NULL related_name=loans null=True
- FK `program` → `duediligence.Program` on_delete=SET_NULL related_name=loans null=True
- FK `post_close_program` → `duediligence.Program` on_delete=SET_NULL related_name=post_close_loans null=True
- FK `msrx_coissue_loan` → `Client_Coissue_Tape` on_delete=SET_NULL related_name=duediligence_loans null=True
- FK `whole_loan` → `freedom.Loan` on_delete=SET_NULL related_name=duediligence_loans null=True
- JSON: closing_docs_s3_path
- status/choices: status
- business: deal, loan_number, all_documents_received, msrx_coissue_loan, whole_loan

### `QCLog`
- path: `duediligence/models/log.py` | bases: `['models.Model']` | label: `duediligence` | table: `duediligence_qclog` | pk: `id (implicit AutoField)`
- cols (8): auth, client, method, route, success, message, details, timestamp
- FK `auth` → `User` on_delete=PROTECT related_name=None null=True
- FK `client` → `msrx.MSRX_User` on_delete=PROTECT related_name=None null=True
- JSON: details
- business: client

### `Program`
- path: `duediligence/models/programs.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_program` | pk: `id (implicit AutoField)`
- cols (6): company, name, state, lien_position, document_types, post_close
- FK `company` → `duediligence.Company` on_delete=CASCADE related_name=programs null=True
- M2M `document_types` → `duediligence.DocumentType` on_delete=None related_name=programs null=None
- FK `post_close` → `self` on_delete=CASCADE related_name=post_close_program null=True
- JSON: none
- status/choices: state(choices=STATE_CHOICES), document_types
- business: document_types

### `ProgramDocumentTypeAlternate`
- path: `duediligence/models/programs.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_program_document_type_alternates` | pk: `id (implicit AutoField)`
- cols (3): program, required_document_type, alternate_document_type
- FK `program` → `duediligence.Program` on_delete=CASCADE related_name=document_type_alternates null=False
- FK `required_document_type` → `duediligence.DocumentType` on_delete=CASCADE related_name=required_document_type_alternates null=False
- FK `alternate_document_type` → `duediligence.DocumentType` on_delete=CASCADE related_name=alternate_document_type_requirements null=False
- JSON: none
- status/choices: required_document_type, alternate_document_type
- business: required_document_type, alternate_document_type
- UniqueConstraint: [('["program", "required_document_type", "alternate_document_type"]', 'unique_program_doc_type_alternate')]

### `PurchaseAdvice`
- path: `duediligence/models/purchaseadvice.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_purchaseadvice` | pk: `id (implicit AutoField)`
- cols (7): deal, active, base_price_percent, brokerage_base_price_percent, brokerage_fee, email_recipients, role
- FK `deal` → `duediligence.Deal` on_delete=CASCADE related_name=purchase_advices null=True
- JSON: email_recipients
- business: deal, base_price_percent, brokerage_base_price_percent

### `StatusTimestamp`
- path: `duediligence/models/status.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_statustimestamp` | pk: `id (implicit AutoField)`
- cols (5): loan, from_status, to_status, auth_user, timestamp
- FK `loan` → `duediligence.Loan` on_delete=CASCADE related_name=status_timestamps null=False
- FK `auth_user` → `auth.User` on_delete=SET_NULL related_name=qc_status_changes null=True
- JSON: none
- status/choices: from_status, to_status
- business: loan

### `StatusEmail`
- path: `duediligence/models/status.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_statusemail` | pk: `id (implicit AutoField)`
- cols (4): deal, active, status_trigger, email_recipients
- FK `deal` → `duediligence.Deal` on_delete=CASCADE related_name=status_emails null=False
- JSON: email_recipients
- status/choices: status_trigger
- business: deal

### `Loan_location`
- path: `duediligence/models/tracker.py` | bases: `['BaseModel']` | label: `duediligence` | table: `duediligence_loan_location` | pk: `id (implicit AutoField)`
- cols (7): loan_number, instance_id, receipt_handle, message_id, loan_json, queue_name, total_pages
- relations: none
- JSON: loan_json
- business: loan_number, loan_json
- UniqueConstraint: [('["loan_number"]', 'uniq_loan_location_loan_number')]

### `Loan_progress_status`
- path: `duediligence/models/tracker.py` | bases: `['models.Model']` | label: `duediligence` | table: `duediligence_loan_progress_status` | pk: `id (implicit AutoField)`
- cols (4): loc_id, status, timestamp, extra_info
- FK `loc_id` → `Loan_location` on_delete=CASCADE related_name=progress_statuses null=False
- JSON: extra_info
- status/choices: status

## `caas` — 31 models

### `Field`
- path: `caas/models/loan_builder/config/field.py` | bases: `['Model']` | label: `caas` | table: `caas_field` | pk: `id (implicit AutoField)`
- cols (5): name, type, default_display, timestamp, updated_by
- FK `updated_by` → `User` on_delete=CASCADE related_name=None null=False
- JSON: none
- status/choices: type(choices=<ListComp>)

### `FieldEnum`
- path: `caas/models/loan_builder/config/field_enum.py` | bases: `['Model']` | label: `caas` | table: `caas_fieldenum` | pk: `id (implicit AutoField)`
- cols (4): value, formfield, timestamp, updated_by
- FK `formfield` → `FormField` on_delete=CASCADE related_name=enums null=True
- FK `updated_by` → `User` on_delete=CASCADE related_name=None null=False
- JSON: none
- unique_together: ("formfield", "value")

### `DefaultFieldEnum`
- path: `caas/models/loan_builder/config/field_enum.py` | bases: `['Model']` | label: `caas` | table: `caas_defaultfieldenum` | pk: `id (implicit AutoField)`
- cols (4): value, field, timestamp, updated_by
- FK `field` → `Field` on_delete=CASCADE related_name=default_enums null=True
- FK `updated_by` → `User` on_delete=CASCADE related_name=None null=False
- JSON: none
- unique_together: ("field", "value")

### `FieldCategory`
- path: `caas/models/loan_builder/config/form_field.py` | bases: `['Model']` | label: `caas` | table: `caas_fieldcategory` | pk: `id (implicit AutoField)`
- cols (2): name, display_name
- relations: none
- JSON: none

### `FieldGroup`
- path: `caas/models/loan_builder/config/form_field.py` | bases: `['Model']` | label: `caas` | table: `caas_fieldgroup` | pk: `id (implicit AutoField)`
- cols (6): name, display_name, form, order, timestamp, updated_by
- FK `form` → `LoanForm` on_delete=CASCADE related_name=fieldgroups null=False
- FK `updated_by` → `User` on_delete=CASCADE related_name=None null=False
- JSON: none
- unique_together: ("name", "form")

### `FormField`
- path: `caas/models/loan_builder/config/form_field.py` | bases: `['Model']` | label: `caas` | table: `caas_formfield` | pk: `id (implicit AutoField)`
- cols (16): form, field, display_name, index, step, override, use_default_display, use_default_enums, required, visible, editable, timestamp, updated_by, category, group, affects_pricing
- FK `form` → `LoanForm` on_delete=CASCADE related_name=formfields null=False
- FK `field` → `Field` on_delete=CASCADE related_name=None null=False
- FK `updated_by` → `User` on_delete=CASCADE related_name=None null=False
- FK `category` → `FieldCategory` on_delete=SET_NULL related_name=None null=True
- FK `group` → `FieldGroup` on_delete=SET_NULL related_name=fields null=True
- JSON: none
- unique_together: ("field", "form")

### `LinkedField`
- path: `caas/models/loan_builder/config/linked_field.py` | bases: `['Model']` | label: `caas` | table: `caas_linkedfield` | pk: `id (implicit AutoField)`
- cols (5): fieldenum, field, value, timestamp, updated_by
- FK `fieldenum` → `FieldEnum` on_delete=CASCADE related_name=linked_fields null=False
- FK `field` → `Field` on_delete=CASCADE related_name=linked_fields null=False
- FK `updated_by` → `User` on_delete=SET_NULL related_name=None null=True
- JSON: none
- unique_together: ("fieldenum", "field")

### `LoanForm`
- path: `caas/models/loan_builder/config/loan_form.py` | bases: `['Model']` | label: `caas` | table: `caas_loanform` | pk: `id (implicit AutoField)`
- cols (8): description, user, timestamp, updated_by, mismo_required, mismo_required_for_pricing, can_use_mismo, allow_note_rate_spread
- FK `user` → `msrx.MSRX_User` on_delete=CASCADE related_name=None null=False
- FK `updated_by` → `User` on_delete=CASCADE related_name=None null=False
- JSON: none
- unique_together: ("description", "user")

### `BaseLoan` **[ABSTRACT]**
- path: `caas/models/loans/base_models/base_loan.py` | bases: `['Model']` | label: `caas` | table: `caas_baseloan` | pk: `id (implicit AutoField)`
- cols (46): agency_commit_num, aggregator_loan_id, tape_loan_id, updated_at, age, agency, aus, aus_findings … origination_date, origination_date, purchase_date, recon_date, settle_date, msr_price
- relations: none
- JSON: msr_price
- status/choices: doc_type, loan_type, product_type, property_type, state
- business: agency_commit_num, aggregator_loan_id, tape_loan_id, loan_balance, loan_type, t_loan_balance, agency_commit_date, agency_commit_exp, boarding_date, msr_price

### `BaseLoanNPI` **[ABSTRACT]**
- path: `caas/models/loans/base_models/base_loan.py` | bases: `['Model']` | label: `caas` | table: `caas_baseloannpi` | pk: `id (implicit AutoField)`
- cols (4): borrower_name, property_address, city, zip
- relations: none
- JSON: none

### `BaseWholeLoan` **[ABSTRACT]**
- path: `caas/models/loans/base_models/base_loan.py` | bases: `['Model']` | label: `caas` | table: `caas_basewholeloan` | pk: `id (implicit AutoField)`
- cols (33): commitment_number, fmc_loan_number, loan_index, loan_group, haf_code, high_bal, buydown, tpo_code, tract_code, msa_cbsa_code, county_code, state_code, uli, delivery_days, delivery_days_padding, piw_waiver, appraised_value, sale_price, enote_flag, subordfin_flag, monthly_income, ratesheet_name, insurance, hr_waiver, hp_waiver, lip_flag, vlip_flag, cra_lowinc_ind, extension_requested, extended, extension_policy, delivery_month, funded_date
- relations: none
- JSON: extension_policy
- status/choices: buydown(choices=BUYDOWN_CHOICES), state_code, lip_flag(choices=BUYDOWN_CHOICES), vlip_flag(choices=BUYDOWN_CHOICES)
- business: commitment_number, fmc_loan_number, loan_index, loan_group, sale_price

### `BaseNQM` **[ABSTRACT]**
- path: `caas/models/loans/base_models/base_loan.py` | bases: `['Model']` | label: `caas` | table: `caas_basenqm` | pk: `id (implicit AutoField)`
- cols (59): agg_loan_num, amortization_type, arm_first_reset_date, arm_index, arm_initial_change_ceiling_rate, arm_initial_change_floor_rate, arm_initial_term, arm_life_of_loan_max_rate … x90x12, x90x24, commit_expiration_date, lock_date, lock_expiration_date, origination_status_date
- relations: none
- JSON: none
- status/choices: amortization_type(choices=<ListComp>), arm_index(choices=<ListComp>), arm_type, bankruptcy_status, broker_compensation_type(choices=<ListComp>), citizenship(choices=<ListComp>), foreclosure_status, income_type(choices=<ListComp>), income_type_term, lock_status(choices=LOCK_STATUS_CHOICES), origination_status(choices=ORIGINATION_STATUS_CHOICES), prepayment_type, origination_status_date
- business: agg_loan_num, arm_life_of_loan_max_rate, arm_life_of_loan_min_rate, commit_expiration_date

### `BaseSecondLien` **[ABSTRACT]**
- path: `caas/models/loans/base_models/base_loan.py` | bases: `['Model']` | label: `caas` | table: `caas_basesecondlien` | pk: `id (implicit AutoField)`
- cols (1): piggyback
- relations: none
- JSON: none

### `BaseAllocationLoan` **[ABSTRACT]**
- path: `caas/models/loans/base_models/base_loan.py` | bases: `['Model']` | label: `caas` | table: `caas_baseallocationloan` | pk: `id (implicit AutoField)`
- cols (5): allocated, cost_basis, loan_pipeline_status, optimized, originator
- relations: none
- JSON: none
- status/choices: loan_pipeline_status
- business: loan_pipeline_status

### `BaseEpicAPILoan` **[ABSTRACT]**
- path: `caas/models/loans/base_models/base_loan.py` | bases: `['Model']` | label: `caas` | table: `caas_baseepicapiloan` | pk: `id (implicit AutoField)`
- cols (4): epic_loan_id, epic_loan_key, epic_loan_created_at, post_close
- relations: none
- JSON: none
- business: epic_loan_id, epic_loan_key, epic_loan_created_at

### `LoanSnapshotFields` **[ABSTRACT]**
- path: `caas/models/loans/base_models/loan_snapshot.py` | bases: `['BaseAllocationLoan', 'BaseLoan', 'BaseEpicAPILoan', 'BaseLoanNPI', 'BaseNQM', 'BaseSecondLien', 'BaseWholeLoan']` | label: `caas` | table: `caas_loansnapshotfields` | pk: `id (implicit AutoField)`
- cols (1): snapshot_timestamp
- relations: none
- JSON: none

### `LoanSnapshotForeignKeys` **[ABSTRACT]**
- path: `caas/models/loans/base_models/loan_snapshot.py` | bases: `['Model']` | label: `caas` | table: `caas_loansnapshotforeignkeys` | pk: `id (implicit AutoField)`
- cols (7): client, tape, aot, selected_wl_resell_price, allocated_pool, meta_product, loan
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=None null=True
- FK `tape` → `freedom.Tape` on_delete=CASCADE related_name=loan_snapshots null=True
- FK `aot` → `freedom.AOTInformation` on_delete=SET_NULL related_name=loan_snapshots null=True
- FK `selected_wl_resell_price` → `freedom.WholeLoanPrice` on_delete=CASCADE related_name=priced_loan_snapshot null=True
- FK `allocated_pool` → `freedom.Pool` on_delete=PROTECT related_name=allocated_loan_snapshots null=True
- FK `meta_product` → `freedom.MetaProductMap` on_delete=SET_NULL related_name=loan_snapshots null=True
- FK `loan` → `freedom.Loan` on_delete=CASCADE related_name=loan_snapshots null=True
- JSON: none
- business: client, tape, selected_wl_resell_price, allocated_pool, loan

### `LoanSnapshot` **[ABSTRACT]**
- path: `caas/models/loans/base_models/loan_snapshot.py` | bases: `['LoanSnapshotFields', 'LoanSnapshotForeignKeys']` | label: `caas` | table: `caas_loansnapshot` | pk: `id (implicit AutoField)`
- cols (0): 
- relations: none
- JSON: none

### `WholeLoanFields` **[ABSTRACT]**
- path: `caas/models/loans/base_models/whole_loan.py` | bases: `['BaseAllocationLoan', 'BaseLoan', 'BaseEpicAPILoan', 'BaseLoanNPI', 'BaseNQM', 'BaseSecondLien', 'BaseWholeLoan']` | label: `caas` | table: `caas_wholeloanfields` | pk: `id (implicit AutoField)`
- cols (0): 
- relations: none
- JSON: none

### `WholeLoanForeignKeys` **[ABSTRACT]**
- path: `caas/models/loans/base_models/whole_loan.py` | bases: `['Model']` | label: `caas` | table: `caas_wholeloanforeignkeys` | pk: `id (implicit AutoField)`
- cols (6): client, tape, aot, selected_wl_resell_price, allocated_pool, meta_product
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=None null=True
- FK `tape` → `freedom.Tape` on_delete=CASCADE related_name=loans null=True
- FK `aot` → `freedom.AOTInformation` on_delete=SET_NULL related_name=loans null=True
- FK `selected_wl_resell_price` → `freedom.WholeLoanPrice` on_delete=CASCADE related_name=priced_loan null=True
- FK `allocated_pool` → `freedom.Pool` on_delete=PROTECT related_name=allocated_loans null=True
- FK `meta_product` → `freedom.MetaProductMap` on_delete=SET_NULL related_name=loans null=True
- JSON: none
- business: client, tape, selected_wl_resell_price, allocated_pool

### `WholeLoan` **[ABSTRACT]**
- path: `caas/models/loans/base_models/whole_loan.py` | bases: `['WholeLoanFields', 'WholeLoanForeignKeys']` | label: `caas` | table: `caas_wholeloan` | pk: `id (implicit AutoField)`
- cols (0): 
- relations: none
- JSON: none

### `Note`
- path: `caas/models/loans/supplementary/note.py` | bases: `['Model']` | label: `caas` | table: `caas_note` | pk: `id (implicit AutoField)`
- cols (5): content, timestamp, loan, user, updated_by
- FK `loan` → `freedom.Loan` on_delete=CASCADE related_name=notes null=False
- FK `user` → `msrx.MSRX_User` on_delete=CASCADE related_name=None null=False
- FK `updated_by` → `User` on_delete=PROTECT related_name=None null=True
- JSON: none
- business: loan

### `OriginationStatusSnapshot`
- path: `caas/models/loans/supplementary/origination_status.py` | bases: `['Model']` | label: `caas` | table: `caas_originationstatussnapshot` | pk: `id (implicit AutoField)`
- cols (3): loan, status, timestamp
- FK `loan` → `freedom.Loan` on_delete=CASCADE related_name=None null=False
- JSON: none
- status/choices: status
- business: loan

### `Workflow`
- path: `caas/models/workflow/config/workflow.py` | bases: `['Model']` | label: `caas` | table: `caas_workflow` | pk: `id (implicit AutoField)`
- cols (8): active, user, user_role, platform, trigger, additional_triggers, alias, comment
- FK `user` → `msrx.MSRX_User` on_delete=CASCADE related_name=caas_workflows null=True
- FK `platform` → `msrx.PlatformConfiguration` on_delete=CASCADE related_name=caas_workflows null=True
- JSON: additional_triggers
- status/choices: trigger(choices=<ListComp>)

### `WorkflowJob`
- path: `caas/models/workflow/config/workflow.py` | bases: `['Model']` | label: `caas` | table: `caas_workflowjob` | pk: `id (implicit AutoField)`
- cols (10): workflow, active, check_business_day, cron_year, cron_month, cron_day, cron_week, cron_hour, cron_minute, cron_second
- FK `workflow` → `Workflow` on_delete=CASCADE related_name=caas_workflow_jobs null=False
- JSON: none

### `WorkflowStep`
- path: `caas/models/workflow/config/workflow.py` | bases: `['Model']` | label: `caas` | table: `caas_workflowstep` | pk: `id (implicit AutoField)`
- cols (4): workflow, index, active, func_name
- FK `workflow` → `Workflow` on_delete=CASCADE related_name=steps null=False
- JSON: none

### `WorkflowStepCSVReport`
- path: `caas/models/workflow/config/workflow.py` | bases: `['Model']` | label: `caas` | table: `caas_workflowstepcsvreport` | pk: `id (implicit AutoField)`
- cols (4): step, alias, filename, function
- FK `step` → `WorkflowStep` on_delete=CASCADE related_name=csv_report null=False
- JSON: none

### `WorkflowStepSQLReport`
- path: `caas/models/workflow/config/workflow.py` | bases: `['Model']` | label: `caas` | table: `caas_workflowstepsqlreport` | pk: `id (implicit AutoField)`
- cols (4): step, alias, filename, sql_s3_path
- FK `step` → `WorkflowStep` on_delete=CASCADE related_name=sql_report null=False
- JSON: none

### `WorkflowStepEmail`
- path: `caas/models/workflow/config/workflow.py` | bases: `['Model']` | label: `caas` | table: `caas_workflowstepemail` | pk: `id (implicit AutoField)`
- cols (2): step, config
- FK `step` → `WorkflowStep` on_delete=CASCADE related_name=email null=False
- FK `config` → `EmailSchedulerConfig` on_delete=SET_NULL related_name=caas_workflow null=True
- JSON: none

### `WorkflowStepSFTP`
- path: `caas/models/workflow/config/workflow.py` | bases: `['Model']` | label: `caas` | table: `caas_workflowstepsftp` | pk: `id (implicit AutoField)`
- cols (3): step, config, remote_dir
- FK `step` → `WorkflowStep` on_delete=CASCADE related_name=sftp null=False
- FK `config` → `msrx.SFTPConfig` on_delete=SET_NULL related_name=caas_workflow null=True
- JSON: none

### `WorkflowLog`
- path: `caas/models/workflow/config/workflow.py` | bases: `['Model']` | label: `caas` | table: `caas_workflowlog` | pk: `id (implicit AutoField)`
- cols (9): time, success, auth, user, platform, workflow, step_reached, job, details
- FK `auth` → `Auth_User` on_delete=PROTECT related_name=caas_workflow_logs null=True
- FK `user` → `msrx.MSRX_User` on_delete=PROTECT related_name=caas_workflow_logs null=True
- FK `platform` → `msrx.PlatformConfiguration` on_delete=PROTECT related_name=caas_workflow_logs null=True
- FK `workflow` → `Workflow` on_delete=PROTECT related_name=caas_workflow_logs null=True
- FK `step_reached` → `WorkflowStep` on_delete=PROTECT related_name=caas_workflow_logs null=True
- FK `job` → `WorkflowJob` on_delete=PROTECT related_name=caas_workflow_logs null=True
- JSON: none

## `TapeManager` — 1 models

### `Tape_Cracking_Log`
- path: `TapeManager/models.py` | bases: `['models.Model']` | label: `TapeManager` | table: `tapemanager_tape_cracking_log` | pk: `id (implicit AutoField)`
- cols (8): bucket, filename, web_url, crack_status, logs, updated_at, open_issue, email
- relations: none
- JSON: none
- status/choices: crack_status

## `Transfer` — 6 models

### `EMResource`
- path: `Transfer/models.py` | bases: `['models.Model']` | label: `Transfer` | table: `transfer_emresource` | pk: `id (implicit AutoField)`
- cols (12): notification, status, status_details, manifest, em_loan_id, em_user_id, raw_data_path, processed_data_path, additional_data, mismo, fnm, updated_at
- relations: none
- JSON: notification, status_details, manifest, additional_data
- status/choices: status, status_details
- business: em_loan_id

### `EMAPILog`
- path: `Transfer/models.py` | bases: `['models.Model']` | label: `Transfer` | table: `transfer_emapilog` | pk: `id (implicit AutoField)`
- cols (5): api_name, api_type, message_send, message_receive, updated_at
- relations: none
- JSON: message_send, message_receive
- status/choices: api_type

### `EMUserMapping`
- path: `Transfer/models.py` | bases: `['models.Model']` | label: `Transfer` | table: `transfer_emusermapping` | pk: `id (implicit AutoField)`
- cols (2): em_user_id, msrx
- FK `msrx` → `msrx.MSRX_User` on_delete=CASCADE related_name=None null=True
- JSON: none

### `TransferConfig`
- path: `Transfer/models.py` | bases: `['models.Model']` | label: `Transfer` | table: `transfer_transferconfig` | pk: `id (implicit AutoField)`
- cols (8): msrx, downstream_template, sftp_path, sftp_username, sftp_pw, sftp_ppk, sftp_openssh, sftp_port
- FK `msrx` → `msrx.MSRX_User` on_delete=CASCADE related_name=None null=True
- JSON: none

### `RoundpointLoanNumbers`
- path: `Transfer/models.py` | bases: `['models.Model']` | label: `Transfer` | table: `transfer_roundpointloannumbers` | pk: `id (implicit AutoField)`
- cols (5): roundpoint_loan_number, burned, seller_id, seller_loan_number, datetime_assigned
- FK `seller_id` → `msrx.MSRX_User` on_delete=CASCADE related_name=None null=True
- JSON: none
- business: roundpoint_loan_number, seller_id, seller_loan_number

### `FtpDirectory`
- path: `Transfer/models.py` | bases: `['models.Model']` | label: `Transfer` | table: `transfer_ftpdirectory` | pk: `id (implicit AutoField)`
- cols (5): client, directory, label, type, updated_at
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=client_sftp_directory null=True
- JSON: none
- status/choices: type(choices=TYPE_CHOICES)
- business: client

## `supertransfer` — 14 models

### `Loan`
- path: `supertransfer/models.py` | bases: `['models.Model']` | label: `supertransfer` | table: `supertransfer_loan` | pk: `id (implicit AutoField)`
- cols (6): seller, buyer, job, updated_at, logged_at, loan_num
- FK `seller` → `MSRX_User` on_delete=CASCADE related_name=owned_super_transfer_loan null=False
- FK `buyer` → `MSRX_User` on_delete=CASCADE related_name=received_super_transfer_loan null=False
- JSON: none
- business: seller, buyer, loan_num

### `MissingFile`
- path: `supertransfer/models.py` | bases: `['models.Model']` | label: `supertransfer` | table: `supertransfer_missingfile` | pk: `id (implicit AutoField)`
- cols (5): updated_at, logged_at, file_type, loan, found
- FK `loan` → `Loan` on_delete=CASCADE related_name=missing_files null=False
- JSON: none
- status/choices: file_type
- business: loan

### `Logs`
- path: `supertransfer/models.py` | bases: `['models.Model']` | label: `supertransfer` | table: `supertransfer_logs` | pk: `id (implicit AutoField)`
- cols (8): buyer, seller, activity_name, loan_number, message, success, tips, updated_at
- FK `buyer` → `MSRX_User` on_delete=PROTECT related_name=buyer_super_transfer_log null=False
- FK `seller` → `MSRX_User` on_delete=PROTECT related_name=seller_super_transfer_log null=False
- JSON: tips
- business: buyer, seller, loan_number

### `BuyerSFTP`
- path: `supertransfer/models.py` | bases: `['models.Model']` | label: `supertransfer` | table: `supertransfer_buyersftp` | pk: `id (implicit AutoField)`
- cols (19): msrx, msrx_group, sftp_path, sftp_path_backup, sftp_username, sftp_pw, sftp_openssh, sftp_directory, connect_using_command, documents_expected, document_renaming_rule, zipfile_name, zipfile_name_datetime_format, deliver_on_schedule, delivery_schedule_month, delivery_schedule_day, delivery_schedule_day_of_week, delivery_schedule_hour, delivery_schedule_minute
- FK `msrx` → `MSRX_User` on_delete=CASCADE related_name=sftp_details null=True
- FK `msrx_group` → `MSRX_User` on_delete=CASCADE related_name=sftp_user_group null=False
- JSON: documents_expected, zipfile_name
- business: documents_expected, document_renaming_rule

### `BoardingFileRules`
- path: `supertransfer/models.py` | bases: `['models.Model']` | label: `supertransfer` | table: `supertransfer_boardingfilerules` | pk: `id (implicit AutoField)`
- cols (12): buyer_sftp, buyer, seller, filename, mapping, excel_sheet_name, deliver_on_schedule, delivery_schedule_month, delivery_schedule_day, delivery_schedule_day_of_week, delivery_schedule_hour, delivery_schedule_minute
- FK `buyer_sftp` → `BuyerSFTP` on_delete=CASCADE related_name=boarding_file_sftp null=True
- FK `buyer` → `MSRX_User` on_delete=CASCADE related_name=boarding_file_buyer null=True
- FK `seller` → `MSRX_User` on_delete=CASCADE related_name=boarding_file_seller null=True
- JSON: mapping
- business: buyer_sftp, buyer, seller

### `RequiredDocuments`
- path: `supertransfer/models.py` | bases: `['models.Model']` | label: `supertransfer` | table: `supertransfer_requireddocuments` | pk: `id (implicit AutoField)`
- cols (4): buyer, bw_document_name, required, investor_document_name
- FK `buyer` → `MSRX_User` on_delete=CASCADE related_name=buyers_required_documents null=False
- JSON: none
- business: buyer, bw_document_name, investor_document_name

### `QualityControl`
- path: `supertransfer/models.py` | bases: `['models.Model']` | label: `supertransfer` | table: `supertransfer_qualitycontrol` | pk: `id (implicit AutoField)`
- cols (242): boarding_staging, first_due_date_prior_to_closing_date, first_due_date_prior_to_origination_date, first_payment_due_date_is_prior_to_the_note_date, second_principal_balance_is_greater_than_0, appraisal_value_less_than_5000, aus_code_is_invalid, borrower_credit_score_is_blank … c_flood_mapping_company_is_blank, c_missing_borrower_email_address, c_old_loan_number_is_blank, c_original_occupancy_code_is_blank, c_boarding_data_does_not_match_msrx_data, updated_at
- FK `boarding_staging` → `Boarding_Staging` on_delete=CASCADE related_name=loan_object null=False
- JSON: none
- status/choices: flood_pay_type_mismatch, hazard_pay_type_mismatch, interest_rate_exceeds_state_max, invalid_hazard_pay_type, lo_type_is_blank, loan_type_3_with_mi_data, mailing_state_contains_number, mailing_state_is_blank_or_not_in_zz_format, mailing_state_not_valid, property_not_in_licensed_state, property_state_is_blank_or_not_in_zz_format, property_state_is_not_valid, property_type_is_blank, property_type_is_invalid, property_type_mismatch, borrower_1_id_type_is_missing, borrower_2_id_type_is_missing, uw_missing_asset_statements, c_mailing_state_is_blank_or_not_in_zz_format
- business: boarding_staging, escrowed_loan_without_escrow_balance, escrowed_loan_without_escrow_payment, loan_closing_date_is_blank, loan_closing_date_on_today_or_in_the_future, loan_has_both_escrow_balance_and_escrow_advance_balance, loan_is_greater_than_30_days_delinquent, loan_term_is_blank_or_zero, loan_type_3_with_mi_data, loan_has_mi_but_no_mi_rate, loan_with_a_negative_lien_amount, maturity_date_is_prior_to_transfer, new_loan_with_late_fee, newly_originated_loan_with_escrow_advance_balance, non_escrowed_loan_with_escrow_balance, non_escrowed_loan_with_escrow_payment, old_loan_number_is_blank, purchase_price_is_blank, roundpoint_loan_number_check_digit_is_invalid, roundpoint_loan_number_is_invalid, seasoned_loan_in_flow_process_requires_pay_history, the_loan_is_not_amortized_using_pi_and_loan_balance_is_not_equ, loan_purpose_is_missing, investor_loan_number_equals_buyer_loan_number, investor_loan_number_equals_seller_loan_number, loan_is_an_e_note, nfp_loan_amount_greater_than_max_amount, nfp_loan_source_must_be_retail, nfp_loan_term_exceeds_maximum, uw_high_cost_loan_not_allowed, uw_high_priced_loan_not_allowed, uw_missing_application_or_loan_approval, uw_missing_income_verification_documents, uw_missing_employment_verification_documents, uw_missing_gfe_or_loan_estimates, uw_missing_property_insurance_documents_from_origination, boarding_data_does_not_match_msrx_data, c_escrowed_loan_without_escrow_balance, c_investor_loan_number_equals_buyer_loan_number, c_investor_loan_number_equals_seller_loan_number…

### `Comment`
- path: `supertransfer/models.py` | bases: `['models.Model']` | label: `supertransfer` | table: `supertransfer_comment` | pk: `id (implicit AutoField)`
- cols (6): author, rule, cleared_by_comment, boarding_staging, body, updated_at
- FK `author` → `MSRX_User` on_delete=CASCADE related_name=author null=False
- FK `boarding_staging` → `Boarding_Staging` on_delete=CASCADE related_name=loan null=False
- JSON: none
- business: boarding_staging

### `QCRuleSettings`
- path: `supertransfer/models.py` | bases: `['models.Model']` | label: `supertransfer` | table: `supertransfer_qcrulesettings` | pk: `id (implicit AutoField)`
- cols (8): rule, readable_rule_name, description, fields, commentable, auto_clear_by_comment, buyer, updated_at
- FK `buyer` → `MSRX_User` on_delete=CASCADE related_name=rule_buyer null=False
- JSON: none
- business: buyer

### `EpicFieldMapping`
- path: `supertransfer/models.py` | bases: `['models.Model']` | label: `supertransfer` | table: `supertransfer_epicfieldmapping` | pk: `id (implicit AutoField)`
- cols (28): bw_field, default_value, always_use_default, use_default_if_null, use_default_if_not_found, skip_if_null, skip_if_not_found, epic_field, epic_subfield, use_str_match, match_threshold, bw_collection_field, coll_default_value, coll_always_use_default, coll_use_default_if_null, coll_use_default_if_not_found, coll_skip_if_null, coll_skip_if_not_found, coll_use_str_match, coll_match_threshold, coll_category, field_category, sub_category, py_type, description, wave, order, source
- relations: none
- JSON: none
- status/choices: py_type

### `EpicCollectionMapping`
- path: `supertransfer/models.py` | bases: `['models.Model']` | label: `supertransfer` | table: `supertransfer_epiccollectionmapping` | pk: `id (implicit AutoField)`
- cols (5): epic_index, field, bw_value, description, bw_category
- FK `field` → `EpicFieldMapping` on_delete=CASCADE related_name=collection null=True
- JSON: none

### `EpicValueMapping`
- path: `supertransfer/models.py` | bases: `['models.Model']` | label: `supertransfer` | table: `supertransfer_epicvaluemapping` | pk: `id (implicit AutoField)`
- cols (8): provided_value, epic_value, coll_mapping, field_mapping, description, bw_category, official, active
- FK `coll_mapping` → `EpicCollectionMapping` on_delete=CASCADE related_name=collection null=True
- FK `field_mapping` → `EpicFieldMapping` on_delete=CASCADE related_name=field null=True
- JSON: none

### `LoanStatusMapping`
- path: `supertransfer/models.py` | bases: `['models.Model']` | label: `supertransfer` | table: `supertransfer_loanstatusmapping` | pk: `id (implicit AutoField)`
- cols (3): epic_id, description, bw_value
- relations: none
- JSON: none

### `ReclassificationLog`
- path: `supertransfer/models.py` | bases: `['models.Model']` | label: `supertransfer` | table: `supertransfer_reclassificationlog` | pk: `id (implicit AutoField)`
- cols (6): document, original_doc_type, new_doc_type, pages, user, timestamp
- FK `document` → `Document` on_delete=CASCADE related_name=None null=False
- FK `original_doc_type` → `DocumentType` on_delete=SET_NULL related_name=reclassify_logs_original_doc_type null=True
- FK `new_doc_type` → `DocumentType` on_delete=SET_NULL related_name=reclassify_logs_new_doc_type null=True
- FK `user` → `MSRX_User` on_delete=SET_NULL related_name=None null=True
- JSON: none
- status/choices: original_doc_type, new_doc_type
- business: document

## `middleware` — 0 models

## `bw_middleware` — 0 models

## `tapecrack` — 5 models

### `TapeCrack`
- path: `tapecrack/models/tapecrack.py` | bases: `['models.Model']` | label: `tapecrack` | table: `tapecrack_tapecrack` | pk: `id (implicit AutoField)`
- cols (11): client, haf, coissue, seasoned, whole, nonqm, mls_pa, boarding, exception_audit, updated_by, validation
- O2O `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=client_tapecrack null=True
- O2O `haf` → `freedom.HedgeAdvisoryFund` on_delete=CASCADE related_name=haf_tapecrack null=True
- FK `updated_by` → `User` on_delete=PROTECT related_name=None null=True
- FK `validation` → `tapecrack.ValidationSQL` on_delete=PROTECT related_name=None null=True
- JSON: none
- business: client, boarding

### `FieldCrackConfig`
- path: `tapecrack/models/tapecrack.py` | bases: `['models.Model']` | label: `tapecrack` | table: `tapecrack_fieldcrackconfig` | pk: `id (implicit AutoField)`
- cols (2): field_name, type
- relations: none
- JSON: none
- status/choices: type

### `ValidationSQL`
- path: `tapecrack/models/tapecrack.py` | bases: `['models.Model']` | label: `tapecrack` | table: `tapecrack_validationsql` | pk: `id (implicit AutoField)`
- cols (3): name, description, validation_sql
- relations: none
- JSON: none

### `BWField`
- path: `tapecrack/models/validation.py` | bases: `['models.Model']` | label: `tapecrack` | table: `tapecrack_bwfield` | pk: `id (implicit AutoField)`
- cols (9): field, active, updated_by, mandatory, allow_ineligible, deny_nonnumeric, deny_zero, deny_duplicates, deny_null
- FK `updated_by` → `User` on_delete=PROTECT related_name=None null=True
- JSON: none

### `BWEnum`
- path: `tapecrack/models/validation.py` | bases: `['models.Model']` | label: `tapecrack` | table: `tapecrack_bwenum` | pk: `id (implicit AutoField)`
- cols (4): field, enum, active, updated_by
- FK `field` → `BWField` on_delete=CASCADE related_name=enum null=False
- FK `updated_by` → `User` on_delete=CASCADE related_name=None null=True
- JSON: none

## `analytics` — 13 models

### `YearlyLLPA`
- path: `analytics/models.py` | bases: `['models.Model']` | label: `analytics` | table: `analytics_yearlyllpa` | pk: `id (implicit AutoField)`
- cols (2): inuse, effective_date
- relations: none
- JSON: none

### `APIProduct`
- path: `analytics/models.py` | bases: `['models.Model']` | label: `analytics` | table: `analytics_apiproduct` | pk: `id (implicit AutoField)`
- cols (4): description, inuse, product_code, agency
- relations: none
- JSON: none

### `AgencyCashWindow`
- path: `analytics/models.py` | bases: `['models.Model']` | label: `analytics` | table: `analytics_agencycashwindow` | pk: `id (implicit AutoField)`
- cols (21): fhlmc_account_identifier, fhlmc_active, fhlmc_commit_url, fhlmc_password, fhlmc_pricing_url, fhlmc_request, fhlmc_seller_num, fhlmc_spec_flag, fhlmc_spec_passthrough, fhlmc_username, fnma_account_identifier, fnma_active, fnma_commit_url, fnma_password, fnma_pricing_url, fnma_request, fnma_seller_num, fnma_spec_flag, fnma_spec_passthrough, fnma_username, msrx_user
- FK `msrx_user` → `MSRX_User` on_delete=CASCADE related_name=agency_cashwindows null=True
- JSON: none
- business: fhlmc_commit_url, fhlmc_seller_num, fnma_commit_url, fnma_seller_num

### `TrialBalanceAggregator`
- path: `analytics/models.py` | bases: `['models.Model']` | label: `analytics` | table: `analytics_trialbalanceaggregator` | pk: `id (implicit AutoField)`
- cols (8): client_name, sftp_path, sftp_username, sftp_pw, sftp_openssh, sftp_directory, msrx, active
- FK `msrx` → `MSRX_User` on_delete=CASCADE related_name=None null=True
- JSON: none
- business: client_name

### `TrialBalanceFile`
- path: `analytics/models.py` | bases: `['models.Model']` | label: `analytics` | table: `analytics_trialbalancefile` | pk: `id (implicit AutoField)`
- cols (8): orig_file_name, aggregator, file_date, updated_at, uploaded_date, has_exceptions, message, progress
- FK `aggregator` → `TrialBalanceAggregator` on_delete=CASCADE related_name=None null=True
- JSON: none
- business: aggregator

### `TrialBalance`
- path: `analytics/models.py` | bases: `['models.Model']` | label: `analytics` | table: `analytics_trialbalance` | pk: `id (implicit AutoField)`
- cols (107): month, agg_loan_num, buyer, aggregator, agg_seller, buyer_name, loan_term, interest_rate … investor_id, investor, investor_type, uploaded_file, seller_loan_num, updated_at
- FK `buyer` → `MSRX_User` on_delete=CASCADE related_name=trial_balance_buyer null=True
- FK `aggregator` → `MSRX_User` on_delete=CASCADE related_name=trial_balance_resell null=True
- FK `agg_seller` → `Client_Aggregator_Seller` on_delete=CASCADE related_name=trial_balance_agg_seller null=True
- FK `resell_loan` → `Client_Coissue_Tape_Resell` on_delete=CASCADE related_name=None null=True
- FK `seasoned_resell_loan` → `Client_Seasoned_Tape_Resell` on_delete=CASCADE related_name=None null=True
- FK `uploaded_file` → `TrialBalanceFile` on_delete=CASCADE related_name=None null=True
- JSON: none
- status/choices: bill_state, mers_reg_status, prop_state, prop_type, co_borrow_state, investor_type
- business: agg_loan_num, buyer, aggregator, agg_seller, buyer_name, loan_term, loan_matures, loan_closes, gse_loan_num, resell_loan, seasoned_resell_loan, rhs_loan_num, investor_id, investor, investor_type, seller_loan_num

### `PolyAssumptionSummary`
- path: `analytics/models.py` | bases: `['models.Model']` | label: `analytics` | table: `analytics_polyassumptionsummary` | pk: `id (implicit AutoField)`
- cols (4): assumption_name, created_at, updated_at, owner
- FK `owner` → `MSRX_User` on_delete=CASCADE related_name=poly_assumption_summary_owner null=True
- JSON: none

### `PolyGeoAssumption`
- path: `analytics/models.py` | bases: `['models.Model']` | label: `analytics` | table: `analytics_polygeoassumption` | pk: `id (implicit AutoField)`
- cols (7): state_name, state_abbr, ti_multiple, ioe_percent, fcl_timeline, reo_timeline, state_prepay_factor
- relations: none
- JSON: none
- status/choices: state_name, state_abbr, state_prepay_factor

### `PolyOneOffAssumption`
- path: `analytics/models.py` | bases: `['models.Model']` | label: `analytics` | table: `analytics_polyoneoffassumption` | pk: `id (implicit AutoField)`
- cols (10): msr_sfee_cur_ratio, msr_sfee_delinq_ratio, msr_sfee_delinq_ratio_15d, msr_sfee_delinq_ratio_30d, msr_sfee_delinq_ratio_60d, msr_sfee_delinq_ratio_90d, msr_sfee_delinq_ratio_fcl, msr_sfee_delinq_ratio_reo, msr_sfee_pp_ratio, msr_forbearance_end_date
- relations: none
- JSON: none

### `PolyFloatRateFeeAssumption`
- path: `analytics/models.py` | bases: `['models.Model']` | label: `analytics` | table: `analytics_polyfloatratefeeassumption` | pk: `id (implicit AutoField)`
- cols (22): msr_ti_remit_flt, msr_remit_flt, msr_ti_flt, msr_pi_flt, msr_pp_flt, msr_corp_cost_flt, msr_corp_cost_mult, msr_inflation_rate, msr_cost_inflation_rate, msr_corp_cost_inflation_rate, msr_corp_cost_num_pmts_30d, msr_corp_cost_num_pmts_60d, msr_corp_cost_num_pmts_90d, msr_ti_remit_num_pmts_30d, msr_ti_remit_num_pmts_60d, msr_ti_remit_num_pmts_90d, msr_remit_num_pmts_30d, msr_remit_num_pmts_60d, msr_remit_num_pmts_90d, msr_misc_fee, msr_strip, summary
- FK `summary` → `PolyAssumptionSummary` on_delete=CASCADE related_name=oneoff_assumptions null=True
- JSON: none

### `PolyAgyRemitCTSAssumption`
- path: `analytics/models.py` | bases: `['models.Model']` | label: `analytics` | table: `analytics_polyagyremitctsassumption` | pk: `id (implicit AutoField)`
- cols (19): agency, remit, product_type, msr_net_cost, msr_delinq_cost_15d, msr_delinq_cost_30d, msr_delinq_cost_60d, msr_delinq_cost_90d, msr_delinq_cost_fcl, msr_delinq_cost_reo, msr_sched_pi_days, msr_unsched_pi_days, msr_comp_int_days, msr_corp_cost_const, msr_late_fee, msr_anc_inc, loss_severity, adco_command_arg, summary
- FK `summary` → `PolyAssumptionSummary` on_delete=CASCADE related_name=agy_remit_cts_assumptions null=True
- JSON: none
- status/choices: agency(choices=agency_choices), remit(choices=remit_choices), product_type(choices=product_choices)

### `PolyRecaptureStripAssumption`
- path: `analytics/models.py` | bases: `['models.Model']` | label: `analytics` | table: `analytics_polyrecapturestripassumption` | pk: `id (implicit AutoField)`
- cols (7): agency, product_type, term_group, msr_recapture_gain, msr_recapture_pct, msr_recapture_pct_mult, summary
- FK `summary` → `PolyAssumptionSummary` on_delete=CASCADE related_name=recapture_assumptions null=True
- JSON: none
- status/choices: agency(choices=agency_choices), product_type(choices=product_choices), term_group(choices=term_choices)

### `StrMatchLog`
- path: `analytics/models.py` | bases: `['models.Model']` | label: `analytics` | table: `analytics_strmatchlog` | pk: `id (implicit AutoField)`
- cols (26): found_value, matched_value, algorithm, function, confidence, threshold, threshold_met, added, app_label, module, value_table, value_obj_id, added_value_obj_id, field_table, field_obj_id, description, confirmed_by, msrx_user, aggregator, timestamp, current, final_value, qc_loan, whole_loan, boarding_stage, root_log
- FK `confirmed_by` → `User` on_delete=SET_NULL related_name=str_match_analyst null=True
- FK `msrx_user` → `MSRX_User` on_delete=CASCADE related_name=str_match_analysis null=True
- FK `aggregator` → `MSRX_User` on_delete=CASCADE related_name=agg_str_match_analysis null=True
- FK `qc_loan` → `QCLoan` on_delete=CASCADE related_name=str_match_analysis null=True
- FK `whole_loan` → `Whole_Loan` on_delete=CASCADE related_name=str_match_analysis null=True
- FK `boarding_stage` → `Boarding_Staging` on_delete=CASCADE related_name=str_match_analysis null=True
- FK `root_log` → `self` on_delete=SET_NULL related_name=updated_log null=True
- JSON: none
- status/choices: boarding_stage
- business: aggregator, qc_loan, whole_loan, boarding_stage

## `base` — 1 models

### `APIActivityLog`
- path: `base/models.py` | bases: `['models.Model']` | label: `base` | table: `api_activity_log` | pk: `id (implicit AutoField)`
- cols (16): created_at, path, method, query_params, files, http_hostname, token, user, aliased_user, request_body, response_type, response_code, response_body, response_time, ip_address, user_agent
- FK `user` → `User` on_delete=SET_NULL related_name=api_activity_logs null=True
- FK `aliased_user` → `User` on_delete=SET_NULL related_name=None null=True
- JSON: none
- status/choices: response_type

## `commitrecon` — 3 models

### `RP_Boarding_Reconciliation_Tape`
- path: `commitrecon/models.py` | bases: `['models.Model']` | label: `commitrecon` | table: `commitrecon_rp_boarding_reconciliation_tape` | pk: `id (implicit AutoField)`
- cols (19): loannumber, sellername, boardedsellerloannumber, boardedterm, boardedamortype, boardedprinbal, panetservfee, boardednoterate, boardedremit, boardedescrowpmt, boardedpropstate, boardedfico, boardedoccupancy, boardedpurpose, boardedltv, pasource, servicerid, nonbifurcatedflag, boardeddeliverymonth
- relations: none
- JSON: none
- status/choices: boardedamortype, boardedpropstate
- business: loannumber, sellername, boardedsellerloannumber

### `PA_Summary`
- path: `commitrecon/models.py` | bases: `['models.Model']` | label: `commitrecon` | table: `commitrecon_pa_summary` | pk: `id (implicit AutoField)`
- cols (34): report_type, commit_cycle, buyer_file_url, seller_file_url, count, delivery_month, status, created, updated_at, buyer, seller, seller_side_fed_reference_num, buyer_side_fed_reference_num, principal_balance, note_rate, avg_service_fee, avg_orig_term, avg_ltv, avg_fico, avg_srp_price, avg_srp_multiple, gross_srp, initial_purchase_price, holdback, subtotal_srp_funding_amount, escrow_bal, wire_fees_net, amount_due_seller, bwft_fee, tax_fee, boarding_fee, flood_fee, collateral_custodian_fee, total_third_party_fees
- FK `commit_cycle` → `Client_Commit_Cycle` on_delete=PROTECT related_name=None null=True
- FK `buyer` → `MSRX_User` on_delete=CASCADE related_name=buyer_purchase_advices null=False
- FK `seller` → `MSRX_User` on_delete=CASCADE related_name=seller_purchase_advices null=False
- JSON: none
- status/choices: report_type(choices=report_type_options), status(choices=STATUS_CHOICES)
- business: commit_cycle, buyer_file_url, seller_file_url, buyer, seller, seller_side_fed_reference_num, buyer_side_fed_reference_num, avg_srp_price, initial_purchase_price, amount_due_seller, boarding_fee

### `AgencyPurchaseLoanNumber`
- path: `commitrecon/models.py` | bases: `['models.Model']` | label: `commitrecon` | table: `commitrecon_agencypurchaseloannumber` | pk: `id (implicit AutoField)`
- cols (8): agency, agency_loan_number, seller_loan_number, agency_purchase_date, seller, commitment, created, modified
- FK `seller` → `MSRX_User` on_delete=PROTECT related_name=agency_purchase_seller null=True
- FK `commitment` → `Client_Coissue_Tape` on_delete=SET_NULL related_name=agency_purchase_loan_number null=True
- JSON: none
- business: agency_loan_number, seller_loan_number, seller, commitment

## `EmailTrading` — 4 models

### `MonitoredMailbox`
- path: `EmailTrading/models.py` | bases: `['models.Model']` | label: `EmailTrading` | table: `emailtrading_monitoredmailbox` | pk: `id (implicit AutoField)`
- cols (6): address, last_triggered, last_pinged, last_active_ping, scanned_folder, active
- relations: none
- JSON: none

### `EmailTrading_Log`
- path: `EmailTrading/models.py` | bases: `['models.Model']` | label: `EmailTrading` | table: `emailtrading_emailtrading_log` | pk: `id (implicit AutoField)`
- cols (6): updated_at, email, success, message, tips, mailbox
- FK `mailbox` → `MonitoredMailbox` on_delete=CASCADE related_name=None null=True
- JSON: tips

### `DowntimeRecord`
- path: `EmailTrading/models.py` | bases: `['models.Model']` | label: `EmailTrading` | table: `emailtrading_downtimerecord` | pk: `id (implicit AutoField)`
- cols (3): start, end, mailbox
- FK `mailbox` → `MonitoredMailbox` on_delete=CASCADE related_name=None null=True
- JSON: none

### `EmailSchedulerConfig`
- path: `EmailTrading/models.py` | bases: `['models.Model']` | label: `EmailTrading` | table: `emailtrading_emailschedulerconfig` | pk: `id (implicit AutoField)`
- cols (9): brand, loan_type, recipients, cc_list, bcc_list, subject, body, file_path, msrx_user
- FK `msrx_user` → `msrx.MSRX_User` on_delete=CASCADE related_name=None null=True
- JSON: none
- status/choices: loan_type
- business: loan_type

## `secondlien` — 5 models

### `ClientTape`
- path: `secondlien/models.py` | bases: `['models.Model']` | label: `secondlien` | table: `secondlien_clienttape` | pk: `id (implicit AutoField)`
- cols (10): seller_client, tape_name, uploadtime, loancount, upb, status, transfer_date, status_details, updated_at, execution
- FK `seller_client` → `msrx.MSRX_User` on_delete=CASCADE related_name=None null=True
- JSON: status_details
- status/choices: status, status_details
- business: seller_client, tape_name, loancount, transfer_date

### `ClientLoan`
- path: `secondlien/models.py` | bases: `['models.Model']` | label: `secondlien` | table: `secondlien_clientloan` | pk: `id (implicit AutoField)`
- cols (20): tapeinfo, seller_client, tape_loan_id, loan_balance, note_rate, origination_date, first_payment_date, price, broker, aggregator_cu, subservicer, investor_cu, warehouse_cu, aggregator_transfer, investor_transfer, updated_at, fico, dti, property_state, cltv
- FK `tapeinfo` → `ClientTape` on_delete=CASCADE related_name=None null=True
- FK `seller_client` → `msrx.MSRX_User` on_delete=CASCADE related_name=None null=True
- FK `aggregator_transfer` → `msrx.Boarding_Staging` on_delete=CASCADE related_name=aggregator_transfer null=True
- FK `investor_transfer` → `msrx.Boarding_Staging` on_delete=CASCADE related_name=investor_transfer null=True
- JSON: none
- status/choices: property_state
- business: tapeinfo, seller_client, tape_loan_id, loan_balance, price, aggregator_cu, investor_cu, aggregator_transfer, investor_transfer

### `ClientSFTP`
- path: `secondlien/models.py` | bases: `['models.Model']` | label: `secondlien` | table: `secondlien_clientsftp` | pk: `id (implicit AutoField)`
- cols (28): msrx, active, is_seller, is_buyer, sftp_path, sftp_username, sftp_pw, sftp_openssh, sftp_directory_from, sftp_directory_to, upload_ingested_files_to_s3, ingestion_s3_upload_bucket, ingestion_s3_upload_directory, ingestion_s3_upload_use_date_subdir, ingestion_s3_upload_date_subdir_offset, delete_sftp_files_after_ingestion, ingest_all_files_in_dir, ingest_pipeline_report, ingest_pipeline_filename_match, ingest_pipeline_field_mappings, ingest_trial_balance_report, ingest_trial_balance_filename_match, ingest_trial_balance_field_mappings, ingest_trial_balance_static_fields, buyer_name_mappings, buyer_id_mappings, ingest_pipeline_assign_loan_numbers, ingest_custom_field_mappings
- FK `msrx` → `msrx.MSRX_User` on_delete=CASCADE related_name=second_lien_sftp_details null=True
- JSON: ingest_pipeline_field_mappings, ingest_trial_balance_field_mappings, ingest_trial_balance_static_fields, buyer_name_mappings, buyer_id_mappings, ingest_custom_field_mappings
- business: is_seller, is_buyer, buyer_name_mappings, buyer_id_mappings, ingest_pipeline_assign_loan_numbers

### `ClientEmail`
- path: `secondlien/models.py` | bases: `['models.Model']` | label: `secondlien` | table: `secondlien_clientemail` | pk: `id (implicit AutoField)`
- cols (3): email_address, msrx, comment
- FK `msrx` → `msrx.MSRX_User` on_delete=CASCADE related_name=second_lien_client_emails null=True
- JSON: none

### `OutgoingReport`
- path: `secondlien/models.py` | bases: `['models.Model']` | label: `secondlien` | table: `secondlien_outgoingreport` | pk: `id (implicit AutoField)`
- cols (11): sftp, send_report, send_by_sftp, send_by_email, email_recipients, is_xlsx_file, filename, mapping, generation_rules, excel_sheet_name, comment
- FK `sftp` → `ClientSFTP` on_delete=CASCADE related_name=outgoing_reports null=True
- M2M `email_recipients` → `ClientEmail` on_delete=None related_name=outgoing_reports null=None
- JSON: mapping, generation_rules

## `rp` — 1 models

### `boarding_staging_table`
- path: `rp/models.py` | bases: `['models.Model']` | label: `rp` | table: `rp_boarding_staging_table` | pk: `id (implicit AutoField)`
- cols (545): cpi_loan_no, t_loan_type_open_1, t_loan_type_open_2, t_loan_term, t_property_value, t_prepmt_penalty_ind, t_old_loan_no, t_aus_code … high_escrow_balance, c_high_escrow_balance, investor_loan_number_equals_seller_loan_number, investor_loan_number_equals_freedom_loan_number, c_investor_loan_number_equals_seller_loan_number, c_investor_loan_number_equals_freedom_loan_number
- FK `seller_id` → `MSRX_User` on_delete=CASCADE related_name=None null=True
- JSON: none
- status/choices: t_loan_type_open_1, t_loan_type_open_2, t_note_type, t_dist_type, t_dist_type_1_flag, t_nu_bill_state, t_nu_prop_state_abbr, t_haz_type_pay_01, t_flood_cntrct_type, t_haz_type_pay_02, t_haz_type_pay_03, t_haz_type_pay_04, t_haz_type_pay_05, t_property_type, t_ownership_type, t_development_type, t_balloon_type, t_eloc_ind_status, flood_pay_type_mismatch, hazard_pay_type_mismatch, interest_rate_exceeds_state_max, invalid_hazard_pay_type, lo_type_is_blank, loan_type_3_with_mi_data, mailing_state_contains_number, mailing_state_is_blank_or_not_in_zz_format, mailing_state_not_valid, property_not_in_licensed_state, property_state_is_blank_or_not_in_zz_format, property_state_is_not_valid, property_type_is_blank, property_type_is_invalid, property_type_mismatch, c_flood_pay_type_mismatch, c_hazard_pay_type_mismatch, c_interest_rate_exceeds_state_max, c_invalid_hazard_pay_type, c_lo_type_is_blank, c_loan_type_3_with_mi_data, c_mailing_state_contains_number, c_mailing_state_is_blank_or_not_in_zz_format, c_mailing_state_not_valid, c_property_not_in_licensed_state, c_property_state_is_blank_or_not_in_zz_format, c_property_state_is_not_valid, c_property_type_is_blank, c_property_type_is_invalid, c_property_type_mismatch
- business: cpi_loan_no, t_loan_type_open_1, t_loan_type_open_2, t_loan_term, t_old_loan_no, t_loan_matures_date, t_loan_date, t_investor_code_perm, t_invest_loan_no, t_pool_pmi_payee, t_pool_pmi_policy_no, t_rhs_loan_no, t_higher_priced_typ, t_purchase_price, escrowed_loan_without_escrow_balance, escrowed_loan_without_escrow_payment, loan_closing_date_is_blank, loan_closing_date_on_today_or_in_the_future, loan_has_both_escrow_balance_and_escrow_advance_balance, loan_is_greater_than_30_days_delinquent, loan_term_is_blank_or_zero, loan_type_3_with_mi_data, loan_with_a_negative_lien_amount, maturity_date_is_prior_to_transfer, new_loan_with_late_fee, newly_originated_loan_with_escrow_advance_balance, non_escrowed_loan_with_escrow_balance, non_escrowed_loan_with_escrow_payment, purchase_price_is_blank, roundpoint_loan_number_check_digit_is_invalid, roundpoint_loan_number_is_invalid, seasoned_loan_in_flow_process_requires_pay_history, the_loan_is_not_amortized_using_p_i_and_loan_balance_is_not_equ, old_loan_number_is_blank, c_escrowed_loan_without_escrow_balance, c_escrowed_loan_without_escrow_payment, c_loan_closing_date_is_blank, c_loan_closing_date_on_today_or_in_the_future, c_loan_has_both_escrow_balance_and_escrow_advance_balance, c_loan_is_greater_than_30_days_delinquent…

## `voxtur` — 7 models

### `InfoExRequest`
- path: `voxtur/models.py` | bases: `['models.Model']` | label: `voxtur` | table: `voxtur_infoexrequest` | pk: `id (implicit AutoField)`
- cols (9): msrx_user, updated_at, created_at, status, order_id, order_guid, loan_event_id, success, errors
- FK `msrx_user` → `MSRX_User` on_delete=CASCADE related_name=infoex_request_user null=True
- JSON: errors
- status/choices: status
- business: loan_event_id

### `InfoExDocument`
- path: `voxtur/models.py` | bases: `['models.Model']` | label: `voxtur` | table: `voxtur_infoexdocument` | pk: `id (implicit AutoField)`
- cols (1): request
- FK `request` → `InfoExRequest` on_delete=CASCADE related_name=documents_document null=True
- JSON: none

### `InfoExDataPoint`
- path: `voxtur/models.py` | bases: `['models.Model']` | label: `voxtur` | table: `voxtur_infoexdatapoint` | pk: `id (implicit AutoField)`
- cols (4): guid, value, group_id, request
- FK `request` → `InfoExRequest` on_delete=CASCADE related_name=datapointgroup_datapoint null=True
- JSON: none

### `APIKeyToView`
- path: `voxtur/models.py` | bases: `['models.Model']` | label: `voxtur` | table: `voxtur_apikeytoview` | pk: `id (implicit AutoField)`
- cols (4): api_key_name, app, view_name, active
- relations: none
- JSON: none

### `AOLPricingPurchase`
- path: `voxtur/models.py` | bases: `['models.Model']` | label: `voxtur` | table: `voxtur_aolpricingpurchase` | pk: `id (implicit AutoField)`
- cols (11): state, attorney_fee, closing_fee, coordination_fee, muni_search_fee, search_and_exam_fee, cpl_fee, purchase_aol_fee_0to300000, purchase_aol_fee_300001to650000, purchase_aol_fee_650001to1000000, updated_at
- relations: none
- JSON: none
- status/choices: state

### `AOLPricingRefinance`
- path: `voxtur/models.py` | bases: `['models.Model']` | label: `voxtur` | table: `voxtur_aolpricingrefinance` | pk: `id (implicit AutoField)`
- cols (9): state, attorney_fee, closing_fee, coordination_fee, muni_search_fee, search_and_exam_fee, cpl_fee, refinance_aol_fee, updated_at
- relations: none
- JSON: none
- status/choices: state

### `AOLPricingHomeEquity`
- path: `voxtur/models.py` | bases: `['models.Model']` | label: `voxtur` | table: `voxtur_aolpricinghomeequity` | pk: `id (implicit AutoField)`
- cols (3): state, search_curative_recording_ins_coverage, updated_at
- relations: none
- JSON: none
- status/choices: state

## `terms` — 4 models

### `Terms_Conditions`
- path: `terms/models.py` | bases: `['models.Model']` | label: `terms` | table: `terms_terms_conditions` | pk: `id (implicit AutoField)`
- cols (5): agreement_text, user_role, platform, version_number, created
- relations: none
- JSON: none
- status/choices: user_role(choices=USER_ROLE_CHOICES)
- UniqueConstraint: [('["user_role", "platform", "version_number"]', 'unique_version')]

### `User_Acceptance`
- path: `terms/models.py` | bases: `['models.Model']` | label: `terms` | table: `terms_user_acceptance` | pk: `id (implicit AutoField)`
- cols (8): user, terms_accepted, first_name, last_name, phone_number, email, accepted_at, updated_on
- FK `user` → `User` on_delete=CASCADE related_name=None null=False
- FK `terms_accepted` → `Terms_Conditions` on_delete=PROTECT related_name=None null=False
- JSON: none

### `PrivacyPolicy`
- path: `terms/models.py` | bases: `['models.Model']` | label: `terms` | table: `terms_privacypolicy` | pk: `id (implicit AutoField)`
- cols (6): privacy_terms, version, updated_on, active, user_role, platform
- relations: none
- JSON: none
- status/choices: user_role(choices=role_choices)

### `PolicyAcknowledgement`
- path: `terms/models.py` | bases: `['models.Model']` | label: `terms` | table: `terms_policyacknowledgement` | pk: `id (implicit AutoField)`
- cols (3): user, policy, acknowledge_date
- FK `user` → `User` on_delete=CASCADE related_name=None null=False
- FK `policy` → `PrivacyPolicy` on_delete=PROTECT related_name=None null=False
- JSON: none

## `benutech` — 2 models

### `PropertySummary`
- path: `benutech/models/property.py` | bases: `['models.Model']` | label: `benutech` | table: `benutech_propertysummary` | pk: `id (implicit AutoField)`
- cols (62): client, sa_property_id, sa_parcel_nbr_primary, sa_site_house_nbr, sa_site_fraction, sa_site_dir, sa_site_street_name, sa_site_post_dir … v_unit, v_mail_address, v_site_address, formatted_sa_owner_1, created_at, updated_at
- FK `client` → `msrx.MSRX_User` on_delete=CASCADE related_name=client null=False
- JSON: none
- status/choices: sa_site_state, mm_fips_state_code, sa_mail_state
- business: client, sa_date_transfer, sa_val_transfer

### `Report`
- path: `benutech/models/property.py` | bases: `['models.Model']` | label: `benutech` | table: `benutech_report` | pk: `id (implicit AutoField)`
- cols (10): property_summary, client_loan_id, sa_property_id, state_county_fips, status, message, report_type, report_link, created_at, updated_at
- FK `property_summary` → `benutech.PropertySummary` on_delete=CASCADE related_name=None null=False
- JSON: none
- status/choices: state_county_fips, status(choices=status_choices), report_type(choices=report_type_choices)
- business: client_loan_id
