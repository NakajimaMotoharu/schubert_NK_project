"""Eighteen individual ResourceScope applicability reviews; dynamic case joins stay pending."""
import copy
import json
import os
import subprocess
from collections import Counter
from pg5540_snapshot_scratch_selected import ROOT,sha
from pg5800_rollback_green import source_test_names
from pg5860_terminal_whole import SOURCE,W
from static_disposition_overlay import BASE,load

PATH='src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/ResourceScope.java'
SS='documents/300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md'
EXPECTED=Counter({('AvoidCatchingGenericException',n):2 for n in(82,86,112,115)})|Counter({('AvoidInstanceofChecksInCatchClause',n):4 for n in(87,116)})|Counter({('AvoidInstanceofChecksInCatchClause',n):1 for n in(98,126)})
SITES={82:('acquire','ADMITTED_BODY_RELEASE_ONCE'),86:('acquire','SECONDARY_FAILURE_IS_NEVER_SUCCESS'),87:('acquire','KNOWN_IO_VS_UNKNOWN_CLOSE_PRECEDENCE'),98:('acquire','PATH_FREE_REASON_WITHOUT_RAW_CAUSE'),112:('use','ADMITTED_BODY_RELEASE_ONCE'),115:('use','SECONDARY_FAILURE_IS_NEVER_SUCCESS'),116:('use','KNOWN_IO_VS_UNKNOWN_CLOSE_PRECEDENCE'),126:('use','PATH_FREE_REASON_WITHOUT_RAW_CAUSE')}
USE={'successfulOwnership','knownIoFailures','unknownBodyFailures','knownBodyUnknownCleanup','unknownCompoundFailures','nullAndNullableContracts','nestedScopes','concurrentScopes'}


def verify_shape(text):
    if text.count('catch (IOException | RuntimeException | Error primary)')!=2 or text.count('catch (IOException | RuntimeException | Error secondary)')!=2:raise ValueError('both admitted body and release catch IO/unknown families')
    if text.count('if (primary instanceof IOException && !(secondary instanceof IOException))\n              throw secondary;')!=1 or text.count('if (primary instanceof IOException && !(secondary instanceof IOException))\n            throw secondary;')!=1:raise ValueError('SS333 known body IO and unknown release retain the unknown secondary')
    if text.count('primary.addSuppressed(new StorageIoException(StorageIoException.Reason.UNAVAILABLE));')!=2 or text.count('throw primary;')!=2:raise ValueError('unknown primary identity and fixed sanitized secondary; no normal return')
    if text.count('failure instanceof StorageIoException storage && failure.getSuppressed().length == 0')!=2 or text.count('? storage.reason()')!=2:raise ValueError('only unsuppressed known IO reason is retained')
    if text.count('if (resource != null) {')!=1 or text.index('@Nullable R resource = acquire.open();')>text.index('R owned;'):raise ValueError('factory failure before ownership; null result release0')


def main():
    parent=BASE/'PG5872-terminal-identity8-v1/manifest.json';digest='091f0368df19afe1944145c4c1a62c78e374937e2003c2efbde343cf430885cd';rows=load(parent,digest,SOURCE)
    if sha(ROOT/PATH)!='639d3e7a51ad7d4fd2b45a9d5b8f7536ece257f08b0db9955249704009d00bbf'or sha(ROOT/SS)!='d861735e91a6930bbf239937deda29f3675fbf50817953a61e07c0255387fa66':raise ValueError('reviewed complete source and SS333 bytes')
    if subprocess.check_output(['git','diff','origin/main','--',SS],cwd=ROOT):raise ValueError('canonical design is origin/main')
    source=(ROOT/PATH).read_text();verify_shape(source);proofp=W/'pg5858-terminal-static-v1/manifest.safe.json';proof=json.loads(proofp.read_bytes())
    if proof['source']!=SOURCE or proof['actualExit']!=0 or proof['allSourceHashes'][PATH]!=sha(ROOT/PATH):raise ValueError('current source/physical proof')
    testroot=ROOT/'src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage';use=source_test_names(testroot/'ResourceScopeTest.java');factory=source_test_names(testroot/'FactoryResourceScopeTest.java')
    if use!=USE or len(factory)!=18 or {name[:10]for name in factory}!={'factory'+str(i).zfill(3)for i in range(1,19)}:raise ValueError('independent eight existing use and eighteen existing factory identities')
    targets=[r for r in rows if r['sourcePath']==PATH]
    if Counter((r['rule'],int(r['beginline']))for r in targets)!=EXPECTED or len(targets)!=18 or any(r['status']!='NOT_REVIEWED_CURRENT_SOURCE'or r['sourceSha256']!=sha(ROOT/PATH)for r in targets):raise ValueError('all and only eighteen current raw warnings')
    decisions=[]
    for row in targets:
        method,contract=SITES[int(row['beginline'])];value=copy.deepcopy(row);cls='FactoryResourceScopeTest'if method=='acquire'else'ResourceScopeTest';names=factory if method=='acquire'else use
        value.update(status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',priorDisposition='REQUIRED_CONTRACT',newDispositionCreated=True,reason='SS333 SSC063/308 explicitly specifies IO versus Runtime/Error compound precedence, single release and path-free normalization. This '+method+' '+contract+' site implements that finite failure matrix. A generic catch neither returns normally nor acknowledges recovery; unknown Runtime/NPE/Error identity propagates, known IO alone is normalized. Narrowing away Error/Runtime or replacing with TWR changes the approved priority. Full source and separate normal/null/IO/unknown/self-failure/nested/parallel fixture identities reviewed; current dynamic joins remain pending.',reviewedMethod=method,reviewedContract=contract,relatedDesign=SS,designSha256=sha(ROOT/SS),programId='NK-OPS-001',testIds=['PT-OPS-RSCOPE001..008']if method=='use'else['PT-IOFACT001..018'],plannedCurrentTestRefs=[{'class':'dev.codex.schubert.nk.storage.'+cls,'method':name}for name in sorted(names)],currentWholeCaseRefs=[],currentWholeJoinPending=True,rawWarningRetained=True,currentPhysicalProofSha256=sha(proofp),noPtExecutedByReview=True)
        decisions.append(value)
    out=BASE/'PG5874-storage-resource18-v1';os.umask(0o077);out.mkdir();dp=out/'decisions.json'
    with dp.open('x')as f:json.dump(decisions,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    counts=Counter(r['status']for r in rows);counts['NOT_REVIEWED_CURRENT_SOURCE']-=18;counts['SOURCE_REBOUND_CURRENT_WHOLE_PENDING']+=18
    value={'actualExit':0,'source':SOURCE,'baseManifestPath':parent.relative_to(ROOT).as_posix(),'baseManifestSha256':digest,'decisionsSha256':sha(dp),'rawFindings':1586,'statusCounts':dict(counts),'newIndividualDispositions':18,'currentWholeJoinPending':True,'executedPtAdded':0,'ptAlternativeCompleted':0,'sourceCodeChanged':False,'rawWarningsRemoved':0,'suppressionAdded':0,'F03Accepted':False,'formalAccepted':False,'vmActions':0}
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(value));print(json.dumps({'manifestSha256':sha(out/'manifest.json'),'decisionsSha256':sha(dp)}))


if __name__=='__main__':main()
