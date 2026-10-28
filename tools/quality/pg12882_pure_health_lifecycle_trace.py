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

SOURCE='105fd644e90918945607b3ac3e4962843c7762bf'
OUT=data.BASE/'PG12882-pure-health-lifecycle-trace-v1'
POST=data.BASE/'PG12883-pure-health-lifecycle-trace-post-v1'
MARKER='previousPureHealthLifecyclePG12882RegistryReference'
REFERENCE='currentPureHealthLifecyclePG12882BindingReference'
PROOF='927664b9e53c777f78d399ca5448afce4e4b15c39870934a25a6529f809249d4'


def inputs():
    prior=data.read_checked(data.BASE/'PG12858-monitor-sequence-trace-v1/manifest.json','05668fb67894a11ac8226baabd546fac403ee14525a393b04cb5b8011078e6cc')
    proof=data.read_checked(data.BASE/'PG12876-pure-health-lifecycle-post-v1/manifest.json',PROOF)
    plan=data.read_checked(data.BASE/'PG12868-pure-health-lifecycle-plan-v1/manifest.json','e3b10e5565ac1d369b3693a5dc3c5b5c80f8022f8d29226d23c578721b64715b')
    normal=data.read_checked(data.BASE/'PG12870-pure-health-lifecycle-six-compile-v1/manifest.json','bc906632f1a362e7d688ac472784c1e4438008421799f7fec927dad8c818b52a')
    assert proof['source']==normal['source']==SOURCE and proof['actualExit']==normal['actualExit']==0
    assert proof['observedTestExecutions']==38 and proof['allMainClassesUnchanged']==1843 and proof['changedTestPhysical']==2
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
    assert len(bindings)==2 and len(value['sourceRows'])==983
    logical={r['path']:r for r in json.loads(raw)['artifacts']};owner_input=[dict(path=r['path'],sha256=r['sha256'],owner=r['canonicalOwner']) for r in bindings];hashes={r['path']:r['sha256'] for r in bindings}
    joined=join_rows(owner_input,logical,hashes,'WBS-F03');validate_join(joined,owner_input,logical,hashes,'WBS-F03')
    value.update(source=SOURCE,oldRowsChangedShaOnly=2,allOtherPriorRowsUnchanged=981,
        currentPureHealthLifecycleFixtureBinding=dict(source=SOURCE,sourceChanges=bindings,originalLogicalJoin=joined,additionalSharedCostPp=0,oldRuntimeReassigned=False,publicMethodsUnchanged=True,originalTestMethodsPreserved=38,newTestIds=0),
        currentPureHealthLifecycleFixtureRuntimeQualification=dict(source=SOURCE,proofManifestSha256=PROOF,originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=38,suites=5,selectedFourMain=proof['selectedFourMain'],selectedMethodDetails=proof['selectedMethodDetails'],selectedMainCoverage100=True,wholeArtifactsCoverage100=proof['wholeArtifactCoverage100'],measurementSha256=proof['measurementSha256'],failures=0,errors=0,skipped=0,aborted=0,rawStatic=22,spotbugsSixExit=0,newProductTestIds=0,whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed={'source','sourceRows','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged'}
    assert all(value[k]==v for k,v in prior.items() if k not in omitted|changed)
    return value


def documents(raw,snap):
    for name in SECTIONS:
        section=json.loads(raw)[name];assert MARKER not in section and REFERENCE not in section
        section[MARKER]={k:copy.deepcopy(section[k]) for k in ['source','manifest','sha256','record','currentAddedTestPaths']}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2389_PureFilesystemAlertLifecycle原38_製造単体結果.md',currentAddedTestPaths=[])
        section[REFERENCE]=dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentPureHealthLifecycleFixtureBinding',qualification='TEST2_OWNED_POOLS_WHOLE38_FOUR_MAIN100_NOT_ALL_451')
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
        bad=copy.deepcopy(reference);r=bad['currentPureHealthLifecycleFixtureBinding']['sourceChanges'][0];assert r[field]!=badvalue;r[field]=badvalue
        try:require(bad)
        except ValueError:labels.append(field)
        else:raise AssertionError('bad ownership accepted')
    for field,badvalue in [('observedTestExecutions',20),('wholeArtifactsCoverage100',True),('oldExecUnion',True)]:
        bad=copy.deepcopy(reference);r=bad['currentPureHealthLifecycleFixtureRuntimeQualification'];assert r[field]!=badvalue;r[field]=badvalue
        try:require(bad)
        except ValueError:labels.append(field)
        else:raise AssertionError('bad qualification accepted')
    observed=audit();assert observed['actualExit']==1 and observed['lastError']==value['wholeWbsAuditBefore']['lastError']
    verify(invocation);POST.mkdir();data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),inventorySha256=data.sha(after),snapshotSha256=data.sha(asnap),oldRowsChangedShaOnly=2,allOtherPriorRowsUnchanged=981,metadataNegativeVectors=len(labels),nonVacuousNegativeLabels=labels,wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=observed,productTestsExecuted=0,newAccepted=0,formalUpdated=False));print(data.sha((POST/'manifest.json').read_bytes()))


if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
