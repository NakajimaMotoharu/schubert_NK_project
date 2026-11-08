"""Bind existing public historical measurements to identical current Main descriptors, never runtime qualification."""
from pathlib import Path
import datetime
import hashlib
import json
import platform
import subprocess

B=Path('evidence/01_PT/018_NK-OPS-001')
C=B/'input/663_public_value_six_source_bridge_scope.json'
O=B/'evidence/PG24190-public-value-six-source-byte-bridge-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_bytes())
assert not O.exists()
c=load(C)
for ref in [c['originalPost'],c['currentMethodMetadata']]:assert sha(Path(ref['path']))==ref['sha256']
old=load(Path(c['originalPost']['path']));current=load(Path(c['currentMethodMetadata']['path']));idx={r['physicalKey']:r for r in current}
assert type(old['actualExit']) is int and old['actualExit']==0
assert old['source']==c['historicalRunSource'] and old['sessionIdentity']==c['originalSessionIdentity'] and old['execSha256']==c['originalExecSha256']
assert old['tests']==18 and old['suites']==4 and old['singleSession'] is True
assert all(type(old[k]) is int and old[k]==0 for k in ['failures','errors','skipped','reruns','productTestsReexecutedByPost'])
assert old['oldCoverageTransferred'] is False and old['formalUpdated'] is False and old['manualCounterExclusions']==[]
assert len(old['cases'])==18 and all(v['result']=='PASS' and v['nonPass']==[] for v in old['cases'])
rows=[]
for target in c['targets']:
    r=idx[target['physicalKey']];name=target['physicalKey'].split(':',1)[1].removesuffix('.class')
    assert r['classSha256']==target['classSha256']==old['physicalClasses'][name]==old['sourcePhysicalInventory'][name]['sha256']
    assert r['sourcePath']==target['mainPath'] and r['sourceSha256']==target['sourceSha256']
    assert {v['physicalKey'] for v in current if v['sourcePath']==r['sourcePath']}=={target['physicalKey']}
    unit=old['fullSourceUnits'][name]
    assert unit['physical']==old['completeSourceUnitClosure'][name]==[name]
    assert unit['metadataOnly'] is False and unit['threeCounter100'] is True
    for key in ['LINE','METHOD','CLASS','BRANCH']:
        x=unit['totals'][key];assert type(x['covered']) is int and type(x['missed']) is int and x['missed']==0
    natural=unit['totals']['BRANCH']['covered']==0
    assert unit['branchNaturallyZero'] is natural and unit['four100'] is (not natural)
    raw_methods=r['structure']['methods']
    assert [(x['name'],x['descriptor'],x['hasCode']) for x in raw_methods]==[(x['name'],x['descriptor'],x['hasCode']) for x in old['sourcePhysicalInventory'][name]['methods']]
    rows.append(dict(**target,historicalRunSource=old['source'],historicalSessionIdentity=old['sessionIdentity'],historicalCounters=unit['totals'],historicalApplicableCountersCovered=True,naturalBranchZero=natural,branchRate=None if natural else 100,methodMetadata=len(raw_methods),historicalMeasuredMethods=unit['totals']['METHOD']['covered'],methodCountDifferenceNotIndependentlyClassified=len(raw_methods)-unit['totals']['METHOD']['covered'],currentRunQualified=False,wholeWbsAccepted=False,newAcceptance=0))
assert len(rows)==6 and sum(x['methodMetadata'] for x in rows)==30 and sum(x['historicalMeasuredMethods'] for x in rows)==18
blob_rows=[]
for name in c['originalTestSourcePaths']:
    assert name.startswith('src/schubert-nk-api/src/test/java/') and not any(s in name for s in ['RootFailedStart','SnapshotKeyCloseWitness'])
    before=subprocess.check_output(['git','rev-parse','--verify',old['source']+':'+name],text=True).strip()
    now=subprocess.check_output(['git','rev-parse','--verify','HEAD:'+name],text=True).strip()
    blob_rows.append(dict(path=name,historicalGitBlob=before,currentGitBlob=now,testSourceIdentical=(before==now),contentsRead=False,currentTestRunQualified=False))
O.mkdir()
for name,value in [('source-byte-bridges.json',rows),('test-source-git-identity.json',blob_rows),('historical-cases.json',old['cases'])]:(O/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=c['source'],historicalRunSource=old['source'],originalPost=c['originalPost'],currentMethodMetadata=c['currentMethodMetadata'],originalTests=18,originalSuites=4,originalCaseCount=18,sourcePrograms=6,physicalClasses=6,knownMethodMetadata=30,historicalMeasuredMethods=18,methodCountDifferenceUnclassified=12,naturalBranchZeroSources=2,currentTestSourcesSame=sum(r['testSourceIdentical'] for r in blob_rows),currentTestSourcesDifferent=sum(not r['testSourceIdentical'] for r in blob_rows),historicalMeasurementOnly=True,currentRunQualified=False,individualMethodFilterOrOracleIndependentlyVerified=False,wholeWbsAccepted=False,compilerOrJvmExecuted=False,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None,os=platform.system(),pythonVersion=platform.python_version(),command=['python3','-B',str(Path(__file__))],files={p.name:sha(p) for p in O.iterdir()},tool=dict(path=str(Path(__file__)),sha256=sha(Path(__file__))))
(O/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,sourcePrograms=6,physicalClasses=6,historicalTests=18,currentTestsSame=result['currentTestSourcesSame'],currentTestsDifferent=result['currentTestSourcesDifferent'],manifestSha256=sha(O/'manifest.json'))))
