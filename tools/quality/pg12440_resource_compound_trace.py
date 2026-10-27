"""Append eight remaining private-builder Main applicability references without changing original artifacts, ownership, budgets or acceptance."""
import copy
import difflib
import json
import subprocess
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg9880_snapshot_nonce_trace import audit
from pg9954_pure_query_registry_metadata import replaced
from pg9338_wbs_reference_metadata_post import validate
from pg10420_role_code_trace import INV,SNAP,SECTIONS
from trace_owner_join import join_rows,validate as validate_join

SOURCE='1be156b6ebb139713db31a561b8b024972975471'
BASE='d2cbfedc1'
OUT=data.BASE/'PG12440-resource-compound-trace-v1'
POST=data.BASE/'PG12442-resource-compound-trace-post-v1'
FIELD='currentResourceCompoundCatchReference'
PINS={'review':('PG12432-resource-compound-context-v1','20cd6d45c1b336ce6f5320a2844e7ca4bd455a8103beb179bb7e19bd252035de'),'reviewPost':('PG12434-resource-compound-context-post-v1','7457fb8e17f085e7022cca8aad1953eb61c5f3ae128d137cde2be6ba03f30ce3'),'index':('PG12436-current-resource-compound-delta-v1','dd6bab9f8cbb6ba1d1bf6a031f0d194e3c61cb60f02017a4dc5bdd56060573f0'),'indexPost':('PG12438-current-resource-compound-delta-post-v1','6d6ca0d4abafa17df506e10ebeb3b64e17e92e91d2a1117e0ca70ea6c9b44a56')}

def inputs():
    v={k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()}
    assert all(m['source']==SOURCE and m['actualExit']==0 for m in v.values())
    raw,snap=[subprocess.check_output(['git','show',BASE+':'+p],cwd=data.ROOT) for p in (INV,SNAP)]
    rows=data.read_checked(data.BASE/PINS['review'][0]/'review.json',v['review']['reviewSha256'])['rows']
    assert len(rows)==46 and all(data.sha((data.ROOT/r['path']).read_bytes())==r['sourceSha256'] for r in rows)
    logical={r['path']:r for r in json.loads(raw)['artifacts']}
    hashes={r['path']:r['sourceSha256'] for r in rows}
    ownership_input=[dict(path=p,sha256=h,owner=logical[p]['owner']) for p,h in sorted(hashes.items())]
    joined=join_rows(ownership_input,logical,hashes,'WBS-F03');validate_join(joined,ownership_input,logical,hashes,'WBS-F03')
    assert len(joined)==2 and {r['canonicalOwner'] for r in joined}=={'WBS-P003-08','WBS-P018-04'} and all(r['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' for r in joined)
    by_path={r['path']:r for r in joined}
    for row in rows:
        row.update(canonicalOwner=by_path[row['path']]['canonicalOwner'],canonicalCostOwner=by_path[row['path']]['canonicalCostOwner'],registeredHistoricalSourceSha256=logical[row['path']]['sha256'],registrationShaMatchesCurrentSource=logical[row['path']]['sha256']==row['sourceSha256'])
    return v,rows,raw,snap

def reference():
    return dict(source=SOURCE,reviewManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/'+PINS['review'][0]+'/manifest.json',reviewManifestSha256=PINS['review'][1],independentPostManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/'+PINS['reviewPost'][0]+'/manifest.json',independentPostSha256=PINS['reviewPost'][1],currentSetManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/'+PINS['index'][0]+'/manifest.json',currentSetSha256=PINS['index'][1],record='evidence/01_PT/018_NK-OPS-001/2334_資源複合例外二Main四十六件_静的PGレビュー仕様.md',findingIds=sorted(r['id'] for r in data.read_checked(data.BASE/PINS['review'][0]/'review.json',data.read_checked(data.BASE/PINS['review'][0]/'manifest.json',PINS['review'][1])['reviewSha256'])['rows']),qualification='SOURCE_ONLY_SELECTED_RAW46_RETAINED_COMPOUND_CLEANUP_PRECEDENCE_NOT_DYNAMIC_PT',historicalArtifactHashesAreNotCurrentByteProof=True,sourceCorrections=0,rawRetained=len(data.read_checked(data.BASE/PINS['review'][0]/'review.json',data.read_checked(data.BASE/PINS['review'][0]/'manifest.json',PINS['review'][1])['reviewSha256'])['rows']),newProductTestsExecuted=0,newAccepted=0,additionalSharedCostPp=0,whole451Accepted=False)

def documents(raw,snap):
    for name in SECTIONS:
        section=json.loads(raw)[name];assert FIELD not in section
        section[FIELD]=copy.deepcopy(reference());raw,_,_=replaced(raw,name,section)
    snap,_,_=replaced(snap,'inventorySha256',data.sha(raw))
    return raw,snap

def main():
    invocation=capture(__file__);assert not OUT.exists();v,rows,raw,snap=inputs()
    assert (data.ROOT/INV).read_bytes()==raw and (data.ROOT/SNAP).read_bytes()==snap
    before=audit();assert before['actualExit']==1
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,boundManifests=PINS,reference=reference(),sourceContexts=[{k:r[k] for k in ('id','path','sourceSha256','canonicalOwner','canonicalCostOwner','registeredHistoricalSourceSha256','registrationShaMatchesCurrentSource')} for r in rows],priorInventorySha256=data.sha(raw),priorSnapshotSha256=data.sha(snap),wholeWbsAuditBefore=before,sourceCorrections=0,productTestsExecuted=0,coverage=None,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

def emit():
    _,_,raw,snap=inputs();assert (data.ROOT/INV).read_bytes()==raw and (data.ROOT/SNAP).read_bytes()==snap
    after,asnap=documents(raw,snap);patch='*** Begin Patch\n'
    for name,a,b in ((INV,raw,after),(SNAP,snap,asnap)):
        patch+='*** Update File: '+str(data.ROOT/name)+'\n'+'\n'.join('@@' if l.startswith('@@') else l for l in list(difflib.unified_diff(a.decode().splitlines(),b.decode().splitlines(),n=1))[2:])+'\n'
    return patch+'*** End Patch\n'

def post():
    invocation=capture(__file__);assert not POST.exists();_,_,raw,snap=inputs();after,asnap=documents(raw,snap)
    assert (data.ROOT/INV).read_bytes()==after and (data.ROOT/SNAP).read_bytes()==asnap
    old,new=json.loads(raw),json.loads(after)
    for field in ('artifacts','requirements','layouts','sharedOwnership','scopeChanges','counts'):assert new[field]==old[field]
    for section in SECTIONS:
        old_fields={k:v for k,v in new[section].items() if k!=FIELD};assert old_fields==old[section] and new[section][FIELD]==reference()
    validate(after,asnap,json.loads(raw),json.loads(snap));before=json.loads((OUT/'manifest.json').read_bytes())['wholeWbsAuditBefore'];observed=audit();assert observed['actualExit']==1 and observed['lastError']==before['lastError']
    _,rows,_,_=inputs();logical={r['path']:r for r in old['artifacts']};hashes={r['path']:r['sourceSha256'] for r in rows};owner_input=[dict(path=p,sha256=h,owner=logical[p]['owner']) for p,h in sorted(hashes.items())];joined=join_rows(owner_input,logical,hashes,'WBS-F03');negative_fields=[]
    for field,wrong in [('canonicalOwner','WBS-F03'),('canonicalCostOwner','WBS-F03'),('sha256','0'*64),('changeOwner','WBS-G13.07'),('currentSourcePtQualificationInferred',True)]:
        bad=copy.deepcopy(joined);assert bad[0][field]!=wrong;bad[0][field]=wrong
        try:validate_join(bad,owner_input,logical,hashes,'WBS-F03')
        except ValueError:negative_fields.append(field)
        else:raise AssertionError('wrong canonical ownership/qualification accepted')
    verify(invocation);POST.mkdir();data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,traceManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),inventorySha256=data.sha(after),snapshotSha256=data.sha(asnap),ownershipNegativeVectors=len(negative_fields),ownershipNegativeFields=negative_fields,sourceRowsRewritten=0,originalArtifactsRequirementsOwnersBudgetsAcceptanceUnchanged=True,wholeWbsAuditBefore=before,wholeWbsAuditAfter=observed,rawRetained=len(data.read_checked(data.BASE/PINS['review'][0]/'review.json',data.read_checked(data.BASE/PINS['review'][0]/'manifest.json',PINS['review'][1])['reviewSha256'])['rows']),sourceCorrections=0,productTestsExecuted=0,coverage=None,whole451Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((POST/'manifest.json').read_bytes()))

if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
