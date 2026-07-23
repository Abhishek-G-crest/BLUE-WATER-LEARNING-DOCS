Hidden features audit
Features not visible from the React sidebar — evidence from routes, viewMaps, fixtures, user_details flags, and cross-references. Source: BLUE-WATER monorepo scan · fixtures + client/src + Django urls.

How visibility actually works
The sidebar is not hardcoded. It renders
userDetails.side_panel_items

where
enabled === true

( sidePanel.js:14–26). Product screens are Redux view IDs in viewMaps.js (141 entries), not URL paths. Live DB JSON can differ from fixtures.
141
pageMaps views
90
Fixture sidebar IDs
54
Views never in fixtures
30
Never enabled in fixtures
8
Flag findings
4
Admin findings
6
Orphan API findings
6
Dead / orphan UI
Filter by category
Findings with evidence
43 items

Risk	Category	Feature	Evidence	Why hidden
Hidden routes	SPA has only 6 URL routes; product screens are Redux view IDs	msrx-frontend/client/src/Router.js:33-44 — /login, /forgot, /reset-password/:token, /mfa, /error, / (PrivateRoute)	Authenticated app stays on `/`; sidebar never changes the URL
Hidden routes	54 pageMaps views never appear in any fixture sidebar	viewMaps.js (141 keys) vs fixtures side_panel_items (90 IDs) — 54 only in pageMaps	Reached via setView() drill-downs, header, or not reached at all
Hidden routes	showUserProfile — header only	headerPanel.js:34 setView("showUserProfile")	Not a sidebar item; Change Password menu
Hidden routes	Due Diligence internal API routes	duediligence/urls.py:172-174 — internal/deals/, internal/portfolios/	Service-style paths; not React sidebar navigation
Hidden routes	Django staff admin panel pages	msrx/urls.py:7-17 — admin_panel_login/, admin_panel_users/, admin_panel_tapes/, admin_panel_middleware/, admin_panel_tape_details/, admin_panel_tape_cracking_log/	Server-rendered; requires is_staff; separate from React sidebar
Feature flags	No LaunchDarkly/Unleash/PostHog — flags are JSON on the user	No featureFlag SDK imports; gating via userDetails.user_details.* and side_panel_items.enabled	Per-user DB JSON, not a flag service
Feature flags	Sidebar enabled gate (primary visibility control)	sidePanel.js:14,26 — filter/find sidebarItem.enabled; MSRX_User.side_panel_items JSONField	Same view ID can be on or off per user/template
Feature flags	msrx_viewer — read-only wizard/pricing mode	msrxViewerWizard.js:131-244; pricingManagement.js:211,229; priceZone.js:66,253	user_details.msrx_viewer trims steps, blocks commit/download
Feature flags	enable_reprocess_loan	dueDiligence/loans/loans.js:182	Button only if user_details.enable_reprocess_loan
Feature flags	enable_bedrock_processing / enable_xml_generation	dueDiligence/documents.js:81-82,428-436	Gates Bedrock re-generate and Generate XML buttons
Feature flags	authorized_mailbox_brands	emailMonitor/status.js:47-65	Controls which mailbox activate buttons appear
Feature flags	fnma_cashscreen / fhlmc_cashscreen	agencyCashScreen.js:184-187	Agency cash screen brand toggles in user_details
Feature flags	Company DD enable_* fields	duediligence/models/groupings.py:44-48 — enable_stacked_bookmarks, enable_stacked_zips, enable_validations	Company-level booleans consumed by Super Transfer
Admin-only	admin_only / staff_only / bwft_only decorators	base/decorators/user_level_decorators.py:70-112 — is_superuser / is_staff / group BWFT	API-level privilege gates; not sidebar labels
Admin-only	REST admin namespace /msrx/api/admin/	api/urls/admin.py — users, tapes, side_panel_templates, resell_config_report (@bwft_only)	Admin API surface; side_panel_templates edits what others see
Admin-only	Staff-only UI affordances	actionRowPreClose.js:17-23 (is_staff); createGrid.js:125-127 Empty Grid if is_staff	Controls appear only for staff users
Admin-only	App-level admin endpoints	duediligence admin_deals/admin_portfolios; freedom admin/loan-pipeline/; analytics admin/*; Transfer admin_boarding_*; tapecrack @admin_only SQL ops	Staff/superuser APIs outside normal nav
Dev tools	Redux DevTools compose	store/store.js — window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__	Browser extension only; not product UI
Dev tools	test_tape / test_pricing harness APIs	api/urls/index.py:224-225	Mounted pricing test endpoints; not sidebar screens
Dev tools	Seasoned valuation routes marked # TEST	api/urls/index.py:205-216 — seasoned_valuation_*	Comment marks as TEST; not fixture-sidebar features
Dev tools	Analytics local-file “dev tool”	analytics/views/analytics.py:203-206 — generates local files; TODO deprecate after Sprint 48	Backend ops helper, not sidebar
Unused APIs	seasoned_pricing_shocks — “route is never called”	api/urls/index.py:196-201 (inline comment)	Still mounted; authors mark unused
Unused APIs	Whole Loan Shadow Bid — no React client	freedom/urls.py:107 wholeloan-shadow-bid/; zero hits under msrx-frontend/client/src	EmailTrading/backend-driven; not in sidebar or FE setView
Unused APIs	CRA check — no frontend references	CRA app mounted; no msrx-frontend matches for cra-check/CRA UI	Backend-only consumer surface
Unused APIs	TapeManager format_converter_* (v1)	TapeManager/urls.py:6-30 — “v1 tape cracking method”; client-specific converters	Legacy HTTP converters; no FE nav
Unused APIs	External commit/pricing API suite	api/urls/index.py:166-183 — get-active-buyers, indicative-pricing, commit, commit-confirm, …	Token/API-key external integrations, not sidebar pages
Unused APIs	MSRX Viewer internal APIs	api/urls/index.py:152-154 — viewer_strat/, viewer_loanlevel/	Viewer-mode backends; paired with msrx_viewer flag
Dead / orphan UI	showNonQMReport — sidebar ID with no pageMaps entry	In fixtures; missing from viewMaps.js (broken target if enabled)	Would blank MainPanel if enabled
Dead / orphan UI	showQCVariables vs showDueDiligenceQCVariables mismatch	Fixture id showQCVariables; pageMaps key showDueDiligenceQCVariables	Name mismatch; sidebar click may not resolve
Dead / orphan UI	showMarketDataModal — modal special-case, not a page	sidePanel.js:46-48 opens market-data modal instead of setView	Not a pageMaps view; Resources item
Dead / orphan UI	showEmailmonitorStatus — registered, no setView caller found	viewMaps.js:272 only; no setView("showEmailmonitorStatus") under client/src	Orphan unless enabled via live DB sidebar JSON
Dead / orphan UI	showAggEmailManager / showBwWlQuick / showTrialBalances / showBulkPricing / showWlQuickCommit	Only in viewMaps.js (plus one view== compare for WlQuickCommit in aggOptions.js) — no setView navigators found	Likely dormant unless live user JSON enables them as sidebar items
Dead / orphan UI	Commented View Income navigation	dueDiligence/loans/loans.js:170-180 — setView("showQCIncome") commented	Functionality left in comments
Legacy	Legacy commit_email APIs kept mounted	api/urls/index.py:142-145 — “legacy apis, keep in here.”	Still live endpoints; not product nav
Legacy	Refinitiv helpers_v1_legacy_auth	freedom/supporting/refinitiv/helpers_v1_legacy_auth.py; helpers.py:412-414	Legacy auth path retained alongside current
Legacy	Deprecated middleware interpolator	api/supporting/support_middleware.py:808-812 — DEPRECATED !!!	Marked deprecated in code
Legacy	EmailTrading attachment helpers deprecated	EmailTrading/supporting/attachment.py:67,315,493	Moved to MSRX API; old helpers remain
Legacy	Commented xtape / xcoissueresult pages	msrx/urls.py:18-20	Fully commented URL routes
Commented	Commented external commit APIs	api/urls/index.py:128-129,158-162 — commit_loans*, api-varde-pricing, api-precommit, api-commit-confirm	Disabled by comment; code/classes may still exist
Commented	Large commented PA aggregation in commitrecon	commitrecon/views.py ~540–620+	Dead commented business logic
Commented	Bifur radio permanently disabled	step3-select.js:72 — <Radio disabled={true} value="bifur"	UI control present but unusable
Commented	Commented Freedom download/commit buttons	freedomActionRow.js:206-287	Actions removed from UI via comments
Fixture-disabled	30 sidebar IDs never enabled:true in fixtures	Parsed all msrx_v2.0/fixtures/**/*.json side_panel_items — 90 unique IDs, 60 ever enabled, 30 never	Present in templates with enabled:false; may still be flipped in live DB
Programmatic views (in pageMaps, not sidebar)
These screens are opened by in-app setView() — never listed as fixture sidebar leaves (subset of the 54).

View / group	Entry point
showTapeDetails / showCommitResults / showWizard	pricingManagement.js setView
showConstraintManager / showBulkBidData*	pools / freedom pricing drill-downs
showFreedomTapeManager	freedomActionRow.js:27
showAdjustProductSpread	configuration/aggOptions.js:21
showExceptionDetails / showExceptionBatch	exceptionManagement.js
showEditLoan	loansPreClose.js
showSeasonedLoanPipeline / showSeasonedMiniStrat	blueRate TapeManagement / PriceWorkflow
DD Create/Edit* / showMiscLoans / showQCIncome*	Due Diligence admin & loan flows
showUserProfile	headerPanel / firstTimeUserModal
Never enabled:true in any fixture (30)
Still registered as sidebar template items with enabled:false. Production users may differ.

View ID
showAgencyCashScreen
showAggregatorDocumentStore
showBoardingProgress
showDueDiligenceIncompleteDeals
showDueDiligenceIncompleteLoans
showEOD
showFreedomGrid
showGlobalSearch
showLoanManagement
showMsrxWizard
showNewPricing
showNonQMReport
showNonQMStrat
showOrder
showParRate
showParRateDashboard
showPipelineReporting
showPoolManagement
showQuickCommit
showSeasonedGetValue
showSeasonedTapeManagement
showSellerDocView
showServicingOverview
showStatus
showSupplementalFileUpload
showTradeReport
showWLSingleLoan
showWholeLoanBoarding
showWholeLoanCommitmentPipeline
showWinLoss
Highest-signal hidden surfaces
1. Per-user sidebar JSON
Primary gate. Dozens of screens exist in code but stay dark until enabled on that user or SidePanels template.

2. Staff admin panels + /api/admin/
Django admin_panel_* pages and REST admin APIs — outside the React sidebar entirely; gated by is_staff / is_superuser / BWFT.

3. Shadow Bid + TapeManager + CRA
Mounted backend features with no frontend navigation found — email/ops/external consumers only.

Method notes
Compared viewMaps.js keys to all fixture side_panel_items; grepped setView callers; scanned Django urlpatterns for admin/internal/legacy/ TEST/never-called comments; confirmed no LaunchDarkly-style SDKs. Unused-export analysis is route/comment/cross-ref based, not a full TypeScript dead-code eliminator.