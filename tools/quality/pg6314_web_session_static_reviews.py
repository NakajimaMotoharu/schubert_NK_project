"""Fourteen current ordinary Web lifecycle/session spans; startup gaps stay held."""
import inspect
import json
import os
import pg6284_web_owned_static_reviews as engine
from pg6298_web_send_qualification import original_source

G='AvoidCatchingGenericException';S='AvoidSynchronizedStatement'
SPEC={
 'EncryptedWebSessionRepository':{
 (305,G):(2,'Both unchecked transaction-body spans keep failure inside the acquired Connection scope. One rollback is attempted before fixed SessionStoreException; direct or nested Error is preserved by the identity-visited cause/suppressed graph, not classified as a valid session. Normal commit precedes return and connection close. This is applicability of the boundary, not blanket proof of all vendor close combinations.'),
 (308,G):(2,'Both unchecked rollback-secondary spans attach only a distinct Throwable to the original, then preserveFatal checks the combined graph before fixed redaction. Failure never becomes a committed mutation, API authorization, or new session. The borrowed DataSource/codec remain outer-owned.'),
 (314,G):(1,'Outer RTE including generated TWR self-suppression failure is inspected for nested Error before fixed SessionStoreException. SQL/close failure cannot escape as a successful snapshot; raw provider details are not retained. Existing transaction/concurrency and Logout fatal/cyclic fixtures supply semantic references, not native completion.')},
 'LocalLogoutCoordinator':{
 (80,G):(2,'Both unchecked Logout-body spans still attempt local invalidation and then preserve the full transient fatal graph before fixed redaction. Only explicit approved wire codes can select CONFIRMED; durable invalidate-and-retain must return normally for QUEUED. Neither exception branch invents remote revoke or local commit success.'),
 (83,G):(2,'Both unchecked invalidation-cleanup spans retain only a distinct secondary on the original. preserveFatal follows identity-visited causes/suppressed even for cyclic provider failures, then emits a fixed catalog failure. This is not retry authorization or proof that failed local destruction completed.')},
 'WebProcessLifetime':{
 (26,S):(1,'Private stateLock serializes hook registration with owner close, not this/class/caller monitors. installed is published only after addShutdownHook returns normally; duplicate registration is rejected. Registration is not VM/process ownership certification.'),
 (81,S):(1,'The same private stateLock serializes installed removal and the finally finished notification. The latch is released only when the caller invokes close after confirmed owned scopes; shutdown-in-progress does not restart or close providers. Remaining unmeasured hook branches are not marked covered by this review.')},
 'WebRuntimeStop':{
 (34,G):(1,'The current confirmed phase advances only after normal close. Checked/RTE failure is inspected for nested fatal identity then converted to fixed IOException, without running a later phase or extending the original deadline. Direct Error is uncaught. Actual runtime stop/postconditions remain a separate held dependency.')},
 'WebLogApplicationRuntime':{
 (249,S):(1,'Private stopLock serializes the exact http/replay/replies owner sequence and stoppedResources cursor. Failure retains the current phase and downstream borrowers; success alone increments its cursor. Public readiness/stopping atomics do not substitute for actual external ownership evidence.'),
 (256,G):(1,'AutoCloseable checked failure and RTE stop at the same resource, preserve any nested Error, and emit fixed unconfirmed state. closed is set only after all three normal returns. This reason deliberately excludes startup catch221 and cleanup270/274, whose compound ownership is still unreviewed.')}
}
TESTS={
 'EncryptedWebSessionRepository':['dev.codex.schubert.nk.web.session.EncryptedWebSessionRepositoryTest','dev.codex.schubert.nk.web.revocation.LocalLogoutCoordinatorTest'],
 'LocalLogoutCoordinator':['dev.codex.schubert.nk.web.revocation.LocalLogoutCoordinatorTest'],
 'WebProcessLifetime':['dev.codex.schubert.nk.web.bootstrap.WebProcessLifetimeTest'],
 'WebRuntimeStop':['dev.codex.schubert.nk.web.bootstrap.WebRuntimeStopTest'],
 'WebLogApplicationRuntime':['dev.codex.schubert.nk.web.bootstrap.WebLogApplicationRuntimeTest']}


def calculate():
    scope={**vars(engine),'PLAN':engine.BASE/'PG6310-web321-static-review-v1/manifest.json',
        'PLAN_SHA':'d848def968743126450d2e5d770c986e00e23352f0bdb57a42ef6b5e07425fe9',
        'SPEC':SPEC,'TESTS':TESTS,'original_source':original_source}
    raw=inspect.getsource(engine.calculate)
    for a,b in (('PG6268-outbox-failure-qualification-v1','PG6298-web-send-qualification-v1'),
        ('pg6268-outbox-failure-qualification-v1','pg6298-web-send-qualification-v1'),
        ('d4e587322de799db097dab934611431448b229953bae5838aa721b7c51ac0225','00b8f41991bf05c2aaf439cc502ecf6afba47f9247587684941ee168dbc75c27'),
        ('len(decisions)!=33','len(decisions)!=14'),('all33 explicit','all14 explicit'),('reviewed=33','reviewed=14'),
        ('rawFindings=1350','rawFindings=1357'),('1338 individual ordinary Web','1346 individual current session/lifecycle')):
        if a not in raw:raise ValueError('one explicit current84/static binding '+a)
        raw=raw.replace(a,b)
    exec(compile(raw,'<14 current ordinary Web spans>','exec'),scope)
    rows,value=scope['calculate']()
    value['unresolved']=['actual current4043 case binding pending','startup221/270/274 remains unreviewed; hook gaps, native/runtime/global quality not certified']
    return rows,value


def main():
    rows,value=calculate();os.umask(0o077);out=engine.BASE/'PG6314-web-session-static-review-v1';out.mkdir()
    with(out/'decisions.json').open('x')as f:json.dump(rows,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value['decisionsSha256']=engine.sha(out/'decisions.json')
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,reviewed=14,statusCounts=value['statusCounts'],manifestSha256=engine.sha(out/'manifest.json'))))


if __name__=='__main__':main()
