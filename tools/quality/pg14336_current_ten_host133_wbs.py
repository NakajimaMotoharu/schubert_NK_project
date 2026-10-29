"""Current133 two-section side overlay; bind corrected summary and retain all prior qualifications unchanged."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg9954_pure_query_registry_metadata import INV,SNAP,SECTIONS,replaced
from pg9338_wbs_reference_metadata_post import validate
from pg9880_snapshot_nonce_trace import audit

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
BEFORE='a634c8b7ca098e7a24d3369b2a6d7d8471f6c2f5'
FIELD='typedGuardCurrentHostPG14336Overlay'
OUT=data.BASE/'PG14336-current-ten-host133-wbs-v1'
REG=('PG14332-current-ten-host133-registry-v1','50b2bdfe8a754cf536eed77af902eee97b5a904046945af126e2d42011671674')
POST=('PG14335-current-ten-host133-registry-post-v2','55aef97a5842de28f46956c48bd1e6dacbe8225443b19f7f57a97ec4c8d0fca2')

def main():
    invocation=capture(__file__);assert not OUT.exists()
    original,snapshot=[subprocess.check_output(['git','show',BEFORE+':'+p],cwd=data.ROOT) for p in (INV,SNAP)]
    assert (data.ROOT/INV).read_bytes()==original and (data.ROOT/SNAP).read_bytes()==snapshot
    r,p=[data.read_checked(data.BASE/name/'manifest.json',pin) for name,pin in (REG,POST)]
    assert all(v['actualExit']==0 and v['source']==SOURCE for v in (r,p))
    assert p['registryManifestSha256']==REG[1] and p['metadataNegativeVectors']==17 and p['postSummaryNegativeVectors']==3 and p['summaryBoundToVerifiedActualFields'] is True
    assert r['tests']==p['originalXmlMethods']==133 and r['suites']==p['originalXmlSuites']==21 and r['originalExecs']==10
    assert r['four100SourcePrograms']==20 and r['incompleteSourcePrograms']==1 and r['unknownOwnerPaths']==p['unknownOwnerPaths']==23 and r['naturalZeroBranchSourcePrograms']==17 and r['metadataSourcePrograms']==1 and r['metadataPhysical']==2 and r['generatedMetadataPhysical']==1
    path=lambda value:str((data.BASE/value[0]/'manifest.json').relative_to(data.ROOT))
    overlay=dict(source=SOURCE,registryManifest=path(REG),registrySha256=REG[1],registryPostManifest=path(POST),registryPostSha256=POST[1],record='evidence/01_PT/018_NK-OPS-001/2642_現十host133件・生成metadata区分_限定registry参照結果.md',originalExecs=10,originalMethods=133,originalSuites=21,fullSourceMeasured=39,measuredPhysical=46,executablePhysical=44,metadataPhysical=2,generatedMetadataPhysical=1,four100SourcePrograms=20,four100Physical=26,four100ExecutablePhysical=25,naturalZeroBranchSourcePrograms=17,naturalZeroBranchPhysical=18,metadataSourcePrograms=1,incompleteSourcePrograms=1,unknownOwnerPaths=23,supplementalOwnershipCandidateCount=1,coverageExecUnion=False,oldSource0061RuntimeTransferred=False,old995RuntimeAndQualificationUnchanged=True,previousPG14306Registry71Preserved=True,currentWholeSourceQualification=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None)
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
