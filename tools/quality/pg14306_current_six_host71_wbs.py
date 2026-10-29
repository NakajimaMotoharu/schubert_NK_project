"""Two-section side references for current71 actual methods and distinct coverage categories; preserve all history."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg9954_pure_query_registry_metadata import INV,SNAP,SECTIONS,replaced
from pg9338_wbs_reference_metadata_post import validate
from pg9880_snapshot_nonce_trace import audit

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
BEFORE='814e95126992d7d8a2f456c002b44caa58a26d9d'
FIELD='typedGuardCurrentHostPG14306Overlay'
OUT=data.BASE/'PG14306-current-six-host71-wbs-v1'
REG=('PG14302-current-six-host71-registry-v1','6fff0d2718570d7f15f6c2427163a7226ababd28656d23960cea3f54b66a852d')
POST=('PG14304-current-six-host71-registry-post-v1','e9fdba39311c8eb9d5f1ec61f448423e8d210eb98fa105ab2eb3c4dbedb17002')

def main():
    invocation=capture(__file__);assert not OUT.exists()
    original,snapshot=[subprocess.check_output(['git','show',BEFORE+':'+p],cwd=data.ROOT) for p in (INV,SNAP)]
    assert (data.ROOT/INV).read_bytes()==original and (data.ROOT/SNAP).read_bytes()==snapshot
    r,p=[data.read_checked(data.BASE/name/'manifest.json',pin) for name,pin in (REG,POST)]
    assert all(v['actualExit']==0 and v['source']==SOURCE for v in (r,p))
    assert p['registryManifestSha256']==REG[1] and p['metadataNegativeVectors']==14
    assert r['tests']==p['originalXmlMethods']==71 and r['suites']==p['originalXmlSuites']==10 and r['originalExecs']==6
    assert r['four100SourcePrograms']==9 and r['incompleteSourcePrograms']==1 and r['unknownOwnerPaths']==12 and r['naturalZeroBranchSourcePrograms']==6 and r['metadataSourcePrograms']==1
    path=lambda value:str((data.BASE/value[0]/'manifest.json').relative_to(data.ROOT))
    overlay=dict(source=SOURCE,registryManifest=path(REG),registrySha256=REG[1],registryPostManifest=path(POST),registryPostSha256=POST[1],record='evidence/01_PT/018_NK-OPS-001/2632_現六host七十一件_限定registry参照結果.md',originalExecs=6,originalMethods=71,originalSuites=10,fullSourceMeasured=17,measuredPhysical=21,executablePhysical=20,metadataPhysical=1,four100SourcePrograms=9,four100Physical=13,naturalZeroBranchSourcePrograms=6,metadataSourcePrograms=1,incompleteSourcePrograms=1,unknownOwnerPaths=12,coverageExecUnion=False,oldSource0061RuntimeTransferred=False,old995RuntimeAndQualificationUnchanged=True,previousPG14264Registry15Preserved=True,currentWholeSourceQualification=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None)
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,beforeGit=BEFORE,registrySha256=REG[1],registryPostSha256=POST[1],inventorySha256=data.sha(result),snapshotSha256=data.sha(new_snapshot),originalMethods=71,originalSuites=10,originalExecs=6,four100SourcePrograms=9,naturalZeroBranchSourcePrograms=6,metadataSourcePrograms=1,incompleteSourcePrograms=1,wholeWbsAuditBefore=before,wholeWbsAuditAfter='INDEPENDENT_POST_PENDING',productTestsExecuted=0,oldRuntimeReassigned=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
