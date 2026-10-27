"""Two exact source hash changes and original two enum tests; preserve original ownership and WBS."""
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

SOURCE='6929166ee735effb5cae211e1f4cfe44f0b97a0a'
OUT=data.BASE/'PG12484-enum-catalog-trace-v1'
POST=data.BASE/'PG12486-enum-catalog-trace-post-v1'
MARKER='previousEnumCatalogPG12484RegistryReference'
REFERENCE='currentEnumCatalogPG12484BindingReference'
PROOF='acef5bf0b2d633aec473b3c5eb2a972711b081bb08bd8b2bc8849623a7eb3cd5'


def inputs():
    prior=data.read_checked(data.BASE/'PG12458-config-template-trace-v1/manifest.json','95d2b841403afa883e9c99e4cbfa903f2e14d46131e72b7a75a0addbd179b425')
    proof=data.read_checked(data.BASE/'PG12482-enum-catalog-post-v1/manifest.json',PROOF)
    plan=data.read_checked(data.BASE/'PG12472-enum-catalog-plan-v1/manifest.json','c0fb1d72f54e07805f66fa6571c2850ae42ce91e69b1f70aa258a46dbac08762')
    normal=data.read_checked(data.BASE/'PG12476-enum-catalog-six-compile-v1/manifest.json','b94f82650e819d85a09fc6edfa0fe0f6fa01a04fd021ce13a5930602150952fe')
    assert proof['source']==normal['source']==SOURCE and proof['actualExit']==normal['actualExit']==0
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    assert all(normal['begin']['inputHashes'][r['path']]==r['sha256'] for r in plan['sourceChanges'])
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
    assert len(bindings)==2 and len(value['sourceRows'])==983 and {r['canonicalOwner'] for r in bindings}=={'WBS-P003-07','WBS-P017-02'}
    logical={r['path']:r for r in json.loads(raw)['artifacts']}
    owner_input=[dict(path=r['path'],sha256=r['sha256'],owner=r['canonicalOwner']) for r in bindings]
    hashes={r['path']:r['sha256'] for r in bindings}
    joined=join_rows(owner_input,logical,hashes,'WBS-F03');validate_join(joined,owner_input,logical,hashes,'WBS-F03')
    assert all(r['ownershipStatus']=='UNKNOWN' for r in joined)
    value.update(source=SOURCE,oldRowsChangedShaOnly=2,allOtherPriorRowsUnchanged=981,
        currentEnumCatalogBinding=dict(source=SOURCE,sourceChanges=bindings,originalLogicalJoin=joined,registryOwnerBasis='PINNED_PRIOR983_APPROVED_OWNER_PAIRS_NOT_CHANGE_OWNER_OR_LOGICAL_UNKNOWN',stringConstants=5,literalReferences=25,independentInverseNegativeVectors=16,additionalSharedCostPp=0,oldRuntimeReassigned=False),
        currentEnumCatalogRuntimeQualification=dict(source=SOURCE,proofManifestSha256=PROOF,originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=2,suites=2,newProductTestIds=0,failures=0,errors=0,skipped=0,aborted=0,rawStatic=0,measurementSha256=proof['measurementSha256'],artifactMeasurements=proof['artifactMeasurements'],wholeArtifactsCoverage100=False,zeroDenominatorCountersAreNA=True,whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed={'source','sourceRows','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged'}
    assert all(value[k]==v for k,v in prior.items() if k not in omitted|changed)
    return value


def documents(raw,snap):
    for name in SECTIONS:
        section=json.loads(raw)[name]
        assert MARKER not in section and REFERENCE not in section
        section[MARKER]={k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2341_StorageBatch固定enum五是正_製造単体結果.md',currentAddedTestPaths=[])
        section[REFERENCE]=dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentEnumCatalogBinding',qualification='SOURCE_BOUND_FIVE_SAMEVALUE_INVERSE16_ORIGINAL_TWO_ENUMS_ONLY_COMPLETE_STORAGE_BATCH_NOT100')
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
        bad=copy.deepcopy(reference);row=bad['currentEnumCatalogBinding']['sourceChanges'][0];assert row[field]!=wrong;row[field]=wrong
        try:require(bad)
        except ValueError:labels.append(field)
        else:raise AssertionError('invalid binding accepted')
    for field,wrong in [('observedTestExecutions',1),('wholeArtifactsCoverage100',True),('oldExecUnion',True)]:
        bad=copy.deepcopy(reference);row=bad['currentEnumCatalogRuntimeQualification'];assert row[field]!=wrong;row[field]=wrong
        try:require(bad)
        except ValueError:labels.append(field)
        else:raise AssertionError('invalid runtime qualification accepted')
    observed=audit();assert observed['actualExit']==1 and observed['lastError']==value['wholeWbsAuditBefore']['lastError']
    verify(invocation);POST.mkdir();data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),inventorySha256=data.sha(after),snapshotSha256=data.sha(asnap),oldRowsChangedShaOnly=2,allOtherPriorRowsUnchanged=981,metadataNegativeVectors=len(labels),nonVacuousNegativeLabels=labels,wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=observed,productTestsExecuted=0,coverage=None,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
