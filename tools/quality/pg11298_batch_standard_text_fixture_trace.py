"""Six Batch standard-to-text Test SHA bindings; canonical owners and historical runs unchanged."""
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

SOURCE = 'd431ad964355c4e5c602fcb94fe0182da6ae3a61'
BASE = 'a5d11e79d'
OUT = data.BASE/'PG11298-batch-standard-text-fixture-trace-v1'
POST = data.BASE/'PG11300-batch-standard-text-fixture-trace-post-v1'


def inputs():
    prior = data.read_checked(data.BASE/'PG11272-http-recorder-fixture-trace-v1/manifest.json',
        'aa24fa0f0e376c2719293f1ab8681973cfb100e429c2d8e4c1d0d8a39292eb4c')
    proof = data.read_checked(data.BASE/'PG11296-batch-standard-text-fixture-post-v1/manifest.json',
        'b65202a2dd54786993e6f777de86903aa6b9ed1012df174f4dccfe0929c99012')
    plan = data.read_checked(data.BASE/'PG11286-batch-standard-text-fixture-plan-v1/manifest.json',
        '70f577eb77407b8d0dc466325cd035b1d23bcd554dd9d8aa810f1c90c30070fc')
    normal = data.read_checked(data.BASE/'PG11290-batch-standard-text-fixture-six-compile-v1/manifest.json',
        'e5f2c258d8faa0b303f3d74edae30c3dfc03adc3e8964290ac022e5d140104d9')
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
    assert len(bindings) == 6 and len(value['sourceRows']) == 983
    assert {r['canonicalOwner'] for r in bindings} == {'WBS-P018-09'}
    assert value['registered'] == 1808 and len(value['unregisteredJavaPaths']) == 2
    value.update(source=SOURCE,oldRowsChangedShaOnly=6,allOtherPriorRowsUnchanged=977,
        currentBatchStandardTextFixtureBinding=dict(source=SOURCE,sourceChanges=bindings,stringConstants=25,firstBinderConstants=2,referencesReplaced=214,
            independentInverseNegativeVectors=20,allMainClassesUnchanged=1843,additionalSharedCostPp=0,
            oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None),
        currentBatchStandardTextFixtureRuntimeQualification=dict(source=SOURCE,proofManifestSha256='b65202a2dd54786993e6f777de86903aa6b9ed1012df174f4dccfe0929c99012',
            originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=107,uniqueMethods=107,
            suites=6,failures=0,errors=0,skipped=0,aborted=0,completeBatchMainClasses=645,
            measurementSha256=proof['measurementSha256'],bundleCounters=proof['bundleCounters'],batchFourCounters100=False,
            selectedValueMainClasses=6,selectedValueFourCounters100=True,rawStatic=52,sourceLocalContexts=20,unclassifiedRaw=32,whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed_keys = {'source','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged','sourceRows'}
    assert all(value[k] == v for k,v in prior.items() if k not in changed_keys and k in value)
    return value


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousBatchStandardTextFixtureRegistryReference' not in section
        section['previousBatchStandardTextFixtureRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2180_Batch標準SDK・text六Test同値fixture結果.md',currentAddedTestPaths=[])
        section['currentBatchStandardTextFixtureBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentBatchStandardTextFixtureBinding',
            qualification='SOURCE_BOUND_25_STRING_214_REFS_2_FIRST_BINDER_107_PT_6_SUITES_SIX_MAIN100_RAW52_CONTEXT20_UNCLASSIFIED32_FULL_BATCH_NOT100')
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
    context = data.read_checked(data.BASE/'PG11299-batch-standard-text-fixture-context-post-v1/manifest.json',
        'f86c7f68cc9d8f0fa2d8c2772d6772bcd521c7e1869a35d439156d66e8dd2c86')
    assert context['actualExit']==0 and context['source']==SOURCE and context['reviewed']==20
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
        bad['currentBatchStandardTextFixtureBinding']['sourceChanges'][0][field] = v
        bads.append(bad)
    for field,v in [('oldExecUnion',True),('observedTestExecutions',24),('batchFourCounters100',True)]:
        bad = copy.deepcopy(reference)
        bad['currentBatchStandardTextFixtureRuntimeQualification'][field] = v
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
        metadataNegativeVectors=len(bads),registered=1808,javaPaths=1810,unknown=2,oldRowsChangedShaOnly=6,
        allOtherPriorRowsUnchanged=977,originalBudgetAndAcceptanceUnchanged=True,oldRuntimeReassigned=False,
        wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=observed,productTestsExecuted=0,newAccepted=0,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()



