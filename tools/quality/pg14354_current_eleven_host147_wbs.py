"""Current147 two-section side overlay; bind corrected summary and retain all prior qualifications unchanged."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg9954_pure_query_registry_metadata import INV,SNAP,SECTIONS,replaced
from pg9338_wbs_reference_metadata_post import validate
from pg9880_snapshot_nonce_trace import audit

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
BEFORE='fc22b765806e8467e86030849842646d9f1728b6'
FIELD='typedGuardCurrentHostPG14354Overlay'
OUT=data.BASE/'PG14354-current-eleven-host147-wbs-v1'
REG=('PG14350-current-eleven-host147-registry-v1','12d817bf7b77c6b50189c35b04535dfd48ae2b206229216e158a9274bf734c87')
POST=('PG14352-current-eleven-host147-registry-post-v1','5a3ef1860ae74402f0011e0d841e0b0aadff53cef064aef220718a1821a325ce')

def main():
    invocation=capture(__file__);assert not OUT.exists()
    original,snapshot=[subprocess.check_output(['git','show',BEFORE+':'+p],cwd=data.ROOT) for p in (INV,SNAP)]
    assert (data.ROOT/INV).read_bytes()==original and (data.ROOT/SNAP).read_bytes()==snapshot
    r,p=[data.read_checked(data.BASE/name/'manifest.json',pin) for name,pin in (REG,POST)]
    assert all(v['actualExit']==0 and v['source']==SOURCE for v in (r,p))
    assert p['registryManifestSha256']==REG[1] and p['metadataNegativeVectors']==19 and p['postSummaryNegativeVectors']==3 and p['summaryBoundToVerifiedActualFields'] is True
    assert r['tests']==p['originalXmlMethods']==147 and r['suites']==p['originalXmlSuites']==24 and r['originalExecs']==11
    assert r['four100SourcePrograms']==32 and r['incompleteSourcePrograms']==1 and r['unknownOwnerPaths']==p['unknownOwnerPaths']==26 and r['naturalZeroBranchSourcePrograms']==25 and r['metadataSourcePrograms']==1 and r['metadataPhysical']==4 and r['generatedMetadataPhysical']==3
    path=lambda value:str((data.BASE/value[0]/'manifest.json').relative_to(data.ROOT))
    overlay=dict(source=SOURCE,registryManifest=path(REG),registrySha256=REG[1],registryPostManifest=path(POST),registryPostSha256=POST[1],record='evidence/01_PT/018_NK-OPS-001/2648_現十一host147件・scope別参照_限定registry結果.md',originalExecs=11,originalMethods=147,originalSuites=24,fullSourceMeasured=59,measuredPhysical=69,executablePhysical=65,metadataPhysical=4,generatedMetadataPhysical=3,four100SourcePrograms=32,four100Physical=41,four100ExecutablePhysical=38,naturalZeroBranchSourcePrograms=25,naturalZeroBranchPhysical=26,metadataSourcePrograms=1,incompleteSourcePrograms=1,unknownOwnerPaths=26,supplementalOwnershipCandidateCount=1,coverageExecUnion=False,oldSource0061RuntimeTransferred=False,old995RuntimeAndQualificationUnchanged=True,previousPG14306Registry71Preserved=True,currentWholeSourceQualification=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None)
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
