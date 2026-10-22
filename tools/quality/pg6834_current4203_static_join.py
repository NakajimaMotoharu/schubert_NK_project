"""All1405 raw retained, eighteen API current statements individually reviewed; Root11 held."""
import copy
import inspect
import pg6716_current4184_static_join as base
from pg6830_original4203_artifacts import read_whole
from pg6822_api_stop_result_equivalence import MAIN,verify_source

ROOT,W,BASE,sha=base.ROOT,base.W,base.BASE,base.sha
OLD='484c92f1ba158a669be3bf68d26b59d8d4622cbd'
PRIOR=BASE/'PG6812-current4202-static-join-v1/manifest.json'
PRIOR_SHA='000e8bfd09e86d50927b847befcb85a8d83751d14ef38bc094324141f6b13c17'
QSHA='8098c42d9af5490123b9a60fcfcb7a79c8f9f432862a34864078a4cb11e16f59'
EXPECTED_RAW=1405
EXPECTED_PAIRS=1387
SUPPLEMENT={k:list(v)for k,v in base.SUPPLEMENT.items()}
SUPPLEMENT.setdefault('ApiManagementServer',[]).extend(['api.bootstrap.ApiManagementServerTest','api.bootstrap.ApiManagementBindTest','api.bootstrap.ApiManagementStopTest','api.bootstrap.ApiManagementDefaultBindTest'])
SPANS={
 (35,'DoNotUseThreads'):('private final ThreadPoolExecutor executor;','CONTEXT_NOT_APPLICABLE','Standalone loopback management owns its private executor; not a Jakarta container thread. Owner prepares queue/state before factory.'),
 (67,'AvoidCatchingGenericException'):('} catch (RuntimeException | Error failure) {','REQUIRED_CONTRACT','Failed startup still owns bound server. Both RTE/Error require cleanup; preserve primary identity and fatal priority, never report ready or release.'),
 (70,'AvoidCatchingGenericException'):('} catch (RuntimeException | Error unconfirmed) {','REQUIRED_CONTRACT','Unexpected cleanup graph is not published. Direct fatal ranking/same-instance handling unchanged; known fixed Runtime result adds the existing preallocated marker outside this catch.'),
 (71,'AvoidInstanceofChecksInCatchClause'):('if (unconfirmed instanceof Error && !(failure instanceof Error)) throw unconfirmed;','REQUIRED_CONTRACT','Only cleanup Error over nonfatal primary wins. All four overlapping PMD spans retained; polymorphic equality cannot replace this explicit priority.'),
 (72,'CompareObjectsWithEquals'):('if (unconfirmed != failure) failure.addSuppressed(cleanupDiagnostic);','REQUIRED_CONTRACT','Throwable identity prevents self-suppression; no provider equals callback. Distinct unexpected secondary only permits the fixed preallocated marker.'),
 (116,'DoNotUseThreads'):('new ThreadPoolExecutor(','CONTEXT_NOT_APPLICABLE','One owned worker/bounded32 queue prepared before bind, not a borrowed container-managed executor.'),
 (123,'DoNotUseThreads'):('var thread = new Thread(task, "api-management");','CONTEXT_NOT_APPLICABLE','Fixed-name own daemon handler; daemon does not prove termination or authorize unrelated thread manipulation.'),
 (222,'DoNotUseThreads'):('boolean interrupted = Thread.interrupted();','CONTEXT_NOT_APPLICABLE','SSC313 captures and temporarily clears preexisting interrupt before timed lock/join, restoring it on every exit. No success inference from the flag.'),
 (228,'DoNotUseThreads'):('Thread.currentThread().interrupt();','CONTEXT_NOT_APPLICABLE','Timed lock interruption restores notification and returns fixed unknown result; public close throws it and no success flag is set.'),
 (238,'DoNotUseThreads'):('executor.shutdownNow();','CONTEXT_NOT_APPLICABLE','Shutdown request only targets this captured executor; actual finite join and started checks still precede closed success.'),
 (240,'DoNotUseThreads'):('if (!executor.awaitTermination(','CONTEXT_NOT_APPLICABLE','Join consumes the same original System.nanoTime deadline minus current time, clamped finite zero; timeout remains unknown, not normal completion.'),
 (244,'DoNotUseThreads'):('Thread.currentThread().interrupt();','CONTEXT_NOT_APPLICABLE','Interrupted join restores current flag and returns fixed Runtime unknown; public boundary throws without closed success or outer release.'),
 (254,'DoNotUseThreads'):('if (interrupted) Thread.currentThread().interrupt();','CONTEXT_NOT_APPLICABLE','Outer finally restores preexisting notification on every outcome; no native owner/service termination is inferred.')}


def bindings():
    scope={**vars(base),'OLD':OLD,'PRIOR':PRIOR,'SUPPLEMENT':SUPPLEMENT}
    exec(compile(inspect.getsource(base.bindings),'<current4203 bindings>','exec'),scope);return scope['bindings']()


def review_changed(row):
    if row['sourcePath']!=MAIN or row['sourceSha256']!='1dce86f75aa63c99fb60cdaacdf9f0f1556912b8da92bf178aff3ec61dac4507':raise ValueError('one exact API Main source')
    item=SPANS.get((int(row['beginline']),row['rule']))
    if item is None:raise ValueError('one individually listed current API span')
    expected,status,reason=item;lines=(ROOT/MAIN).read_text().splitlines();at=int(row['beginline'])-1
    if lines[at].strip()!=expected:raise ValueError('exact current API statement')
    verify_source();value=copy.deepcopy(row)
    value.update(status=status,reason='1495/PG-D506 exact current API review: '+reason,
      reviewedSourceSnippet=' | '.join(lines[max(0,at-1):min(len(lines),int(row['endline'])+2)]),rawWarningRetained=True,
      reviewMethod='EXACT_CURRENT_SPAN_RUNTIME_RESULT_DEADLINE_AND_EXCEPTION_REGION',formalAccepted=False,ptAlternativeCompleted=0,
      relatedQualityEvidence='1495/1496 original30/current4203 and exact five-outcome source proof; related regression, not per-site heap-exhaustion causality')
    return value


def definition():
    raw=inspect.getsource(base.main)
    for before,after in (('PG6712-broker-parent-qualification-v3','PG6826-api-management-result-original-v1'),('pg6712-broker-parent-qualification-v3','pg6826-api-management-result-original-v1'),
      ('PG6716-current4184-static-join-v1','PG6834-current4203-static-join-v1'),('pg6716_current4184_static_join.py','pg6834_current4203_static_join.py'),('all8511667','all8511669')):raw=raw.replace(before,after)
    scope={**vars(base),'OLD':OLD,'PRIOR':PRIOR,'PRIOR_SHA':PRIOR_SHA,'QSHA':QSHA,'EXPECTED_RAW':EXPECTED_RAW,'EXPECTED_PAIRS':EXPECTED_PAIRS,
      'read_whole':read_whole,'bindings':bindings,'review_changed':review_changed}
    exec(compile(raw,'<current4203 raw1405 join>','exec'),scope);return scope['main']


if __name__=='__main__':definition()()
