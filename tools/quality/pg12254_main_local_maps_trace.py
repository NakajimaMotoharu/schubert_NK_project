"""Append four Main applicability references without changing original artifacts, ownership, budgets or acceptance."""
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

SOURCE='d8a2b7952b321b75fe7fcc1c8d3acb287faca6ec'
BASE='7edd5d08a6e590ecbc9dac493202ca552dd4e5a7'
OUT=data.BASE/'PG12254-main-local-maps-trace-v1'
POST=data.BASE/'PG12255-main-local-maps-trace-post-v1'
FIELD='currentThreadConfinedMainMapReference'
PINS={'review':('PG12246-main-local-maps-context-v1','1481093beb6c7d9642959dcd0b4b956236fda824f2df97379cbaf5ec23d7948e'),'reviewPost':('PG12248-main-local-maps-post-v1','6167dcf7e8671527f16ec20d4c6f0f2fe2b02257a9b404a03719bd588b900fb3'),'index':('PG12250-current-main-local-maps-delta-v1','fb90f713360f60c7e10d089ce428ff2dd158a1e65bd3397b8aa3080cd9915738'),'indexPost':('PG12252-current-main-local-maps-delta-post-v1','01cdb3a25fcda4dcc33543fc239c3e240db90c9a410d695233e9539b7f10845d')}

def inputs():
    v={k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()}
    assert all(m['source']==SOURCE and m['actualExit']==0 for m in v.values())
    raw,snap=[subprocess.check_output(['git','show',BASE+':'+p],cwd=data.ROOT) for p in (INV,SNAP)]
    assert data.sha(raw)==v['review']['inventorySha256']
    rows=data.read_checked(data.BASE/PINS['review'][0]/'review.json',v['review']['reviewSha256'])['rows']
    assert len(rows)==4 and all(data.sha((data.ROOT/r['path']).read_bytes())==r['sourceSha256'] for r in rows)
    return v,rows,raw,snap

def reference():
    return dict(source=SOURCE,reviewManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/'+PINS['review'][0]+'/manifest.json',reviewManifestSha256=PINS['review'][1],independentPostManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/'+PINS['reviewPost'][0]+'/manifest.json',independentPostSha256=PINS['reviewPost'][1],currentSetManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/'+PINS['index'][0]+'/manifest.json',currentSetSha256=PINS['index'][1],record='evidence/01_PT/018_NK-OPS-001/2312_Main局所Map四件_静的適用性レビュー.md',findingIds=['PMD-00122','PMD-03094','PMD-03111','PMD-07323'],qualification='SOURCE_APPLICABILITY_ONLY_RAW4_RETAINED_NO_NEW_PT_OTHER3_NOT_RUNTIME_QUALIFIED',historicalArtifactHashMismatchRetained=1,sourceCorrections=0,rawRetained=4,newProductTestsExecuted=0,newAccepted=0,additionalSharedCostPp=0,whole451Accepted=False)

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
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,boundManifests=PINS,reference=reference(),sourceRows=[{k:r[k] for k in ('id','path','sourceSha256','canonicalOwner','canonicalCostOwner','registeredHistoricalSourceSha256','registrationShaMatchesCurrentSource')} for r in rows],priorInventorySha256=data.sha(raw),priorSnapshotSha256=data.sha(snap),wholeWbsAuditBefore=before,sourceCorrections=0,productTestsExecuted=0,coverage=None,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

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
    verify(invocation);POST.mkdir();data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,traceManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),inventorySha256=data.sha(after),snapshotSha256=data.sha(asnap),sourceRowsRewritten=0,originalArtifactsRequirementsOwnersBudgetsAcceptanceUnchanged=True,wholeWbsAuditBefore=before,wholeWbsAuditAfter=observed,rawRetained=4,sourceCorrections=0,productTestsExecuted=0,coverage=None,whole451Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((POST/'manifest.json').read_bytes()))

if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
