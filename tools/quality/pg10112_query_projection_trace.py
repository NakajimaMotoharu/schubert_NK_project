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
SOURCE = 'dd138e9def675f9278ae4b1bdb8c5ee3e34f2b77'
BEFORE = 'fe20e90ba'
PMO = 'documents/400_PGPT/470_PMO/'
INV = PMO+'485_WBS網羅性・受入対応.json'
SNAP = PMO+'486_WBS現行実績.json'
OUT = data.BASE/'PG10112-query-projection-trace-v1'
CHECK = data.BASE/'PG10114-query-projection-registry-check-v1'
POST = data.BASE/'PG10116-query-projection-trace-post-v1'
SUBJECTS = (
    ('admin/UserQueryRequest.java','admin/UserQuerySqlContractTest.java','WBS-P010-01','ADM',
        'evidence/01_PT/010_NK-ADM-001/081_NK-ADM-001_SQL満杯page契約単体テスト仕様書.md'),
    ('log/LogRequest.java','log/LogSqlContractTest.java','WBS-P018-09','LOG',
        'evidence/01_PT/010_NK-ADM-001/081_NK-ADM-001_SQL満杯page契約単体テスト仕様書.md'),
    ('question/QuestionQueryRequest.java','question/QuestionSqlContractTest.java','WBS-P013-01','QRY',
        'evidence/01_PT/014_NK-QRY-001/005_NK-QRY-001_通知有効終端・満杯page契約仕様書.md'))
MAIN_PREFIX = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/'
TEST_PREFIX = MAIN_PREFIX.replace('/main/','/test/')
NEW = []
SECTIONS = ('currentJavaPathExplicitRegistryMeasurement','currentIncrementalHostOwnership')


def inputs():
    prior = data.read_checked(data.BASE/'PG10088-query-sql-batch-trace-v1/manifest.json',
        '3b6d5b8d2d4ac20a54d89faeddea478ae2bfedcd749eb5166859dd536bb45ffe')
    normal = data.read_checked(data.BASE/'PG10100-query-batch-six-compile-v1/manifest.json',
        'a2a8eb62b574693a47e5ce82b830185a7db3fd41f4af61ba4341b598c5f8e3f3')
    proof = data.read_checked(data.BASE/'PG10108-query-batch-quality-post-v1/manifest.json',
        '0e8f91b6eebb5f67081f9232b4fbb5dbb625cb92775458e5d171ad63b9e35360')
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
    assert len(rows) == 976
    by_path = {r['path']:r for r in rows}
    proof = data.read_checked(data.BASE/'PG10108-query-batch-quality-post-v1/manifest.json',
        '0e8f91b6eebb5f67081f9232b4fbb5dbb625cb92775458e5d171ad63b9e35360')
    changes = copy.deepcopy(proof['changedSourceBindings'])
    changed = {r['path']:r for r in changes}
    assert set(changed) == {TEST_PREFIX+s[1] for s in SUBJECTS}
    assert all(r['sha256'] == hashes[r['path']] for r in rows if r['path'] not in changed)
    for _,test,owner,tag,spec in SUBJECTS:
        path = TEST_PREFIX+test
        row = by_path[path]
        assert row['sha256'] == changed[path]['previousSha256']
        assert hashes[path] == changed[path]['currentSha256']
        assert row['canonicalOwner'] == row['canonicalCostOwner'] == owner
        assert row['methodTestIds'] == [f'PT-{tag}-SQL{i:03d}' for i in range(1,9)]
        assert 'currentSourceRuntimeProof' not in row and 'currentIndependentSpec' not in row
        added = 2 if tag == 'QRY' else 1
        row['sha256'] = hashes[path]
        row['methodTestIds'] += [f'PT-{tag}-SQL{i:03d}' for i in range(9,9+added)]
        row['currentIndependentSpec'] = spec
        row['currentSourceRuntimeProof'] = dict(source=SOURCE,tests=52,suites=7,
            groupNewTestIds=4,newProgramTestIds=added,programSqlMethodCount=8+added,
            programAllMethodCount=18 if tag == 'QRY' else 17,
            manifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10106-query-batch-post-v1/manifest.json',
            sha256='b83f269bd2f8573e5e9f10341ad4fc96d6b0a93589e98d0c11e66467c00f0b2d',
            sharedRunReferenceNotAdditive=True,historicalProofReassigned=False)
        changed[path].update(source=SOURCE,canonicalOwner=owner,canonicalCostOwner=owner,
            proofManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10108-query-batch-quality-post-v1/manifest.json',
            proofSha256='0e8f91b6eebb5f67081f9232b4fbb5dbb625cb92775458e5d171ad63b9e35360',
            additionalAllocatedCostPp=0)
    universe = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    logical = {r['path'] for r in json.loads(old_raw)['artifacts']}
    unknown = sorted(universe-(logical|{r['path'] for r in rows}))
    assert len(universe) == 1803 and unknown == prior['unregisteredJavaPaths'] and len(unknown) == 2
    return dict(source=SOURCE,sourceRows=rows,sourceCount=976,newLogicalCandidates=968,
        currentModifiedLogicalBindings=prior['currentModifiedLogicalBindings'],
        changedTestBindings=changes,previousChangedTestBindings=prior['previousChangedTestBindings'],
        previousCurrentChangedTestBindingsReference=dict(
            manifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10088-query-sql-batch-trace-v1/manifest.json',
            sha256='3b6d5b8d2d4ac20a54d89faeddea478ae2bfedcd749eb5166859dd536bb45ffe',
            arrayPath='changedTestBindings',count=639),
        unregisteredCurrentSourceBindings=prior['unregisteredCurrentSourceBindings'],
        newTestPaths=NEW,registered=1801,javaPaths=1803,registeredMain=965,totalMain=965,
        registeredTest=836,totalTest=838,unregisteredJavaPaths=unknown,newPathsAdded=0,newMethodIds=4,
        allOther973RowsUnchanged=True,historicalRuntimeProofsPreserved=True,canonicalOwnerAndCostPreserved=True,
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
    print(json.dumps(dict(actualExit=0,registered=1801,total=1803,unknown=2,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


def expected_documents(old_raw, old_snap):
    value = json.loads((OUT/'manifest.json').read_bytes())
    check = json.loads((CHECK/'manifest.json').read_bytes())
    assert check['actualExit'] == 0 and check['registryManifestSha256'] == data.sha((OUT/'manifest.json').read_bytes())
    inv = json.loads(old_raw)
    for name in SECTIONS:
        section = inv[name]
        keys = ('source','manifest','sha256','record','currentAddedTestPaths','currentChangedTestBindings',
            'currentChangedTestBindingReference','currentChangedTestBindingsInlineComplete')
        assert 'previousQueryProjectionRegistryOverlay' not in section
        section['previousQueryProjectionRegistryOverlay'] = {k:copy.deepcopy(section[k]) for k in keys}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),
            record='evidence/01_PT/018_NK-OPS-001/2026_当52SQLTest変更追跡_結果.md',currentAddedTestPaths=NEW,
            currentChangedTestBindings=[],currentChangedTestBindingsInlineComplete=False,
            currentChangedTestBindingReference=dict(manifest=str((OUT/'manifest.json').relative_to(ROOT)),
                sha256=data.sha((OUT/'manifest.json').read_bytes()),arrayPath='changedTestBindings',count=3,source=SOURCE))
        if name == SECTIONS[0]:
            section.update(javaPaths=1803,registered=1801,unregistered=2,
                main=dict(total=965,registered=965,unregistered=0),test=dict(total=838,registered=836,unregistered=2),
                independentPostManifest=str((CHECK/'manifest.json').relative_to(ROOT)),
                independentPostSha256=data.sha((CHECK/'manifest.json').read_bytes()))
        else:
            section.update(sourceRows=976,newLogicalCandidates=968,
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
        snapshotSha256=data.sha(snap),allOther973RowsUnchanged=True,historicalRuntimeProofsPreserved=True,
        original941AndHistorical943Preserved=True,
        originalBudgetAndAcceptanceUnchanged=True,metadataNegativeVectors=negatives,registered=1801,total=1803,unknown=2,
        wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=after,
        productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,registered=1801,unknown=2,auditBefore=1,auditAfter=1,
        manifestSha256=data.sha((POST/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    if not sys.argv[1:]:
        prepare()
    elif sys.argv[1:] == ['--emit-patch']:
        emit()
    else:
        raise ValueError('no-argument preparation or explicit patch emission only')
