Exception handling & fault tree
Inventory of ~4,187 handlers across Django, Express/React, and document workers. Catch-alls dominate; almost no typed recovery, APM, or global process handlers.

4187
Total handlers
~2,682
except Exception
~344
Bare except:
~29
transaction.atomic sites
Dominant pattern
Catch-all → print/activity_log → return failure JSON or swallow. No Sentry/Datadog, no DRF EXCEPTION_HANDLER, no Express 4-arg error middleware, no React ErrorBoundary, no process.on(uncaughtException|unhandledRejection).
Handler volume by layer
Layer	Mechanism	Count
Django API (msrx_v2.0)	except	1942
Document workers (super_transfer_client)	except	1216
Express BFF + React (msrx-frontend)	.catch / try	1029
Django apps (except density)
App	except	Exception	bare	atomic
api
549	457	78	7
freedom
435	378	40	6
duediligence
280	178	88	14
TapeManager	126	96	27	0
supertransfer	118	100	16	1
EmailTrading	81	68	10	0
Transfer	75	37	31	1*
analytics	72	66	4	0
commitrecon	37	30	4	1
Bloomberg
31	0	29	0
* Transfer uses one raw conn.rollback() in RoundPoint file_generators. Due diligence QC rules contribute most bare excepts (operations.py returns True on failure).

Fault tree
User-visible / data fault
Blank / modal error UI
API returns status:false
Partial DB write
Silent wrong result
Process / request hang
Render throw
(no ErrorBoundary)
BFF .catch empty body
View catch-all
→ Response(str(e))
ActivityLogMiddleware
process_exception
Multi-step save
without atomic()
msr_commit DD fail
commit still True
QC ops bare except
→ return True
@handle_exception
→ return None
extract* field skip
defaults
Middleware __call__
except → return None
No Node uncaught /
unhandledRejection
Axios interceptor
reject (status false / 503)
Fault tree (OR gates implied): top event occurs if any child branch fires. Source: static audit of msrx_v2.0, msrx-frontend, super_transfer_client.

Central mechanisms
ActivityLogMiddleware
Catch: all Exception in process_exception; also __call__ catch-all

User message: "Something went wrong" (500 JSON); exception_log stripped before client

Logging: print_exception + APIActivityLog on success path

Rollback: none (business txns independent)

Gap: __call__ except prints and returns None — no HTTP response

@try_except (Django)
Catch: Exception

User message: configurable; default "Something went wrong."

Response shape: Response({False, error_msg}) — set literal, likely buggy

Escape: swallowed; no re-raise

Express axios interceptor
Trigger: backend status===false → reject @400; network → fabricate 503

Logging: pino logger.error / info

Routes: ~399 .catch → often empty body, status only

Retry: none

STC @handle_exception + HTTP retry
Decorator: catch-all → print → return None

request_with_retry: 3× on 429/5xx + RequestException, exponential backoff, then re-raise

Extractors: field-level skip / defaults (~885 excepts)

Dimension analysis

Possible exceptions (what is actually caught)
~85% catch-all Exception or bare except. Typed catches are rare (~5%): IntegrityError (loan_tracking retry), Model.DoesNotExist, requests.RequestException (workers), ValueError, AWS ClientError, Bloomberg RequestError / PriceUpdateError / MSRUpdateError.

No shared AppError / DomainError hierarchy. Business “exceptions” modules (supertransfer/views/exceptions.py) are domain objects, not Python exceptions.


Recovery logic
Layer	Typical recovery	Risk
API views	Return {status:false, details:str(e)}; stop request	No compensate; partial side effects may remain
QC rules (operations.py)
Bare except → return True (rule passes)	False-negative QC / silent pass
STC extract*
Skip field / use default / continue loan	Incomplete extraction treated as success
loan_tracking IntegrityError
Re-fetch under select_for_update	Real recovery (race)
msr_commit DD create fail
Log warning; commit still success	Commit/DD inconsistency
React handleError	setErrorObject + setErrorModal(true)	No retry; modal only

Rollback & database transactions
Django transaction.atomic() auto-rolls back if an exception leaves the block. Only ~29 explicit sites (duediligence views/utils heaviest; also msr_commit, tape_management, api_handler, serializers, volume_caps, RoundPoint conn.rollback).

Gap
Vast majority of multi-step .save() paths have no atomic wrapper — mid-flight failure can persist partial state. Middleware logging writes are not transactional with business ops.

User-facing messages
Surface	Message
View catch-all (common)	Raw str(e) in details — info disclosure
Middleware process_exception	"Something went wrong"
@try_except default	"Something went wrong."
Express route .catch	Often empty HTTP body; status code only
React apiHoc	Error modal via props.setErrorObject(err)
EmailTrading / MSR commit fail	Email to admins (+ sanitized client mail)
Workers	N/A (batch); status via MSRX APIs

Logging
print_exception
Traceback to console (Django + workers). Primary debug path.

activity_log / APIActivityLog
Per-request audit; stores path, bodies, tokens, response codes.

Express logger
Interceptor logs success/error; no email from logger path.


Monitoring & alerting

Retry behavior

Unhandled & weak paths
#	Issue	Impact
1
Middleware __call__ returns None on exception	Hung / empty WSGI response
2
No Node uncaughtException / unhandledRejection	BFF process crash risk
3
No React ErrorBoundary	White screen on render throws
4
QC bare except → True	Rules silently pass
5
@handle_exception → None	Silent worker data loss
6
Most writes lack atomic()	Partial persistence
7
str(e) in API JSON	Leak internals to client
8
Express empty .catch body	Opaque client errors
9
msr_commit DD soft-fail	Commit OK, DD missing
10
Views without try rely only on middleware	Generic 500 if process_exception runs
End-to-end request fault path
React axios → handleError modal ← Express route .catch (empty) ← axios interceptor (status false → 400 / network → 503) ← Django view try/except (str(e) JSON) ← else ActivityLogMiddleware.process_exception ("Something went wrong") ← else WSGI / hang if middleware __call__ swallows

Parallel: STC worker → request_with_retry → Django API same path; local extract* swallows field errors without user UI.

Highest-value review targets