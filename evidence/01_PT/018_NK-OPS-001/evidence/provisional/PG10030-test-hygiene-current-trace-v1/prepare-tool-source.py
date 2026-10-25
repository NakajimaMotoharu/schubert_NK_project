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
SOURCE = '5012c53265d8d8d789ea2a3edf0b63fa45853a6a'
BEFORE = 'f976f66749bb22d811de46be88df5529a8168ac1'
PMO = 'documents/400_PGPT/470_PMO/'
INV = PMO+'485_WBS網羅性・受入対応.json'
SNAP = PMO+'486_WBS現行実績.json'
OUT = data.BASE/'PG10030-test-hygiene-current-trace-v1'
CHECK = data.BASE/'PG10032-test-hygiene-registry-check-v1'
POST = data.BASE/'PG10034-test-hygiene-trace-post-v1'
SUBJECTS = (
    ('question/QuestionQueryRequest.java','question/QuestionQueryPlainContractTest.java','WBS-P013-01','QRY',
        '2015_質問通知plain契約8_単体テスト仕様書.md'),
    ('log/LogRequest.java','log/LogPlainContractTest.java','WBS-P018-09','LOG',
        '2016_Logplain契約8_単体テスト仕様書.md'))
MAIN_PREFIX = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/'
TEST_PREFIX = MAIN_PREFIX.replace('/main/','/test/')
NEW = []
SECTIONS = ('currentJavaPathExplicitRegistryMeasurement','currentIncrementalHostOwnership')


def inputs():
    prior = data.read_checked(data.BASE/'PG10004-query-pair-trace-v1/manifest.json',
        'e60fb8cf887388730ea66f1f511c45f11e64be1e29c44d80e22fc838d8335ebd')
    normal = data.read_checked(data.BASE/'PG10024-test-hygiene-six-compile-v1/manifest.json',
        '5888cf524ecdc64fcb510d01ea800c6018222f1db790ad057466dae4b89072bf')
    proof = data.read_checked(data.BASE/'PG10026-test-hygiene-normal-post-v1/manifest.json',
        '6094f2b3027cdb314f951668c2656fbcb9b2f34c2f59a2dd9779fc146fc701c2')
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
    assert len(rows) == 973
    proof_path = data.BASE/'PG10026-test-hygiene-normal-post-v1/manifest.json'
    proof = data.read_checked(proof_path,'6094f2b3027cdb314f951668c2656fbcb9b2f34c2f59a2dd9779fc146fc701c2')
    original = data.read_checked(data.BASE/'PG9992-query-pair-six-compile-v1/manifest.json',
        '33f7f2f8d1676bcc53f03252733530a33042a8dc910a36e2624ad1f54206c284')['begin']['inputHashes']
    changes = []
    for row in rows:
        path = row['path']
        assert row['sha256'] == original[path]
        if row['sha256'] != hashes[path]:
            assert path in proof['changedSourceHashes'] and '/src/test/java/' in path
            changes.append(dict(path=path,previousSha256=row['sha256'],currentSha256=hashes[path],source=SOURCE,
                canonicalOwner=row['canonicalOwner'],canonicalCostOwner=row['canonicalCostOwner'],
                proofManifest=str(proof_path.relative_to(ROOT)),proofSha256='6094f2b3027cdb314f951668c2656fbcb9b2f34c2f59a2dd9779fc146fc701c2',
                additionalAllocatedCostPp=0,currentSourceRuntimeQualificationInferred=False))
            row['sha256'] = hashes[path]
    universe = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    logical = {r['path'] for r in json.loads(old_raw)['artifacts']}
    unknown = sorted(universe-(logical|{r['path'] for r in rows}))
    assert len(universe) == 1800 and unknown == prior['unregisteredJavaPaths'] and len(unknown) == 2
    unknown_changes = [dict(path=p,previousSha256=original[p],currentSha256=hashes[p],
        canonicalOwner='UNKNOWN',canonicalCostOwner='UNKNOWN',source=SOURCE)
        for p in unknown if p in proof['changedSourceHashes']]
    assert {r['path'] for r in changes+unknown_changes} == set(proof['changedSourceHashes'])
    return dict(source=SOURCE,sourceRows=rows,sourceCount=973,newLogicalCandidates=965,
        currentModifiedLogicalBindings=prior['currentModifiedLogicalBindings'],
        changedTestBindings=changes,previousChangedTestBindings=prior['previousChangedTestBindings'],
        previousTestHygieneChangedTestBindings=prior['changedTestBindings'],
        unregisteredCurrentSourceBindings=unknown_changes,
        newTestPaths=NEW,registered=1798,javaPaths=1800,registeredMain=965,totalMain=965,
        registeredTest=833,totalTest=835,unregisteredJavaPaths=unknown,newPathsAdded=0,
        changedKnownTestHashes=len(changes),changedUnregisteredTestHashes=len(unknown_changes),
        allPrior973RowsPreservedExceptExplicitSha256=True,canonicalOwnerAndCostPreserved=True,
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
        keys = ('source','manifest','sha256','record','currentAddedTestPaths','currentChangedTestBindings')
        assert 'previousTestHygieneRegistryOverlay' not in section
        section['previousTestHygieneRegistryOverlay'] = {k:copy.deepcopy(section[k]) for k in keys}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(ROOT)),
            sha256=data.sha((OUT/'manifest.json').read_bytes()),
            record='evidence/01_PT/018_NK-OPS-001/2023_Testsource意味保持変更・現source登録_結果.md',currentAddedTestPaths=NEW,
            currentChangedTestBindings=value['changedTestBindings'],
            unregisteredCurrentSourceBindings=value['unregisteredCurrentSourceBindings'])
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
        snapshotSha256=data.sha(snap),allPrior973RowsPreservedExceptExplicitSha256=True,original941AndHistorical943Preserved=True,
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
