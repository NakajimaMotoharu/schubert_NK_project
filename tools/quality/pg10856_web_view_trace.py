"""Web eight Test fixture source SHA and genuine68method qualification; old runtime unchanged."""
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
BASE = 'ce5dded70ecd53d2202fc4b07517d8f8d85a1f01'
SOURCE = 'd959404cdef9bdfaa9be8de5a3c787db13a72c1a'
PRIOR = 'ee63139a02a4b8b716f22be94a2dfc300fd363a754f8663f5cf9fe46e1480544'
PROOF = '0bc7ae26b46d0084fbce8b2591f5d670531792f1090e2f34b544227798518749'
OUT = data.BASE/'PG10856-web-view-trace-v1'
POST = data.BASE/'PG10858-web-view-trace-post-v1'
RECORD = 'evidence/01_PT/016_NK-WEB-002/107_LogScenario八Test五十五是正・六十八PT・全Web計測結果.md'


def inputs():
    prior = data.read_checked(data.BASE/'PG10816-protocol-component-quality-trace-v1/manifest.json',PRIOR)
    proof = data.read_checked(data.BASE/'PG10855-web-view-post-recovery-v1/manifest.json',PROOF)
    normal = data.read_checked(data.BASE/'PG10846-web-view-six-compile-v1/manifest.json',
        '8ac965984ed15b14e172677cf0c254012b70bece197feca7fea137df98cc751e')
    assert proof['source'] == normal['source'] == SOURCE
    assert proof['actualExit'] == normal['actualExit'] == normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in hashes.items())
    raw,snap = [subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT) for p in (INV,SNAP)]
    return prior,proof,hashes,raw,snap


def expected(prior,proof,hashes):
    value = copy.deepcopy(prior)
    for key in ('actualExit','invocation','priorRegistrySha256','proofManifestSha256','wholeWbsAuditBefore'):
        value.pop(key,None)
    changes = {r['path']:r for r in proof['sourceChanges']}
    assert len(changes) == 8
    bindings = []
    for old,new in zip(prior['sourceRows'],value['sourceRows']):
        if old['path'] in changes:
            item = changes[old['path']]
            assert old['sha256'] == item['beforeSha256'] != item['sha256'] == hashes[old['path']]
            assert old['canonicalOwner'] == old['canonicalCostOwner'] == old['owner'] != 'UNKNOWN'
            new['sha256'] = item['sha256']
            bindings.append(dict(path=old['path'],beforeSha256=old['sha256'],sha256=new['sha256'],
                canonicalOwner=old['canonicalOwner'],canonicalCostOwner=old['canonicalCostOwner']))
        restored = copy.deepcopy(new)
        restored['sha256'] = old['sha256']
        assert restored == old
    assert len(bindings) == 8 and len(value['sourceRows']) == 983
    assert value['registered'] == 1808 and len(value['unregisteredJavaPaths']) == 2
    value.update(source=SOURCE,oldRowsChangedShaOnly=8,allOtherPriorRowsUnchanged=975,
        currentWebViewFixtureBinding=dict(source=SOURCE,sourceChanges=bindings,proofManifestSha256=PROOF,
            constantsAdded=55,referencesReplaced=284,independentInverseNegativeVectors=33,mainClassesUnchanged=1843,
            otherTestClassesUnchanged=proof['otherTestClassesUnchanged'],productTestsExecuted=0,coverage=None,
            additionalSharedCostPp=0,whole451Accepted=False,oldRuntimeReassigned=False),
        currentWebViewFixtureRuntimeQualification=dict(source=SOURCE,proofManifestSha256=PROOF,
            originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=68,uniqueMethods=68,
            localeRuns=['ja-JP'],testsPerLocale=68,suitesPerLocale=8,failures=0,errors=0,skipped=0,aborted=0,
            coverageSha256=proof['coverageSha256'],allWebPhysicalMainClasses=proof['allWebPhysicalMainClasses'],
            analyzedClassesPerLocale=proof['analyzedClassesPerLocale'],nonExecutablePackageMetadataPerLocale=proof['nonExecutablePackageMetadataPerLocale'],
            webFourCounters100=False,staticRawGate=1,remainingPmd=19,oldExecUnion=False,wholeJavaCoverage100=False,
            actualNetworkActions=0,actualDatabaseActions=0,actualRootActions=0,whole451Accepted=False,
            oldRuntimeReassigned=False,additionalSharedCostPp=0))
    changed_keys = {'source','oldRowsChangedShaOnly','allOtherPriorRowsUnchanged','sourceRows'}
    assert all(value[k] == v for k,v in prior.items() if k not in changed_keys and k in value)

    return value


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousWebViewFixtureRegistryReference' not in section
        section['previousWebViewFixtureRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record=RECORD,currentAddedTestPaths=[])
        section['currentWebViewFixtureBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentWebViewFixtureBinding',
            qualification='SOURCE_BOUND_WEB_VIEW_55_FIXTURES_68_PT_FULL_WEB_COUNTERS_NOT100')
        if name == SECTIONS[0]:
            section.update(independentPostManifest=str((POST/'manifest.json').relative_to(ROOT)),independentPostSha256=None)
        else:
            section.update(guardManifest=str((POST/'manifest.json').relative_to(ROOT)),guardSha256=None)
        raw,before,after = replaced(raw,name,section)
        pairs.append((before,after))
    snap,before,after = replaced(snap,'inventorySha256',data.sha(raw))
    return raw,snap,pairs,[(before,after)]


def contract(value,reference):
    if any(value.get(k) != v for k,v in reference.items()):
        raise ValueError('exact source-only bindings; all original runtime and owner/cost fields immutable')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    prior,proof,hashes,raw,snap = inputs()
    assert (ROOT/INV).read_bytes() == raw and (ROOT/SNAP).read_bytes() == snap
    reference = expected(prior,proof,hashes)
    observed = audit()
    assert observed['actualExit'] == 1
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,priorRegistrySha256=PRIOR,
        proofManifestSha256=PROOF,wholeWbsAuditBefore=observed,**reference))
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
    reference = expected(prior,proof,hashes)
    contract(value,reference)
    after,asnap,_,_ = documents(raw,snap)
    assert (ROOT/INV).read_bytes() == after and (ROOT/SNAP).read_bytes() == asnap
    validate(after,asnap,json.loads(raw),json.loads(snap))
    rejected = []
    mutations = [
        ('owner',lambda v:v['currentWebViewFixtureBinding']['sourceChanges'][0].update(canonicalOwner='UNKNOWN')),
        ('cost',lambda v:v['currentWebViewFixtureBinding'].update(additionalSharedCostPp=1)),
        ('runtime-transfer',lambda v:v['currentTraceContextRuntimeQualification'].update(source=SOURCE)),
        ('invented-pt',lambda v:v['currentWebViewFixtureBinding'].update(productTestsExecuted=9)),
        ('invented-coverage',lambda v:v['currentWebViewFixtureBinding'].update(coverage=100)),
        ('unknown',lambda v:v.update(unregisteredJavaPaths=[])),
        ('sha',lambda v:v['sourceRows'][0].update(sha256='0'*64)),
        ('source',lambda v:v.update(source=prior['source']))]
    for label,edit in mutations:
        damaged = copy.deepcopy(reference)
        edit(damaged)
        assert damaged != reference
        try:
            contract(damaged,reference)
        except ValueError:
            rejected.append(label)
        else:
            raise AssertionError('invalid source-only qualification accepted')
    observed = audit()
    assert observed['actualExit'] == 1 and observed['lastError'] == value['wholeWbsAuditBefore']['lastError']
    verify(invocation)
    POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        registryManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),inventorySha256=data.sha(after),snapshotSha256=data.sha(asnap),
        metadataNegativeVectors=rejected,registered=1808,total=1810,unknown=2,
        oldRowsChangedShaOnly=8,allOtherPriorRowsUnchanged=975,newPathsAdded=0,
        originalBudgetAndAcceptanceUnchanged=True,oldRuntimeReassigned=False,
        wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=observed,
        productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
