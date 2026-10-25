"""Bind the parent's explicit static oracle review to unchanged current methods, not old PT."""
import datetime as dt
import json
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

ROOT=data.ROOT;BASE=data.BASE;SOURCE=data.SOURCE
OUT=BASE/'PG9610-observation-worker44-oracle-trace-v1'
SPEC=ROOT/'evidence/01_PT/018_NK-OPS-001/1949_G13ObservationWorker44_既存oracle意味照合仕様.md'
SPEC_SHA='17ec50079d1e05a9117972c91b75a8cf1f7a75aa7d7bc6eb5bfb81d4adccb352'
REVIEW=ROOT/'evidence/01_PT/018_NK-OPS-001/1950_G13ObservationWorker44_独立期待値意味対応表.md'
REVIEW_SHA='5f472d934a5338733d368bdfad1d76b683d4b979a82bfc9625fb988b6b7138d1'
ORACLE=ROOT/'evidence/01_PT/018_NK-OPS-001/1864_APIObservationOwnedWorker_製造・単体仕様.md'
ORACLE_SHA='b8d5702298999c0ca86c24604563be259f8c570e209913fdcc786570d11cb935'
MAIN='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/OwnedApiObservationWorker.java'
TEST='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/OwnedApiObservationWorkerTest.java'
CLASS='dev/codex/schubert/nk/api/monitoring/OwnedApiObservationWorker'
STEM='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/'

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    assert data.sha(SPEC.read_bytes())==SPEC_SHA and data.sha(REVIEW.read_bytes())==REVIEW_SHA and data.sha(ORACLE.read_bytes())==ORACLE_SHA
    normal=data.read_checked(BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json',data.PINS['normal'][1])
    subject=data.read_checked(BASE/'PG9592-current-test-method-post-v1/manifest.json','d73ffe203a58ca9fab7f19f0b4baa7b2588fb25ad7e13c75c0c6411f5a719a18')
    methods=data.read_checked(BASE/'PG9592-current-test-method-post-v1/method-declaration-bindings.json',subject['bindingsSha256'])
    selected={r['method']:r for r in methods if r['path']==TEST};assert set(selected)=={'obsOwn'+str(i).zfill(3) for i in range(1,45)}
    names=[MAIN,TEST,STEM+'ApiOutboxObservationPumpTest.java',STEM+'ApiReadOnlyObservationAttemptTest.java',STEM+'OutboxObservationRepositoryTest.java',
      'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiOutboxObservationPump.java',
      'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiReadOnlyObservationAttempt.java']
    hashes={p:normal['begin']['inputHashes'][p] for p in names}
    assert all(data.sha((ROOT/p).read_bytes())==data.sha((data.NORMAL/p).read_bytes())==h for p,h in hashes.items())
    graph=data.read_checked(BASE/'PG9386-composite-reference-graph-v3/manifest.json',data.PINS['graph'][1])
    main_map=data.read_checked(BASE/'PG9386-composite-reference-graph-v3/main-class-sources.json',graph['mainMapSha256'])
    assert main_map[CLASS]['owner']=='WBS-P018-09' and main_map[CLASS]['path']==MAIN
    class_manifest=data.read_checked(BASE/'PG9564-g07-host-main-class-provenance-v1/manifest.json','458970306a06b661c558c67f25b5769308fffb91d2c7d8603f996084a70de2ff')
    proofs=data.read_checked(BASE/'PG9564-g07-host-main-class-provenance-v1/public-main-class-proofs.json',class_manifest['publicClassProofsSha256'])
    physical=[r for r in proofs if r['className']==CLASS];assert len(physical)==1 and physical[0]['sha256']==main_map[CLASS]['sha256']
    assert physical[0]['sourceSha256']==hashes[MAIN] and physical[0]['source']==SOURCE
    oracle={};review={}
    for line_number,line in enumerate(ORACLE.read_text().splitlines(),1):
        if not line.startswith('| OBSOWN'):continue
        cells=[x.strip() for x in line.split('|')[1:-1]];assert len(cells)==3 and cells[0] not in oracle
        oracle[cells[0]]=dict(path=str(ORACLE.relative_to(ROOT)),sha256=ORACLE_SHA,line=line_number,rowSha256=data.sha(line.encode()),
          originalInputAndOperation=cells[1],originalIndependentExpectedBasis=cells[2])
    for line_number,line in enumerate(REVIEW.read_text().splitlines(),1):
        if not line.startswith('| OBSOWN'):continue
        cells=[x.strip() for x in line.split('|')[1:-1]];assert len(cells)==4 and cells[0] not in review
        review[cells[0]]=dict(path=str(REVIEW.relative_to(ROOT)),sha256=REVIEW_SHA,line=line_number,rowSha256=data.sha(line.encode()),
          reviewedMainPaths=cells[1].split(','),reviewedAssertionOrFixtureRelation=cells[2],applicability=cells[3])
    ids={'OBSOWN'+str(i).zfill(3) for i in range(1,45)};assert set(oracle)==set(review)==ids
    source_lines=(ROOT/TEST).read_text().splitlines();records=[]
    for test_id in sorted(ids):
        method=selected['obsOwn'+test_id[-3:]]
        assert method['parameterCount']==0 and method['fileCanonicalOwner']==method['fileCanonicalCostOwner']=='WBS-P018-09'
        assert method['sourceSha256']==hashes[TEST] and method['compiledDescriptor']=='()V'
        body='\n'.join(source_lines[method['startLine']-1:method['endLine']])
        assert 'void '+method['method']+'(' in body and '@Test' in body and ('assert' in body or 'asynchronous(' in body)
        records.append(dict(methodDeclarationKey=method['methodDeclarationKey'],existingTestId=test_id,
          sourcePath=TEST,sourceSha256=hashes[TEST],startLine=method['startLine'],endLine=method['endLine'],
          bodySha256=data.sha(body.encode()),compiledDescriptor='()V',physicalTestClassSha256=method['physicalClassSha256'],
          canonicalOwner='WBS-P018-09',costOwner='WBS-G13.07',referenceAdditionalBudgetPp=0,
          independentOracle=oracle[test_id],parentReview=review[test_id],
          reviewStatus='STATIC_METHOD_ORACLE_RELATION_REVIEWED_NOT_DYNAMIC_PT',reviewDoesNotProveEveryFaultCombination=True,
          oldSourcePtTransferred=False,productExecuted=False,newTestIdInvented=False,whole451Accepted=False))
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    verify(invocation);OUT.mkdir();data.write(OUT/'method-oracle-review.json',records)
    result=dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      specSha256=SPEC_SHA,reviewSha256=REVIEW_SHA,oracleSpecSha256=ORACLE_SHA,sourceHashes=hashes,
      normalManifestSha256=data.PINS['normal'][1],currentMainClassProof=physical[0],
      methodsReviewed=44,existingTestIds=44,sourceSpecRows=44,methodOracleReviewSha256=data.sha((OUT/'method-oracle-review.json').read_bytes()),
      staticReviewOnly=True,oldDynamicResultsTransferred=False,productTestsExecuted=0,newTestIds=0,newMain=0,
      coverage=None,formalUpdated=False,newAccepted=0,effortPercent=None,wholeG13Accepted=False,whole451Accepted=False)
    data.write(OUT/'manifest.json',result)
    print(json.dumps(dict(actualExit=0,methodsReviewed=44,productTestsExecuted=0)))
    print('manifestSha256='+data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
