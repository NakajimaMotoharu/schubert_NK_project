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
OUT = data.BASE / 'PG9734-semantic-current-snapshot-post-v1'
BEFORE = 'ccd741fe4cd3317d4821dc1c657b749382cfe077'
SOURCE = 'fd3d04df5710ca28f0e34f919cbc103e569a607b'


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
    joinpath = data.BASE / 'PG9732-semantic-current-source-registration-v1/manifest.json'
    joined = data.read_checked(joinpath,'109b6ab29e88c75e0743feb627f462e19fb4955a119883b14fe12c435103779a')
    prior = data.read_checked(data.BASE / 'PG9674-page-current-source-registration-v1/manifest.json',
        '52bb8cb2514dc0308543de65af37f0261e546aca840e50ec0c4a00d179aeece5')
    normal = data.read_checked(data.BASE / 'PG9694-semantic-direct-fixed-six-compile-v1/manifest.json',
        '7d2e18f86d2bc9e5c61473da8b8924aa7c6668bf8903541d5502902d2dac1d7a')
    assert joined['actualExit'] == normal['actualExit'] == 0 and joined['source'] == normal['source'] == SOURCE
    rows = joined['sourceRows']
    assert rows[:-1] == prior['sourceRows'] and len(rows) == len({r['path'] for r in rows}) == 958
    added = rows[-1]
    assert added['path'].endswith('/layout/SemanticDirectBoundaryTest.java')
    assert added['owner'] == added['canonicalOwner'] == added['canonicalCostOwner'] == 'WBS-P002-02'
    assert added['ownershipStatus'] == 'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED'
    assert added['currentSourcePtQualificationInferred'] is False
    hashes = normal['begin']['inputHashes']
    universe = {p for p in hashes if p.endswith('.java') and '/java/' in p}
    registered = universe & ({r['path'] for r in inv['artifacts']} | {r['path'] for r in rows})
    tests = {p for p in universe if '/src/test/java/' in p}
    assert len(universe) == 1791 and len(registered) == 1783 and len(tests) == 826 and len(registered & tests) == 818
    assert sorted(universe - registered) == joined['unregisteredJavaPaths']
    current = inv['currentIncrementalHostOwnership']
    measured = inv['currentJavaPathExplicitRegistryMeasurement']
    for value in (current,measured):
        assert value['source'] == SOURCE and value['manifest'] == str(joinpath.relative_to(ROOT))
        assert value['sha256'] == data.sha(joinpath.read_bytes())
        assert value['previousSemanticBoundarySourceOverlay']['source'] == prior['source']
        assert value['previousSemanticBoundarySourceOverlay']['sha256'] == '52bb8cb2514dc0308543de65af37f0261e546aca840e50ec0c4a00d179aeece5'
    assert current['sourceRows'] == 958 and current['newLogicalCandidates'] == 950
    assert current['legacyOwnerLabelsDifferingFromCanonical'] == sum(r['legacyReportedOwner'] != r['canonicalOwner'] for r in rows)
    assert measured['javaPaths'] == 1791 and measured['registered'] == 1783 and measured['unregistered'] == 8
    assert measured['main'] == dict(total=965,registered=965,unregistered=0)
    assert measured['test'] == dict(total=826,registered=818,unregistered=8)
    proof_path = ROOT / current['guardManifest']
    assert proof_path == ROOT / measured['independentPostManifest']
    proof = data.read_checked(proof_path,current['guardSha256'])
    assert current['guardSha256'] == measured['independentPostSha256'] == '4b5478aefdf326b64aec579988cf4fd53795b0013715de1fc60d3eaddcc1d749'
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
        sourceRows=958,registered=1783,javaPaths=1791,unregistered=8,main=measured['main'],test=measured['test'],
        old957AllFieldsPreserved=True,metadataCounterexamples=negatives,original941Historical943BudgetAcceptancePreserved=True,
        wholeWbsAudit=dict(command=command,actualExit=result.returncode,lastError=error,passed=False),
        productTestsExecuted=0,newTestIds=0,newAccepted=0,formalUpdated=False,effortPercent=None,coverage=None))
    print(json.dumps(dict(actualExit=0,registered=1783,javaPaths=1791,wholeWbsAuditExit=result.returncode,
        manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
