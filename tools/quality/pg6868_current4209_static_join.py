"""All1409 raw retained; twenty-two current Web spans individually reviewed, Root11 still held."""
import copy
import inspect
import pg6716_current4184_static_join as base
import pg6834_current4203_static_join as prior
from pg6864_original4209_artifacts import read_whole
from pg6860_web_deadline_structure import MAIN,verify_source

ROOT,W,BASE,sha=base.ROOT,base.W,base.BASE,base.sha
OLD='4c0343a55b5fe41dad766a520558363e81f01541'
PRIOR=BASE/'PG6834-current4203-static-join-v1/manifest.json'
PRIOR_SHA='a84ea30d8138161a229cadee6dd58ccff646be907f01a082ad6b361b8707aa82'
QSHA='69dba2782be8034e9efac8505b5019d466da0100bd1a3bc105f57760b61466fd'
EXPECTED_RAW=1409
EXPECTED_PAIRS=1387
SUPPLEMENT={k:list(v)for k,v in prior.SUPPLEMENT.items()}
for name in('web.bootstrap.WebManagementServerTest','web.bootstrap.WebUnstartedManagementTest','web.bootstrap.WebRuntimeStopTest','web.bootstrap.WebManagementDeadlineTest'):
    if name not in SUPPLEMENT.setdefault('WebManagementServer',[]):SUPPLEMENT['WebManagementServer'].append(name)
SPANS={
 (36,'DoNotUseThreads'):('private final ThreadPoolExecutor executor;','CONTEXT_NOT_APPLICABLE','Standalone loopback management owns a private executor, not a Jakarta-managed container executor. Owner/state are prepared before bind.'),
 (47,'AvoidUsingVolatile'):('private volatile boolean started;','REQUIRED_CONTRACT','Readiness handler and stopping owner need actual normal-start visibility. Volatile does not prove socket release or replace the stop lock; deleting it creates a data race.'),
 (70,'AvoidCatchingGenericException'):('} catch (RuntimeException | Error failure) {','REQUIRED_CONTRACT','Startup failure still owns the bound server. Clean up while preserving original checked-IO/Runtime/Error boundary and direct fatal priority.'),
 (73,'AvoidCatchingGenericException'):('} catch (RuntimeException | Error unconfirmed) {','REQUIRED_CONTRACT','Unexpected cleanup failure cannot disclose its raw graph. Preserve old identity/priority; known fixed IO results add only preallocated diagnostic outside this catch.'),
 (74,'AvoidInstanceofChecksInCatchClause'):('if (unconfirmed instanceof Error && !(failure instanceof Error)) throw unconfirmed;','REQUIRED_CONTRACT','Direct cleanup fatal wins only over nonfatal primary. All overlapping warning spans are retained; provider equals/polymorphic substitution cannot preserve this priority.'),
 (75,'CompareObjectsWithEquals'):('if (unconfirmed != failure) failure.addSuppressed(cleanupDiagnostic);','REQUIRED_CONTRACT','Throwable identity avoids self-suppression and provider equals callback. Only the existing preallocated fixed marker is attached.'),
 (118,'DoNotUseThreads'):('new ThreadPoolExecutor(','CONTEXT_NOT_APPLICABLE','One owned management worker with bounded32 queue, prepared before bind; standalone service and not application-container thread replacement.'),
 (125,'DoNotUseThreads'):('var thread = new Thread(task, "web-management");','CONTEXT_NOT_APPLICABLE','Fixed-name owned daemon handler. Daemon status never proves termination; actual executor join and socket release remain mandatory.'),
 (223,'DoNotUseThreads'):('boolean entryInterrupted = Thread.interrupted();','CONTEXT_NOT_APPLICABLE','SSC335 clears an entry notification only for finite lock acquisition. It is restored before vendor stop and on every exit; unlike API it is not cleared through the join.'),
 (229,'DoNotUseThreads'):('Thread.currentThread().interrupt();','CONTEXT_NOT_APPLICABLE','New interrupt during finite lock wait restores the flag and returns fixed IO unknown; vendor stop/closed success are not issued.'),
 (233,'DoNotUseThreads'):('if (entryInterrupted) Thread.currentThread().interrupt();','CONTEXT_NOT_APPLICABLE','Restore entry notification before the unchanged Web vendor-stop/await state table. API semantics cannot be copied to Web.'),
 (237,'DoNotUseThreads'):('boolean interrupted = Thread.currentThread().isInterrupted();','CONTEXT_NOT_APPLICABLE','Unchanged Web snapshot before its JDK stop; original caller notification remains visible to vendor and is preserved afterward.'),
 (243,'DoNotUseThreads'):('if (interrupted) Thread.currentThread().interrupt();','CONTEXT_NOT_APPLICABLE','Preserve original vendor-visible notification even if stop clears it. The following await remains interrupted/unknown, not a successful receipt.'),
 (246,'DoNotUseThreads'):('executor.shutdownNow();','CONTEXT_NOT_APPLICABLE','Request shutdown of this captured private executor only. The following actual finite await/start checks precede closed completion.'),
 (248,'DoNotUseThreads'):('if (!executor.awaitTermination(','CONTEXT_NOT_APPLICABLE','Await consumes the same nano deadline after lock and vendor stop, clamped finite zero, never a fresh full duration or inferred termination.'),
 (252,'DoNotUseThreads'):('Thread.currentThread().interrupt();','CONTEXT_NOT_APPLICABLE','Interrupted executor join restores notification and returns fixed IO unknown. Success cache/outer release must not be fabricated.'),
 (262,'DoNotUseThreads'):('if (entryInterrupted) Thread.currentThread().interrupt();','CONTEXT_NOT_APPLICABLE','Outer finally restores entry notification on acquisition timeout, new IRQ, normal return and unexpected failure. Unlock remains in its acquired-only finally.')}


def bindings():
    scope={**vars(base),'OLD':OLD,'PRIOR':PRIOR,'SUPPLEMENT':SUPPLEMENT}
    exec(compile(inspect.getsource(base.bindings),'<current4209 bindings>','exec'),scope);return scope['bindings']()


def review_changed(row):
    if row['sourcePath']!=MAIN or row['sourceSha256']!='faf5d362d6fbd723fce76e471708c1092563b2c09762ef6460e427df5991354a':raise ValueError('one exact finite-stop Web Main')
    item=SPANS.get((int(row['beginline']),row['rule']))
    if item is None:raise ValueError('one explicitly reviewed current Web span')
    expected,status,reason=item;lines=(ROOT/MAIN).read_text().splitlines();at=int(row['beginline'])-1
    if lines[at].strip()!=expected:raise ValueError('exact current Web statement')
    verify_source();value=copy.deepcopy(row)
    value.update(status=status,reason='1501/1502/1503 PG-D509 SS335 current review: '+reason,
      reviewedSourceSnippet=' | '.join(lines[max(0,at-1):min(len(lines),int(row['endline'])+2)]),rawWarningRetained=True,
      reviewMethod='EXACT_CURRENT_WEB_SPAN_SHARED_DEADLINE_ORIGINAL_IRQ_STATE_AND_EXCEPTION_REGION',formalAccepted=False,ptAlternativeCompleted=0,
      relatedQualityEvidence='Genuine old three finite own-fixture timeouts, identical-oracle original42/current4209 and strict structural expansion; not vendor preemption, per-site heap failure, actual Root or native evidence')
    return value


def definition():
    raw=inspect.getsource(base.main)
    for before,after in(('PG6712-broker-parent-qualification-v3','PG6854-web-deadline-original-v1'),('pg6712-broker-parent-qualification-v3','pg6854-web-deadline-original-v1'),
      ('PG6716-current4184-static-join-v1','PG6868-current4209-static-join-v1'),('pg6716_current4184_static_join.py','pg6868_current4209_static_join.py'),('all8511667','all8511669')):raw=raw.replace(before,after)
    scope={**vars(base),'OLD':OLD,'PRIOR':PRIOR,'PRIOR_SHA':PRIOR_SHA,'QSHA':QSHA,'EXPECTED_RAW':EXPECTED_RAW,'EXPECTED_PAIRS':EXPECTED_PAIRS,
      'read_whole':read_whole,'bindings':bindings,'review_changed':review_changed}
    exec(compile(raw,'<current4209 raw1409 join>','exec'),scope);return scope['main']


if __name__=='__main__':definition()()
