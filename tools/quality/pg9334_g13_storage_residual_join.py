"""Existing source relationship/hash audit only; never load a native test helper."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import subprocess
import trace_owner_join_storage_residual as owner
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9334-g13-storage-residual-join-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def dataset(v):return sha(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    prior_path=BASE/'PG9320-g13-storage-companion-join-v1/manifest.json'
    normal_path=BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json'
    assert sha(prior_path.read_bytes())=='a68a1cddb4cbf42db72f8d9794170d229ac4ce2a068822694e910951adbe58bd'
    assert sha(normal_path.read_bytes())=='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    prior=json.loads(prior_path.read_bytes());normal=json.loads(normal_path.read_bytes())
    assert prior['source']==normal['source']==SOURCE and prior['actualExit']==normal['actualExit']==0
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    assert dataset(inventory['artifacts'])=='ac5dee93b15167133a713c60d255b490400cbaee12362d7f1d0328161318ef99'
    assert dataset(inventory['currentPhysicalCandidate'])=='38247ee2b8850d5ab64f37f8d5536c8b14d7aa1962fab7be9c7ec190a930a01a'
    logical={row['path']:row for row in inventory['artifacts']};old=prior['sourceRows'];hashes=normal['begin']['inputHashes']
    assert len(old)==279 and len(owner.DECISIONS)==10
    originals=[dict(path=row['path'],sha256=row['sha256'],owner=row['legacyReportedOwner']) for row in old]
    relationships=[]
    for name,(main_name,expected,kind) in sorted(owner.DECISIONS.items()):
        path=owner.PREFIX+name+'.java';main_path=owner.PREFIX.replace('/src/test/java/','/src/main/java/')+main_name+'.java'
        assert path not in logical and path not in {row['path'] for row in old}
        assert logical[main_path]['owner']==logical[main_path]['costOwner']==expected
        text=(ROOT/path).read_text();assert re.search(r'\b'+re.escape(main_name)+r'\b',text)
        assert sha((ROOT/path).read_bytes())==hashes[path] and sha((ROOT/main_path).read_bytes())==hashes[main_path]
        driver=None
        if kind=='TEST_HELPER':
            driver=owner.PREFIX+name.removesuffix('Child')+'Test.java'
            assert sha((ROOT/driver).read_bytes())==hashes[driver]
            assert name+'.class' in (ROOT/driver).read_text() and '@Test' not in text
        else:assert '@Test' in text
        relationships.append(dict(path=path,kind=kind,mainPath=main_path,mainSha256=hashes[main_path],
          primaryOwner=expected,primaryCostOwner=expected,driverTest=driver,testExecuted=False,
          sharedDependenciesSeparatelyCharged=False,actualNativeActions=0))
        originals.append(dict(path=path,sha256=hashes[path],owner=None))
    joined=owner.join_rows(originals,logical,hashes,'WBS-G13.07');owner.validate(joined,originals,logical,hashes,'WBS-G13.07')
    for before,after in zip(old,joined):assert all(before[k]==after[k] for k in ('path','sha256','canonicalOwner','canonicalCostOwner','basis','ownershipStatus'))
    assert len(joined)==289 and subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    spec=ROOT/'evidence/01_PT/018_NK-OPS-001/1900_G13StorageResidual_残10path責任対応仕様.md'
    verify(invocation);OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          prior279ManifestSha256=sha(prior_path.read_bytes()),normalManifestSha256=sha(normal_path.read_bytes()),
          frozenResponsibilitySpecSha256=sha(spec.read_bytes()),sourceRows=joined,originalInputs=originals,relationships=relationships,
          previous279CanonicalPreserved=True,original941AndHistorical943Unchanged=True,newExplicitSourceOwners=10,
          sourceCount=289,javaPaths=1789,registered=1114,unregisteredTest=675,registeredMain=965,totalMain=965,
          registeredTest=149,totalTest=824,storageTestSourceRegistered=29,storageTestSourceTotal=29,
          newTestOwners=8,newHelperOwners=2,productTestsExecuted=0,testClassLoading=0,newTestIds=0,newMain=0,
          coverage=None,formalUpdated=False,newAccepted=0,effortPercent=None,wholeG13Accepted=False,
          whole451Accepted=False,wholeWbsAudit='HOLD_OLD_QUALIFIED_VS_CURRENT_SOURCE_SCOPE',
          oldSourceResultsTransferred=False,costReallocated=False,actualAllocatedPp=None),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,newExplicitSourceOwners=10,registered=1114,unregistered=675,manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
