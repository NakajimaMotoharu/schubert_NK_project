"""Read-only source relationships; native tests are never selected or executed."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import subprocess
import pg998_metrics as metrics
import trace_owner_join_storage_companion as owner
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9320-g13-storage-companion-join-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
GROUP='G13_STORAGE_COMPANION19_OWNER_V1'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def dataset(value):return sha(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    events=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP for row in events)
    identifier=metrics.append(GROUP,'GROUP_START',dict(primaryWbs='WBS-G13.07',wbsLeafIds=['WBS-G13.07'],source=SOURCE,
      workCategory='CONTRACT_AUDIT',groupStartEstimatePp=dict(low=.25,base=.5,high=1),groupCapPp=1,
      quotaBefore=dict(usedPercent=62,remainingPercent=38,resetsAt=1793382075),quotaObservedAtUTC='2026-10-25T02:42:22Z',
      original90Preservation=dict(capturedLowerBoundPp=87,cumulativeExactPp=None,unknownIntervalPp=2,cap=90,
        preservationReservePp=2,reserveIsMeasurement=False,rebased=False,newLargeGroupsSuppressed=True),
      plannedOutcome='NINETEEN_EXACT_STORAGE_TEST_SOURCE_OWNERS; NO_TEST_CLASS_LOADING_OR_NATIVE_EXECUTION',
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None))
    normal_path=BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json'
    prior_path=BASE/'PG9312-g13-four-main-join-v1/manifest.json'
    assert sha(normal_path.read_bytes())=='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    assert sha(prior_path.read_bytes())=='7fd038ec63dbf02d5f7b2d2c8b71d651a08da16b19d1bbbe518429ebe569b6b4'
    normal=json.loads(normal_path.read_bytes()); prior=json.loads(prior_path.read_bytes())
    assert normal['source']==prior['source']==SOURCE and normal['actualExit']==prior['actualExit']==0
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    assert dataset(inventory['artifacts'])=='ac5dee93b15167133a713c60d255b490400cbaee12362d7f1d0328161318ef99'
    assert dataset(inventory['currentPhysicalCandidate'])=='38247ee2b8850d5ab64f37f8d5536c8b14d7aa1962fab7be9c7ec190a930a01a'
    logical={row['path']:row for row in inventory['artifacts']}; hashes=normal['begin']['inputHashes']
    old=prior['sourceRows']; assert len(old)==260 and len(owner.DECISIONS)==19
    originals=[dict(path=row['path'],sha256=row['sha256'],owner=row['legacyReportedOwner']) for row in old]
    references=[]
    for name,expected in sorted(owner.DECISIONS.items()):
        path=owner.PREFIX+name+'.java'
        main_path=path.replace('/src/test/java/','/src/main/java/').removesuffix('Test.java')+'.java'
        assert path not in logical and path not in {row['path'] for row in old}
        assert logical[main_path]['owner']==logical[main_path]['costOwner']==expected
        text=(ROOT/path).read_text(); class_name=name.removesuffix('Test')
        assert re.search(r'\b'+re.escape(class_name)+r'\b',text) and '@Test' in text
        assert sha((ROOT/path).read_bytes())==hashes[path]
        assert sha((ROOT/main_path).read_bytes())==hashes[main_path]
        references.append(dict(testPath=path,mainPath=main_path,testSha256=hashes[path],mainSha256=hashes[main_path],
          owner=expected,costOwner=expected,basis='ORIGINAL_MAIN_RESPONSIBILITY_AND_EXACT_REVIEWED_COMPANION_SOURCE',
          testExecuted=False,testExecutionStatus='UNRUN_HOLD_NOT_PASS'))
        originals.append(dict(path=path,sha256=hashes[path],owner=None))
    joined=owner.join_rows(originals,logical,hashes,'WBS-G13.07')
    owner.validate(joined,originals,logical,hashes,'WBS-G13.07')
    for before,after in zip(old,joined):
        assert all(before[key]==after[key] for key in ('path','sha256','canonicalOwner','canonicalCostOwner','basis','ownershipStatus'))
    assert len(joined)==279 and subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    verify(invocation); OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          startEventId=identifier,sourceRows=joined,originalInputs=originals,sourceCount=279,companionReferences=references,
          prior260ManifestSha256=sha(prior_path.read_bytes()),normalManifestSha256=sha(normal_path.read_bytes()),
          original941AndHistorical943Unchanged=True,previous260CanonicalMappingsPreserved=True,
          newExplicitTestSourceOwners=19,javaPathDenominator=1789,explicitRegistered=1104,
          registeredMain=965,totalMain=965,registeredTest=139,totalTest=824,remainingUnregisteredTests=685,
          testClassLoading=0,productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,
          wholeG13Accepted=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,
          actualVmActions=0,actualNativeActions=0,costReallocated=False,actualAllocatedPp=None),stream,sort_keys=True,indent=2)
        stream.write('\n')
    print(json.dumps(dict(actualExit=0,newExplicitTestOwners=19,productTestsExecuted=0,manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
