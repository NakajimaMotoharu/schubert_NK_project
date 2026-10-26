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
BASE = '2cb0690bb'
SOURCE = '8788668513552ce50862797cb700d2b7a4162ac1'
PRIOR = '9a00d5ede29463b85a6cedd23f8c851741530f94ed7ea53bbd4c6b0e1de741e2'
PROOF = '3d06dba306747ab6039845c106e185e103102fd4d441ac257f684eb66cdb0d36'
PMO = 'documents/400_PGPT/470_PMO/'
INV,SNAP = PMO+'485_WBS網羅性・受入対応.json',PMO+'486_WBS現行実績.json'
OUT,POST = data.BASE/'PG10324-user-query-oracle-trace-v1',data.BASE/'PG10326-user-query-oracle-trace-post-v1'
SECTIONS = ('currentJavaPathExplicitRegistryMeasurement','currentIncrementalHostOwnership')
PREFIX = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/admin/'
APP,REPLAY,ORACLE = [PREFIX+'UserQuery'+n+'.java' for n in ('ApplicationServiceTest','ReplayServiceTest','WireOracle')]
SPEC = 'evidence/01_PT/010_NK-ADM-001/085_NK-ADM-001_User照会期待wire独立性仕様.md'
RECORD = 'evidence/01_PT/018_NK-OPS-001/2050_UserQuery独立oracle五path追跡結果.md'


def inputs():
    prior = data.read_checked(data.BASE/'PG10292-query-oracle-trace-v1/manifest.json',PRIOR)
    user = data.read_checked(data.BASE/'PG10320-user-query-oracle-post-v1/manifest.json',PROOF)
    query = data.read_checked(data.BASE/'PG10304-query-test-literal-post-v1/manifest.json',
        'f468fca21fd5601f4a620cca5564ed022878a0831a09499f559bf172006e1904')
    normal = data.read_checked(data.BASE/'PG10318-user-query-oracle-six-compile-v1/manifest.json',
        '04ac980e0ed4a2b18e83dd41521bfe9adda035251b7ce8ca6f3a90b9fae89942')
    assert user['actualExit'] == query['actualExit'] == normal['actualExit'] == normal['testsExecuted'] == 0
    assert user['source'] == normal['source'] == SOURCE and user['originalProductTestsExecuted'] == query['originalProductTestsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in hashes.items())
    raw,snap = [subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT) for p in (INV,SNAP)]
    return prior,dict(user=user,query=query),hashes,raw,snap


def expected(prior,proof,hashes,raw):
    rows = copy.deepcopy(prior['sourceRows'])
    assert len(rows) == 982
    index = {r['path']:r for r in rows}
    bindings = []
    subjects = [(p,'WBS-P014-01' if p.endswith('ApplicationServiceTest.java') else 'WBS-P014-03',
        proof['query'],'PG10304-query-test-literal-post-v1',
        'f468fca21fd5601f4a620cca5564ed022878a0831a09499f559bf172006e1904',
        'evidence/01_PT/014_NK-QRY-001/011_NK-QRY-001_重複literal是正結果.md',None)
        for p in sorted(proof['query']['sourceHashes'])]
    subjects += [(p,'WBS-P010-01',proof['user'],'PG10320-user-query-oracle-post-v1',PROOF,SPEC,27)
        for p in (APP,REPLAY)]
    assert len(subjects) == 4
    for path,owner,qualified,run,digest,spec,vectors in subjects:
        row = index[path]
        assert row['canonicalOwner'] == row['canonicalCostOwner'] == row['owner'] == owner
        assert row['sha256'] != hashes[path] and qualified['sourceHashes'][path] == hashes[path]
        bindings.append(dict(path=path,previousSha256=row['sha256'],sha256=hashes[path],
            canonicalOwner=owner,canonicalCostOwner=owner,independentSpec=spec,
            currentSource=SOURCE,sourceSpecificOracleMetadataProof=dict(source=qualified['source'],
                manifest=str((data.BASE/run/'manifest.json').relative_to(ROOT)),sha256=digest,
                metadataVectors=vectors,sharedMetadataReferenceNotAdditive=True,
                originalProductTestsExecuted=0,coverageMeasured=False,originalProductPtStatus='NOT_EXECUTED_HOLD'),
            originalRuntimeProofReassigned=False,additionalSharedCostPp=0))
        row['sha256'] = hashes[path]
    assert ORACLE not in index and proof['user']['sourceHashes'][ORACLE] == hashes[ORACLE]
    rows.append(dict(path=ORACLE,sha256=hashes[ORACLE],owner='WBS-G03.01',
        canonicalOwner='WBS-G03.01',canonicalCostOwner='WBS-G03.01',changeOwner='WBS-G13.07',
        legacyReportedOwner=None,basis='PG-D679_EXPLICIT_USER_QUERY_TEST_ORACLE_RESPONSIBILITY',
        ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',relatedBusinessOwners=['WBS-P010-01'],
        actualAllocatedPp=None,additionalSharedCostPp=0,historicalCostsReallocated=False,
        historicalRunReassigned=False,independentSpec=SPEC,productTestIds=[],
        oracleMetadataIds=['META-USR-WIRE001..027','META-USR-NEG001..003','META-USR-ISOLATION','META-USR-SOURCE'],
        currentSourcePtQualificationInferred=False,sourceSpecificOracleMetadataProof=copy.deepcopy(bindings[-1]['sourceSpecificOracleMetadataProof'])))
    changed_paths = {p for p, *_ in subjects}
    for old,new in zip(prior['sourceRows'],rows):
        adjusted = copy.deepcopy(new)
        if old['path'] in changed_paths: adjusted['sha256'] = old['sha256']
        assert adjusted == old
    logical = {r['path']:r for r in json.loads(raw)['artifacts']}
    assert len(logical) == 941
    universe = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    known = set(logical)|{r['path'] for r in rows}
    unknown = sorted(universe-known)
    assert len(universe) == 1810 and unknown == prior['unregisteredJavaPaths'] and len(unknown) == 2
    mains = {p for p in universe if '/src/main/java/' in p}
    tests = universe-mains
    legacy = sum(r.get('legacyReportedOwner') != r['canonicalOwner'] for r in rows)
    assert legacy == prior['legacyOwnerLabelsDifferingFromCanonical']+1
    keep = {k:copy.deepcopy(prior[k]) for k in ('currentModifiedLogicalBindings','previousChangedTestBindings',
        'changedTestBindings','unregisteredCurrentSourceBindings')}
    return dict(source=SOURCE,sourceRows=rows,sourceCount=len(rows),newTestPaths=[ORACLE],newPathsAdded=1,
        changedOracleTestBindings=bindings,oldRowsChangedShaOnly=4,allOtherPriorRowsUnchanged=978,
        previousChangedOracleBindingsReference=dict(manifest=str((data.BASE/'PG10292-query-oracle-trace-v1/manifest.json').relative_to(ROOT)),
            sha256=PRIOR,arrayPath='changedOracleTestBindings',count=len(prior['changedOracleTestBindings']),source=prior['source']),
        newLogicalCandidates=prior['newLogicalCandidates']+1,javaPaths=len(universe),registered=len(universe)-len(unknown),
        registeredMain=len(mains&known),totalMain=len(mains),registeredTest=len(tests&known),totalTest=len(tests),
        unregisteredJavaPaths=unknown,legacyOwnerLabelsDifferingFromCanonical=legacy,
        productTestsExecuted=0,metadataVectors=27,newAccepted=0,formalUpdated=False,effortPercent=None,**keep)


def contract(value,reference):
    if {k:value[k] for k in reference} != reference:
        raise ValueError('exact source, independent metadata, original ownership/cost/runtime and UNKNOWN required')


def documents(raw,snap):
    value = json.loads((OUT/'manifest.json').read_bytes())
    pairs = []
    for name in SECTIONS:
        section = json.loads(raw)[name]
        assert 'previousUserQueryOracleRegistryReference' not in section
        section['previousUserQueryOracleRegistryReference'] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),record=RECORD,currentAddedTestPaths=[ORACLE])
        section['currentQueryOracleMetadataBindingsReference'] = dict(manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),arrayPath='changedOracleTestBindings',count=4,
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
        allOtherPriorRowsUnchanged=978,oldRowsChangedShaOnly=4,newPathsAdded=1,
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
