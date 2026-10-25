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
SOURCE = 'bba24d15923831a17e5464328b70fdb950fb2fcf'
BEFORE = '43e3b27d82cfdbd25c4fcd4beb0cd4ad4c21945f'
PMO = 'documents/400_PGPT/470_PMO/'
INV = PMO+'485_WBS網羅性・受入対応.json'
SNAP = PMO+'486_WBS現行実績.json'
OUT = data.BASE/'PG10004-query-pair-trace-v1'
CHECK = data.BASE/'PG10006-query-pair-registry-check-v1'
POST = data.BASE/'PG10008-query-pair-trace-post-v1'
SUBJECTS = (
    ('question/QuestionQueryRequest.java','question/QuestionQueryPlainContractTest.java','WBS-P013-01','QRY',
        '2015_質問通知plain契約8_単体テスト仕様書.md'),
    ('log/LogRequest.java','log/LogPlainContractTest.java','WBS-P018-09','LOG',
        '2016_Logplain契約8_単体テスト仕様書.md'))
MAIN_PREFIX = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/'
TEST_PREFIX = MAIN_PREFIX.replace('/main/','/test/')
NEW = [TEST_PREFIX+s[1] for s in SUBJECTS]
SECTIONS = ('currentJavaPathExplicitRegistryMeasurement','currentIncrementalHostOwnership')


def inputs():
    prior = data.read_checked(data.BASE/'PG9982-plain-core-trace-v1/manifest.json',
        'ddca86f481cba3be23f37c2b2c4f580caf04ad0090670c8848ff755cada66855')
    normal = data.read_checked(data.BASE/'PG9992-query-pair-six-compile-v1/manifest.json',
        '33f7f2f8d1676bcc53f03252733530a33042a8dc910a36e2624ad1f54206c284')
    proof = data.read_checked(data.BASE/'PG10000-query-pair-quality-post-v1/manifest.json',
        '338dc497fde269a4f2e60821394976f838ed438de7c3bd4e3841a65c2ff1bc26')
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
    assert len(rows) == 971 and not set(NEW) & {r['path'] for r in rows}
    assert all(r['sha256'] == hashes[r['path']] for r in rows)
    template = next(r for r in rows if r['path'].endswith('/UserQueryCanonicalCoreTest.java'))
    for main,test,owner,tag,spec in SUBJECTS:
        path = TEST_PREFIX+test
        row = copy.deepcopy(template)
        row.update(path=path,sha256=hashes[path],owner=owner,canonicalOwner=owner,canonicalCostOwner=owner,
            basis='EXPLICIT_PLAIN_SPEC_AND_ORIGINAL_LOGICAL_MAIN_OWNER',mainSourceSubjects=[MAIN_PREFIX+main],
            independentSpec='evidence/01_PT/018_NK-OPS-001/'+spec,
            methodTestIds=[f'PT-{tag}-PLAIN{i:03d}' for i in range(1,9)],
            ownerProofManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10000-query-pair-quality-post-v1/manifest.json',
            ownerProofSha256='338dc497fde269a4f2e60821394976f838ed438de7c3bd4e3841a65c2ff1bc26',
            sourceSpecificRuntimeProof=dict(source=SOURCE,tests=16,suites=2,newTestIds=16,programMethodCount=8,
                sharedRunReferenceNotAdditive=True,
                manifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9998-query-pair-post-v1/manifest.json',
                sha256='9cc448696e53581d68239ac67cb22ae25a019c2a41d04ebaf2ec9b0f15bfa9d8',reassignedToCurrentSource=False))
        rows.append(row)
    universe = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    logical = {r['path'] for r in json.loads(old_raw)['artifacts']}
    unknown = sorted(universe-(logical|{r['path'] for r in rows}))
    assert len(universe) == 1800 and unknown == prior['unregisteredJavaPaths'] and len(unknown) == 2
    return dict(source=SOURCE,sourceRows=rows,sourceCount=973,newLogicalCandidates=965,
        currentModifiedLogicalBindings=prior['currentModifiedLogicalBindings'],
        changedTestBindings=prior['changedTestBindings'],previousChangedTestBindings=prior['previousChangedTestBindings'],
        newTestPaths=NEW,registered=1798,javaPaths=1800,registeredMain=965,totalMain=965,
        registeredTest=833,totalTest=835,unregisteredJavaPaths=unknown,newPathsAdded=2,
        allPrior971RowsUnchanged=True,canonicalOwnerAndCostPreserved=True,
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
    print(json.dumps(dict(actualExit=0,registered=1798,total=1800,unknown=2,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


def expected_documents(old_raw, old_snap):
    value = json.loads((OUT/'manifest.json').read_bytes())
    check = json.loads((CHECK/'manifest.json').read_bytes())
    assert check['actualExit'] == 0 and check['registryManifestSha256'] == data.sha((OUT/'manifest.json').read_bytes())
    inv = json.loads(old_raw)
    for name in SECTIONS:
        section = inv[name]
        keys = ('source','manifest','sha256','record','currentAddedTestPaths')
        assert 'previousQueryPairRegistryOverlay' not in section
        section['previousQueryPairRegistryOverlay'] = {k:copy.deepcopy(section[k]) for k in keys}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),
            record='evidence/01_PT/018_NK-OPS-001/2019_質問通知Log二Test現source登録_結果.md',currentAddedTestPaths=NEW)
        if name == SECTIONS[0]:
            section.update(javaPaths=1800,registered=1798,unregistered=2,
                main=dict(total=965,registered=965,unregistered=0),test=dict(total=835,registered=833,unregistered=2),
                independentPostManifest=str((CHECK/'manifest.json').relative_to(ROOT)),
                independentPostSha256=data.sha((CHECK/'manifest.json').read_bytes()))
        else:
            section.update(sourceRows=973,newLogicalCandidates=965,
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
        snapshotSha256=data.sha(snap),allPrior971RowsUnchanged=True,original941AndHistorical943Preserved=True,
        originalBudgetAndAcceptanceUnchanged=True,metadataNegativeVectors=negatives,registered=1798,total=1800,unknown=2,
        wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=after,
        productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,registered=1798,unknown=2,auditBefore=1,auditAfter=1,
        manifestSha256=data.sha((POST/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    if not sys.argv[1:]:
        prepare()
    elif sys.argv[1:] == ['--emit-patch']:
        emit()
    else:
        raise ValueError('no-argument preparation or explicit patch emission only')
