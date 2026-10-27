"""One exact source hash update and original2/new2 independent public value diagnostics/null Tests; preserve original ownership and WBS."""
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

SOURCE='03ffd8803faf780d872d002426c599a2a0a3814f'
OUT=data.BASE/'PG12536-public-record-trace-v1'
POST=data.BASE/'PG12537-public-record-trace-post-v1'
MARKER='previousPublicRecordPG12536RegistryReference'
REFERENCE='currentPublicRecordPG12536BindingReference'
PROOF='a323962266faa692be827b8e169d837da893472cd8ae7f5c56f6b61b3ac1a2bc'


def inputs():
    prior=data.read_checked(data.BASE/'PG12512-pure-resource-profile-trace-v1/manifest.json','34a6818a534b3749df66d499d10fde74dbbc783a24014e118332ead636291734')
    proof=data.read_checked(data.BASE/'PG12534-public-record-post-v1/manifest.json',PROOF)
    plan=data.read_checked(data.BASE/'PG12524-public-record-oracle-plan-v1/manifest.json','c6d8ebd9aaf16f7f0edd1c9db95359e9d96d4c49eb6d56520f4899d1bd17de28')
    normal=data.read_checked(data.BASE/'PG12528-public-record-six-compile-v1/manifest.json','59a22edd2c2584134bb3f2d4a5bc3de042d007afee84f6aa8e0bd17e8a24c735')
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
    assert len(bindings)==1 and len(value['sourceRows'])==983 and {r['canonicalOwner'] for r in bindings}=={'WBS-P018-03'}
    logical={r['path']:r for r in json.loads(raw)['artifacts']}
    owner_input=[dict(path=r['path'],sha256=r['sha256'],owner=r['canonicalOwner']) for r in bindings]
    hashes={r['path']:r['sha256'] for r in bindings}
    joined=join_rows(owner_input,logical,hashes,'WBS-F03');validate_join(joined,owner_input,logical,hashes,'WBS-F03')
    assert all(r['ownershipStatus']=='UNKNOWN' for r in joined)
    value.update(source=SOURCE,oldRowsChangedShaOnly=1,allOtherPriorRowsUnchanged=982,
        currentPublicRecordBinding=dict(source=SOURCE,sourceChanges=bindings,originalLogicalJoin=joined,registryOwnerBasis='PINNED_PRIOR983_APPROVED_OWNER_PAIRS_NOT_CHANGE_OWNER_OR_LOGICAL_UNKNOWN',originalMethodsPreserved=2,newMethods=2,newTestIds=['PT-OPS-OBSDATA-003','PT-OPS-OBSDATA-004'],independentGoldenSha256=plan['independentGoldenSha256'],newMissingFieldVectors=7,independentSourceNegativeVectors=13,independentGoldenNegativeVectors=3,additionalSharedCostPp=0,oldRuntimeReassigned=False),
        currentPublicRecordRuntimeQualification=dict(source=SOURCE,proofManifestSha256=PROOF,originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=4,suites=1,originalMethods=2,newMethods=2,newProductTestIds=2,newTestIds=['PT-OPS-OBSDATA-003','PT-OPS-OBSDATA-004'],diagnosticFourCounters=proof['diagnosticFourCounters'],naturalDiagnosticBranchDenominatorZero=True,failures=0,errors=0,skipped=0,aborted=0,rawStatic=0,measurementSha256=proof['measurementSha256'],artifactMeasurements=proof['artifactMeasurements'],wholeArtifactsCoverage100=False,zeroDenominatorCountersAreNA=True,whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed={'source','sourceRows','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged'}
    assert all(value[k]==v for k,v in prior.items() if k not in omitted|changed)
    return value


def documents(raw,snap):
    for name in SECTIONS:
        section=json.loads(raw)[name]
        assert MARKER not in section and REFERENCE not in section
        section[MARKER]={k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2347_公開値診断・null契約二追加_製造単体結果.md',currentAddedTestPaths=[])
        section[REFERENCE]=dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentPublicRecordBinding',qualification='SOURCE_BOUND_OLD2_NEW2_DIAGNOSTIC_CANARY_SEVEN_NULL_VECTORS_COMPLETE_STORAGE_BATCH_NOT100')
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
        bad=copy.deepcopy(reference);row=bad['currentPublicRecordBinding']['sourceChanges'][0];assert row[field]!=wrong;row[field]=wrong
        try:require(bad)
        except ValueError:labels.append(field)
        else:raise AssertionError('invalid binding accepted')
    for field,wrong in [('observedTestExecutions',3),('wholeArtifactsCoverage100',True),('oldExecUnion',True)]:
        bad=copy.deepcopy(reference);row=bad['currentPublicRecordRuntimeQualification'];assert row[field]!=wrong;row[field]=wrong
        try:require(bad)
        except ValueError:labels.append(field)
        else:raise AssertionError('invalid runtime qualification accepted')
    observed=audit();assert observed['actualExit']==1 and observed['lastError']==value['wholeWbsAuditBefore']['lastError']
    verify(invocation);POST.mkdir();data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),inventorySha256=data.sha(after),snapshotSha256=data.sha(asnap),oldRowsChangedShaOnly=1,allOtherPriorRowsUnchanged=982,metadataNegativeVectors=len(labels),nonVacuousNegativeLabels=labels,wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=observed,productTestsExecuted=0,coverage=None,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
