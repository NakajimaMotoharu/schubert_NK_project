"""Metadata-only two-side binding of original methods and explicitly separate resource domain."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg9954_pure_query_registry_metadata import INV,SNAP,SECTIONS,replaced
from pg9338_wbs_reference_metadata_post import validate
from pg9880_snapshot_nonce_trace import audit

BEFORE='2743c34974ed6be7184fdac20bba346097c13f2d'
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
FIELD='typedGuardCurrentHostPG14856Overlay'
REG=('PG14852-current908-named69-registry-v1','46d6f90a7c719ef536105cd9233c5653c834291255e04f10dbdf58334d41345a')
POST=('PG14854-current908-named69-registry-post-v1','12d557e00d0b8c4e95001a4666f52bb228b9124a82332f7be0964ce8cb65176b')
OUT=data.BASE/'PG14856-current908-named69-wbs-v1'
COPY_KEYS=['additionalQualificationReferences','qualificationReplacedUnitHistory','additionalScopeReferences','supplementalOwnershipCandidates','jointQualificationReferences','jointQualificationReplacedUnitHistory','resourceOnlyReferences','javascriptResourceDomain']
RECORD='evidence/01_PT/018_NK-OPS-001/2786_Current908・69DTO追加Source結合_結果.md'

def main():
    invocation=capture(__file__);assert not OUT.exists()
    raw,snap=[subprocess.check_output(['git','show',BEFORE+':'+name],cwd=data.ROOT) for name in [INV,SNAP]]
    assert raw==(data.ROOT/INV).read_bytes() and snap==(data.ROOT/SNAP).read_bytes()
    r,p=[data.read_checked(data.BASE/name/'manifest.json',pin) for name,pin in [REG,POST]]
    assert r['actualExit']==p['actualExit']==0 and r['source']==p['source']==SOURCE and p['registryManifestSha256']==REG[1]
    assert p['metadataNegativeVectors']==24 and p['resourceOnlyOriginalMethods']==35 and p['newSourcePrograms']==69 and p['nodeChildrenNotAddedToJavaMethods'] is True
    assert all(json.dumps(v,sort_keys=True)==json.dumps(r[k],sort_keys=True) for k,v in p['summary'].items())
    for v in [r,p]:verify(v['invocation'])
    path=lambda pair:str((data.BASE/pair[0]/'manifest.json').relative_to(data.ROOT))
    overlay=dict(source=SOURCE,registryManifest=path(REG),registrySha256=REG[1],registryPostManifest=path(POST),registryPostSha256=POST[1],record=RECORD,summary=p['summary'],sourceContractReference=r['additionalSourceContractReference'],coverageExecUnion=False,oldSourceRuntimeTransferred=False,allPreviousSideReferencesPreserved=True,currentWholeSourceQualification=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None)
    overlay.update({key:r[key] for key in COPY_KEYS})
    old=json.loads(raw);result=raw
    for name in SECTIONS:
        section=copy.deepcopy(old[name]);assert FIELD not in section
        section[FIELD]=copy.deepcopy(overlay);result,_,_=replaced(result,name,section)
    new_snap,_,_=replaced(snap,'inventorySha256',data.sha(result));validate(result,new_snap,old,json.loads(snap))
    restored=json.loads(result)
    for name in SECTIONS:restored[name].pop(FIELD)
    assert restored==old
    before=audit();assert before['actualExit']==1 and before['lastError']=='ValueError: current physical candidate exact Git/worktree scope'
    verify(invocation);OUT.mkdir();data.write(OUT/'before.safe.json',dict(inventorySha256=data.sha(raw),snapshotSha256=data.sha(snap),wholeWbsAudit=before))
    # Mechanical metadata rewrite; no original acceptance, scope, or cost changes.
    (data.ROOT/INV).write_bytes(result);(data.ROOT/SNAP).write_bytes(new_snap)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,beforeGit=BEFORE,registrySha256=REG[1],registryPostSha256=POST[1],inventorySha256=data.sha(result),snapshotSha256=data.sha(new_snap),wholeWbsAuditBefore=before,wholeWbsAuditAfter='INDEPENDENT_POST_PENDING',productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
