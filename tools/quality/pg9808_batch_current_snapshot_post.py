"""Independent two-Test registry update; full snapshot semantics and actual audit HOLD retained."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import g07_host_class_provenance_inputs as data
import pg9338_wbs_reference_metadata_post as metadata
from host_tool_invocation import capture, verify

ROOT = data.ROOT
PMO = ROOT / 'documents/400_PGPT/470_PMO'
SOURCE = '58913ab374ef54d138fa3fad8c80cccd03d87c10'
BEFORE = 'e8b43eda3a74e2c4ef56436bfa14cc5227207823'
OUT = data.BASE / 'PG9808-batch-current-snapshot-post-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    invpath = PMO / '485_WBS網羅性・受入対応.json'
    snappath = PMO / '486_WBS現行実績.json'
    old_inv = json.loads(subprocess.check_output(['git','show',BEFORE + ':' + str(invpath.relative_to(ROOT))],cwd=ROOT))
    old_snap = json.loads(subprocess.check_output(['git','show',BEFORE + ':' + str(snappath.relative_to(ROOT))],cwd=ROOT))
    invraw,snapraw = invpath.read_bytes(),snappath.read_bytes()
    metadata.validate(invraw,snapraw,old_inv,old_snap)
    inv,snap = json.loads(invraw),json.loads(snapraw)
    assert snap['inventorySha256'] == data.sha(invraw)
    joined_path = data.BASE / 'PG9806-batch-current-source-registration-v1/manifest.json'
    joined = data.read_checked(joined_path,'0c9d2e5dc36b66b318e5351ee2e9e2463aab23a20c3cc2cd9917e60ae98af470')
    prior = data.read_checked(data.BASE / 'PG9766-outbox-current-source-registration-v1/manifest.json',
        '180c761500bf3e7fc08326f26fcea2b020dd398bdaa4231b55bef4c20a1f5815')
    normal = data.read_checked(data.BASE / 'PG9792-batch-boundary-six-compile-v1/manifest.json',
        'aadb6fcfee66e10f1e6357493ac5c15d60babe72570dc506b87e522f9a238a86')
    assert joined['actualExit'] == normal['actualExit'] == 0 and joined['source'] == normal['source'] == SOURCE
    rows = joined['sourceRows']
    assert rows[:-2] == prior['sourceRows'] and len(rows) == len({r['path'] for r in rows}) == 961
    expected = {'BatchRunValueBoundaryTest.java':'WBS-P017-02','CleanupValueBoundaryTest.java':'WBS-P017-07'}
    assert {Path(r['path']).name:r['canonicalOwner'] for r in rows[-2:]} == expected
    assert all(r['owner'] == r['canonicalOwner'] == r['canonicalCostOwner'] and not r['currentSourcePtQualificationInferred'] for r in rows[-2:])
    assert all(r['ownershipStatus'] == 'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED' for r in rows[-2:])
    hashes = normal['begin']['inputHashes']
    assert all(hashes[r['path']] == r['sha256'] == data.sha((ROOT / r['path']).read_bytes()) for r in rows)
    universe = {p for p in hashes if p.endswith('.java') and '/java/' in p}
    registered = universe & ({r['path'] for r in inv['artifacts']} | {r['path'] for r in rows})
    tests = {p for p in universe if '/src/test/java/' in p}
    assert len(universe) == 1794 and len(registered) == 1786 and len(tests) == 829 and len(registered & tests) == 821
    assert sorted(universe - registered) == joined['unregisteredJavaPaths'] == prior['unregisteredJavaPaths']
    current,measured = inv['currentIncrementalHostOwnership'],inv['currentJavaPathExplicitRegistryMeasurement']
    for value in (current,measured):
        assert value['source'] == SOURCE and value['manifest'] == str(joined_path.relative_to(ROOT))
        assert value['sha256'] == data.sha(joined_path.read_bytes())
        previous = value['previousBatchBoundarySourceOverlay']
        assert previous['source'] == prior['source'] and previous['sha256'] == '180c761500bf3e7fc08326f26fcea2b020dd398bdaa4231b55bef4c20a1f5815'
        assert value['currentModifiedLogicalBindings'] == joined['currentModifiedLogicalBindings'] == prior['currentModifiedLogicalBindings']
    assert current['sourceRows'] == 961 and current['newLogicalCandidates'] == 953
    assert current['legacyOwnerLabelsDifferingFromCanonical'] == sum(r['legacyReportedOwner'] != r['canonicalOwner'] for r in rows)
    assert measured['javaPaths'] == 1794 and measured['registered'] == 1786 and measured['unregistered'] == 8
    assert measured['main'] == dict(total=965,registered=965,unregistered=0)
    assert measured['test'] == dict(total=829,registered=821,unregistered=8)
    proof_path = ROOT / current['guardManifest']
    proof_sha = '4578485d372283f2ad70a3a8b7a654d30d94c15a8e8443773e3fb3517435a883'
    assert proof_path == ROOT / measured['independentPostManifest']
    assert current['guardSha256'] == measured['independentPostSha256'] == proof_sha
    proof = data.read_checked(proof_path,proof_sha)
    assert proof['actualExit'] == 0 and proof['source'] == SOURCE and proof['newTestIds'] == 4
    negatives = []
    for label,editinv,editsnap in [
        ('old-pointer',None,lambda v:v.update(inventorySha256=old_snap['inventorySha256'])),
        ('source-promoted',None,lambda v:v.update(source=SOURCE)),
        ('effort-invented',None,lambda v:v.update(wholeEffortCompletionRate=50)),
        ('original-owner-mutated',lambda v:v['artifacts'][0].update(owner='WBS-G13.07'),None),
        ('old-candidate-promoted',lambda v:v['currentPhysicalCandidate'].update(source=SOURCE),None)]:
        a,b = copy.deepcopy(inv),copy.deepcopy(snap)
        if editinv:
            editinv(a)
            b['inventorySha256'] = data.sha(metadata.dump(a))
        if editsnap:
            editsnap(b)
        try:
            metadata.validate(metadata.dump(a),metadata.dump(b),old_inv,old_snap)
        except ValueError:
            negatives.append(label)
        else:
            raise AssertionError('unapproved snapshot semantics accepted')
    for name in ('481_PGPT詳細WBS.json','484_WBSコスト枠・細分化.json'):
        path = PMO / name
        assert path.read_bytes() == subprocess.check_output(['git','show',BEFORE + ':' + str(path.relative_to(ROOT))],cwd=ROOT)
    command = [sys.executable,'-B',str(ROOT / 'tools/quality/wbs_progress_audit.py')]
    audit = subprocess.run(command,cwd=ROOT,capture_output=True,timeout=60,check=False)
    error = audit.stderr.decode().splitlines()[-1]
    assert audit.returncode == 1 and not audit.stdout and error == 'ValueError: current physical candidate exact Git/worktree scope'
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        joinManifestSha256=data.sha(joined_path.read_bytes()),inventorySha256=data.sha(invraw),snapshotSha256=data.sha(snapraw),
        sourceRows=961,registered=1786,javaPaths=1794,unregistered=8,main=measured['main'],test=measured['test'],
        old959AllFieldsPreserved=True,unchangedModifiedLogicalBindingPreserved=True,metadataCounterexamples=negatives,
        original941Historical943BudgetAcceptancePreserved=True,
        wholeWbsAudit=dict(command=command,actualExit=audit.returncode,lastError=error,passed=False),
        productTestsExecuted=0,newTestIds=0,newAccepted=0,formalUpdated=False,effortPercent=None,coverage=None))
    print(json.dumps(dict(actualExit=0,registered=1786,javaPaths=1794,wholeWbsAuditExit=audit.returncode,
        manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
