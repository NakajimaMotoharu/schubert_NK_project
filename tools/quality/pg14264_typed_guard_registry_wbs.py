"""Mechanical two-section side references for current3 exec and pending4 contexts; never reassign old runtime."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg9954_pure_query_registry_metadata import INV,SNAP,SECTIONS,replaced
from pg9338_wbs_reference_metadata_post import validate
from pg9880_snapshot_nonce_trace import audit
from f03_api_inbound_four_trace_v1 import state_after

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
BEFORE='a79d74918b6008991eb247e9e7458a10a77e5ead'
FIELD='typedGuardCurrentHostPG14264Overlay'
OUT=data.BASE/'PG14264-typed-guard-current-registry-wbs-v1'
REG=('PG14260-typed-guard-current-host-registry-v1','03a68a17327f53e61845e0b4ec9d6485800a4bdb25bf525561c986e7a6adc6bb')
POST=('PG14262-typed-guard-current-registry-post-v1','eba07fb08969621da238f316362a53733e0b6de01218b011f1802d7454f9910a')
CONTEXT=('PG14246-api-inbound-four-context-v1','6205e36fb7902a958401352718f05d06c949098348883a7d10eca73b709a7c98')
CONTEXT_POST=('PG14248-api-inbound-four-post-v1','ba3b2059477cde39356a50a2b17b328b8e5d9b2e91f8a6e5924bccfafd60fb87')

def main():
    invocation=capture(__file__);assert not OUT.exists()
    original,snapshot=[subprocess.check_output(['git','show',BEFORE+':'+p],cwd=data.ROOT) for p in (INV,SNAP)]
    assert (data.ROOT/INV).read_bytes()==original and (data.ROOT/SNAP).read_bytes()==snapshot
    r,p,c,cp=[data.read_checked(data.BASE/name/'manifest.json',pin) for name,pin in (REG,POST,CONTEXT,CONTEXT_POST)]
    assert all(v['actualExit']==0 and v['source']==SOURCE for v in (r,p,c,cp))
    assert p['registryManifestSha256']==REG[1] and p['metadataNegativeVectors']==12
    assert r['tests']==p['originalXmlMethods']==15 and r['suites']==p['originalXmlSuites']==4 and r['originalExecs']==3
    assert r['four100SourcePrograms']==3 and r['incompleteSourcePrograms']==1 and r['unknownOwnerPaths']==6
    assert c['sourceContexts']==cp['sourceContexts']==4 and cp['reviewManifestSha256']==CONTEXT[1]
    ids,refs,pending=state_after();assert (len(ids),len(refs),len(pending),len(ids-refs))==(6247,3682,2821,2565)
    path=lambda value:str((data.BASE/value[0]/'manifest.json').relative_to(data.ROOT))
    overlay=dict(source=SOURCE,registryManifest=path(REG),registrySha256=REG[1],registryPostManifest=path(POST),registryPostSha256=POST[1],record='evidence/01_PT/018_NK-OPS-001/2622_現typed修正source三exec・受信四文脈_参照結合結果.md',originalExecs=3,originalMethods=15,originalSuites=4,fullSourceMeasured=4,four100SourcePrograms=3,four100Physical=3,incompleteSourcePrograms=1,unknownOwnerPaths=6,coverageExecUnion=False,oldSource0061RuntimeTransferred=False,contextManifest=path(CONTEXT),contextSha256=CONTEXT[1],contextPostManifest=path(CONTEXT_POST),contextPostSha256=CONTEXT_POST[1],contextOriginalIds=['PMD-00196','PMD-00198','PMD-00255','PMD-00256'],contextSourceRows=4,contextWholeJoinPending=True,historicalRawIds=6247,referenceIdsAcrossRecordedSourceDomains=3682,pendingIdsAcrossRecordedSourceDomains=2821,noReferenceHistoricalIds=2565,old995RuntimeAndQualificationUnchanged=True,currentWholeSourceQualification=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None)
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,beforeGit=BEFORE,registrySha256=REG[1],registryPostSha256=POST[1],contextSha256=CONTEXT[1],contextPostSha256=CONTEXT_POST[1],inventorySha256=data.sha(result),snapshotSha256=data.sha(new_snapshot),originalMethods=15,originalSuites=4,originalExecs=3,four100SourcePrograms=3,incompleteSourcePrograms=1,newContextRows=4,wholeWbsAuditBefore=before,wholeWbsAuditAfter='INDEPENDENT_POST_PENDING',productTestsExecuted=0,oldRuntimeReassigned=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
