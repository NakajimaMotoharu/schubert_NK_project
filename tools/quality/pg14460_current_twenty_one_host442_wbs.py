"""Current442 two-section side overlay; bind corrected summary and retain all prior qualifications unchanged."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg9954_pure_query_registry_metadata import INV,SNAP,SECTIONS,replaced
from pg9338_wbs_reference_metadata_post import validate
from pg9880_snapshot_nonce_trace import audit
from f03_monitor_seven_failure_fourteen_trace_v1 import state_after

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
BEFORE='884c96e8c28cae18418133ca8b526759ca37bcfe'
FIELD='typedGuardCurrentHostPG14460Overlay'
OUT=data.BASE/'PG14460-current-twenty-one-host442-wbs-v1'
REG=('PG14457-current-twenty-one-host442-registry-v2','78ed777bdafa82aa595cbd4afb9a0cdd829eda1262e5e3e262eddc88928fa268')
POST=('PG14458-current-twenty-one-host442-registry-post-v1','5cdf5e6df4cd286083c7c84027ebb69dc1fffe339c077655ed64e8bc04d2712c')

def main():
    invocation=capture(__file__);assert not OUT.exists()
    original,snapshot=[subprocess.check_output(['git','show',BEFORE+':'+p],cwd=data.ROOT) for p in (INV,SNAP)]
    assert (data.ROOT/INV).read_bytes()==original and (data.ROOT/SNAP).read_bytes()==snapshot
    r,p=[data.read_checked(data.BASE/name/'manifest.json',pin) for name,pin in (REG,POST)]
    assert all(v['actualExit']==0 and v['source']==SOURCE for v in (r,p))
    assert p['sourceContextProofCounterNegativeVectors']==r['sourceContextProofCounterNegativeVectors']==5 and p['registryManifestSha256']==REG[1] and p['metadataNegativeVectors']==23 and p['postSummaryNegativeVectors']==3 and p['summaryBoundToVerifiedActualFields'] is True
    assert r['tests']==p['originalXmlMethods']==442 and r['suites']==p['originalXmlSuites']==64 and r['originalExecs']==21
    assert r['four100SourcePrograms']==78 and r['incompleteSourcePrograms']==1 and r['unknownOwnerPaths']==p['unknownOwnerPaths']==38 and r['naturalZeroBranchSourcePrograms']==56 and r['metadataSourcePrograms']==1 and r['metadataPhysical']==5 and r['generatedMetadataPhysical']==4
    ids,refs,pending=state_after()
    assert (len(ids),len(refs),len(pending),len(ids-refs))==(6247,3696,2835,2551)
    assert p['sourceContractContexts']==r['additionalSourceContractReference']['sourceContexts']==14 and p['additionalScopes']==len(r['additionalScopeReferences'])==1
    path=lambda value:str((data.BASE/value[0]/'manifest.json').relative_to(data.ROOT))
    overlay=dict(source=SOURCE,registryManifest=path(REG),registrySha256=REG[1],registryPostManifest=path(POST),registryPostSha256=POST[1],record='evidence/01_PT/018_NK-OPS-001/2678_現二十一host442件・candidate区分_限定registry結果.md',originalExecs=21,originalMethods=442,originalSuites=64,fullSourceMeasured=136,measuredPhysical=171,executablePhysical=166,metadataPhysical=5,generatedMetadataPhysical=4,four100SourcePrograms=78,four100Physical=112,four100ExecutablePhysical=108,naturalZeroBranchSourcePrograms=56,naturalZeroBranchPhysical=57,metadataSourcePrograms=1,incompleteSourcePrograms=1,unknownOwnerPaths=38,supplementalOwnershipCandidateCount=1,coverageExecUnion=False,oldSource0061RuntimeTransferred=False,old995RuntimeAndQualificationUnchanged=True,previousPG14306Registry71Preserved=True,currentWholeSourceQualification=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None)
    overlay.update(sourceContractReference=r['additionalSourceContractReference'],sourceContextReasonRows=14,historicalRaw=6247,historicalReferenced=3696,historicalCurrentWholePending=2835,historicalWithoutContext=2551,sourceContextQualityAccepted=False)
    assert r['ownerStatusCounts']==p['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':105,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':58,'UNKNOWN':38}
    overlay.update(ownerStatusCounts=r['ownerStatusCounts'],sourceContextReferencesAlreadyCounted=True)
    old=json.loads(original);result=original
    for name in SECTIONS:
        section=copy.deepcopy(old[name]);assert FIELD not in section
        section[FIELD]=copy.deepcopy(overlay);result,_,_=replaced(result,name,section)
    new_snapshot,_,_=replaced(snapshot,'inventorySha256',data.sha(result))
    validate(result,new_snapshot,old,json.loads(snapshot));restored=json.loads(result)
    for name in SECTIONS:restored[name].pop(FIELD)
    assert restored==old
    before=audit();assert before['actualExit']==1 and before['lastError']=='ValueError: current physical candidate exact Git/worktree scope'
    verify(invocation);OUT.mkdir()
    data.write(OUT/'before.safe.json',dict(inventorySha256=data.sha(original),snapshotSha256=data.sha(snapshot),wholeWbsAudit=before))
    # Bulk mechanical metadata-only JSON rewrite: source/config/old semantics are unchanged.
    (data.ROOT/INV).write_bytes(result);(data.ROOT/SNAP).write_bytes(new_snapshot)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,beforeGit=BEFORE,registrySha256=REG[1],registryPostSha256=POST[1],inventorySha256=data.sha(result),snapshotSha256=data.sha(new_snapshot),originalMethods=r['tests'],originalSuites=r['suites'],originalExecs=r['originalExecs'],four100SourcePrograms=r['four100SourcePrograms'],naturalZeroBranchSourcePrograms=r['naturalZeroBranchSourcePrograms'],metadataSourcePrograms=r['metadataSourcePrograms'],generatedMetadataPhysical=r['generatedMetadataPhysical'],unknownOwnerPaths=p['unknownOwnerPaths'],incompleteSourcePrograms=r['incompleteSourcePrograms'],wholeWbsAuditBefore=before,wholeWbsAuditAfter='INDEPENDENT_POST_PENDING',productTestsExecuted=0,oldRuntimeReassigned=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
