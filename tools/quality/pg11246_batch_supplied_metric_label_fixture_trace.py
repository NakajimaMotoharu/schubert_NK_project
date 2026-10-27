"""Three Batch supplied metric/label Test SHA bindings; canonical owners and historical runs unchanged."""
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

SOURCE = 'ef86a244b2f528a2d60bd0f22a94a853ce3146ff'
BASE = '0ea02b2e2'
OUT = data.BASE/'PG11246-batch-supplied-metric-label-fixture-trace-v1'
POST = data.BASE/'PG11248-batch-supplied-metric-label-fixture-trace-post-v1'


def inputs():
    prior = data.read_checked(data.BASE/'PG11218-web-supplied-metric-fixture-trace-v1/manifest.json',
        '7fe0887ff4775b11278d861b2f43c22c6a5ce467b4d452d6e67a3abc3a100195')
    proof = data.read_checked(data.BASE/'PG11244-batch-supplied-metric-label-fixture-post-v1/manifest.json',
        'bbe1078458fcab7da33b9a541290b4b2fcf21d9017a681c00e83471d25e61aee')
    plan = data.read_checked(data.BASE/'PG11234-batch-supplied-metric-label-fixture-plan-v1/manifest.json',
        '6f1074d826b78dd85bad11d2cf041e3515cf0d587a0639372302ac15e9d5fbe3')
    normal = data.read_checked(data.BASE/'PG11238-batch-supplied-metric-label-fixture-six-compile-v1/manifest.json',
        '5c832221f384ea840e6a9b5cf9b55e7c6f797e472647d7831c3a8ad1409f0bbe')
    assert proof['actualExit'] == normal['actualExit'] == 0 and proof['source'] == normal['source'] == SOURCE
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())

    assert all(r['sha256'] == normal['begin']['inputHashes'][r['path']] for r in plan['sourceChanges'])
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
    assert len(bindings) == 3 and len(value['sourceRows']) == 983
    assert {r['canonicalOwner'] for r in bindings} == {'WBS-P018-09'}
    assert value['registered'] == 1808 and len(value['unregisteredJavaPaths']) == 2
    value.update(source=SOURCE,oldRowsChangedShaOnly=3,allOtherPriorRowsUnchanged=980,
        currentBatchSuppliedMetricLabelFixtureBinding=dict(source=SOURCE,sourceChanges=bindings,stringConstants=23,factoryCallConstants=2,referencesReplaced=180,
            independentInverseNegativeVectors=11,allMainClassesUnchanged=1843,additionalSharedCostPp=0,
            oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None),
        currentBatchSuppliedMetricLabelFixtureRuntimeQualification=dict(source=SOURCE,proofManifestSha256='bbe1078458fcab7da33b9a541290b4b2fcf21d9017a681c00e83471d25e61aee',
            originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=30,uniqueMethods=30,
            suites=3,failures=0,errors=0,skipped=0,aborted=0,completeBatchMainClasses=645,
            measurementSha256=proof['measurementSha256'],bundleCounters=proof['bundleCounters'],batchFourCounters100=False,
            selectedValueMainClasses=6,selectedValueFourCounters100=True,rawStatic=9,sourceLocalContexts=8,unclassifiedRaw=1,whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed_keys = {'source','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged','sourceRows'}
    assert all(value[k] == v for k,v in prior.items() if k not in changed_keys and k in value)
    return value


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousBatchSuppliedMetricLabelFixtureRegistryReference' not in section
        section['previousBatchSuppliedMetricLabelFixtureRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2172_Batch供給metric label三Test実行結果.md',currentAddedTestPaths=[])
        section['currentBatchSuppliedMetricLabelFixtureBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentBatchSuppliedMetricLabelFixtureBinding',
            qualification='SOURCE_BOUND_25_CONSTANTS_182_REFS_30_PT_3_SUITES_SIX_MAIN100_RAW9_CONTEXT8_COMPARABLE1_FULL_BATCH_NOT100')
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
    context = data.read_checked(data.BASE/'PG11247-batch-supplied-metric-label-fixture-context-post-v1/manifest.json',
        'f9c21953fe2e41cc507e0bd249358ef8d3fe4c21af75c9771889f73d529cb817')
    assert context['actualExit']==0 and context['source']==SOURCE and context['reviewed']==8
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
        bad['currentBatchSuppliedMetricLabelFixtureBinding']['sourceChanges'][0][field] = v
        bads.append(bad)
    for field,v in [('oldExecUnion',True),('observedTestExecutions',24),('batchFourCounters100',True)]:
        bad = copy.deepcopy(reference)
        bad['currentBatchSuppliedMetricLabelFixtureRuntimeQualification'][field] = v
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
        metadataNegativeVectors=len(bads),registered=1808,javaPaths=1810,unknown=2,oldRowsChangedShaOnly=3,
        allOtherPriorRowsUnchanged=980,originalBudgetAndAcceptanceUnchanged=True,oldRuntimeReassigned=False,
        wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=observed,productTestsExecuted=0,newAccepted=0,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()



