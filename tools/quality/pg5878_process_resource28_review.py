"""Twenty-eight specified query-release failure sites; no query/process/runtime/PT execution."""
import copy
import json
import os
from collections import Counter
from pg5540_snapshot_scratch_selected import ROOT,sha
from pg5800_rollback_green import source_test_names
from pg5860_terminal_whole import SOURCE,W
from static_disposition_overlay import BASE,load

PATH='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/ProcessResourceScope.java'
TEST='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ProcessResourceScopeTest.java'
EXPECTED=Counter({('AvoidCatchingGenericException',n):2 for n in(44,48,68,71)})|Counter({('AvoidInstanceofChecksInCatchClause',n):2 for n in(49,50,51,52,53,72,73,74,75,77)})
METHODS={'queryown001LiteralTwentyFourFailurePriorityRows','queryown002FactoryAndNullBoundariesNeverReleaseUnownedResource','queryown003SharedAndPreexistingExceptionsKeepIdentityWithoutSelfSuppression','queryown004ParallelScopesRetainDistinctOwnersAndReverseNestedRelease'}


def verify_shape(text):
    counts={'catch (IOException | InterruptedException | RuntimeException | Error primary)':2,'catch (RuntimeException | Error cleanup)':2,'primary instanceof IOException':2,'primary instanceof InterruptedException':4,'primary instanceof StopGateException':2,'!(cleanup instanceof StopGateException)':2,'Thread.currentThread().interrupt();':2,'throw cleanup;':2,'primary.addSuppressed(new StopGateException(StopGateFailure.COMMAND_FAILURE));':2,'throw primary;':2,'if (resource != null) {':1}
    if any(text.count(fragment)!=count for fragment,count in counts.items()):raise ValueError('SS333/343 fixed checked-stop/unknown priority, cancellation and single-release shapes')
    if text.index('@Nullable R resource = acquire.open();')>text.index('R owned;'):raise ValueError('factory not protected as already-owned resource')


def main():
    parent=BASE/'PG5874-storage-resource18-v1/manifest.json';digest='cf5b78c76561861ef2a4a034ce88924312f7ffb10c4c72089f83af8f22607e3d';rows=load(parent,digest,SOURCE);text=(ROOT/PATH).read_text();verify_shape(text)
    proofp=W/'pg5858-terminal-static-v1/manifest.safe.json';proof=json.loads(proofp.read_bytes())
    if proof['source']!=SOURCE or proof['actualExit']!=0 or proof['allSourceHashes'][PATH]!=sha(ROOT/PATH):raise ValueError('current exact source/compiled Main')
    names=source_test_names(ROOT/TEST)
    if len(names)!=7 or not METHODS<=names or 'String[] winner = {"Ncre", "bbce", "bbce", "bbce", "bbbb", "bbbb"};'not in(ROOT/TEST).read_text():raise ValueError('independent literal six-by-four failure oracle and four scope method identities')
    targets=[r for r in rows if r['sourcePath']==PATH and r['status']=='NOT_REVIEWED_CURRENT_SOURCE']
    if len(targets)!=28 or Counter((r['rule'],int(r['beginline']))for r in targets)!=EXPECTED or any(r['sourceSha256']!=sha(ROOT/PATH)for r in targets):raise ValueError('exact eight catch/twenty type rows; existing two thread premises not reclassified')
    decisions=[]
    for row in targets:
        method='acquire'if int(row['beginline'])<60 else'use';value=copy.deepcopy(row)
        value.update(status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',priorDisposition='REQUIRED_CONTRACT',newDispositionCreated=True,reason='SS333 SSC063/308 and SS343 specify query cleanup: known IO/interruption/StopGate body versus unknown cleanup selects the same unknown cleanup and retains cancellation; otherwise the original primary node survives with a fixed path-free COMMAND_FAILURE secondary. The '+method+' catch/type site neither normalizes unknown failure to success nor proves external process completion. The current complete source and separate literal24-row normal/known/unknown priority table, null/factory/shared/nested/parallel contracts were reviewed. Current full XML joins remain pending.',reviewedMethod=method,relatedDesign=['SS333 SSC063/308','SS343 query/stop scope'],programId='NK-OPS-001',testIds=['QUERYOWN001..004'],plannedCurrentTestRefs=[{'class':'dev.codex.schubert.nk.batch.platform.ProcessResourceScopeTest','method':n}for n in sorted(METHODS)],currentWholeCaseRefs=[],currentWholeJoinPending=True,rawWarningRetained=True,currentPhysicalProofSha256=sha(proofp),noPtExecutedByReview=True)
        decisions.append(value)
    out=BASE/'PG5878-process-resource28-v1';os.umask(0o077);out.mkdir();dp=out/'decisions.json'
    with dp.open('x')as f:json.dump(decisions,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    counts=Counter(r['status']for r in rows);counts['NOT_REVIEWED_CURRENT_SOURCE']-=28;counts['SOURCE_REBOUND_CURRENT_WHOLE_PENDING']+=28
    value={'actualExit':0,'source':SOURCE,'baseManifestPath':parent.relative_to(ROOT).as_posix(),'baseManifestSha256':digest,'decisionsSha256':sha(dp),'rawFindings':1586,'statusCounts':dict(counts),'newIndividualDispositions':28,'currentWholeJoinPending':True,'executedPtAdded':0,'ptAlternativeCompleted':0,'sourceCodeChanged':False,'rawWarningsRemoved':0,'suppressionAdded':0,'F03Accepted':False,'formalAccepted':False,'vmActions':0}
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(value));print(json.dumps({'manifestSha256':sha(out/'manifest.json'),'decisionsSha256':sha(dp)}))


if __name__=='__main__':main()
