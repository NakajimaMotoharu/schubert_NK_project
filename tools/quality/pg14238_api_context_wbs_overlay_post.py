"""Independent fixed42 WBS side-reference post; all historical semantic state and actual whole-audit HOLD retained."""
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg9954_pure_query_registry_metadata import INV,SNAP,SECTIONS
from pg9338_wbs_reference_metadata_post import validate
from pg9880_snapshot_nonce_trace import audit
from pg14236_api_context_wbs_overlay import SOURCE,BEFORE,FIELD,REVIEW,POST

OUT=data.BASE/'PG14238-api-seven-context-wbs-post-v1'

def require(ok,message):
    if not ok:raise ValueError(message)

def contract(raw,snap,old,old_snap,expected):
    validate(raw,snap,old,old_snap)
    parsed=json.loads(raw)
    for name in SECTIONS:
        require(parsed[name].pop(FIELD)==expected,'fixed new-source reference overlay only, not old runtime reassignment')
    require(parsed==old,'every old field/row/runtime/qualification unchanged')

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only post')
    m=data.read_checked(data.BASE/'PG14236-api-seven-context-wbs-overlay-v1/manifest.json','b203571c753fe698264ffc692d5c3526f9ce85d6e7d03aef7facebfeb8245f1f')
    review=data.read_checked(data.BASE/REVIEW[0]/'manifest.json',REVIEW[1]);post=data.read_checked(data.BASE/POST[0]/'manifest.json',POST[1])
    require(m['source']==review['source']==post['source']==SOURCE and m['actualExit']==review['actualExit']==post['actualExit']==0,'genuine source/results')
    expected=dict(source=SOURCE,reviewManifest=str((data.BASE/REVIEW[0]/'manifest.json').relative_to(data.ROOT)),reviewSha256=REVIEW[1],independentPostManifest=str((data.BASE/POST[0]/'manifest.json').relative_to(data.ROOT)),independentPostSha256=POST[1],record='evidence/01_PT/018_NK-OPS-001/2614_API七Main四十二件_現source文脈再束縛結果.md',sourceReasonRows=42,sourceFiles=7,sourceHashes=review['sourceHashes'],originalIds=[f'PMD-{i:05d}' for first in (1,8,15,22,30,37,62) for i in range(first,first+6)],workerHeldIds=[f'PMD-{i:05d}' for i in range(55,61)],historicalRawIdCount=6247,referenceIdsAcrossRecordedSourceDomains=3678,pendingIdsAcrossRecordedSourceDomains=2817,noReferenceHistoricalIds=2569,currentWholeSourceQualification=False,old995RuntimeAndQualificationUnchanged=True,productTestsExecuted=0,coverage=None,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False)
    original,snapshot=[subprocess.check_output(['git','show',BEFORE+':'+p],cwd=data.ROOT) for p in (INV,SNAP)]
    old,old_snap=json.loads(original),json.loads(snapshot)
    raw,snap=(data.ROOT/INV).read_bytes(),(data.ROOT/SNAP).read_bytes()
    require(data.sha(raw)==m['inventorySha256'] and data.sha(snap)==m['snapshotSha256'],'actual WBS byte hash binding')
    contract(raw,snap,old,old_snap,expected)
    require(all(data.sha((data.ROOT/p).read_bytes())==h for p,h in review['sourceHashes'].items()),'all seven current source hashes unchanged')
    labels=[]
    for label,mutate in [('source',lambda a,b:a[SECTIONS[0]][FIELD].update(source='0'*40)),('count',lambda a,b:a[SECTIONS[0]][FIELD].update(sourceReasonRows=48)),('worker',lambda a,b:a[SECTIONS[0]][FIELD].update(workerHeldIds=[])),('PT',lambda a,b:a[SECTIONS[0]][FIELD].update(productTestsExecuted=42)),('accepted',lambda a,b:a[SECTIONS[0]][FIELD].update(newAccepted=1)),('old-qualification',lambda a,b:a[SECTIONS[0]].update(currentQualification={'forged':True})),('old-owner',lambda a,b:a['artifacts'][0].update(owner='WBS-F03')),('whole',lambda a,b:a[SECTIONS[1]][FIELD].update(currentWholeSourceQualification=True)),('snapshot',lambda a,b:b.update(wholeEffortCompletionRate=50))]:
        a,b=json.loads(raw),json.loads(snap);mutate(a,b)
        changed=json.dumps(a,ensure_ascii=False).encode();b['inventorySha256']=data.sha(changed)
        try:contract(changed,json.dumps(b).encode(),old,old_snap,expected)
        except ValueError:labels.append(label)
        else:raise ValueError('false WBS metadata accepted: '+label)
    for name in ('481_PGPT詳細WBS.json','484_WBSコスト枠・細分化.json'):
        p='documents/400_PGPT/470_PMO/'+name
        require((data.ROOT/p).read_bytes()==subprocess.check_output(['git','show',BEFORE+':'+p],cwd=data.ROOT),'original master plan/budget unchanged')
    after=audit();require(after['actualExit']==m['wholeWbsAuditBefore']['actualExit']==1 and after['lastError']=='ValueError: current physical candidate exact Git/worktree scope','genuine whole audit HOLD before/after')
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,writerManifestSha256='b203571c753fe698264ffc692d5c3526f9ce85d6e7d03aef7facebfeb8245f1f',inventorySha256=data.sha(raw),snapshotSha256=data.sha(snap),metadataNegativeVectors=len(labels),nonVacuousLabels=labels,old995RuntimeAndQualificationUnchanged=True,onlyTwoMetadataSectionsChanged=True,snapshotOnlyChangedField='inventorySha256',sourceReasonRows=42,workerHeld=6,referenceIdsAcrossRecordedSourceDomains=3678,currentWholeSourceQualification=False,wholeWbsAuditBefore=m['wholeWbsAuditBefore'],wholeWbsAuditAfter=after,productTestsExecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
