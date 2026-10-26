"""Seven independent Protocol expected values and genuine2locale/8execution qualification; old runtime unchanged."""
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
BASE = '6f24d3738'
SOURCE = '1f20074cdfd20e13527525ed8d0e57faff28e276'
PRIOR = 'f69f2d00ae617830342ec64854b1f17b3bb6e99b4e700b14879575ac84a98d17'
PROOF = '8eb053d83246889be0c5c843f183ebdd0eeaa97e256b9b74ff819bd3ed29c0b1'
OUT = data.BASE/'PG10766-protocol-semantic-oracle-trace-v1'
POST = data.BASE/'PG10768-protocol-semantic-oracle-trace-post-v1'
RECORD = 'evidence/01_PT/001_NK-PRO-001/1188_Semantic独立期待値七・診断保護・定数九PGPT結果.md'


def inputs():
    prior = data.read_checked(data.BASE/'PG10746-protocol-uppercase-locale-trace-v1/manifest.json',PRIOR)
    proof = data.read_checked(data.BASE/'PG10765-protocol-semantic-recovery-post-v1/manifest.json',PROOF)
    normal = data.read_checked(data.BASE/'PG10756-protocol-semantic-six-compile-v1/manifest.json',
        '5273ae8b8a1bc9bb275793444b298801943eb5dba30f027be706913c7056fbc9')
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
    assert len(changes) == 1
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
    assert len(bindings) == 1 and len(value['sourceRows']) == 983
    assert value['registered'] == 1808 and len(value['unregisteredJavaPaths']) == 2
    value.update(source=SOURCE,oldRowsChangedShaOnly=1,allOtherPriorRowsUnchanged=982,
        currentProtocolSemanticOracleBinding=dict(source=SOURCE,sourceChanges=bindings,proofManifestSha256=PROOF,
            sameValueConstants=9,independentExpectedAssertions=7,uppercaseRedactionGuardsAdded=1,mainClassesUnchanged=1843,otherTestClassesUnchanged=proof['otherTestClassesUnchanged'],
            productTestsExecuted=0,coverage=None,additionalSharedCostPp=0,whole451Accepted=False,oldRuntimeReassigned=False),
        currentProtocolSemanticRuntimeQualification=dict(source=SOURCE,proofManifestSha256=PROOF,
            originalHostManifestSha256=proof['originalHostManifestSha256'],observedTestExecutions=8,uniqueMethods=4,
            localeRuns=['ja-JP','tr-TR'],testsPerLocale=4,suitesPerLocale=1,failures=0,errors=0,skipped=0,aborted=0,
            coverageSha256=proof['coverageSha256'],allProtocolPhysicalMainClasses=176,analyzedClassesPerLocale=169,
            nonExecutablePackageMetadataPerLocale=7,oldExecUnion=False,wholeJavaCoverage100=False,
            actualNetworkActions=0,actualDatabaseActions=0,actualRootActions=0,whole451Accepted=False,
            oldRuntimeReassigned=False,additionalSharedCostPp=0))
    assert value['currentProtocolLocaleRuntimeQualification'] == prior['currentProtocolLocaleRuntimeQualification']
    assert value['currentProtocolUppercaseFixtureBinding'] == prior['currentProtocolUppercaseFixtureBinding']
    assert value['currentGraphDiagnosticConstantsBinding'] == prior['currentGraphDiagnosticConstantsBinding']
    assert value['currentGraphImportBinding'] == prior['currentGraphImportBinding']
    assert value['currentQuerySemanticConstantsBinding'] == prior['currentQuerySemanticConstantsBinding']
    for key in ('currentTraceContextRuntimeQualification','currentPublicTemplateRuntimeQualification',
                'currentPureViewRuntimeQualification','currentAnmNameMetadataBinding'):
        assert value[key] == prior[key]
    assert value['currentFixedErrorOracleBinding'] == prior['currentFixedErrorOracleBinding']
    assert value['currentLogCleanupLiteralBinding'] == prior['currentLogCleanupLiteralBinding']
    return value


def documents(raw,snap):
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousProtocolSemanticRegistryReference' not in section
        section['previousProtocolSemanticRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record=RECORD,currentAddedTestPaths=[])
        section['currentProtocolSemanticOracleBindingReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),objectPath='currentProtocolSemanticOracleBinding',
            qualification='SOURCE_BOUND_PRIMITIVE_ORACLES_WITH_SEPARATE_GENUINE_LOCALE_PT_COUNTERS_PARTIAL')
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
        ('owner',lambda v:v['currentProtocolSemanticOracleBinding']['sourceChanges'][0].update(canonicalOwner='UNKNOWN')),
        ('cost',lambda v:v['currentProtocolSemanticOracleBinding'].update(additionalSharedCostPp=1)),
        ('runtime-transfer',lambda v:v['currentTraceContextRuntimeQualification'].update(source=SOURCE)),
        ('invented-pt',lambda v:v['currentProtocolSemanticOracleBinding'].update(productTestsExecuted=9)),
        ('invented-coverage',lambda v:v['currentProtocolSemanticOracleBinding'].update(coverage=100)),
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
        oldRowsChangedShaOnly=1,allOtherPriorRowsUnchanged=982,newPathsAdded=0,
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
