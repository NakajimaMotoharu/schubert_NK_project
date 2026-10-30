"""Add current816 as side metadata only, never mutate old qualification or cost/acceptance."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg9954_pure_query_registry_metadata import INV,SNAP,SECTIONS,replaced
from pg9338_wbs_reference_metadata_post import validate
from pg9880_snapshot_nonce_trace import audit

BEFORE='38f3fbef21e923c5da0afe1109e2a1d73b90692e'
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
FIELD='typedGuardCurrentHostPG14684Overlay'
REG=('PG14680-current816-incremental-registry-v1','2060df0aefd44244ce8a944c79d96e800fbcd8abe5ed3bcfbb0c64e4fe8d3b29')
POST=('PG14683-current816-incremental-registry-post-v2','ada11a00d7ee4f5aea2c2881dd95dec2fdf086e09a661c4998ec8d9f77f6dbed')
OUT=data.BASE/'PG14684-current816-wbs-v1'

def main():
    invocation=capture(__file__);assert not OUT.exists()
    raw,snap=[subprocess.check_output(['git','show',BEFORE+':'+p],cwd=data.ROOT) for p in [INV,SNAP]]
    assert raw==(data.ROOT/INV).read_bytes() and snap==(data.ROOT/SNAP).read_bytes()
    r,p=[data.read_checked(data.BASE/n/'manifest.json',h) for n,h in [REG,POST]]
    assert r['source']==p['source']==SOURCE and r['actualExit']==p['actualExit']==0 and p['registryManifestSha256']==REG[1] and p['metadataNegativeVectors']==20 and p['moduleMappingChecks']==dict(positive=6,negative=4)
    assert all(json.dumps(v,sort_keys=True)==json.dumps(r[k],sort_keys=True) for k,v in p['summary'].items())
    for value in [r,p]:verify(value['invocation'])
    path=lambda v:str((data.BASE/v[0]/'manifest.json').relative_to(data.ROOT))
    overlay=dict(source=SOURCE,registryManifest=path(REG),registrySha256=REG[1],registryPostManifest=path(POST),registryPostSha256=POST[1],record='evidence/01_PT/018_NK-OPS-001/2744_Current816WBS結合_検証結果.md',summary=p['summary'],additionalQualificationReferences=r['additionalQualificationReferences'],qualificationReplacedUnitHistory=r['qualificationReplacedUnitHistory'],additionalScopeReferences=r['additionalScopeReferences'],sourceContractReference=r['additionalSourceContractReference'],supplementalOwnershipCandidates=r['supplementalOwnershipCandidates'],coverageExecUnion=False,oldSourceRuntimeTransferred=False,allPreviousSideReferencesPreserved=True,currentWholeSourceQualification=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None)
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
    # Mechanical metadata-only JSON rewrite; old semantics and source remain unchanged.
    (data.ROOT/INV).write_bytes(result);(data.ROOT/SNAP).write_bytes(new_snap)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,beforeGit=BEFORE,registrySha256=REG[1],registryPostSha256=POST[1],inventorySha256=data.sha(result),snapshotSha256=data.sha(new_snap),wholeWbsAuditBefore=before,wholeWbsAuditAfter='INDEPENDENT_POST_PENDING',productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
