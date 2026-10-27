"""Four exact source hash changes and original34 pure resource/profile/value tests; preserve original ownership and WBS."""
import copy
import difflib
import json
import subprocess
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9880_snapshot_nonce_trace import audit
from pg9954_pure_query_registry_metadata import replaced
from pg9338_wbs_reference_metadata_post import validate
from pg10420_role_code_trace import INV, SNAP, SECTIONS
from trace_owner_join import join_rows, validate as validate_join

SOURCE='c099786934c864f31a6fb520184366c22c84f6ea'
OUT=data.BASE/'PG12512-pure-resource-profile-trace-v1'
POST=data.BASE/'PG12514-pure-resource-profile-trace-post-v1'
MARKER='previousPureResourceProfilePG12512RegistryReference'
REFERENCE='currentPureResourceProfilePG12512BindingReference'
PROOF='da60d127406d686a74b23eb3300411c455cb88c21d0a9f53d401230974dadd87'


def inputs():
    prior=data.read_checked(data.BASE/'PG12484-enum-catalog-trace-v1/manifest.json','66aa004399ee507c8214996c12a487097b09b2f8dcc1e7188df3f9a2e0e4f922')
    proof=data.read_checked(data.BASE/'PG12506-pure-resource-profile-post-v1/manifest.json',PROOF)
    plan=data.read_checked(data.BASE/'PG12496-pure-resource-profile-plan-v1/manifest.json','2afc6237ad922fab24e622ab94b8c9886518bcd742ec76041eb54a1c49f42f14')
    normal=data.read_checked(data.BASE/'PG12500-pure-resource-profile-six-compile-v1/manifest.json','4927aa643bcd905142e5fb4091bfb9050570843435216679d1a21bd9214bd06c')
    assert proof['source']==normal['source']==SOURCE and proof['actualExit']==normal['actualExit']==0
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    assert all(normal['begin']['inputHashes'][r['path']]==r['sha256'] for r in plan['sourceChanges'])
    context=data.read_checked(data.BASE/'PG12508-pure-resource-profile-context-v1/manifest.json','36f949bf42338516cef966581451c0d8294054518606e2888cad53df47f51719')
    context_post=data.read_checked(data.BASE/'PG12510-pure-resource-profile-context-post-v1/manifest.json','e82716db72a0148c01d8df05ecf122cb3377893557be6933fa87e2cbd70b3b80')
    assert context['source']==context_post['source']==SOURCE and context['actualExit']==context_post['actualExit']==0
    raw,snap=[subprocess.check_output(['git','show',SOURCE+':'+p],cwd=data.ROOT) for p in (INV,SNAP)]
    return prior,proof,plan,raw,snap


def expected(prior,proof,plan,raw):
    value=copy.deepcopy(prior)
    omitted={'actualExit','invocation','priorRegistrySha256','proofManifestSha256','wholeWbsAuditBefore'}
    for key in omitted:value.pop(key,None)
    changes={r['path']:r for r in plan['sourceChanges']};bindings=[]
    for row in value['sourceRows']:
        if row['path'] not in changes:continue
        item=changes[row['path']]
        assert row['sha256']==item['beforeSha256'] and row['owner']==row['canonicalOwner']==row['canonicalCostOwner']
        row['sha256']=item['sha256']
        bindings.append(dict(path=row['path'],beforeSha256=item['beforeSha256'],sha256=item['sha256'],canonicalOwner=row['canonicalOwner'],canonicalCostOwner=row['canonicalCostOwner']))
    assert len(bindings)==4 and len(value['sourceRows'])==983 and {r['canonicalOwner'] for r in bindings}=={'WBS-P003-08','WBS-P018-08','WBS-P018-03'}
    logical={r['path']:r for r in json.loads(raw)['artifacts']}
    owner_input=[dict(path=r['path'],sha256=r['sha256'],owner=r['canonicalOwner']) for r in bindings]
    hashes={r['path']:r['sha256'] for r in bindings}
    joined=join_rows(owner_input,logical,hashes,'WBS-F03');validate_join(joined,owner_input,logical,hashes,'WBS-F03')
    assert all(r['ownershipStatus']=='UNKNOWN' for r in joined)
    value.update(source=SOURCE,oldRowsChangedShaOnly=4,allOtherPriorRowsUnchanged=979,
        currentPureResourceProfileBinding=dict(source=SOURCE,sourceChanges=bindings,originalLogicalJoin=joined,registryOwnerBasis='PINNED_PRIOR983_APPROVED_OWNER_PAIRS_NOT_CHANGE_OWNER_OR_LOGICAL_UNKNOWN',stringConstants=8,literalReferences=48,typedIfConstants=7,independentInverseNegativeVectors=57,additionalSharedCostPp=0,oldRuntimeReassigned=False),
        currentPureResourceProfileRuntimeQualification=dict(source=SOURCE,proofManifestSha256=PROOF,originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=34,suites=5,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0,rawStatic=9,sourceLocalContexts=9,contextManifestSha256='36f949bf42338516cef966581451c0d8294054518606e2888cad53df47f51719',contextPostManifestSha256='e82716db72a0148c01d8df05ecf122cb3377893557be6933fa87e2cbd70b3b80',measurementSha256=proof['measurementSha256'],artifactMeasurements=proof['artifactMeasurements'],wholeArtifactsCoverage100=False,zeroDenominatorCountersAreNA=True,whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed={'source','sourceRows','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged'}
    assert all(value[k]==v for k,v in prior.items() if k not in omitted|changed)
    return value


def documents(raw,snap):
    for name in SECTIONS:
        section=json.loads(raw)[name]
        assert MARKER not in section and REFERENCE not in section
        section[MARKER]={k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2344_Pure資源・固定profile・公開値十五是正_製造単体結果.md',currentAddedTestPaths=[])
        section[REFERENCE]=dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentPureResourceProfileBinding',qualification='SOURCE_BOUND_FIFTEEN_SAMEVALUE_INVERSE57_ORIGINAL34_RESOURCE27_PROFILE5_VALUE2_RAW9_CONTEXT9_THREE_COMPLETE_ARTIFACTS_NOT100')
        if name==SECTIONS[0]:section.update(independentPostManifest=str((POST/'manifest.json').relative_to(data.ROOT)),independentPostSha256=None)
        else:section.update(guardManifest=str((POST/'manifest.json').relative_to(data.ROOT)),guardSha256=None)
        raw,_,_=replaced(raw,name,section)
    snap,_,_=replaced(snap,'inventorySha256',data.sha(raw))
    return raw,snap


def main():
    invocation=capture(__file__);assert not OUT.exists()
    prior,proof,plan,raw,snap=inputs()
    assert (data.ROOT/INV).read_bytes()==raw and (data.ROOT/SNAP).read_bytes()==snap
    for name in SECTIONS:assert MARKER not in json.loads(raw)[name] and REFERENCE not in json.loads(raw)[name]
    before=audit();assert before['actualExit']==1
    value=expected(prior,proof,plan,raw);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,wholeWbsAuditBefore=before,**value))
    print(data.sha((OUT/'manifest.json').read_bytes()))


def emit():
    _,_,_,raw,snap=inputs()
    assert (data.ROOT/INV).read_bytes()==raw and (data.ROOT/SNAP).read_bytes()==snap
    after,asnap=documents(raw,snap);patch='*** Begin Patch\n'
    for name,a,b in ((INV,raw,after),(SNAP,snap,asnap)):
        patch+='*** Update File: '+str(data.ROOT/name)+'\n'+'\n'.join('@@' if l.startswith('@@') else l for l in list(difflib.unified_diff(a.decode().splitlines(),b.decode().splitlines(),n=0))[2:])+'\n'
    return patch+'*** End Patch\n'


def post():
    invocation=capture(__file__);assert not POST.exists()
    prior,proof,plan,raw,snap=inputs();reference=expected(prior,proof,plan,raw)
    value=json.loads((OUT/'manifest.json').read_bytes())
    def require(candidate):
        if any(candidate.get(k)!=v for k,v in reference.items()):raise ValueError('exact original owner/current source/runtime qualification required')
    require(value);after,asnap=documents(raw,snap)
    assert (data.ROOT/INV).read_bytes()==after and (data.ROOT/SNAP).read_bytes()==asnap
    validate(after,asnap,json.loads(raw),json.loads(snap));labels=[]
    for field,wrong in [('canonicalOwner','WBS-F03'),('canonicalCostOwner','WBS-F03'),('sha256','0'*64)]:
        bad=copy.deepcopy(reference);row=bad['currentPureResourceProfileBinding']['sourceChanges'][0];assert row[field]!=wrong;row[field]=wrong
        try:require(bad)
        except ValueError:labels.append(field)
        else:raise AssertionError('invalid binding accepted')
    for field,wrong in [('observedTestExecutions',33),('wholeArtifactsCoverage100',True),('oldExecUnion',True)]:
        bad=copy.deepcopy(reference);row=bad['currentPureResourceProfileRuntimeQualification'];assert row[field]!=wrong;row[field]=wrong
        try:require(bad)
        except ValueError:labels.append(field)
        else:raise AssertionError('invalid runtime qualification accepted')
    observed=audit();assert observed['actualExit']==1 and observed['lastError']==value['wholeWbsAuditBefore']['lastError']
    verify(invocation);POST.mkdir();data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),inventorySha256=data.sha(after),snapshotSha256=data.sha(asnap),oldRowsChangedShaOnly=4,allOtherPriorRowsUnchanged=979,metadataNegativeVectors=len(labels),nonVacuousNegativeLabels=labels,wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=observed,productTestsExecuted=0,coverage=None,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
