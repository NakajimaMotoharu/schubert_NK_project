"""Register four existing Main responsibilities; source and execution qualification unchanged."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import pg998_metrics as metrics
import trace_owner_join_api_readiness as previous
import trace_owner_join_explicit_main_gaps as owner
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9312-g13-four-main-join-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
GROUP='G13_FOUR_MAIN_EXPLICIT_OWNER_V1'

def sha(data):return hashlib.sha256(data).hexdigest()
def dataset(value):return sha(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    events=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP for row in events)
    identifier=metrics.append(GROUP,'GROUP_START',dict(primaryWbs='WBS-G13.07',wbsLeafIds=['WBS-G13.07'],source=SOURCE,
      workCategory='CONTRACT_AUDIT',groupStartEstimatePp=dict(low=.25,base=.5,high=1),groupCapPp=1,
      quotaBefore=dict(usedPercent=62,remainingPercent=38,resetsAt=1793382075),quotaObservedAtUTC='2026-10-25T02:36:50Z',
      original90Preservation=dict(capturedLowerBoundPp=87,cumulativeExactPp=None,unknownIntervalPp=2,cap=90,
        preservationReservePp=2,reserveIsMeasurement=False,rebased=False,newLargeGroupsSuppressed=True),
      plannedOutcome='FOUR_EXACT_MAIN_OWNER_RULES_ONLY; ORIGINAL941_AND_OLD256_PRESERVED; NO_NATIVE_OR_PT_OR_ACCEPTANCE',
      toolConstructionAndEnvironmentRework=dict(preflightMissingGuessedDocumentDirectory=2,exclusivePp=None),
      actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None))
    pins={
      'prior':('PG9288-api-pure-readiness-trace-v1/manifest.json','6a721ba74684d07681c61ba56593796363063f6e6eaa313cf62749dc94a2f7a6'),
      'gap':('PG9304-g13-registered-owner-gap-v1/manifest.json','bf0371f1eb4a85462ee8db6b265814fe933038b9084243aba933ada81ba162f0'),
      'post':('PG9305-g13-registered-owner-post-v1/manifest.json','d7e18d48aa6ab253b3ce981c06dba02a7caf850e892c66ae7b96ee6b41141b03'),
      'normal':('PG9246-web-life-lock-six-compile-v1/manifest.json','989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46')}
    proofs={}
    for key,(path,digest) in pins.items():
        assert sha((BASE/path).read_bytes())==digest; proofs[key]=json.loads((BASE/path).read_bytes())
        assert proofs[key]['source']==SOURCE and proofs[key]['actualExit']==0
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    assert dataset(inventory['artifacts'])=='ac5dee93b15167133a713c60d255b490400cbaee12362d7f1d0328161318ef99'
    assert dataset(inventory['currentPhysicalCandidate'])=='38247ee2b8850d5ab64f37f8d5536c8b14d7aa1962fab7be9c7ec190a930a01a'
    logical={row['path']:row for row in inventory['artifacts']}; old=proofs['prior']['sourceRows']
    assert len(old)==256
    missing={row['path'] for row in proofs['gap']['sourceRows'] if row['sourceSet']=='main' and row['canonicalOwner'] is None}
    assert missing==set(owner.DECISIONS)
    hashes=proofs['normal']['begin']['inputHashes']
    originals=[dict(path=row['path'],sha256=row['sha256'],owner=row['legacyReportedOwner']) for row in old]
    for path in sorted(missing):
        assert path not in logical and previous.canonical(path,logical)['canonicalOwner'] is None
        assert sha((ROOT/path).read_bytes())==hashes[path]
        originals.append(dict(path=path,sha256=hashes[path],owner=None))
    joined=owner.join_rows(originals,logical,hashes,'WBS-G13.07')
    owner.validate(joined,originals,logical,hashes,'WBS-G13.07')
    for prior,current in zip(old,joined):
        assert all(prior[key]==current[key] for key in ('path','sha256','canonicalOwner','canonicalCostOwner','basis','ownershipStatus'))
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    design='documents/900_OTHER/910_台帳/914_詳細設計修正管理台帳.md'
    assert b'SSC-295' in (ROOT/design).read_bytes()
    verify(invocation); OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          startEventId=identifier,witnesses=pins,sourceRows=joined,sourceCount=260,originalInputs=originals,
          original941Unchanged=True,historical943Unchanged=True,previous256CanonicalMappingsPreserved=True,
          newExactMainCandidates=4,remainingUnregisteredMain=0,remainingUnregisteredTests=704,
          javaPathDenominator=1789,explicitRegistered=1085,unknownScope='EXPLICIT_REGISTRY_ONLY_NOT_METHOD_TRACE',
          ledgerWitness=dict(path=design,sha256=sha((ROOT/design).read_bytes()),decision='SSC295_RELOCATION_NOT_NATIVE_QUALIFICATION'),
          registeredOwnersAreNotWbsAcceptance=True,historicalCostsReallocated=False,actualAllocatedPp=None,
          productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,wholeG13Accepted=False,whole451Accepted=False,
          formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualJmsConnections=0),stream,sort_keys=True,indent=2)
        stream.write('\n')
    print(json.dumps(dict(actualExit=0,sourceRows=260,mainGapFilled=4,manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
