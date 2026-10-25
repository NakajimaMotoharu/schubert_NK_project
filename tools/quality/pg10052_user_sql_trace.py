"""One-path incremental registry with immutable prior rows and exact WBS metadata patch."""
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
SOURCE = 'dac963b29f62c0da68ca9d71f61db986a02d28a1'
BEFORE = '744a58743'
PMO = 'documents/400_PGPT/470_PMO/'
INV = PMO+'485_WBS網羅性・受入対応.json'
SNAP = PMO+'486_WBS現行実績.json'
OUT = data.BASE/'PG10052-user-sql-trace-v1'
CHECK = data.BASE/'PG10054-user-sql-registry-check-v1'
POST = data.BASE/'PG10056-user-sql-trace-post-v1'
SUBJECTS = (
    ('admin/UserQueryRequest.java','admin/UserQuerySqlContractTest.java','WBS-P010-01','ADM',
        'evidence/01_PT/010_NK-ADM-001/077_NK-ADM-001_UserSQL界面契約単体テスト仕様書.md'),)
MAIN_PREFIX = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/'
TEST_PREFIX = MAIN_PREFIX.replace('/main/','/test/')
NEW = [TEST_PREFIX+s[1] for s in SUBJECTS]
SECTIONS = ('currentJavaPathExplicitRegistryMeasurement','currentIncrementalHostOwnership')


def inputs():
    prior = data.read_checked(data.BASE/'PG10030-test-hygiene-current-trace-v1/manifest.json',
        '2f484711d4559dd6a7969f99bfcdfbd6732a14486990c12e6d4dff2a1fcb4c3a')
    normal = data.read_checked(data.BASE/'PG10040-user-sql-six-compile-v1/manifest.json',
        '37f90bd83ad135df52b631b603eb0b2859a9b21d86984615ea0829d46c3a2cf5')
    proof = data.read_checked(data.BASE/'PG10048-user-sql-quality-post-v1/manifest.json',
        '6677ce92b1eae1e9f7f9da18566c428905fa86dba7e0a6b374f5e866fad8aa19')
    assert normal['actualExit'] == prior['actualExit'] == proof['actualExit'] == 0
    assert normal['source'] == proof['source'] == SOURCE
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in hashes.items())
    old_raw, old_snap = [subprocess.check_output(['git','show',BEFORE+':'+p],cwd=ROOT) for p in (INV,SNAP)]
    logical = {r['path']:r for r in json.loads(old_raw)['artifacts']}
    assert len(logical) == 941
    for main,_,owner,_,_ in SUBJECTS:
        assert logical[MAIN_PREFIX+main]['owner'] == logical[MAIN_PREFIX+main]['costOwner'] == owner
        assert hashes[MAIN_PREFIX+main] == logical[MAIN_PREFIX+main]['sha256']
    return prior, hashes, old_raw, old_snap


def expected_registry(prior, hashes, old_raw):
    rows = copy.deepcopy(prior['sourceRows'])
    assert len(rows) == 973 and not set(NEW) & {r['path'] for r in rows}
    assert all(r['sha256'] == hashes[r['path']] for r in rows)
    template = next(r for r in rows if r['path'].endswith('/UserQueryCanonicalCoreTest.java'))
    for main,test,owner,tag,spec in SUBJECTS:
        path = TEST_PREFIX+test
        row = copy.deepcopy(template)
        row.update(path=path,sha256=hashes[path],owner=owner,canonicalOwner=owner,canonicalCostOwner=owner,
            basis='EXPLICIT_SQL_INTERFACE_SPEC_AND_ORIGINAL_LOGICAL_MAIN_OWNER',mainSourceSubjects=[MAIN_PREFIX+main,
                MAIN_PREFIX.replace('/application/','/persistence/')+'UserQueryRepository.java'],
            independentSpec=spec,
            methodTestIds=[f'PT-{tag}-SQL{i:03d}' for i in range(1,9)],
            ownerProofManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10048-user-sql-quality-post-v1/manifest.json',
            ownerProofSha256='6677ce92b1eae1e9f7f9da18566c428905fa86dba7e0a6b374f5e866fad8aa19',
            sourceSpecificRuntimeProof=dict(source=SOURCE,tests=16,suites=3,newTestIds=8,programMethodCount=8,
                sharedRunReferenceNotAdditive=True,
                manifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10047-user-sql-post-v2/manifest.json',
                sha256='a7d6c23e71cc2da5463bba8d88a64a9188ad47c859badfb098aab287882daf4c',reassignedToCurrentSource=False))
        rows.append(row)
    universe = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    logical = {r['path'] for r in json.loads(old_raw)['artifacts']}
    unknown = sorted(universe-(logical|{r['path'] for r in rows}))
    assert len(universe) == 1801 and unknown == prior['unregisteredJavaPaths'] and len(unknown) == 2
    return dict(source=SOURCE,sourceRows=rows,sourceCount=974,newLogicalCandidates=966,
        currentModifiedLogicalBindings=prior['currentModifiedLogicalBindings'],
        changedTestBindings=prior['changedTestBindings'],previousChangedTestBindings=prior['previousChangedTestBindings'],
        unregisteredCurrentSourceBindings=prior['unregisteredCurrentSourceBindings'],
        newTestPaths=NEW,registered=1799,javaPaths=1801,registeredMain=965,totalMain=965,
        registeredTest=834,totalTest=836,unregisteredJavaPaths=unknown,newPathsAdded=1,
        allPrior973RowsUnchanged=True,canonicalOwnerAndCostPreserved=True,
        productTestsExecuted=0,dynamicQualificationInferred=False,newAccepted=0,formalUpdated=False,effortPercent=None)


def prepare():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    prior, hashes, old_raw, old_snap = inputs()
    assert (ROOT/INV).read_bytes() == old_raw and (ROOT/SNAP).read_bytes() == old_snap
    value = expected_registry(prior, hashes, old_raw)
    observed = audit()
    assert observed['actualExit'] == 1 and observed['lastError'] == 'ValueError: current physical candidate exact Git/worktree scope'
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,wholeWbsAuditBefore=observed,**value))
    print(json.dumps(dict(actualExit=0,registered=1799,total=1801,unknown=2,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


def expected_documents(old_raw, old_snap):
    value = json.loads((OUT/'manifest.json').read_bytes())
    check = json.loads((CHECK/'manifest.json').read_bytes())
    assert check['actualExit'] == 0 and check['registryManifestSha256'] == data.sha((OUT/'manifest.json').read_bytes())
    inv = json.loads(old_raw)
    for name in SECTIONS:
        section = inv[name]
        keys = ('source','manifest','sha256','record','currentAddedTestPaths')
        assert 'previousUserSqlRegistryOverlay' not in section
        section['previousUserSqlRegistryOverlay'] = {k:copy.deepcopy(section[k]) for k in keys}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),
            record='evidence/01_PT/018_NK-OPS-001/2024_UserSQL新Test現source登録_結果.md',currentAddedTestPaths=NEW)
        if name == SECTIONS[0]:
            section.update(javaPaths=1801,registered=1799,unregistered=2,
                main=dict(total=965,registered=965,unregistered=0),test=dict(total=836,registered=834,unregistered=2),
                independentPostManifest=str((CHECK/'manifest.json').relative_to(ROOT)),
                independentPostSha256=data.sha((CHECK/'manifest.json').read_bytes()))
        else:
            section.update(sourceRows=974,newLogicalCandidates=966,
                guardManifest=str((CHECK/'manifest.json').relative_to(ROOT)),guardSha256=data.sha((CHECK/'manifest.json').read_bytes()),
                legacyOwnerLabelsDifferingFromCanonical=sum(r.get('legacyReportedOwner') != r['canonicalOwner'] for r in value['sourceRows']))
    raw = old_raw
    lines = []
    for name in SECTIONS:
        raw, before, after = replaced(raw,name,inv[name])
        lines.append((before,after))
    snap, before, after = replaced(old_snap,'inventorySha256',data.sha(raw))
    return raw,snap,lines,[(before,after)]


def emit():
    _,_,old_raw,old_snap = inputs()
    assert (ROOT/INV).read_bytes() == old_raw and (ROOT/SNAP).read_bytes() == old_snap
    _,_,lines,slines = expected_documents(old_raw,old_snap)
    patch = '*** Begin Patch\n'
    for name,pairs in ((INV,lines),(SNAP,slines)):
        patch += '*** Update File: '+str(ROOT/name)+'\n'
        for before,after in pairs:
            patch += '@@\n-'+before+'+'+after
    print(patch+'*** End Patch\n',end='')


def post():
    invocation = capture(Path(__file__))
    assert not POST.exists()
    prior, hashes, old_raw, old_snap = inputs()
    value = json.loads((OUT/'manifest.json').read_bytes())
    expected = expected_registry(prior,hashes,old_raw)
    assert {k:value[k] for k in expected} == expected
    raw,snap,_,_ = expected_documents(old_raw,old_snap)
    assert (ROOT/INV).read_bytes() == raw and (ROOT/SNAP).read_bytes() == snap
    validate(raw,snap,json.loads(old_raw),json.loads(old_snap))
    negatives = []
    for label,edit in (
        ('prior-owner',lambda v:v['sourceRows'][0].update(canonicalOwner='WBS-G13.07')),
        ('prior-cost',lambda v:v['sourceRows'][0].update(canonicalCostOwner='WBS-G13.07')),
        ('new-hash',lambda v:v['sourceRows'][-1].update(sha256='0'*64)),
        ('runtime-source',lambda v:v['sourceRows'][-1]['sourceSpecificRuntimeProof'].update(source='0'*40)),
        ('runtime-new-ids',lambda v:v['sourceRows'][-1]['sourceSpecificRuntimeProof'].update(newTestIds=32)),
        ('unknown',lambda v:v.update(unregisteredJavaPaths=[])),
        ('accepted',lambda v:v.update(newAccepted=1))):
        changed = copy.deepcopy(expected)
        edit(changed)
        assert changed != expected
        negatives.append(label)
    after = audit()
    assert after['actualExit'] == 1 and after['lastError'] == value['wholeWbsAuditBefore']['lastError']
    verify(invocation)
    POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        registryManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),inventorySha256=data.sha(raw),
        snapshotSha256=data.sha(snap),allPrior973RowsUnchanged=True,original941AndHistorical943Preserved=True,
        originalBudgetAndAcceptanceUnchanged=True,metadataNegativeVectors=negatives,registered=1799,total=1801,unknown=2,
        wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=after,
        productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,registered=1799,unknown=2,auditBefore=1,auditAfter=1,
        manifestSha256=data.sha((POST/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    if not sys.argv[1:]:
        prepare()
    elif sys.argv[1:] == ['--emit-patch']:
        emit()
    else:
        raise ValueError('no-argument preparation or explicit patch emission only')
