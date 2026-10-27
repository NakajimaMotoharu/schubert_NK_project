"""Four supplied Web metric Test SHA bindings; canonical owners and all historical qualifications preserved."""
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

SOURCE = 'ae55baa85af2174fa01d73b62ad8899d3f44f306'
BASE = '0fb1a78e2'
OUT = data.BASE/'PG11218-web-supplied-metric-fixture-trace-v1'
POST = data.BASE/'PG11220-web-supplied-metric-fixture-trace-post-v1'


def inputs():
    prior = data.read_checked(data.BASE/'PG11192-api-catalog-scalar-pool-trace-v1/manifest.json',
        '11dc1bc6c678115298de68b7be7d0fb7b81fd42f2e1a94d352347515d8d05c81')
    proof = data.read_checked(data.BASE/'PG11216-web-supplied-metric-fixture-post-v1/manifest.json',
        '4e2e884eee64d318cb2faceaceffed3e61e577bcd595943babc4e03734b22c77')
    plan = data.read_checked(data.BASE/'PG11206-web-supplied-metric-fixture-plan-v1/manifest.json',
        '7343097d7d599f6d094f0ea225b7ee5a6aac2869f1e61a60e81cdd8783461e6b')
    normal = data.read_checked(data.BASE/'PG11210-web-supplied-metric-fixture-six-compile-v1/manifest.json',
        '11fb92b0b53b9dba26b93c8aa3e08c09c6c754b1b43fca1c20767ac270666d73')
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
    assert {r['canonicalOwner'] for r in bindings} == {'WBS-P018-09'}
    assert value['registered'] == 1808 and len(value['unregisteredJavaPaths']) == 2
    value.update(source=SOURCE,oldRowsChangedShaOnly=4,allOtherPriorRowsUnchanged=979,
        currentWebSuppliedMetricFixtureBinding=dict(source=SOURCE,sourceChanges=bindings,stringConstants=32,factoryCallConstants=1,referencesReplaced=206,
            independentInverseNegativeVectors=13,allMainClassesUnchanged=1843,additionalSharedCostPp=0,
            oldRuntimeReassigned=False,productTestsExecuted=0,coverage=None),
        currentWebSuppliedMetricFixtureRuntimeQualification=dict(source=SOURCE,proofManifestSha256='4e2e884eee64d318cb2faceaceffed3e61e577bcd595943babc4e03734b22c77',
            originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=32,uniqueMethods=32,
            suites=4,failures=0,errors=0,skipped=0,aborted=0,completeWebMainClasses=358,
            measurementSha256=proof['measurementSha256'],bundleCounters=proof['bundleCounters'],webFourCounters100=False,
            selectedValueMainClasses=10,selectedValueFourCounters100=False,rawStatic=14,sourceLocalContexts=14,unclassifiedRaw=0,whole451Accepted=False,oldExecUnion=False,additionalSharedCostPp=0))
    changed_keys = {'source','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged','sourceRows'}
    assert all(value[k] == v for k,v in prior.items() if k not in changed_keys and k in value)
    return value


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousWebSuppliedMetricFixtureRegistryReference' not in section
        section['previousWebSuppliedMetricFixtureRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record='evidence/01_PT/018_NK-OPS-001/2166_Web供給metric四Test実行結果.md',currentAddedTestPaths=[])
        section['currentWebSuppliedMetricFixtureBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentWebSuppliedMetricFixtureBinding',
            qualification='SOURCE_BOUND_33_CONSTANTS_207_REFS_32_PT_4_SUITES_RAW14_CONTEXT14_FULL_WEB_NOT100')
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
    context = data.read_checked(data.BASE/'PG11219-web-supplied-metric-fixture-context-post-v1/manifest.json',
        'bc889d966d644be0ab9ea4a4e72f24e44edebf9ad4a560ebc38d1b25867464b8')
    assert context['actualExit']==0 and context['source']==SOURCE and context['reviewed']==14
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
        bad['currentWebSuppliedMetricFixtureBinding']['sourceChanges'][0][field] = v
        bads.append(bad)
    for field,v in [('oldExecUnion',True),('observedTestExecutions',24),('webFourCounters100',True)]:
        bad = copy.deepcopy(reference)
        bad['currentWebSuppliedMetricFixtureRuntimeQualification'][field] = v
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



