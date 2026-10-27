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

SOURCE = '5eeb36dd1995ebbca2eb3ba7be30b4c4e1b69b81'
BASE = '18036a7e2'
OUT = data.BASE/'PG11192-api-catalog-scalar-pool-trace-v1'
POST = data.BASE/'PG11194-api-catalog-scalar-pool-trace-post-v1'


def inputs():
    prior = data.read_checked(data.BASE/'PG11166-api-metric-fixture-trace-v1/manifest.json',
        'd6b06246b2ad94e41e2c611e9d66feb163ea0ca8dbecd6ce9f15d75de57f80dc')
    proof = data.read_checked(data.BASE/'PG11190-api-catalog-scalar-pool-post-v1/manifest.json',
        'f391e0c02c03d0b716e9f47a13d4cb4acb2bf00df67f5db6ad781cf2e33af8a7')
    plan = data.read_checked(data.BASE/'PG11180-api-catalog-scalar-pool-literal-plan-v1/manifest.json',
        '5bcfbb8bd0fd308a053026d152fd5282f312be1fe630212d5fa5dee04c793a9f')
    normal = data.read_checked(data.BASE/'PG11184-api-catalog-scalar-pool-six-compile-v1/manifest.json',
        'b969eabaf6bc2a4ca11e09532164925246302c919c2cd2e6000b63fb42984a7b')
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
        currentApiCatalogScalarPoolFixtureBinding=dict(source=SOURCE,sourceChanges=bindings,constantsAdded=23,referencesReplaced=162,
            independentInverseNegativeVectors=9,allMainClassesUnchanged=1843,additionalSharedCostPp=0,
            oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None),
        currentApiCatalogScalarPoolFixtureRuntimeQualification=dict(source=SOURCE,proofManifestSha256='f391e0c02c03d0b716e9f47a13d4cb4acb2bf00df67f5db6ad781cf2e33af8a7',
            originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=46,uniqueMethods=46,
            suites=3,failures=0,errors=0,skipped=0,aborted=0,completeApiMainClasses=467,
            measurementSha256=proof['measurementSha256'],bundleCounters=proof['bundleCounters'],apiFourCounters100=False,
            selectedValueMainClasses=5,selectedValueFourCounters100=False,rawStatic=10,sourceLocalContexts=8,unclassifiedRaw=2,whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed_keys = {'source','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged','sourceRows'}
    assert all(value[k] == v for k,v in prior.items() if k not in changed_keys and k in value)
    return value


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousApiCatalogScalarPoolFixtureRegistryReference' not in section
        section['previousApiCatalogScalarPoolFixtureRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2162_API catalog scalar pool三Test実行結果.md',currentAddedTestPaths=[])
        section['currentApiCatalogScalarPoolFixtureBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentApiCatalogScalarPoolFixtureBinding',
            qualification='SOURCE_BOUND_23_CONSTANTS_162_REFS_46_PT_3_SUITES_RAW10_CONTEXT8_COMPARABLE2_FULL_API_NOT100')
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
    context = data.read_checked(data.BASE/'PG11193-api-catalog-scalar-pool-context-post-v1/manifest.json',
        '8d83e5ba41b8ca3396868ae865e289bd6743707574d007f273ea3d070b113559')
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
        bad['currentApiCatalogScalarPoolFixtureBinding']['sourceChanges'][0][field] = v
        bads.append(bad)
    for field,v in [('oldExecUnion',True),('observedTestExecutions',24),('apiFourCounters100',True)]:
        bad = copy.deepcopy(reference)
        bad['currentApiCatalogScalarPoolFixtureRuntimeQualification'][field] = v
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



