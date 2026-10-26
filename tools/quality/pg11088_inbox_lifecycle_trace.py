"""Two current form Test SHA bindings and genuine16-method qualification, all prior owner/cost unchanged."""
import copy
import difflib
import json
from pathlib import Path
import subprocess
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9880_snapshot_nonce_trace import audit
from pg9954_pure_query_registry_metadata import replaced
from pg9338_wbs_reference_metadata_post import validate
from pg10420_role_code_trace import INV, SNAP, SECTIONS

SOURCE = 'f97723798f3f71a9112b4bbecfba531dba9b34b6'
BASE = 'ebea8774d'
OUT = data.BASE/'PG11088-inbox-lifecycle-trace-v1'
POST = data.BASE/'PG11090-inbox-lifecycle-trace-post-v1'


def inputs():
    prior = data.read_checked(data.BASE/'PG11046-api-request-trace-v1/manifest.json',
        '50c22418669fcc59bb38939cf9cda03dedaab07cc86932c9c45faba05248a861')
    proof = data.read_checked(data.BASE/'PG11086-inbox-lifecycle-post-v1/manifest.json',
        '09269e164031c8533a7517eb1b3e6fccd91cc0adfce00e824bd291656bb6c200')
    plan = data.read_checked(data.BASE/'PG11064-inbox-value-literal-plan-v1/manifest.json',
        'f615b529edc3942a68b8d817d07f03123d1056eecca2419acdd4256b8b232913')
    normal = data.read_checked(data.BASE/'PG11080-inbox-lifecycle-six-compile-v1/manifest.json',
        'a58e4f704b97a8fc58ff094db32231e455767e5b15972af3b66fc933f91a3641')
    assert proof['actualExit'] == normal['actualExit'] == 0 and proof['source'] == normal['source'] == SOURCE
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())

    lifecycle = data.read_checked(data.BASE/'PG11078-inbox-value-lifecycle-source-post-v1/manifest.json',
        '054e9c15a32220f5920d410cdb66c9aadecf0174c3f692129472ac52209ff6ee')
    changes = {r['path']:r for r in lifecycle['sourceChanges']}
    assert lifecycle['actualExit']==0 and len(changes)==3
    plan = copy.deepcopy(plan)
    for row in plan['sourceChanges']:
        if row['path'] in changes:
            item=changes[row['path']]
            assert row['sha256']==item['beforeSha256']
            row['sha256']=item['sha256']
        assert row['sha256']==normal['begin']['inputHashes'][row['path']]
    old = [subprocess.check_output(['git','show',BASE+':'+p],cwd=data.ROOT) for p in (INV,SNAP)]
    return prior,proof,plan,old


def expected(prior,proof,plan):
    value = copy.deepcopy(prior)
    for key in ('actualExit','invocation','priorRegistrySha256','proofManifestSha256','wholeWbsAuditBefore'):
        value.pop(key,None)
    changed = {r['path']:r for r in plan['sourceChanges']}
    bindings = []
    for row in value['sourceRows']:
        if row['path'] not in changed:
            continue
        item = changed[row['path']]
        assert row['sha256'] == item['beforeSha256'] and row['canonicalOwner'] == row['canonicalCostOwner'] == row['owner']
        row['sha256'] = item['sha256']
        bindings.append(dict(path=row['path'],beforeSha256=item['beforeSha256'],sha256=item['sha256'],
            canonicalOwner=row['canonicalOwner'],canonicalCostOwner=row['canonicalCostOwner']))
    assert len(bindings) == 4 and len(value['sourceRows']) == 983
    assert {r['canonicalOwner'] for r in bindings} == {'WBS-P006-01','WBS-P014-01'}
    assert value['registered'] == 1808 and len(value['unregisteredJavaPaths']) == 2
    value.update(source=SOURCE,oldRowsChangedShaOnly=4,allOtherPriorRowsUnchanged=979,
        currentInboxValueFixtureBinding=dict(source=SOURCE,sourceChanges=bindings,constantsAdded=12,referencesReplaced=89,
            independentInverseNegativeVectors=12,independentLifecycleNegativeVectors=12,twrOwnedDeclarations=15,twrScopes=8,normalCloseAssertionsAdded=3,numericBoundaryConstants=1,allMainClassesUnchanged=1843,additionalSharedCostPp=0,
            oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None),
        currentInboxValueFixtureRuntimeQualification=dict(source=SOURCE,proofManifestSha256='09269e164031c8533a7517eb1b3e6fccd91cc0adfce00e824bd291656bb6c200',
            originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=15,uniqueMethods=15,
            suites=4,failures=0,errors=0,skipped=0,aborted=0,completeApiMainClasses=467,
            measurementSha256=proof['measurementSha256'],bundleCounters=proof['bundleCounters'],apiFourCounters100=False,
            selectedValueMainClasses=16,selectedValueFourCounters100=False,rawStatic=0,sourceLocalContexts=0,whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed_keys = {'source','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged','sourceRows'}
    assert all(value[k] == v for k,v in prior.items() if k not in changed_keys and k in value)
    return value


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousInboxValueFixtureRegistryReference' not in section
        section['previousInboxValueFixtureRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2146_Inbox純粋値四Test・所有是正結果.md',currentAddedTestPaths=[])
        section['currentInboxValueFixtureBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentInboxValueFixtureBinding',
            qualification='SOURCE_BOUND_12_CONSTANTS_15_OWNED_TWR_15_PT_SELECTED_STATIC0_COMPLETE_API_NOT100')
        if name == SECTIONS[0]:
            section.update(independentPostManifest=str((POST/'manifest.json').relative_to(data.ROOT)),independentPostSha256=None)
        else:
            section.update(guardManifest=str((POST/'manifest.json').relative_to(data.ROOT)),guardSha256=None)
        raw,before,after = replaced(raw,name,section)
        pairs.append((before,after))
    snap,before,after = replaced(snap,'inventorySha256',data.sha(raw))
    return raw,snap,pairs,[(before,after)]


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    prior,proof,plan,(raw,snap) = inputs()
    assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    observed = audit()
    assert observed['actualExit'] == 1
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,wholeWbsAuditBefore=observed,**expected(prior,proof,plan)))
    print(data.sha((OUT/'manifest.json').read_bytes()))


def emit():
    _,_,_,(raw,snap) = inputs()
    assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    after,asnap,_,_ = documents(raw,snap)
    patch = '*** Begin Patch\n'
    for name,before,result in ((INV,raw,after),(SNAP,snap,asnap)):
        patch += '*** Update File: '+str(data.ROOT/name)+'\n'
        lines = list(difflib.unified_diff(before.decode().splitlines(),result.decode().splitlines(),n=2))[2:]
        patch += '\n'.join('@@' if line.startswith('@@') else line for line in lines)+'\n'
    return patch+'*** End Patch\n'


def contract(value,reference):
    if any(value.get(k) != v for k,v in reference.items()):
        raise ValueError('exact source/owner/cost/runtime metadata required')


def post():
    invocation = capture(Path(__file__))
    assert not POST.exists()
    prior,proof,plan,(raw,snap) = inputs()
    value = json.loads((OUT/'manifest.json').read_bytes())
    reference = expected(prior,proof,plan)
    contract(value,reference)
    after,asnap,_,_ = documents(raw,snap)
    assert (data.ROOT/INV).read_bytes() == after and (data.ROOT/SNAP).read_bytes() == asnap
    validate(after,asnap,json.loads(raw),json.loads(snap))
    bads = []
    for field,v in [('canonicalOwner','WBS-G13.07'),('canonicalCostOwner','WBS-F03'),('sha256','0'*64)]:
        bad = copy.deepcopy(reference)
        bad['currentInboxValueFixtureBinding']['sourceChanges'][0][field] = v
        bads.append(bad)
    for field,v in [('oldExecUnion',True),('observedTestExecutions',16),('apiFourCounters100',True)]:
        bad = copy.deepcopy(reference)
        bad['currentInboxValueFixtureRuntimeQualification'][field] = v
        bads.append(bad)
    for bad in bads:
        try:
            contract(bad,reference)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid source/owner/cost/runtime metadata accepted')
    observed = audit()
    assert observed['actualExit'] == 1 and observed['lastError'] == value['wholeWbsAuditBefore']['lastError']
    verify(invocation)
    POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        registryManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),inventorySha256=data.sha(after),snapshotSha256=data.sha(asnap),
        metadataNegativeVectors=len(bads),registered=1808,javaPaths=1810,unknown=2,oldRowsChangedShaOnly=4,
        allOtherPriorRowsUnchanged=979,originalBudgetAndAcceptanceUnchanged=True,oldRuntimeReassigned=False,
        wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=observed,productTestsExecuted=0,newAccepted=0,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()


