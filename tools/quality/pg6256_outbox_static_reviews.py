"""31 exact ordinary Outbox/log applicability sites; mixed cleanup/setup BUG1566/1567 stay open."""
import inspect
import pg6254_ss319_static_reviews as engine

R='REQUIRED_CONTRACT'
G='AvoidCatchingGenericException'
S='AvoidSynchronizedStatement'

SPEC={
 'OutboxJmsSender':{
  (38,G):(1,R,'Own JMSContext factory RuntimeException is classified as fixed unconfirmed lifecycle send failure before any stage/commit. Null context is rejected rather than treated as successful send; no provider text is emitted.'),
  (48,G):(1,R,'Staging may fail with checked JMS or unchecked provider exception. It attempts rollback then throws typed unconfirmed send, not SENT; commit is not issued on this path.'),
  (54,G):(1,R,'Commit RuntimeException is rolled back, then only exact duplicate-id cause/linked graph evidence can count as previously confirmed delivery. Other failures remain typed unconfirmed. Rollback/close suppressed edges do not manufacture duplicate confirmation.'),
  (63,G):(1,R,'Outer lifecycle RTE is wrapped once in fixed OutboxSendException and retained as primary through owned finally close. This applies to the provider failure classification only; mixed cleanup Error remains BUG1566, not approved here.'),
  (67,G):(1,R,'Original provider Error is stored as primary then rethrown as the same Error. It cannot be caught by ordinary dispatch OutboxSendException/RTE retry; the owned finally still attempts close.'),
  (81,'AvoidInstanceofChecksInCatchClause'):(1,R,'When no primary exists, cleanup Error must propagate as Error rather than be wrapped as an ordinary lifecycle send failure. This narrow type predicate is required. The separate nonnull-primary branch remains BUG1566/unclassified, not a blanket approval of cleanup.'),
  (123,G):(1,R,'Untrusted fixed-width header decoding RTE is translated to fixed OutboxIntegrityException before JMS context acquisition. It rejects invalid wire identity rather than making a dummy/success result or exposing body values.'),
  (148,G):(1,R,'Fixed payload/layout intrinsic constraint RTE is translated to fixed integrity rejection before JMS acquisition. QWKREQ01 byte/length/data constraints are independent of transport duplicate confirmation.'),
  (167,G):(1,R,'Rollback RTE is retained only as secondary failure on the still-unconfirmed primary, with reference self-suppression guard. It is not evidence of confirmed commit or permission to mark SENT; Error remains fatal rather than caught by this helper.')},
 'OwnedOutboxDispatcher':{
  (43,S):(1,R,'Private final lock serializes one-shot start/stopping state and worker start against wake/close. It is not this/class or caller data; before-start create does not claim a thread is alive.'),
  (51,S):(1,R,'Private lock publishes wake only to this already-started healthy worker and notifies the same guarded wait. Wake does not perform DB/JMS work while request transaction is held.'),
  (60,S):(1,R,'Healthy reads started/stopping/failed under the same private monitor used by writes. It is a component state result, not proof of Root/native termination or active ownership.'),
  (68,S):(1,R,'Own worker wait/signalled/stopping state is read/reset atomically under private lock; fallible DB/JMS dispatch occurs after leaving the monitor. This does not hold a monitor through remote I/O.'),
  (77,'EmptyCatchBlock'):(1,R,'A failed dispatch leaves durable leases/retry rows authoritative. The bounded later cycle does not mark SENT from an exception, expose raw text or replay an uncommitted request transaction. Exhaustion/lease SQL has separate tests; this is not fatal Error normalization.'),
  (77,G):(1,R,'Only SQL/RTE temporary dispatch failures reach this durable retry cycle. Error has its own outer failure publication/rethrow. The same warning does not approve newly found cleanup Error demotion inside sender BUG1566.'),
  (84,S):(1,R,'Interrupted own worker publishes failed=true and notifies under the same private monitor after restoring interrupt. It does not represent successful shutdown or normal processing.'),
  (88,G):(1,R,'Worker Error must publish failed and wake health waiters before rethrowing the identical Error to its fixed redacted uncaught handler. No Error message/cause is logged and no ordinary retry is selected here.'),
  (89,S):(1,R,'Fatal state publication uses the same private lock as healthy/wake/start; notification cannot race a plain failed read. The lock is local to the owned worker.'),
  (101,S):(1,R,'Close publishes stopping and notifies only its own worker before actual join outside the lock. Self-join is rejected. Requesting stop/daemon state is not completion, and actual native/Unit deadline remains a separate unverified criterion.')},
 'OutboxDispatcher':{
  (45,G):(1,R,'Only typed send failure or RTE is converted to durable send-failure/lease-lost accounting; markSent occurs exclusively after sender returns normally. Direct Error is not caught here. BUG1566 covers lower-layer Error demotion, so this does not certify whole dispatch safety.'),
  (68,G):(1,R,'Claim transaction rolls back SQL/RTE then rethrows, and its returned Connection is in TWR. Claim must commit before any separate JMS send. Unreturned setup Error is a distinct BUG1567 outside this protected claim scope.'),
  (81,G):(1,R,'Short markSent transaction rolls back and rethrows SQL/RTE, never holds the DB transaction across JMS send. Lease compare-and-set and current timing semantics stay in repository tests; no SENT result on rollback failure.'),
  (95,G):(1,R,'Short markFailure transaction rolls back and rethrows SQL/RTE rather than reporting a durable retry mark that did not commit. Its own Connection closes through TWR; BUG1567 setup gap is not classified here.')},
 'WebLogDispatcher':{
  (85,G):(1,R,'The inner SQL/RTE transaction catch retains primary before best-effort rollback and rethrows it. Claimed rows and result marks remain separately committed around JMS, not one transaction held over network send.'),
  (89,G):(1,R,'Rollback SQL/RTE failure is only distinct suppressed diagnostic on the original transaction failure; it does not turn failed action/commit into success or markSent.'),
  (91,G):(1,R,'A rollback Error is propagated as Error after retaining the earlier nonfatal SQL/RTE failure. Outer ownership finally still closes; Error does not enter ordinary send-failure accounting.'),
  (97,G):(2,R,'Outer SQL/RTE/Error capture sets primary then rethrows the same failure so finally close cannot manufacture success. This covers setup Error immediately after acquiring the connection, unlike BUG1567 unreturned factory gap. Both overlapping unchecked spans are retained.'),
  (109,G):(2,R,'Owned connection close SQL/RTE/Error is explicit. With no primary it propagates; with primary, fatal priority and reference identity are applied before rethrowing/retaining failure. Normal close is not a DB commit receipt.'),
  (111,'AvoidInstanceofChecksInCatchClause'):(1,R,'Distinct cleanup Error is propagated as Error, retaining primary; self-reference is excluded. This implements the existing Web-log compound exception contract rather than replacing Error by a retryable SQL/RTE wrapper. It does not impose a different same-fatal ranking on unrelated owners.')}
}


def calculate():
    raw=inspect.getsource(engine.calculate)
    raw=raw.replace('spec=specifications()','spec=SPEC')
    start=raw.index('        prefixes=');end=raw.index('        decisions.append',start)
    raw=raw[:start]+"        refs=[]  # No relevant selected113 XML; actual current whole join remains mandatory.\n"+raw[end:]
    raw=raw.replace('len(decisions)!=117','len(decisions)!=31').replace('all117','all31').replace('reviewed=117','reviewed=31').replace('1330 individual','1331 individual')
    scope={**vars(engine),'PLAN':engine.BASE/'PG6254-ss319-static-review-v1/manifest.json',
        'PLAN_SHA':'6b793f008695b4a68a21fcc9d5c082d43a45414ebfc07981db21b117344124ad','SPEC':SPEC}
    exec(compile(raw,'<31 exact ordinary Outbox source scopes>','exec'),scope)
    rows,value=scope['calculate']()
    value['unresolved']+=['OutboxJmsSender close catch primary-nonfatal/cleanup Error BUG1566 not classified',
        'OutboxDispatcher unreturned setup Error BUG1567 not classified',
        'No relevant selected113 case refs; genuine current whole case join required, no historical PT imported']
    return rows,value


def main():
    import json
    import os
    rows,value=calculate();os.umask(0o077);out=engine.BASE/'PG6256-outbox-static-review-v1';out.mkdir()
    with(out/'decisions.json').open('x')as f:json.dump(rows,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value['decisionsSha256']=engine.sha(out/'decisions.json')
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,reviewed=31,statusCounts=value['statusCounts'],manifestSha256=engine.sha(out/'manifest.json'))))


if __name__=='__main__':main()
