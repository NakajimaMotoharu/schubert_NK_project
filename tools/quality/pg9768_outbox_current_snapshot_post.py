"""Independent bounded source registry and snapshot check, retaining genuine whole-audit HOLD."""
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
OUT = data.BASE / 'PG9768-outbox-current-snapshot-post-v1'
BEFORE = 'b9ad40f37a1391cf70073861a95a9a0a3dc22173'
SOURCE = 'e598a81bb4200b4e4930278b31479ff927aa025f'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    invpath = PMO / '485_WBS網羅性・受入対応.json'
    snappath = PMO / '486_WBS現行実績.json'
    old_inv = json.loads(subprocess.check_output(['git','show',BEFORE + ':' + str(invpath.relative_to(ROOT))],cwd=ROOT))
    old_snap = json.loads(subprocess.check_output(['git','show',BEFORE + ':' + str(snappath.relative_to(ROOT))],cwd=ROOT))
    invraw = invpath.read_bytes()
    snapraw = snappath.read_bytes()
    metadata.validate(invraw,snapraw,old_inv,old_snap)
    inv = json.loads(invraw)
    snap = json.loads(snapraw)
    joinpath = data.BASE / 'PG9766-outbox-current-source-registration-v1/manifest.json'
    joined = data.read_checked(joinpath,'180c761500bf3e7fc08326f26fcea2b020dd398bdaa4231b55bef4c20a1f5815')
    prior = data.read_checked(data.BASE / 'PG9732-semantic-current-source-registration-v1/manifest.json',
        '109b6ab29e88c75e0743feb627f462e19fb4955a119883b14fe12c435103779a')
    normal = data.read_checked(data.BASE / 'PG9750-outbox-report-six-compile-v1/manifest.json',
        '7b1c2b2e67dab622cc3e905e1c04ac5819a587f90992c404cf6cab3f0ceebb96')
    assert joined['actualExit'] == normal['actualExit'] == 0 and joined['source'] == normal['source'] == SOURCE
    rows = joined['sourceRows']
    assert rows[:-1] == prior['sourceRows'] and len(rows) == len({r['path'] for r in rows}) == 959
    added = rows[-1]
    assert added['path'].endswith('/messaging/outbound/OutboxDispatchReportBoundaryTest.java')
    assert added['owner'] == added['canonicalOwner'] == added['canonicalCostOwner'] == 'WBS-P006-02'
    assert added['ownershipStatus'] == 'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED'
    assert added['currentSourcePtQualificationInferred'] is False
    hashes = normal['begin']['inputHashes']
    universe = {p for p in hashes if p.endswith('.java') and '/java/' in p}
    registered = universe & ({r['path'] for r in inv['artifacts']} | {r['path'] for r in rows})
    tests = {p for p in universe if '/src/test/java/' in p}
    assert len(universe) == 1792 and len(registered) == 1784 and len(tests) == 827 and len(registered & tests) == 819
    assert sorted(universe - registered) == joined['unregisteredJavaPaths']
    current = inv['currentIncrementalHostOwnership']
    measured = inv['currentJavaPathExplicitRegistryMeasurement']
    for value in (current,measured):
        assert value['source'] == SOURCE and value['manifest'] == str(joinpath.relative_to(ROOT))
        assert value['sha256'] == data.sha(joinpath.read_bytes())
        assert value['previousOutboxCountBoundarySourceOverlay']['source'] == prior['source']
        assert value['previousOutboxCountBoundarySourceOverlay']['sha256'] == '109b6ab29e88c75e0743feb627f462e19fb4955a119883b14fe12c435103779a'
    assert current['sourceRows'] == 959 and current['newLogicalCandidates'] == 951
    assert current['legacyOwnerLabelsDifferingFromCanonical'] == sum(r['legacyReportedOwner'] != r['canonicalOwner'] for r in rows)
    assert measured['javaPaths'] == 1792 and measured['registered'] == 1784 and measured['unregistered'] == 8
    assert measured['main'] == dict(total=965,registered=965,unregistered=0)
    assert measured['test'] == dict(total=827,registered=819,unregistered=8)
    proof_path = ROOT / current['guardManifest']
    assert proof_path == ROOT / measured['independentPostManifest']
    proof = data.read_checked(proof_path,current['guardSha256'])
    assert current['guardSha256'] == measured['independentPostSha256'] == '8b9963b22aac0b2d9dc1241c35cc07537980cd670a616854ca46a8c2cb0dc6c9'
    assert proof['actualExit'] == 0 and proof['source'] == SOURCE
    assert current['currentModifiedLogicalBindings'] == measured['currentModifiedLogicalBindings'] == joined['currentModifiedLogicalBindings']
    modified = joined['currentModifiedLogicalBindings']
    assert len(modified) == 1 and modified[0]['canonicalOwner'] == modified[0]['canonicalCostOwner'] == 'WBS-P006-02'
    assert not modified[0]['originalLogicalRowModified'] and not modified[0]['oldDynamicResultsTransferred']
    assert not joined['wholeWbsAuditBefore']['passed'] and joined['wholeWbsAuditBefore']['actualExit'] == 1
    negatives = []
    for label,editinv,editsnap in [
        ('old-pointer',None,lambda v:v.update(inventorySha256=old_snap['inventorySha256'])),
        ('source-promoted',None,lambda v:v.update(source=SOURCE)),
        ('effort-invented',None,lambda v:v.update(wholeEffortCompletionRate=50)),
        ('old-owner-mutated',lambda v:v['artifacts'][0].update(owner='WBS-G13.07'),None),
        ('old-candidate-promoted',lambda v:v['currentPhysicalCandidate'].update(source=SOURCE),None)]:
        a = copy.deepcopy(inv)
        b = copy.deepcopy(snap)
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
            raise AssertionError('unapproved semantics accepted')
    for name in ('481_PGPT詳細WBS.json','484_WBSコスト枠・細分化.json'):
        path = PMO / name
        assert path.read_bytes() == subprocess.check_output(['git','show',BEFORE + ':' + str(path.relative_to(ROOT))],cwd=ROOT)
    command = [sys.executable,'-B',str(ROOT / 'tools/quality/wbs_progress_audit.py')]
    result = subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False,timeout=60)
    assert result.returncode == 1 and not result.stdout
    error = result.stderr.decode().splitlines()[-1]
    assert error == 'ValueError: current physical candidate exact Git/worktree scope'
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        joinManifestSha256=data.sha(joinpath.read_bytes()),inventorySha256=data.sha(invraw),snapshotSha256=data.sha(snapraw),
        sourceRows=959,registered=1784,javaPaths=1792,unregistered=8,main=measured['main'],test=measured['test'],
        old958AllFieldsPreserved=True,metadataCounterexamples=negatives,original941Historical943BudgetAcceptancePreserved=True,
        wholeWbsAudit=dict(command=command,actualExit=result.returncode,lastError=error,passed=False),
        productTestsExecuted=0,newTestIds=0,newAccepted=0,formalUpdated=False,effortPercent=None,coverage=None))
    print(json.dumps(dict(actualExit=0,registered=1784,javaPaths=1792,wholeWbsAuditExit=result.returncode,
        manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
