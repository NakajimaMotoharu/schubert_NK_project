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
OUT = data.BASE / 'PG9676-page-current-snapshot-post-v1'
BEFORE = '2bd5c2e237d8a6ebe0a77e0b1e72b608ae8c231e'
SOURCE = '3154be39380de4771111f859ffb8315420274b0a'


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
    joinpath = data.BASE / 'PG9674-page-current-source-registration-v1/manifest.json'
    joined = data.read_checked(joinpath,'52bb8cb2514dc0308543de65af37f0261e546aca840e50ec0c4a00d179aeece5')
    prior = data.read_checked(data.BASE / 'PG9546-shared-fixture7-source-join-v1/manifest.json',
        '4d82743eb894ccd448a2ef88b40f566bc0fb08a8ee4b5128a925e49c08b7dd61')
    normal = data.read_checked(data.BASE / 'PG9660-pagination-six-compile-v1/manifest.json',
        'f2ae182bb3a88eff78542ce0c18f3a497263aaabb7ed7fdbea5237a9ab467c2c')
    assert joined['actualExit'] == normal['actualExit'] == 0 and joined['source'] == normal['source'] == SOURCE
    rows = joined['sourceRows']
    assert rows[:-1] == prior['sourceRows'] and len(rows) == len({r['path'] for r in rows}) == 957
    added = rows[-1]
    assert added['path'].endswith('/layout/PayloadPaginationBoundaryTest.java')
    assert added['owner'] == added['canonicalOwner'] == added['canonicalCostOwner'] == 'WBS-P002-02'
    assert added['ownershipStatus'] == 'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED'
    assert added['currentSourcePtQualificationInferred'] is False
    hashes = normal['begin']['inputHashes']
    universe = {p for p in hashes if p.endswith('.java') and '/java/' in p}
    registered = universe & ({r['path'] for r in inv['artifacts']} | {r['path'] for r in rows})
    tests = {p for p in universe if '/src/test/java/' in p}
    assert len(universe) == 1790 and len(registered) == 1782 and len(tests) == 825 and len(registered & tests) == 817
    assert sorted(universe - registered) == joined['unregisteredJavaPaths']
    current = inv['currentIncrementalHostOwnership']
    measured = inv['currentJavaPathExplicitRegistryMeasurement']
    for value in (current,measured):
        assert value['source'] == SOURCE and value['manifest'] == str(joinpath.relative_to(ROOT))
        assert value['sha256'] == data.sha(joinpath.read_bytes())
        assert value['previousPageBoundarySourceOverlay']['source'] == prior['source']
        assert value['previousPageBoundarySourceOverlay']['sha256'] == '4d82743eb894ccd448a2ef88b40f566bc0fb08a8ee4b5128a925e49c08b7dd61'
    assert current['sourceRows'] == 957 and current['newLogicalCandidates'] == 949
    assert current['legacyOwnerLabelsDifferingFromCanonical'] == sum(r['legacyReportedOwner'] != r['canonicalOwner'] for r in rows)
    assert measured['javaPaths'] == 1790 and measured['registered'] == 1782 and measured['unregistered'] == 8
    assert measured['main'] == dict(total=965,registered=965,unregistered=0)
    assert measured['test'] == dict(total=825,registered=817,unregistered=8)
    proof_path = ROOT / current['guardManifest']
    assert proof_path == ROOT / measured['independentPostManifest']
    proof = data.read_checked(proof_path,current['guardSha256'])
    assert current['guardSha256'] == measured['independentPostSha256'] == '9db0e573444f6fd72649fd68efcddfe8e6d15eedb1e0d2069efbb9d7525bd445'
    assert proof['actualExit'] == 0 and proof['source'] == SOURCE
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
        sourceRows=957,registered=1782,javaPaths=1790,unregistered=8,main=measured['main'],test=measured['test'],
        old956AllFieldsPreserved=True,metadataCounterexamples=negatives,original941Historical943BudgetAcceptancePreserved=True,
        wholeWbsAudit=dict(command=command,actualExit=result.returncode,lastError=error,passed=False),
        productTestsExecuted=0,newTestIds=0,newAccepted=0,formalUpdated=False,effortPercent=None,coverage=None))
    print(json.dumps(dict(actualExit=0,registered=1782,javaPaths=1790,wholeWbsAuditExit=result.returncode,
        manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
