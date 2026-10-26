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
BASE = 'ee137dcc4'
SOURCE = '3d9f1d9fd395e8cb9456b0a540e1f29bcb87876e'
PRIOR = '56bc45aad23d1292a3ad9b4b625d5c335836959b26de4348f8cd72c49b10c9d1'
PROOF = '4c3768f759dd1f74271bf91b008742bf8fcd3639ab5e41adf59e4123d4a8a9d1'
PMO = 'documents/400_PGPT/470_PMO/'
INV,SNAP = PMO+'485_WBS網羅性・受入対応.json',PMO+'486_WBS現行実績.json'
OUT,POST = data.BASE/'PG10384-media-oracle-trace-v1',data.BASE/'PG10386-media-oracle-trace-post-v1'
SECTIONS = ('currentJavaPathExplicitRegistryMeasurement','currentIncrementalHostOwnership')
PREFIX = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/admin/'
APP,REPLAY,ORACLE = [PREFIX+'UserQuery'+n+'.java' for n in ('ApplicationServiceTest','ReplayServiceTest','WireOracle')]
SPEC = 'evidence/01_PT/009_NK-MED-001/007_NK-MED-001_同値定数化・静的分類結果.md'
RECORD = 'evidence/01_PT/018_NK-OPS-001/2060_Media三最終SHA追跡結果.md'


def inputs():
    prior = data.read_checked(data.BASE/'PG10352-result-profile-trace-v1/manifest.json',PRIOR)
    proof = data.read_checked(data.BASE/'PG10380-media-literal-post-v1/manifest.json',PROOF)
    normal = data.read_checked(data.BASE/'PG10378-media-literal-six-compile-v1/manifest.json',
        'c6862b046f1fae580ce0c8a3a07399f2cc2ca7d4657ca479c499ee6d80d4af9b')
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
    owners = dict(MediaReplayFixture='WBS-P009-01',MediaStageFixture='WBS-P009-01',MediaReplayServiceTest='WBS-P009-02')
    for path,current_sha in sorted(proof['sourceHashes'].items()):
        row = index[path]
        owner = owners[Path(path).stem]
        assert row['owner'] == row['canonicalOwner'] == row['canonicalCostOwner'] == owner
        assert row['sha256'] != current_sha == hashes[path]
        bindings.append(dict(path=path,previousSha256=row['sha256'],sha256=current_sha,
            canonicalOwner=owner,canonicalCostOwner=owner,independentSpec=SPEC,
            sourceSpecificOracleMetadataProof=dict(source=SOURCE,manifest=str((data.BASE/'PG10380-media-literal-post-v1/manifest.json').relative_to(ROOT)),
                sha256=PROOF,sharedReferenceNotAdditive=True,sameValueStringConstants=17,
                originalProductTestsExecuted=0,coverageMeasured=False,originalProductPtStatus='NOT_EXECUTED_HOLD',
                actualAssertionInvocationCounts=None),
            originalCorrelationSourceProof=proof['originalOracleSourceProof'],
            originalRuntimeProofReassigned=False,additionalSharedCostPp=0))
        row['sha256'] = current_sha
    assert len(bindings) == 3
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
        'changedTestBindings','unregisteredCurrentSourceBindings','changedOracleTestBindings','previousChangedOracleBindingsReference','changedResultProfileBindings')}
    return dict(source=SOURCE,sourceRows=rows,sourceCount=len(rows),newTestPaths=[],newPathsAdded=0,
        changedMediaOracleBindings=bindings,oldRowsChangedShaOnly=3,allOtherPriorRowsUnchanged=980,
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
        assert 'previousMediaOracleRegistryReference' not in section
        section['previousMediaOracleRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record=RECORD,currentAddedTestPaths=[])
        section['currentMediaOracleMetadataBindingsReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),arrayPath='changedMediaOracleBindings',count=3,
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
        ('current-hash',lambda v:v['changedMediaOracleBindings'][0].update(sha256='0'*64)),
        ('false-pt',lambda v:v['changedMediaOracleBindings'][0]['sourceSpecificOracleMetadataProof'].update(originalProductTestsExecuted=24)),
        ('false-coverage',lambda v:v['changedMediaOracleBindings'][0]['sourceSpecificOracleMetadataProof'].update(coverageMeasured=True)),
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
        allOtherPriorRowsUnchanged=980,oldRowsChangedShaOnly=3,newPathsAdded=0,
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
