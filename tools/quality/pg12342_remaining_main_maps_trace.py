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

SOURCE='442441c83f73935eb2bd33cd40a7b9884eb7dfe3'
BASE='3370b92a2'
OUT=data.BASE/'PG12342-remaining-main-maps-trace-v1'
POST=data.BASE/'PG12344-remaining-main-maps-trace-post-v1'
FIELD='currentRemainingPrivateMapReference'
PINS={'review':('PG12334-remaining-main-maps-context-v1','4227b10cee4cf12fdb0bf19af53bd3f75236625d4470680294fa8d80cb91a17e'),'reviewPost':('PG12336-remaining-main-maps-post-v1','e180597ce36baed2150998a199c08d182ca79f147fd08f8b1ef36abf36b02db0'),'index':('PG12338-current-remaining-main-maps-delta-v1','ac6daf60dbf666a1ed0af9b17a49c1ad651e963e7bc54a555ab7c7733521fdde'),'indexPost':('PG12340-current-remaining-main-maps-delta-post-v1','ef0537f204a8fcfad0e50918464abe66e8bff61322453dbb6b51bc0d482f3949')}

def inputs():
    v={k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()}
    assert all(m['source']==SOURCE and m['actualExit']==0 for m in v.values())
    raw,snap=[subprocess.check_output(['git','show',BASE+':'+p],cwd=data.ROOT) for p in (INV,SNAP)]
    assert data.sha(raw)==v['review']['inventorySha256']
    rows=data.read_checked(data.BASE/PINS['review'][0]/'review.json',v['review']['reviewSha256'])['rows']
    assert len(rows)==8 and all(data.sha((data.ROOT/r['path']).read_bytes())==r['sourceSha256'] for r in rows)
    return v,rows,raw,snap

def reference():
    return dict(source=SOURCE,reviewManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/'+PINS['review'][0]+'/manifest.json',reviewManifestSha256=PINS['review'][1],independentPostManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/'+PINS['reviewPost'][0]+'/manifest.json',independentPostSha256=PINS['reviewPost'][1],currentSetManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/'+PINS['index'][0]+'/manifest.json',currentSetSha256=PINS['index'][1],record='evidence/01_PT/018_NK-OPS-001/2323_Main残Map八件_所有・copyレビュー仕様.md',findingIds=['PMD-02847','PMD-02848','PMD-02849','PMD-02850','PMD-02853','PMD-02854','PMD-02855','PMD-03093'],qualification='SOURCE_ONLY_SELECTED_RAW8_RETAINED_LOCAL_BUILDER_COPY_IMMUTABLE_VALUES_NO_DYNAMIC_QUALIFICATION',historicalArtifactHashesAreNotCurrentByteProof=True,sourceCorrections=0,rawRetained=len(data.read_checked(data.BASE/PINS['review'][0]/'review.json',data.read_checked(data.BASE/PINS['review'][0]/'manifest.json',PINS['review'][1])['reviewSha256'])['rows']),newProductTestsExecuted=0,newAccepted=0,additionalSharedCostPp=0,whole451Accepted=False)

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
    verify(invocation);POST.mkdir();data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,traceManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),inventorySha256=data.sha(after),snapshotSha256=data.sha(asnap),sourceRowsRewritten=0,originalArtifactsRequirementsOwnersBudgetsAcceptanceUnchanged=True,wholeWbsAuditBefore=before,wholeWbsAuditAfter=observed,rawRetained=len(data.read_checked(data.BASE/PINS['review'][0]/'review.json',data.read_checked(data.BASE/PINS['review'][0]/'manifest.json',PINS['review'][1])['reviewSha256'])['rows']),sourceCorrections=0,productTestsExecuted=0,coverage=None,whole451Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((POST/'manifest.json').read_bytes()))

if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
