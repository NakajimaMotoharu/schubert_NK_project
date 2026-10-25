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
SOURCE = '70165b0768a1fabd13371cc25a55978fcf3452ba'
BEFORE = 'ab5f2b1c15a3b6e07b954a0b603f2f0d57770899'
PMO = 'documents/400_PGPT/470_PMO/'
INV = PMO+'485_WBS網羅性・受入対応.json'
SNAP = PMO+'486_WBS現行実績.json'
OUT = data.BASE/'PG9982-plain-core-trace-v1'
CHECK = data.BASE/'PG9984-plain-core-registry-check-v1'
POST = data.BASE/'PG9986-plain-core-trace-post-v1'
MAIN = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/admin/UserQueryRequest.java'
NEW = MAIN.replace('/main/','/test/').replace('UserQueryRequest.java','UserQueryCanonicalCoreTest.java')
SECTIONS = ('currentJavaPathExplicitRegistryMeasurement','currentIncrementalHostOwnership')


def inputs():
    prior = data.read_checked(data.BASE/'PG9950-pure-query-test-registry-v1/manifest.json',
        '6f3437117368244ae1dca486f4187e750015f90f42ca9ab07556292e2dc59986')
    normal = data.read_checked(data.BASE/'PG9968-plain-core-fixed-six-compile-v1/manifest.json',
        '277ca65ee5a596e94d9e222d919ed8acd4e3a7efe72883446b769db41e51363f')
    proof = data.read_checked(data.BASE/'PG9978-plain-core-quality-post-v1/manifest.json',
        'de9e91e5529a130892b3ec76b23cdc9e677ca08be6ef11c56490562552b97fc0')
    assert normal['actualExit'] == prior['actualExit'] == proof['actualExit'] == 0
    assert normal['source'] == proof['source'] == SOURCE
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in hashes.items())
    old_raw, old_snap = [subprocess.check_output(['git','show',BEFORE+':'+p],cwd=ROOT) for p in (INV,SNAP)]
    logical = {r['path']:r for r in json.loads(old_raw)['artifacts']}
    assert len(logical) == 941 and logical[MAIN]['owner'] == logical[MAIN]['costOwner'] == 'WBS-P010-01'
    assert hashes[MAIN] == logical[MAIN]['sha256']
    return prior, hashes, old_raw, old_snap


def expected_registry(prior, hashes, old_raw):
    rows = copy.deepcopy(prior['sourceRows'])
    assert len(rows) == 970 and NEW not in {r['path'] for r in rows}
    assert all(r['sha256'] == hashes[r['path']] for r in rows)
    row = copy.deepcopy(next(r for r in rows if r['path'].endswith('/UserQueryResponseBoundaryTest.java')))
    row.update(path=NEW,sha256=hashes[NEW],basis='EXPLICIT_2012_CORE001_004_AND_ORIGINAL_LOGICAL_USER_QUERY_MAIN_P01001',
        independentSpec='evidence/01_PT/018_NK-OPS-001/2012_User要求plain正規化4_単体テスト仕様書.md',
        methodTestIds=['PT-ADM-CORE001','PT-ADM-CORE002','PT-ADM-CORE003','PT-ADM-CORE004'],
        ownerProofManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9978-plain-core-quality-post-v1/manifest.json',
        ownerProofSha256='de9e91e5529a130892b3ec76b23cdc9e677ca08be6ef11c56490562552b97fc0',
        sourceSpecificRuntimeProof=dict(source=SOURCE,tests=8,suites=2,newTestIds=4,relatedRegressionMethods=4,
            manifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9974-plain-core-fixed-post-v1/manifest.json',
            sha256='7e37b3f71ef9716661798c908ec231c45a2883cbe0e97df55dbbee13c1a7fe5b',reassignedToCurrentSource=False))
    rows.append(row)
    universe = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    logical = {r['path'] for r in json.loads(old_raw)['artifacts']}
    unknown = sorted(universe-(logical|{r['path'] for r in rows}))
    assert len(universe) == 1798 and unknown == prior['unregisteredJavaPaths'] and len(unknown) == 2
    return dict(source=SOURCE,sourceRows=rows,sourceCount=971,newLogicalCandidates=963,
        currentModifiedLogicalBindings=prior['currentModifiedLogicalBindings'],
        changedTestBindings=prior['changedTestBindings'],previousChangedTestBindings=prior['previousChangedTestBindings'],
        newTestPaths=[NEW],registered=1796,javaPaths=1798,registeredMain=965,totalMain=965,
        registeredTest=831,totalTest=833,unregisteredJavaPaths=unknown,newPathsAdded=1,
        allPrior970RowsUnchanged=True,canonicalOwnerAndCostPreserved=True,
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
    print(json.dumps(dict(actualExit=0,registered=1796,total=1798,unknown=2,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


def expected_documents(old_raw, old_snap):
    value = json.loads((OUT/'manifest.json').read_bytes())
    check = json.loads((CHECK/'manifest.json').read_bytes())
    assert check['actualExit'] == 0 and check['registryManifestSha256'] == data.sha((OUT/'manifest.json').read_bytes())
    inv = json.loads(old_raw)
    for name in SECTIONS:
        section = inv[name]
        keys = ('source','manifest','sha256','record','currentAddedTestPaths')
        assert 'previousPlainCoreRegistryOverlay' not in section
        section['previousPlainCoreRegistryOverlay'] = {k:copy.deepcopy(section[k]) for k in keys}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),
            record='evidence/01_PT/018_NK-OPS-001/2014_User正規化Test現source登録_結果.md',currentAddedTestPaths=[NEW])
        if name == SECTIONS[0]:
            section.update(javaPaths=1798,registered=1796,unregistered=2,
                main=dict(total=965,registered=965,unregistered=0),test=dict(total=833,registered=831,unregistered=2),
                independentPostManifest=str((CHECK/'manifest.json').relative_to(ROOT)),
                independentPostSha256=data.sha((CHECK/'manifest.json').read_bytes()))
        else:
            section.update(sourceRows=971,newLogicalCandidates=963,
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
        ('runtime-new-ids',lambda v:v['sourceRows'][-1]['sourceSpecificRuntimeProof'].update(newTestIds=8)),
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
        snapshotSha256=data.sha(snap),allPrior970RowsUnchanged=True,original941AndHistorical943Preserved=True,
        originalBudgetAndAcceptanceUnchanged=True,metadataNegativeVectors=negatives,registered=1796,total=1798,unknown=2,
        wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=after,
        productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,registered=1796,unknown=2,auditBefore=1,auditAfter=1,
        manifestSha256=data.sha((POST/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    if not sys.argv[1:]:
        prepare()
    elif sys.argv[1:] == ['--emit-patch']:
        emit()
    else:
        raise ValueError('no-argument preparation or explicit patch emission only')
