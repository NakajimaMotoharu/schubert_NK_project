"""Three Test-only oracle source bindings, preserving all other rows and historical runtime."""
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

ROOT = data.ROOT
BASE = 'a92151f94'
SOURCE = 'b120eebab4bbe1f8d02c245a06e51e0783a616c5'
PRIOR = '7a7f15450a3c11638eb55b856f2cd9769d3617c1f00bab45a2c70c68e57fc71a'
PROOF = '8ad578efae703ed775a28a2c07cec9620c20a3d08313989db11f2a3e434f1931'
PMO = 'documents/400_PGPT/470_PMO/'
INV,SNAP = PMO+'485_WBS網羅性・受入対応.json',PMO+'486_WBS現行実績.json'
OUT,POST = data.BASE/'PG10352-result-profile-trace-v1',data.BASE/'PG10354-result-profile-trace-post-v1'
SECTIONS = ('currentJavaPathExplicitRegistryMeasurement','currentIncrementalHostOwnership')
PREFIX = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/admin/'
APP,REPLAY,ORACLE = [PREFIX+'UserQuery'+n+'.java' for n in ('ApplicationServiceTest','ReplayServiceTest','WireOracle')]
SPEC = 'evidence/01_PT/018_NK-OPS-001/2054_五Test同値定数化・静的分類結果.md'
RECORD = 'evidence/01_PT/018_NK-OPS-001/2056_成功profile五最終SHA追跡結果.md'


def inputs():
    prior = data.read_checked(data.BASE/'PG10324-user-query-oracle-trace-v1/manifest.json',PRIOR)
    proof = data.read_checked(data.BASE/'PG10348-result-profile-literal-post-v1/manifest.json',PROOF)
    normal = data.read_checked(data.BASE/'PG10346-result-profile-literal-six-compile-v1/manifest.json',
        'c7119960eb3cbf1514d58454c9f56e07780757339f4294d49ae82181acf24965')
    assert proof['actualExit'] == normal['actualExit'] == normal['testsExecuted'] == 0
    assert proof['source'] == normal['source'] == SOURCE and proof['originalProductTestsExecuted'] == 0
    assert proof['actualAssertionInvocationCounts'] is None
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in hashes.items())
    raw,snap = [subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT) for p in (INV,SNAP)]
    return prior,proof,hashes,raw,snap


def expected(prior,proof,hashes,raw):
    rows = copy.deepcopy(prior['sourceRows'])
    assert len(rows) == 983
    index = {r['path']:r for r in rows}
    bindings = []
    owners = dict(UserCommandServiceTest='WBS-P010-02',UserMutationReplayServiceTest='WBS-P010-03',
        QuestionMutationApplicationServiceTest='WBS-P014-02',QuestionMutationReplayServiceTest='WBS-P013-02',
        SessionOperationTokenLifecycleTest='WBS-P015-03')
    for path,current_sha in sorted(proof['sourceHashes'].items()):
        row = index[path]
        owner = owners[Path(path).stem]
        assert row['owner'] == row['canonicalOwner'] == row['canonicalCostOwner'] == owner
        assert row['sha256'] != current_sha == hashes[path]
        bindings.append(dict(path=path,previousSha256=row['sha256'],sha256=current_sha,
            canonicalOwner=owner,canonicalCostOwner=owner,independentSpec=SPEC,
            sourceSpecificOracleMetadataProof=dict(source=SOURCE,manifest=str((data.BASE/'PG10348-result-profile-literal-post-v1/manifest.json').relative_to(ROOT)),
                sha256=PROOF,sharedReferenceNotAdditive=True,independentSuccessPredicatesUnchanged=12,
                originalProductTestsExecuted=0,coverageMeasured=False,originalProductPtStatus='NOT_EXECUTED_HOLD',
                actualAssertionInvocationCounts=None),
            originalClassifierSourceProof=dict(source='2e1ee53459a9cca85a4b821c72901073903a78e3',
                manifest=str((data.BASE/'PG10339-result-profile-oracle-post-v2/manifest.json').relative_to(ROOT)),
                sha256='935e104fcd4e3c8054ca677f2f9097225ff0f179538d7e3ac7a32dda03a87d6f'),
            metricCorrectionReference=dict(manifest=str((data.BASE/'PG10349-assert-prefix-metric-correction-v1/manifest.json').relative_to(ROOT)),
                sha256='a9546154434952712380f83b4752af700ca0d62895bcfc9b5537ba9d8527e811'),
            originalRuntimeProofReassigned=False,additionalSharedCostPp=0))
        row['sha256'] = current_sha
    assert len(bindings) == 5
    changed = {r['path'] for r in bindings}
    for old,new in zip(prior['sourceRows'],rows):
        adjusted = copy.deepcopy(new)
        if old['path'] in changed: adjusted['sha256'] = old['sha256']
        assert adjusted == old
    logical = {r['path']:r for r in json.loads(raw)['artifacts']}
    assert len(logical) == 941
    universe = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    known = set(logical)|{r['path'] for r in rows}
    unknown = sorted(universe-known)
    assert len(universe) == 1810 and unknown == prior['unregisteredJavaPaths'] and len(unknown) == 2
    mains = {p for p in universe if '/src/main/java/' in p}
    tests = universe-mains
    keep = {k:copy.deepcopy(prior[k]) for k in ('currentModifiedLogicalBindings','previousChangedTestBindings',
        'changedTestBindings','unregisteredCurrentSourceBindings','changedOracleTestBindings','previousChangedOracleBindingsReference')}
    return dict(source=SOURCE,sourceRows=rows,sourceCount=len(rows),newTestPaths=[],newPathsAdded=0,
        changedResultProfileBindings=bindings,oldRowsChangedShaOnly=5,allOtherPriorRowsUnchanged=978,
        newLogicalCandidates=prior['newLogicalCandidates'],javaPaths=len(universe),registered=len(universe)-len(unknown),
        registeredMain=len(mains&known),totalMain=len(mains),registeredTest=len(tests&known),totalTest=len(tests),
        unregisteredJavaPaths=unknown,legacyOwnerLabelsDifferingFromCanonical=sum(r.get('legacyReportedOwner') != r['canonicalOwner'] for r in rows),
        productTestsExecuted=0,actualAssertionInvocationCounts=None,newAccepted=0,formalUpdated=False,effortPercent=None,**keep)


def contract(value,reference):
    if {k:value[k] for k in reference} != reference:
        raise ValueError('exact source, independent metadata, original ownership/cost/runtime and UNKNOWN required')


def documents(raw,snap):
    value = json.loads((OUT/'manifest.json').read_bytes())
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousResultProfileRegistryReference' not in section
        section['previousResultProfileRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record=RECORD,currentAddedTestPaths=[])
        section['currentResultProfileMetadataBindingsReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),arrayPath='changedResultProfileBindings',count=5,
            qualification='ORACLE_METADATA_ONLY_ORIGINAL_PT_NOT_EXECUTED_HOLD')
        if name == SECTIONS[0]:
            section.update(javaPaths=value['javaPaths'],registered=value['registered'],unregistered=len(value['unregisteredJavaPaths']),
                main=dict(total=value['totalMain'],registered=value['registeredMain'],unregistered=value['totalMain']-value['registeredMain']),
                test=dict(total=value['totalTest'],registered=value['registeredTest'],unregistered=value['totalTest']-value['registeredTest']),
                independentPostManifest=str((POST/'manifest.json').relative_to(ROOT)),independentPostSha256=None)
        else:
            section.update(sourceRows=value['sourceCount'],newLogicalCandidates=value['newLogicalCandidates'],
                legacyOwnerLabelsDifferingFromCanonical=value['legacyOwnerLabelsDifferingFromCanonical'],
                guardManifest=str((POST/'manifest.json').relative_to(ROOT)),guardSha256=None)
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
        for before,after in lines: patch += '@@\n-'+before+'+'+after
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
        ('old-owner',lambda v:v['sourceRows'][0].update(canonicalOwner='UNKNOWN')),
        ('new-cost',lambda v:v['sourceRows'][-1].update(canonicalCostOwner='WBS-P014-01')),
        ('new-hash',lambda v:v['sourceRows'][-1].update(sha256='0'*64)),
        ('current-hash',lambda v:v['changedResultProfileBindings'][0].update(sha256='0'*64)),
        ('false-pt',lambda v:v['changedResultProfileBindings'][0]['sourceSpecificOracleMetadataProof'].update(originalProductTestsExecuted=24)),
        ('false-coverage',lambda v:v['changedResultProfileBindings'][0]['sourceSpecificOracleMetadataProof'].update(coverageMeasured=True)),
        ('source',lambda v:v.update(source=prior['source'])),
        ('unknown',lambda v:v.update(unregisteredJavaPaths=[])),
        ('legacy-count',lambda v:v.update(legacyOwnerLabelsDifferingFromCanonical=0)),
        ('acceptance',lambda v:v.update(newAccepted=1))]
    negatives = []
    for label,edit in edits:
        changed = copy.deepcopy(reference)
        edit(changed)
        try: contract(changed,reference)
        except ValueError: negatives.append(label)
        else: raise AssertionError('invalid metadata accepted')
    observed = audit()
    assert observed['actualExit'] == 1 and observed['lastError'] == value['wholeWbsAuditBefore']['lastError']
    verify(invocation)
    POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        registryManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),inventorySha256=data.sha(after),snapshotSha256=data.sha(asnap),
        metadataNegativeVectors=negatives,registered=value['registered'],total=value['javaPaths'],unknown=len(value['unregisteredJavaPaths']),
        allOtherPriorRowsUnchanged=978,oldRowsChangedShaOnly=5,newPathsAdded=0,
        originalBudgetAndAcceptanceUnchanged=True,originalRuntimeProofReassigned=False,
        wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=observed,
        forwardPostHashNullReason='acyclic immutable post binds actual inventory raw hash',
        productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']: print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
