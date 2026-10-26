"""Three final source hashes and exact-source runtime fragment; no Product execution."""
import copy
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

ROOT = data.ROOT
BASE = 'd4dd8337f'
SOURCE = '65bcd70a1dec722bd70be03468d9343142a7e789'
PRIOR = '81fc5567bfe107396df12f1ce7b82b50fce0e93dd29731655cb29f2db457e2da'
PROOF = '6be15fbffe5f9b43b3dfbf9977340b0d077b7376e5f376049c513774a06a6fe8'
OUT = data.BASE/'PG10444-pure-view-trace-v1'
POST = data.BASE/'PG10446-pure-view-trace-post-v1'
RECORD = 'evidence/01_PT/018_NK-OPS-001/2068_純粋表示三最終SHA・当source限定PT追跡結果.md'


def inputs():
    prior = data.read_checked(data.BASE/'PG10420-role-code-trace-v1/manifest.json',PRIOR)
    proof = data.read_checked(data.BASE/'PG10440-pure-view-post-v1/manifest.json',PROOF)
    normal = data.read_checked(data.BASE/'PG10434-pure-view-six-compile-v1/manifest.json',
        'd202203f8377e778f1c8b43af42cbad0e8a97614cb0b82e7e97b3143652b5f7e')
    assert proof['actualExit'] == normal['actualExit'] == normal['testsExecuted'] == 0
    assert proof['source'] == normal['source'] == SOURCE
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in hashes.items())
    raw,snap = [subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT) for p in (INV,SNAP)]
    return prior,proof,hashes,raw,snap


def expected(prior,proof,hashes,raw):
    prepared = data.read_checked(data.BASE/'PG10436-pure-view-preflight-v1/manifest.json',
        '0e438c202ff2866b8904bf099a6641129b51329ae29742d83f71c9d7392ced59')
    cases = data.read_checked(data.BASE/'PG10436-pure-view-preflight-v1/cases.json',prepared['casesSha256'])
    changed = proof['sourceHashes']
    assert len(changed) == 3 and changed == prepared['changedTestSourceHashes']
    assert len(cases) == proof['tests'] == 4 and len({r['path'] for r in cases}) == proof['suites'] == 3
    assert {r['path'] for r in cases} == set(changed)
    value = copy.deepcopy(prior)
    for key in ('actualExit','invocation','priorRegistrySha256','proofManifestSha256','wholeWbsAuditBefore'):
        value.pop(key)
    rows = value['sourceRows']
    assert len(rows) == 983
    bindings = []
    for row in rows:
        p = row['path']
        if p not in changed:
            continue
        assert hashes[p] == changed[p] != row['sha256']
        assert row['canonicalOwner'] == row['canonicalCostOwner'] == row['owner'] != 'UNKNOWN'
        subset = [r for r in cases if r['path'] == p]
        assert all(r['canonicalOwner'] == row['canonicalOwner'] for r in subset)
        bindings.append(dict(path=p,previousSha256=row['sha256'],sha256=changed[p],
            canonicalOwner=row['canonicalOwner'],canonicalCostOwner=row['canonicalCostOwner'],
            independentSpec='evidence/01_PT/018_NK-OPS-001/2066_純粋表示モデル三Test_同値定数化・限定再試験仕様.md',
            currentSourceRuntimeFragment=dict(source=SOURCE,
                manifest=str((data.BASE/'PG10440-pure-view-post-v1/manifest.json').relative_to(ROOT)),sha256=PROOF,
                cases=subset,selectedMethodCount=len(subset),additionalSharedCostPp=0,
                qualification='EXACT_SELECTED_METHODS_ONLY_NOT_WHOLE_CLASS_OR_WBS',
                unselectedMethodsExecuted=False,wholeJavaCoverage100=False),
            historicalB98RuntimeReassigned=False))
        row['sha256'] = changed[p]
    assert len(bindings) == 3
    for old,new in zip(prior['sourceRows'],rows):
        adjusted = copy.deepcopy(new)
        if old['path'] in changed:
            adjusted['sha256'] = old['sha256']
        assert adjusted == old
    known = {r['path'] for r in rows}|{r['path'] for r in json.loads(raw)['artifacts']}
    universe = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    assert len(universe) == prior['javaPaths'] == 1810
    assert sorted(universe-known) == prior['unregisteredJavaPaths'] and len(universe-known) == 2
    value.update(source=SOURCE,changedPureViewLiteralBindings=bindings,
        oldRowsChangedShaOnly=3,allOtherPriorRowsUnchanged=980,
        historicalBindingsRetainedWithoutRuntimeReassignment=True,
        currentPureViewRuntimeQualification=dict(source=SOURCE,selectedMethodCount=4,selectedSourceCount=3,
            newTestIds=0,newAccepted=0,wholeJavaCoverage100=False,oldExecUnion=False))
    return value


def contract(value,reference):
    if {k:value[k] for k in reference} != reference:
        raise ValueError('exact current source, fragment, historical ownership and UNKNOWN required')


def documents(raw,snap):
    value = json.loads((OUT/'manifest.json').read_bytes())
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousPureViewLiteralRegistryReference' not in section
        section['previousPureViewLiteralRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record=RECORD,currentAddedTestPaths=[])
        section['currentPureViewLiteralBindingsReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),arrayPath='changedPureViewLiteralBindings',count=3,
            qualification='SOURCE_METADATA_AND_FOUR_METHOD_CURRENT_SOURCE_FRAGMENT_ONLY')
        if name == SECTIONS[0]:
            section.update(independentPostManifest=str((POST/'manifest.json').relative_to(ROOT)),independentPostSha256=None)
        else:
            section.update(guardManifest=str((POST/'manifest.json').relative_to(ROOT)),guardSha256=None)
        assert value['registered'] == 1808
        raw,before,after = replaced(raw,name,section)
        pairs.append((before,after))
    snap,before,after = replaced(snap,'inventorySha256',data.sha(raw))
    return raw,snap,pairs,[(before,after)]


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    prior,proof,hashes,raw,snap = inputs()
    assert (ROOT/INV).read_bytes() == raw and (ROOT/SNAP).read_bytes() == snap
    value = expected(prior,proof,hashes,raw)
    observed = audit()
    assert observed['actualExit'] == 1
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,priorRegistrySha256=PRIOR,
        proofManifestSha256=PROOF,wholeWbsAuditBefore=observed,**value))
    print(data.sha((OUT/'manifest.json').read_bytes()))


def emit():
    _,_,_,raw,snap = inputs()
    assert (ROOT/INV).read_bytes() == raw and (ROOT/SNAP).read_bytes() == snap
    _,_,pairs,spairs = documents(raw,snap)
    patch = '*** Begin Patch\n'
    for name,lines in ((INV,pairs),(SNAP,spairs)):
        patch += '*** Update File: '+str(ROOT/name)+'\n'
        for before,after in lines:
            patch += '@@\n-'+before+'+'+after
    return patch+'*** End Patch\n'


def post():
    invocation = capture(Path(__file__))
    assert not POST.exists()
    prior,proof,hashes,raw,snap = inputs()
    value = json.loads((OUT/'manifest.json').read_bytes())
    reference = expected(prior,proof,hashes,raw)
    contract(value,reference)
    after,asnap,_,_ = documents(raw,snap)
    assert (ROOT/INV).read_bytes() == after and (ROOT/SNAP).read_bytes() == asnap
    validate(after,asnap,json.loads(raw),json.loads(snap))
    edits = [
        ('owner',lambda v:v['sourceRows'][0].update(canonicalOwner='UNKNOWN')),
        ('cost',lambda v:v['sourceRows'][-1].update(canonicalCostOwner='WBS-P014-01')),
        ('current-hash',lambda v:v['changedPureViewLiteralBindings'][0].update(sha256='0'*64)),
        ('runtime-old-source',lambda v:v['changedPureViewLiteralBindings'][0]['currentSourceRuntimeFragment'].update(source=prior['source'])),
        ('false-whole-class',lambda v:v['changedPureViewLiteralBindings'][0]['currentSourceRuntimeFragment'].update(unselectedMethodsExecuted=True)),
        ('false-coverage',lambda v:v['currentPureViewRuntimeQualification'].update(wholeJavaCoverage100=True)),
        ('selected-source-four',lambda v:v['currentPureViewRuntimeQualification'].update(selectedSourceCount=4)),
        ('method-three',lambda v:v['currentPureViewRuntimeQualification'].update(selectedMethodCount=3)),
        ('old-runtime-transfer',lambda v:v['roleRuntimeQualification'].update(source=SOURCE)),
        ('unknown',lambda v:v.update(unregisteredJavaPaths=[])),
        ('source',lambda v:v.update(source=prior['source'])),
        ('new-path',lambda v:v.update(newPathsAdded=1)),
        ('acceptance',lambda v:v.update(newAccepted=1))]
    negatives = []
    for label,edit in edits:
        changed = copy.deepcopy(reference)
        edit(changed)
        try:
            contract(changed,reference)
        except ValueError:
            negatives.append(label)
        else:
            raise AssertionError('invalid metadata accepted')
    observed = audit()
    assert observed['actualExit'] == 1 and observed['lastError'] == value['wholeWbsAuditBefore']['lastError']
    verify(invocation)
    POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        registryManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),inventorySha256=data.sha(after),snapshotSha256=data.sha(asnap),
        metadataNegativeVectors=negatives,registered=1808,total=1810,unknown=2,
        allOtherPriorRowsUnchanged=980,oldRowsChangedShaOnly=3,newPathsAdded=0,
        originalBudgetAndAcceptanceUnchanged=True,originalRuntimeProofReassigned=False,
        wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=observed,
        forwardPostHashNullReason='acyclic immutable post binds actual inventory raw hash',
        productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
