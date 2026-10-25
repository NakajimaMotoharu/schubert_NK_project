"""Independent reference/byte/boundary checks for the parent's semantic review, not a second PT."""
import copy
import datetime as dt
import json
from pathlib import Path
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

ROOT=data.ROOT;BASE=data.BASE;SOURCE=data.SOURCE
SUBJECT=BASE/'PG9610-observation-worker44-oracle-trace-v1'
SUBJECT_SHA='e2d953b07c08be7c455724b1b1d001fd0e45ef8819a2525a15eb6c6002f6e286'
OUT=BASE/'PG9612-observation-worker44-oracle-post-v1'

def validate(actual,expected):
    if actual!=expected:raise ValueError('same current method, unchanged independent spec row and bounded static review only')

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    primary=data.read_checked(SUBJECT/'manifest.json',SUBJECT_SHA)
    assert primary['actualExit']==0 and primary['source']==SOURCE and primary['methodsReviewed']==44
    records=data.read_checked(SUBJECT/'method-oracle-review.json',primary['methodOracleReviewSha256'])
    normal=data.read_checked(BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json',data.PINS['normal'][1])
    for path,digest in primary['sourceHashes'].items():
        assert digest==normal['begin']['inputHashes'][path]==data.sha((ROOT/path).read_bytes())==data.sha((data.NORMAL/path).read_bytes())
    method_manifest=data.read_checked(BASE/'PG9592-current-test-method-post-v1/manifest.json','d73ffe203a58ca9fab7f19f0b4baa7b2588fb25ad7e13c75c0c6411f5a719a18')
    methods=data.read_checked(BASE/'PG9592-current-test-method-post-v1/method-declaration-bindings.json',method_manifest['bindingsSha256'])
    methods={r['methodDeclarationKey']:r for r in methods}
    oracle_path=ROOT/'evidence/01_PT/018_NK-OPS-001/1864_APIObservationOwnedWorker_製造・単体仕様.md'
    review_path=ROOT/'evidence/01_PT/018_NK-OPS-001/1950_G13ObservationWorker44_独立期待値意味対応表.md'
    assert data.sha(oracle_path.read_bytes())==primary['oracleSpecSha256']=='b8d5702298999c0ca86c24604563be259f8c570e209913fdcc786570d11cb935'
    assert data.sha(review_path.read_bytes())==primary['reviewSha256']=='5f472d934a5338733d368bdfad1d76b683d4b979a82bfc9625fb988b6b7138d1'
    oracles={};reviews={}
    for document,destination,width in ((oracle_path,oracles,3),(review_path,reviews,4)):
        for number,line in enumerate(document.read_text().splitlines(),1):
            parts=[p.strip() for p in line.split('|')]
            if len(parts)!=width+2 or not re.fullmatch(r'OBSOWN[0-9]{3}',parts[1]):continue
            assert parts[1] not in destination
            destination[parts[1]]=(number,line,parts[1:-1])
    ids={r['existingTestId'] for r in records};assert len(records)==len(ids)==44 and ids==set(oracles)==set(reviews)
    expected=[]
    for row in records:
        test_id=row['existingTestId'];number=int(test_id.removeprefix('OBSOWN'));assert 1<=number<=44
        method=methods[row['methodDeclarationKey']]
        assert method['method']==f'obsOwn{number:03}' and method['compiledDescriptor']=='()V' and method['parameterCount']==0
        assert method['fileCanonicalOwner']=='WBS-P018-09'
        lines=(ROOT/method['path']).read_text().splitlines();body='\n'.join(lines[method['startLine']-1:method['endLine']])
        old_line,old_text,old=oracles[test_id];new_line,new_text,new=reviews[test_id]
        expected.append(dict(methodDeclarationKey=method['methodDeclarationKey'],existingTestId=test_id,
          sourcePath=method['path'],sourceSha256=method['sourceSha256'],startLine=method['startLine'],endLine=method['endLine'],
          bodySha256=data.sha(body.encode()),compiledDescriptor='()V',physicalTestClassSha256=method['physicalClassSha256'],
          canonicalOwner='WBS-P018-09',costOwner='WBS-G13.07',referenceAdditionalBudgetPp=0,
          independentOracle=dict(path=str(oracle_path.relative_to(ROOT)),sha256=primary['oracleSpecSha256'],line=old_line,
            rowSha256=data.sha(old_text.encode()),originalInputAndOperation=old[1],originalIndependentExpectedBasis=old[2]),
          parentReview=dict(path=str(review_path.relative_to(ROOT)),sha256=primary['reviewSha256'],line=new_line,
            rowSha256=data.sha(new_text.encode()),reviewedMainPaths=new[1].split(','),reviewedAssertionOrFixtureRelation=new[2],applicability=new[3]),
          reviewStatus='STATIC_METHOD_ORACLE_RELATION_REVIEWED_NOT_DYNAMIC_PT',reviewDoesNotProveEveryFaultCombination=True,
          oldSourcePtTransferred=False,productExecuted=False,newTestIdInvented=False,whole451Accepted=False))
    validate(records,expected)
    # A literal, independent arithmetic witness, never a Production call used for expected.
    assert 2_000_000-1_000_000==1_000_000
    time_row=next(r for r in records if r['existingTestId']=='OBSOWN025')
    source=(ROOT/time_row['sourcePath']).read_text().splitlines()
    body='\n'.join(source[time_row['startLine']-1:time_row['endLine']])
    assert all(text in body for text in ('TimeUnit.MILLISECONDS.toNanos(2)','TimeUnit.SECONDS.toNanos(50)',
      'assertEquals(2, clock.get());','assertEquals(2, limits.get());'))
    rejected=[]
    for label,edit in (('missing',lambda x:x.pop()),('duplicate',lambda x:x.append(copy.deepcopy(x[0]))),
      ('case',lambda x:x[0].update(existingTestId='OBSOWN999')),('spec-line',lambda x:x[0]['independentOracle'].update(line=0)),
      ('expected-changed',lambda x:x[0]['independentOracle'].update(originalIndependentExpectedBasis='PASS')),
      ('body',lambda x:x[0].update(bodySha256='0'*64)),('owner',lambda x:x[0].update(canonicalOwner='WBS-P005-01')),
      ('execution',lambda x:x[0].update(productExecuted=True)),('old-pt',lambda x:x[0].update(oldSourcePtTransferred=True)),
      ('all451',lambda x:x[0].update(whole451Accepted=True))):
        changed=copy.deepcopy(records);edit(changed)
        try:validate(changed,expected)
        except ValueError:rejected.append(label)
        else:raise AssertionError('unproved oracle review record accepted')
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      subjectManifestSha256=SUBJECT_SHA,staticMethodOracleRelationsVerified=44,sourceSpecRows=44,
      methodOracleReviewSha256=primary['methodOracleReviewSha256'],independentMetadataCounterexamples=rejected,
      independentLiteralArithmeticVectors=1,semanticReviewIsParentRecordNotIndependentDynamicTest=True,
      ownPostVerifiesReferencesBytesBoundariesOnly=True,productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,
      oldDynamicResultsTransferred=False,formalUpdated=False,newAccepted=0,effortPercent=None,wholeG13Accepted=False,whole451Accepted=False)
    data.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,staticMethodOracleRelationsVerified=44,metadataCounterexamples=len(rejected))))
    print('manifestSha256='+data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
