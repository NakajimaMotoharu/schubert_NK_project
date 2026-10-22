"""All1405 raw retained; eighteen exact Web spans individually reviewed, Root11 held."""
import copy
import inspect
import pg6716_current4184_static_join as base
from pg6786_original4197_web_artifacts import read_whole
from pg6780_web_management_result_selected import MAIN

ROOT,W,BASE,sha=base.ROOT,base.W,base.BASE,base.sha
OLD='d549f8855fe1733bdb67543e310048dc271a8a56'
PRIOR=BASE/'PG6774-current4197-transfer-static-join-v1/manifest.json'
PRIOR_SHA='35d0612faf698480c5258930fcab172278e7ad2f6584d3c36a5a4759e1ec42bc'
QSHA='60eb1d48db665286a8cfd5d4495c51b80e1ee6cce7af282595a96f5f07f99539'
EXPECTED_RAW=1405
EXPECTED_PAIRS=1387
SUPPLEMENT={k:list(v)for k,v in base.SUPPLEMENT.items()}
SUPPLEMENT.setdefault('WebManagementServer',[]).extend(['web.bootstrap.WebManagementServerTest','web.bootstrap.WebUnstartedManagementTest','web.bootstrap.WebRuntimeStopTest'])
SPANS={
 (36,'DoNotUseThreads'):('private final ThreadPoolExecutor executor;','CONTEXT_NOT_APPLICABLE','JavaSE standalone loopback owner, not Jakarta managed executor; prepared before bind and retained until actual join.'),
 (47,'AvoidUsingVolatile'):('private volatile boolean started;','REQUIRED_CONTRACT','Successful start publishes to lock-free ready/promote/HTTP readers; stopLock alone does not cover those reads.'),
 (69,'AvoidCatchingGenericException'):('} catch (RuntimeException | Error failure) {','REQUIRED_CONTRACT','Failed startup still owns bound server; preserve original identity and perform required cleanup; never emit success.'),
 (73,'AvoidCatchingGenericException'):('} catch (RuntimeException | Error unconfirmed) {','REQUIRED_CONTRACT','Unexpected cleanup RTE/Error ranked separately; diagnostic addition from typed fixed IO occurs outside this catch, preserving old failure region. Preallocated fixed marker has no provider cause.'),
 (74,'AvoidInstanceofChecksInCatchClause'):('if (unconfirmed instanceof Error && !(failure instanceof Error)) throw unconfirmed;','REQUIRED_CONTRACT','Only cleanup Error over nonfatal primary wins; primary Error beats nonfatal cleanup. All four overlapping raw spans retained.'),
 (75,'CompareObjectsWithEquals'):('if (unconfirmed != failure) failure.addSuppressed(cleanupDiagnostic);','REQUIRED_CONTRACT','Throwable object identity prevents self-suppression; arbitrary equals would execute provider code and violate identity priority.'),
 (118,'DoNotUseThreads'):('new ThreadPoolExecutor(','CONTEXT_NOT_APPLICABLE','One private worker and bounded32 queue are acquired before bind; not borrowed container pool.'),
 (125,'DoNotUseThreads'):('var thread = new Thread(task, "web-management");','CONTEXT_NOT_APPLICABLE','Names only its own daemon worker; daemon status is not termination evidence.'),
 (225,'DoNotUseThreads'):('boolean interrupted = Thread.currentThread().isInterrupted();','CONTEXT_NOT_APPLICABLE','Snapshot caller notification immediately before own vendor stop, with mandatory actual stop/join checks.'),
 (231,'DoNotUseThreads'):('if (interrupted) Thread.currentThread().interrupt();','CONTEXT_NOT_APPLICABLE','Finally restores pre-stop interrupt even on vendor throw/clear; does not assert release.'),
 (234,'DoNotUseThreads'):('executor.shutdownNow();','CONTEXT_NOT_APPLICABLE','Requests shutdown only for this captured executor; following await/started admission remains required.'),
 (236,'DoNotUseThreads'):('if (!executor.awaitTermination(remaining.toNanos(), TimeUnit.NANOSECONDS))','CONTEXT_NOT_APPLICABLE','Finite validated remaining budget; timeout yields typed fixed IO, public wrapper still throws and no closed success is stored.'),
 (239,'DoNotUseThreads'):('Thread.currentThread().interrupt();','CONTEXT_NOT_APPLICABLE','Interrupted join restores notification and returns fixed-IO result; public close throws same result and no outer release proof is inferred.')}


def bindings():
    scope={**vars(base),'OLD':OLD,'PRIOR':PRIOR,'SUPPLEMENT':SUPPLEMENT}
    exec(compile(inspect.getsource(base.bindings),'<Web4197 bindings>','exec'),scope);return scope['bindings']()


def review_changed(row):
    if row['sourcePath']!=MAIN or row['sourceSha256']!='9e47b933695a0ff065e281c8d1bf88da32b003f66de1fcccda52fdcc587babe3':raise ValueError('one fixed Web Main only')
    item=SPANS.get((int(row['beginline']),row['rule']))
    if item is None:raise ValueError('only individually listed current spans')
    expected,status,reason=item;lines=(ROOT/MAIN).read_text().splitlines();at=int(row['beginline'])-1
    if lines[at].strip()!=expected:raise ValueError('exact current statement required')
    from pg6781_web_stop_result_equivalence import verify_source
    verify_source()
    value=copy.deepcopy(row);value.update(status=status,reason='1487/PG-D504 exact current review: '+reason,
      reviewedSourceSnippet=' | '.join(lines[max(0,at-1):min(len(lines),int(row['endline'])+2)]),rawWarningRetained=True,
      reviewMethod='EXACT_CURRENT_SPAN_STATE_MACHINE_AND_EXCEPTION_REGION',formalAccepted=False,ptAlternativeCompleted=0,
      relatedQualityEvidence='1487 original28/current4197 and structural proof; related component regression, not per-site allocation-failure causality')
    return value


def definition():
    raw=inspect.getsource(base.main)
    for before,after in (('PG6712-broker-parent-qualification-v3','PG6782-web-management-result-original-v1'),('pg6712-broker-parent-qualification-v3','pg6782-web-management-result-original-v1'),
      ('PG6716-current4184-static-join-v1','PG6790-current4197-web-static-join-v1'),('pg6716_current4184_static_join.py','pg6790_current4197_web_static_join.py'),('all8511667','all8511669')):raw=raw.replace(before,after)
    scope={**vars(base),'OLD':OLD,'PRIOR':PRIOR,'PRIOR_SHA':PRIOR_SHA,'QSHA':QSHA,'EXPECTED_RAW':EXPECTED_RAW,'EXPECTED_PAIRS':EXPECTED_PAIRS,
      'read_whole':read_whole,'bindings':bindings,'review_changed':review_changed}
    exec(compile(raw,'<Web4197 raw1405 join>','exec'),scope);return scope['main']


if __name__=='__main__':definition()()
