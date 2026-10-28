"""Two Main SHA updates, canonical ownership retained; same-source pure21 qualification only."""
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

SOURCE='0124b5938a50f4ceea542486c336ba12146cb1b4'
OUT=data.BASE/'PG12828-exact-registry-trace-v1'
POST=data.BASE/'PG12829-exact-registry-trace-post-v1'
MARKER='previousExactRegistryPG12828RegistryReference'
REFERENCE='currentExactRegistryPG12828BindingReference'
PROOF='3ba0058d651605f37b1a03293001919b431ce83471ebc14464de1a14bbe00aa3'


def inputs():
    prior=data.read_checked(data.BASE/'PG12804-api-policy-trace-v1/manifest.json','f595af6aa0bb60875d61573bc6de8ff0bef98e0d8dfb5b9ab7761fff4cc7f178')
    proof=data.read_checked(data.BASE/'PG12842-exact-registry-caller-post-v1/manifest.json',PROOF)
    plan=data.read_checked(data.BASE/'PG12817-exact-registry-plan-v3/manifest.json','88a9d3eebc46f473fdc492e5ecdd8806b380aae78701312631019e40eb41e978')
    normal=data.read_checked(data.BASE/'PG12819-exact-registry-six-compile-v2/manifest.json','8a5081b03b988d4370df0c3fa45c69eeeda6d5296543a38f1e2239b0ae088f89')
    assert proof['source']==normal['source']==SOURCE and proof['actualExit']==normal['actualExit']==0
    assert proof['observedTestExecutions']==19 and proof['allMainClassesUnchanged']==1843 and proof['changedTestPhysical']==6
    assert all(data.sha((data.ROOT/p).read_bytes())==digest for p,digest in normal['begin']['inputHashes'].items())
    raw,snap=[subprocess.check_output(['git','show',SOURCE+':'+p],cwd=data.ROOT) for p in [INV,SNAP]]
    return prior,proof,plan,raw,snap


def expected(prior,proof,plan,raw):
    value=copy.deepcopy(prior);omitted={'actualExit','invocation','priorRegistrySha256','proofManifestSha256','wholeWbsAuditBefore'}
    for k in omitted:value.pop(k,None)
    changes={r['path']:r for r in plan['sourceChanges']};bindings=[]
    for row in value['sourceRows']:
        if row['path'] not in changes:continue
        p=changes[row['path']];assert row['sha256']==p['beforeSha256'] and row['owner']==row['canonicalOwner']==row['canonicalCostOwner']=='WBS-P018-09'
        row['sha256']=p['sha256'];bindings.append(dict(path=row['path'],beforeSha256=p['beforeSha256'],sha256=p['sha256'],canonicalOwner=row['canonicalOwner'],canonicalCostOwner=row['canonicalCostOwner']))
    assert len(bindings)==1 and len(value['sourceRows'])==983
    logical={r['path']:r for r in json.loads(raw)['artifacts']};owner_input=[dict(path=r['path'],sha256=r['sha256'],owner=r['canonicalOwner']) for r in bindings];hashes={r['path']:r['sha256'] for r in bindings}
    joined=join_rows(owner_input,logical,hashes,'WBS-F03');validate_join(joined,owner_input,logical,hashes,'WBS-F03')
    value.update(source=SOURCE,oldRowsChangedShaOnly=1,allOtherPriorRowsUnchanged=982,
        currentExactRegistryFixtureBinding=dict(source=SOURCE,sourceChanges=bindings,originalLogicalJoin=joined,additionalSharedCostPp=0,oldRuntimeReassigned=False,publicMethodsUnchanged=True,originalTestMethodsPreserved=10,newTestIds=0),
        currentExactRegistryFixtureRuntimeQualification=dict(source=SOURCE,proofManifestSha256=PROOF,originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=19,suites=2,selectedRegistryMain=proof['selectedRegistryMain'],selectedRegistryInner=proof['selectedRegistryInner'],selectedMethodDetails=proof['selectedMethodDetails'],selectedMainCoverage100=True,wholeArtifactsCoverage100=proof['wholeArtifactCoverage100'],measurementSha256=proof['measurementSha256'],failures=0,errors=0,skipped=0,aborted=0,rawStatic=9,spotbugsSixExit=0,newProductTestIds=0,whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed={'source','sourceRows','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged'}
    assert all(value[k]==v for k,v in prior.items() if k not in omitted|changed)
    return value


def documents(raw,snap):
    for name in SECTIONS:
        section=json.loads(raw)[name];assert MARKER not in section and REFERENCE not in section
        section[MARKER]={k:copy.deepcopy(section[k]) for k in ['source','manifest','sha256','record','currentAddedTestPaths']}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2384_ExactDurationRegistry全10・同期契約_製造単体結果.md',currentAddedTestPaths=[])
        section[REFERENCE]=dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentExactRegistryFixtureBinding',qualification='TEST1_UNIT_STRING_WHOLE19_EXACT_REGISTRY_OUTER_INNER100_NOT_ALL_451')
        if name==SECTIONS[0]:section.update(independentPostManifest=str((POST/'manifest.json').relative_to(data.ROOT)),independentPostSha256=None)
        else:section.update(guardManifest=str((POST/'manifest.json').relative_to(data.ROOT)),guardSha256=None)
        raw,_,_=replaced(raw,name,section)
    snap,_,_=replaced(snap,'inventorySha256',data.sha(raw));return raw,snap


def main():
    invocation=capture(__file__);assert not OUT.exists();prior,proof,plan,raw,snap=inputs()
    assert (data.ROOT/INV).read_bytes()==raw and (data.ROOT/SNAP).read_bytes()==snap
    for name in SECTIONS:assert MARKER not in json.loads(raw)[name] and REFERENCE not in json.loads(raw)[name]
    before=audit();assert before['actualExit']==1
    value=expected(prior,proof,plan,raw);verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,wholeWbsAuditBefore=before,**value));print(data.sha((OUT/'manifest.json').read_bytes()))


def emit():
    _,_,_,raw,snap=inputs();assert (data.ROOT/INV).read_bytes()==raw and (data.ROOT/SNAP).read_bytes()==snap
    after,asnap=documents(raw,snap);patch='*** Begin Patch\n'
    for name,a,b in [(INV,raw,after),(SNAP,snap,asnap)]:
        patch+='*** Update File: '+str(data.ROOT/name)+'\n'+'\n'.join('@@' if l.startswith('@@') else l for l in list(difflib.unified_diff(a.decode().splitlines(),b.decode().splitlines(),n=0))[2:])+'\n'
    return patch+'*** End Patch\n'


def post():
    invocation=capture(__file__);assert not POST.exists();prior,proof,plan,raw,snap=inputs();reference=expected(prior,proof,plan,raw);value=json.loads((OUT/'manifest.json').read_bytes())
    def require(candidate):
        if any(candidate.get(k)!=v for k,v in reference.items()):raise ValueError('exact canonical owner/source and bounded pure21 qualification required')
    require(value);after,asnap=documents(raw,snap);assert (data.ROOT/INV).read_bytes()==after and (data.ROOT/SNAP).read_bytes()==asnap;validate(after,asnap,json.loads(raw),json.loads(snap))
    labels=[]
    for field,badvalue in [('canonicalOwner','WBS-F03'),('canonicalCostOwner','WBS-F03'),('sha256','0'*64)]:
        bad=copy.deepcopy(reference);r=bad['currentExactRegistryFixtureBinding']['sourceChanges'][0];assert r[field]!=badvalue;r[field]=badvalue
        try:require(bad)
        except ValueError:labels.append(field)
        else:raise AssertionError('bad ownership accepted')
    for field,badvalue in [('observedTestExecutions',20),('wholeArtifactsCoverage100',True),('oldExecUnion',True)]:
        bad=copy.deepcopy(reference);r=bad['currentExactRegistryFixtureRuntimeQualification'];assert r[field]!=badvalue;r[field]=badvalue
        try:require(bad)
        except ValueError:labels.append(field)
        else:raise AssertionError('bad qualification accepted')
    observed=audit();assert observed['actualExit']==1 and observed['lastError']==value['wholeWbsAuditBefore']['lastError']
    verify(invocation);POST.mkdir();data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),inventorySha256=data.sha(after),snapshotSha256=data.sha(asnap),oldRowsChangedShaOnly=1,allOtherPriorRowsUnchanged=982,metadataNegativeVectors=len(labels),nonVacuousNegativeLabels=labels,wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=observed,productTestsExecuted=0,newAccepted=0,formalUpdated=False));print(data.sha((POST/'manifest.json').read_bytes()))


if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
