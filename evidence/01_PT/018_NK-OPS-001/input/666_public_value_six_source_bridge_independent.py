"""Independent public metadata bridge check. No original tests, archives, classbytes or backend execution."""
from pathlib import Path
import copy
import datetime
import hashlib
import json

B=Path('evidence/01_PT/018_NK-OPS-001')
C=B/'input/663_public_value_six_source_bridge_scope.json'
P=B/'evidence/PG24190-public-value-six-source-byte-bridge-v1'
O=B/'evidence/PG24192-public-value-six-source-byte-independent-v1'
load=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def verify(rows,cases,manifest,post,inventory,cfg):
    assert len(rows)==6 and len({r['mainPath'] for r in rows})==6
    assert manifest['historicalMeasurementOnly'] is True and manifest['currentRunQualified'] is False
    assert manifest['individualMethodFilterOrOracleIndependentlyVerified'] is False
    expected_paths={r['mainPath'] for r in cfg['targets']}
    expected_current=[r for r in inventory if r['sourcePath'] in expected_paths]
    assert len(expected_current)==6
    bykey={r['physicalKey']:r for r in rows}
    assert set(bykey)=={r['physicalKey'] for r in expected_current}
    for current in expected_current:
        r=bykey[current['physicalKey']];name=current['physicalKey'].split(':',1)[1][:-6]
        assert r['classSha256']==current['classSha256']==post['physicalClasses'][name]
        assert r['mainPath']==current['sourcePath'] and r['sourceSha256']==current['sourceSha256']
        assert (r['owner'],r['costOwner'])==(current['owner'],current['costOwner'])
        assert r['historicalCounters']==post['fullSourceUnits'][name]['totals']
        assert r['historicalRunSource']==post['source'] and r['historicalSessionIdentity']==post['sessionIdentity']
        assert r['methodMetadata']==len(current['structure']['methods'])
        assert r['currentRunQualified'] is False and r['newAcceptance']==0
        branch=r['historicalCounters']['BRANCH']
        assert r['naturalBranchZero'] is (branch['covered']==0)
        assert r['branchRate']==(None if branch['covered']==0 else 100)
    assert cases==post['cases'] and len(cases)==18
    assert len({(r['classname'],r['name']) for r in cases})==18
    assert all(r['result']=='PASS' and r['nonPass']==[] for r in cases)

assert not O.exists()
c=load(C);m=load(P/'manifest.json');post=load(Path(c['originalPost']['path']));inventory=load(Path(c['currentMethodMetadata']['path']))
for ref in [c['originalPost'],c['currentMethodMetadata']]:assert sha(Path(ref['path']))==ref['sha256']
for name,pin in m['files'].items():assert sha(P/name)==pin
rows=load(P/'source-byte-bridges.json');cases=load(P/'historical-cases.json');test_sources=load(P/'test-source-git-identity.json')
verify(rows,cases,m,post,inventory,c)
assert len(test_sources)==4 and all(r['testSourceIdentical'] is True and r['historicalGitBlob']==r['currentGitBlob'] and r['contentsRead'] is False and r['currentTestRunQualified'] is False for r in test_sources)
negatives=[]
for label,mutate in [('current-class-digest',lambda r,t,m:r[0].update(classSha256='0'*64)),
                       ('source-role-digest',lambda r,t,m:r[0].update(sourceSha256=r[0]['classSha256'])),
                       ('source-missing',lambda r,t,m:r.pop()),
                       ('case-missing',lambda r,t,m:t.pop()),
                       ('case-failed',lambda r,t,m:t[0].update(result='FAIL')),
                       ('counter-gap',lambda r,t,m:r[0]['historicalCounters']['LINE'].update(missed=1)),
                       ('runtime-transfer',lambda r,t,m:m.update(currentRunQualified=True)),
                       ('natural-zero-fake-percent',lambda r,t,m:next(x for x in r if x['naturalBranchZero']).update(branchRate=100))]:
    a,b,d=copy.deepcopy(rows),copy.deepcopy(cases),copy.deepcopy(m);mutate(a,b,d)
    assert (a,b,d)!=(rows,cases,m)
    try:verify(a,b,d,post,inventory,c)
    except AssertionError:negatives.append(label)
    else:raise AssertionError(label)
O.mkdir()
result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=c['source'],historicalRunSource=post['source'],producerManifest={'path':str(P/'manifest.json'),'sha256':sha(P/'manifest.json')},sourcePrograms=6,physicalClasses=6,knownMethodMetadata=30,historicalMeasuredMethods=18,methodCountDifferenceUnclassified=12,historicalTests=18,historicalSuites=4,originalCaseRefs=18,currentTestSourcesSame=4,currentTestSourcesDifferent=0,naturalBranchZeroSources=2,metadataNegativeChecks=negatives,exactCurrentMainByteHistoryBound=True,historicalMeasurementOnly=True,currentRunQualified=False,individualMethodFilterOrOracleIndependentlyVerified=False,wholeWbsAccepted=False,dependencyClosureQualification='NOT_VERIFIED_NOT_TRANSFERRED',compilerOrJvmExecuted=False,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None,tool={'path':str(Path(__file__)),'sha256':sha(Path(__file__))})
(O/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,sourcePrograms=6,historicalCaseRefs=18,negativeChecks=len(negatives),currentRunQualified=False,manifestSha256=sha(O/'manifest.json'))))
