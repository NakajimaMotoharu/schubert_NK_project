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

SOURCE = '9b255cbe300d1feffeeee076cfa5af318c9b1bb1'
BASE = '183644b09'
OUT = data.BASE/'PG11046-api-request-trace-v1'
POST = data.BASE/'PG11048-api-request-trace-post-v1'


def inputs():
    prior = data.read_checked(data.BASE/'PG11020-form-lifecycle-trace-v1/manifest.json',
        '5d58d536e3162b19421055f087b865af67efde8aa9644695cfa120c24f294bdb')
    proof = data.read_checked(data.BASE/'PG11044-api-request-post-v1/manifest.json',
        '5a6444609c3ce10bc16a40cb024b2b02510cb9b6fae3e96087edf4b37c052c4a')
    plan = data.read_checked(data.BASE/'PG11034-api-request-literal-plan-v1/manifest.json',
        'da263fb3fbf96b3d2de05be39b2c7e4787475f873e8a0b22509ba14e4e1e970b')
    normal = data.read_checked(data.BASE/'PG11038-api-request-six-compile-v1/manifest.json',
        '5f2d2363b5d3ddaf1c61b59e096ffe5705725b332dcf4324381181c1c6c90e7b')
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
    assert len(bindings) == 4 and len(value['sourceRows']) == 983
    assert {r['canonicalOwner'] for r in bindings} == {'WBS-P008-01','WBS-P009-01','WBS-P011-01','WBS-P013-01'}
    assert value['registered'] == 1808 and len(value['unregisteredJavaPaths']) == 2
    value.update(source=SOURCE,oldRowsChangedShaOnly=4,allOtherPriorRowsUnchanged=979,
        currentApiRequestFixtureBinding=dict(source=SOURCE,sourceChanges=bindings,constantsAdded=12,referencesReplaced=72,
            independentInverseNegativeVectors=14,privateIdentifierRenames=1,numericBoundaryConstants=1,allMainClassesUnchanged=1843,additionalSharedCostPp=0,
            oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None),
        currentApiRequestFixtureRuntimeQualification=dict(source=SOURCE,proofManifestSha256='5a6444609c3ce10bc16a40cb024b2b02510cb9b6fae3e96087edf4b37c052c4a',
            originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=16,uniqueMethods=16,
            suites=4,failures=0,errors=0,skipped=0,aborted=0,completeApiMainClasses=467,
            measurementSha256=proof['measurementSha256'],bundleCounters=proof['bundleCounters'],apiFourCounters100=False,
            selectedRequestMainClasses=4,selectedRequestFourCounters100=False,rawStatic=17,sourceLocalContexts=0,whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed_keys = {'source','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged','sourceRows'}
    assert all(value[k] == v for k,v in prior.items() if k not in changed_keys and k in value)
    return value


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousApiRequestFixtureRegistryReference' not in section
        section['previousApiRequestFixtureRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2142_API request四Test実行結果.md',currentAddedTestPaths=[])
        section['currentApiRequestFixtureBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentApiRequestFixtureBinding',
            qualification='SOURCE_BOUND_12_CONSTANTS_PRIVATE_RENAME_BOUNDARY_16_PT_RAW17_API_NOT100')
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
        bad['currentApiRequestFixtureBinding']['sourceChanges'][0][field] = v
        bads.append(bad)
    for field,v in [('oldExecUnion',True),('observedTestExecutions',40),('apiFourCounters100',True)]:
        bad = copy.deepcopy(reference)
        bad['currentApiRequestFixtureRuntimeQualification'][field] = v
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

