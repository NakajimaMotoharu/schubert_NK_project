"""Append immutable auxiliary-cardinality correction references; no source or acceptance changes."""
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
BASE='f60feaf1dda04b5789be1e235837aeb210e28fd1'
OUT=data.BASE/'PG12276-context-cardinality-trace-v1'
POST=data.BASE/'PG12278-context-cardinality-trace-post-v1'
FIELD='currentContextCardinalitySupplementReference'
PINS={'supplement':('PG12272-context-cardinality-supplement-v1','d2dbc3890af82f6a5dade993e3ee4e18198f303f35951f105d40b22a8c3a9373'),'independentPost':('PG12274-context-cardinality-post-v1','8da37464e00bf938e289cde878df65bd016b418ea140b38bfd74469343911544')}

def inputs():
    v={k:data.read_checked(data.BASE/f/'manifest.json',h) for k,(f,h) in PINS.items()}
    assert all(m['source']==SOURCE and m['actualExit']==0 for m in v.values())
    assert v['independentPost']['metadataNegativeVectors']==49
    assert v['independentPost']['currentSourceDerivedRaw']==8597
    assert v['independentPost']['sourceDomainsNonAdditive'] is True
    raw,snap=[subprocess.check_output(['git','show',BASE+':'+p],cwd=data.ROOT) for p in (INV,SNAP)]
    return v,[],raw,snap

def reference():
    post=data.read_checked(data.BASE/PINS['independentPost'][0]/'manifest.json',PINS['independentPost'][1])
    return dict(executionSource=SOURCE,sourceDomainsNonAdditive=True,
        manifests={k:dict(path='evidence/01_PT/018_NK-OPS-001/evidence/provisional/'+f+'/manifest.json',sha256=h) for k,(f,h) in PINS.items()},
        corrections=copy.deepcopy(post['domains']),correctedField='rawRetained',
        fieldMeaning='COUNT_UNIQUE_SELECTED_REVIEWED_RETAINED_FINDING_IDS',
        record='evidence/01_PT/018_NK-OPS-001/2316_Context補助件数二件_是正仕様・結果.md',
        qualification='AUXILIARY_METADATA_CORRECTION_TWO_DOMAINS_NO_NEW_PRODUCT_RESULT',
        oldManifestsAndOriginalResultsImmutable=True,sourceCorrections=0,
        productTestsExecuted=0,coverage=None,newAccepted=0,additionalSharedCostPp=0,whole451Accepted=False)

def documents(raw,snap):
    for name in SECTIONS:
        section=json.loads(raw)[name];assert FIELD not in section
        section[FIELD]=copy.deepcopy(reference());raw,_,_=replaced(raw,name,section)
    snap,_,_=replaced(snap,'inventorySha256',data.sha(raw))
    return raw,snap

def main():
    invocation=capture(__file__);assert not OUT.exists();_,_,raw,snap=inputs()
    assert (data.ROOT/INV).read_bytes()==raw and (data.ROOT/SNAP).read_bytes()==snap
    before=audit();assert before['actualExit']==1
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,boundManifests=PINS,reference=reference(),sourceContexts=[],correctedMetadataFields=2,priorInventorySha256=data.sha(raw),priorSnapshotSha256=data.sha(snap),wholeWbsAuditBefore=before,sourceCorrections=0,productTestsExecuted=0,coverage=None,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

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
    verify(invocation);POST.mkdir();data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,traceManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),inventorySha256=data.sha(after),snapshotSha256=data.sha(asnap),sourceRowsRewritten=0,originalArtifactsRequirementsOwnersBudgetsAcceptanceUnchanged=True,wholeWbsAuditBefore=before,wholeWbsAuditAfter=observed,correctedMetadataFields=2,sourceCorrections=0,productTestsExecuted=0,coverage=None,whole451Accepted=False,newAccepted=0,effortPercent=None));print(data.sha((POST/'manifest.json').read_bytes()))

if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
