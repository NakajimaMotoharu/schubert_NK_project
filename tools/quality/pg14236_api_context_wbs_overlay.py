"""Mechanical two-section WBS metadata addition only, preserve all historical rows/acceptance/source domains."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg9954_pure_query_registry_metadata import INV,SNAP,SECTIONS,replaced
from pg9338_wbs_reference_metadata_post import validate
from pg9880_snapshot_nonce_trace import audit
from f03_api_seven_context_trace_v1 import state_after,new_ids

BEFORE='0d8f87a9804a318cc4f13381ff2af989fd151713'
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG14236-api-seven-context-wbs-overlay-v1'
FIELD='apiApplicationContextsPG14236Overlay'
REVIEW=('PG14232-api-seven-forty-two-context-v1','72a764b48dc4a9ad405eec9515123c3ebc1c459968469fd16d769a341e314288')
POST=('PG14234-api-seven-forty-two-post-v1','95c0ee8c3d1b5af371d78a11e518fc95e592196968910c12629d0c421e7c27fe')

def main():
    invocation=capture(__file__);assert not OUT.exists()
    original,snapshot=[subprocess.check_output(['git','show',BEFORE+':'+p],cwd=data.ROOT) for p in (INV,SNAP)]
    assert (data.ROOT/INV).read_bytes()==original and (data.ROOT/SNAP).read_bytes()==snapshot
    review=data.read_checked(data.BASE/REVIEW[0]/'manifest.json',REVIEW[1]);post=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1])
    assert review['source']==post['source']==SOURCE and review['actualExit']==post['actualExit']==post['productTestsExecuted']==0
    assert post['reviewManifestSha256']==REVIEW[1] and post['metadataNegativeVectors']==14
    assert review['sourceContexts']==post['sourceContexts']==42 and review['sourceFiles']==post['sourceFiles']==7
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in review['sourceHashes'].items())
    ids,refs,pending=state_after();assert (len(ids),len(refs),len(pending),len(ids-refs))==(6247,3678,2817,2569)
    overlay=dict(source=SOURCE,reviewManifest=str((data.BASE/REVIEW[0]/'manifest.json').relative_to(data.ROOT)),reviewSha256=REVIEW[1],independentPostManifest=str((data.BASE/POST[0]/'manifest.json').relative_to(data.ROOT)),independentPostSha256=POST[1],record='evidence/01_PT/018_NK-OPS-001/2614_API七Main四十二件_現source文脈再束縛結果.md',sourceReasonRows=42,sourceFiles=7,sourceHashes=review['sourceHashes'],originalIds=sorted(new_ids()),workerHeldIds=review['workerHeldIds'],historicalRawIdCount=6247,referenceIdsAcrossRecordedSourceDomains=3678,pendingIdsAcrossRecordedSourceDomains=2817,noReferenceHistoricalIds=2569,currentWholeSourceQualification=False,old995RuntimeAndQualificationUnchanged=True,productTestsExecuted=0,coverage=None,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False)
    value=json.loads(original);result=original
    for name in SECTIONS:
        section=copy.deepcopy(value[name]);assert FIELD not in section
        section[FIELD]=copy.deepcopy(overlay);result,_,_=replaced(result,name,section)
    new_snapshot,_,_=replaced(snapshot,'inventorySha256',data.sha(result))
    validate(result,new_snapshot,value,json.loads(snapshot))
    restored=json.loads(result)
    for name in SECTIONS:restored[name].pop(FIELD)
    assert restored==value
    before=audit();assert before['actualExit']==1 and before['lastError']=='ValueError: current physical candidate exact Git/worktree scope'
    verify(invocation);OUT.mkdir()
    data.write(OUT/'before.safe.json',dict(inventorySha256=data.sha(original),snapshotSha256=data.sha(snapshot),wholeWbsAudit=before))
    # Bulk mechanical JSON metadata rewrite, never source/config/acceptance edits.
    (data.ROOT/INV).write_bytes(result);(data.ROOT/SNAP).write_bytes(new_snapshot)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,beforeGit=BEFORE,reviewManifestSha256=REVIEW[1],postManifestSha256=POST[1],inventorySha256=data.sha(result),snapshotSha256=data.sha(new_snapshot),originalRawIdCount=6247,referenceIdsAcrossRecordedDomains=3678,pendingIdsAcrossRecordedDomains=2817,noReferenceHistoricalIds=2569,newSourceReasonRows=42,old995RuntimeUnchanged=True,oldSourceQualificationsTransferred=False,wholeWbsAuditBefore=before,wholeWbsAuditAfter='INDEPENDENT_POST_PENDING',productTestsExecuted=0,newAccepted=0,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
