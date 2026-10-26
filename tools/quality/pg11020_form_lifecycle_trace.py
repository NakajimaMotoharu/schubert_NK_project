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

SOURCE = '9c37bc73a20bab2028413db2c08f6bbdf28c76a6'
BASE = '8efcc554c'
OUT = data.BASE/'PG11020-form-lifecycle-trace-v1'
POST = data.BASE/'PG11022-form-lifecycle-trace-post-v1'


def inputs():
    prior = data.read_checked(data.BASE/'PG10958-form-literal-trace-v1/manifest.json',
        '77e58f6f185a0baebb4c22eb0a4a81bb9af802d7a30d370d46f79698e7da30db')
    proof = data.read_checked(data.BASE/'PG11014-form-close-assert-post-v1/manifest.json',
        'c5272833fa8e1597c93ee20fd5b2bc8fa382ddc9a82e1649108298e78d1caeaa')
    plan = data.read_checked(data.BASE/'PG10974-four-form-literal-plan-v1/manifest.json',
        '6505e1d96b9f996694629586f54f1e57bc8c5143840bad02a5177e544570a09e')
    normal = data.read_checked(data.BASE/'PG11008-form-close-assert-six-compile-v1/manifest.json',
        '5150b4e1aceb6ac51c8a38d253108f6729307cd7df77253b8a37f2c44426ea63')
    assert proof['actualExit'] == normal['actualExit'] == 0 and proof['source'] == normal['source'] == SOURCE
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())

    lifecycle = data.read_checked(data.BASE/'PG10994-form-lifecycle-source-post-v1/manifest.json',
        '5c56476572f520c3e10b83d801fa0ec6203063c6774fccb3600eb18c466cb869')
    close = data.read_checked(data.BASE/'PG10996-form-close-assert-source-post-v1/manifest.json',
        '29bc9b8f4eb0dd2c010da23b5481a8275ba389b709169e41771d6971f403b919')
    assert lifecycle['actualExit'] == close['actualExit'] == 0
    life_changes = {r['path']:r for r in lifecycle['sourceChanges']}
    close_changes = {r['path']:r for r in close['sourceChanges']}
    assert set(life_changes) == set(close_changes) and len(life_changes) == 2
    plan = copy.deepcopy(plan)
    for row in plan['sourceChanges']:
        path = row['path']
        if path in life_changes:
            assert row['sha256'] == life_changes[path]['beforeSha256']
            assert life_changes[path]['sha256'] == close_changes[path]['beforeSha256']
            row['sha256'] = close_changes[path]['sha256']
        assert row['sha256'] == normal['begin']['inputHashes'][path]
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
    assert {r['canonicalOwner'] for r in bindings} == {'WBS-P016-16','WBS-P016-17','WBS-P016-18','WBS-P015-07'}
    assert value['registered'] == 1808 and len(value['unregisteredJavaPaths']) == 2
    value.update(source=SOURCE,oldRowsChangedShaOnly=4,allOtherPriorRowsUnchanged=979,
        currentRemainingFormLifecycleBinding=dict(source=SOURCE,sourceChanges=bindings,constantsAdded=27,referencesReplaced=235,
            independentInverseNegativeVectors=12,independentLifecycleNegativeVectors=7,independentCloseAssertionNegativeVectors=6,allMainClassesUnchanged=1843,additionalSharedCostPp=0,
            oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None),
        currentRemainingFormLifecycleRuntimeQualification=dict(source=SOURCE,proofManifestSha256='c5272833fa8e1597c93ee20fd5b2bc8fa382ddc9a82e1649108298e78d1caeaa',
            originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=40,uniqueMethods=40,
            suites=4,failures=0,errors=0,skipped=0,aborted=0,completeWebMainClasses=358,
            measurementSha256=proof['measurementSha256'],bundleCounters=proof['bundleCounters'],webFourCounters100=False,
            selectedFormMainClasses=10,selectedFormFourCounters100=True,rawStatic=12,sourceLocalContexts=12,whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed_keys = {'source','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged','sourceRows'}
    assert all(value[k] == v for k,v in prior.items() if k not in changed_keys and k in value)
    return value


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousRemainingFormLifecycleRegistryReference' not in section
        section['previousRemainingFormLifecycleRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/016_NK-WEB-002/113_残四form二十七是正・lifecycle追加発見結果.md',currentAddedTestPaths=[])
        section['currentRemainingFormLifecycleBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentRemainingFormLifecycleBinding',
            qualification='SOURCE_BOUND_27_CONSTANTS_40_PT_TEN_FORM_MAIN_FOUR100_RAW12_CONTEXTS_FULL_WEB_NOT100')
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
    context_post = data.read_checked(data.BASE/'PG11018-form-remaining-context-post-v1/manifest.json',
        'cf7b7c88c64f9a04eafab135b022b05eeb2f2b08538e77ea52a943518ffb7947')
    assert context_post['actualExit'] == 0 and context_post['source'] == SOURCE and context_post['sourceLocalContexts'] == 12
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
        bad['currentRemainingFormLifecycleBinding']['sourceChanges'][0][field] = v
        bads.append(bad)
    for field,v in [('oldExecUnion',True),('observedTestExecutions',68),('webFourCounters100',True)]:
        bad = copy.deepcopy(reference)
        bad['currentRemainingFormLifecycleRuntimeQualification'][field] = v
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
        contextIndependentPostSha256='cf7b7c88c64f9a04eafab135b022b05eeb2f2b08538e77ea52a943518ffb7947',
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
