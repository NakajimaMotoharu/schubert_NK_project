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
BASE = '2f41ce31b'
SOURCE = '21228608b9defca3eb6fac7e0485f28a56925246'
PRIOR = '60e7171d7cc12586844ce56836204e6fa73afb55424b14f115887a64d0defa3c'
PROOF = 'f6c380e1e7a6971e8b79eaf6da9b5df25b4efdee65c206cf3b91ef4028e29fb3'
PMO = 'documents/400_PGPT/470_PMO/'
INV,SNAP = PMO+'485_WBS網羅性・受入対応.json',PMO+'486_WBS現行実績.json'
OUT,POST = data.BASE/'PG10292-query-oracle-trace-v1',data.BASE/'PG10294-query-oracle-trace-post-v1'
SECTIONS = ('currentJavaPathExplicitRegistryMeasurement','currentIncrementalHostOwnership')
PREFIX = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/question/'
APP,REPLAY,ORACLE = [PREFIX+'QuestionQuery'+n+'.java' for n in ('ApplicationServiceTest','ReplayServiceTest','WireOracle')]
SPEC = 'evidence/01_PT/014_NK-QRY-001/009_NK-QRY-001_期待wire独立性仕様.md'
RECORD = 'evidence/01_PT/018_NK-OPS-001/2048_Query独立oracle三path追跡結果.md'


def inputs():
    prior = data.read_checked(data.BASE/'PG10270-scenario-media-trace-v1/manifest.json',PRIOR)
    proof = data.read_checked(data.BASE/'PG10287-query-wire-oracle-source-post-v2/manifest.json',PROOF)
    normal = data.read_checked(data.BASE/'PG10284-query-wire-oracle-six-compile-v1/manifest.json',
        '34ab5aef610fb1352732c926c7ca56438fc38b8434d218196d34f693aa6adbf0')
    assert proof['actualExit'] == normal['actualExit'] == normal['testsExecuted'] == 0
    assert proof['source'] == normal['source'] == SOURCE and proof['originalProductTestsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in hashes.items())
    raw,snap = [subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT) for p in (INV,SNAP)]
    return prior,proof,hashes,raw,snap


def expected(prior,proof,hashes,raw):
    rows = copy.deepcopy(prior['sourceRows'])
    assert len(rows) == 981
    index = {r['path']:r for r in rows}
    bindings = []
    for path,owner in ((APP,'WBS-P014-01'),(REPLAY,'WBS-P014-03')):
        row = index[path]
        assert row['canonicalOwner'] == row['canonicalCostOwner'] == row['owner'] == owner
        assert row['sha256'] != hashes[path] and proof['sourceHashes'][path] == hashes[path]
        bindings.append(dict(path=path,previousSha256=row['sha256'],sha256=hashes[path],
            canonicalOwner=owner,canonicalCostOwner=owner,independentSpec=SPEC,
            sourceSpecificOracleMetadataProof=dict(source=SOURCE,manifest=str((data.BASE/'PG10287-query-wire-oracle-source-post-v2/manifest.json').relative_to(ROOT)),
                sha256=PROOF,metadataVectors=24,sharedMetadataReferenceNotAdditive=True,
                originalProductTestsExecuted=0,coverageMeasured=False,originalProductPtStatus='NOT_EXECUTED_HOLD'),
            originalRuntimeProofReassigned=False,additionalSharedCostPp=0))
        row['sha256'] = hashes[path]
    assert ORACLE not in index and proof['sourceHashes'][ORACLE] == hashes[ORACLE]
    rows.append(dict(path=ORACLE,sha256=hashes[ORACLE],owner='WBS-G03.01',
        canonicalOwner='WBS-G03.01',canonicalCostOwner='WBS-G03.01',changeOwner='WBS-G13.07',
        legacyReportedOwner=None,basis='PG-D678_EXPLICIT_TEST_ONLY_ORACLE_RESPONSIBILITY',
        ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',relatedBusinessOwners=['WBS-P014-01','WBS-P014-03'],
        actualAllocatedPp=None,additionalSharedCostPp=0,historicalCostsReallocated=False,
        historicalRunReassigned=False,independentSpec=SPEC,productTestIds=[],
        oracleMetadataIds=['META-QRY-WIRE001..024','META-QRY-NEG001..005','META-QRY-ISOLATION','META-QRY-SOURCE'],
        currentSourcePtQualificationInferred=False,sourceSpecificOracleMetadataProof=copy.deepcopy(bindings[0]['sourceSpecificOracleMetadataProof'])))
    for old,new in zip(prior['sourceRows'],rows):
        adjusted = copy.deepcopy(new)
        if old['path'] in (APP,REPLAY): adjusted['sha256'] = old['sha256']
        assert adjusted == old
    logical = {r['path']:r for r in json.loads(raw)['artifacts']}
    assert len(logical) == 941
    universe = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    known = set(logical)|{r['path'] for r in rows}
    unknown = sorted(universe-known)
    assert len(universe) == 1809 and unknown == prior['unregisteredJavaPaths'] and len(unknown) == 2
    mains = {p for p in universe if '/src/main/java/' in p}
    tests = universe-mains
    legacy = sum(r.get('legacyReportedOwner') != r['canonicalOwner'] for r in rows)
    assert legacy == prior['legacyOwnerLabelsDifferingFromCanonical']+1
    keep = {k:copy.deepcopy(prior[k]) for k in ('currentModifiedLogicalBindings','previousChangedTestBindings',
        'changedTestBindings','unregisteredCurrentSourceBindings')}
    return dict(source=SOURCE,sourceRows=rows,sourceCount=len(rows),newTestPaths=[ORACLE],newPathsAdded=1,
        changedOracleTestBindings=bindings,oldRowsChangedShaOnly=2,allOtherPriorRowsUnchanged=979,
        newLogicalCandidates=prior['newLogicalCandidates']+1,javaPaths=len(universe),registered=len(universe)-len(unknown),
        registeredMain=len(mains&known),totalMain=len(mains),registeredTest=len(tests&known),totalTest=len(tests),
        unregisteredJavaPaths=unknown,legacyOwnerLabelsDifferingFromCanonical=legacy,
        productTestsExecuted=0,metadataVectors=24,newAccepted=0,formalUpdated=False,effortPercent=None,**keep)


def contract(value,reference):
    if {k:value[k] for k in reference} != reference:
        raise ValueError('exact source, independent metadata, original ownership/cost/runtime and UNKNOWN required')


def documents(raw,snap):
    value = json.loads((OUT/'manifest.json').read_bytes())
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousQueryOracleRegistryReference' not in section
        section['previousQueryOracleRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record=RECORD,currentAddedTestPaths=[ORACLE])
        section['currentQueryOracleMetadataBindingsReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),arrayPath='changedOracleTestBindings',count=2,
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
        ('current-hash',lambda v:v['changedOracleTestBindings'][0].update(sha256='0'*64)),
        ('false-pt',lambda v:v['changedOracleTestBindings'][0]['sourceSpecificOracleMetadataProof'].update(originalProductTestsExecuted=24)),
        ('false-coverage',lambda v:v['changedOracleTestBindings'][0]['sourceSpecificOracleMetadataProof'].update(coverageMeasured=True)),
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
        allOtherPriorRowsUnchanged=979,oldRowsChangedShaOnly=2,newPathsAdded=1,
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
