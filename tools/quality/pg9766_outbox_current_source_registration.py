"""Add one explicitly reviewed Test responsibility, keep historical source and qualification separate."""
import copy
import datetime as dt
import json
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
import pg9762_outbox_quality_source_post as reviewed
import sys
from host_tool_invocation import capture, verify

ROOT = data.ROOT
OUT = data.BASE / 'PG9766-outbox-current-source-registration-v1'
SOURCE = reviewed.SOURCE


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    prior = data.read_checked(data.BASE / 'PG9732-semantic-current-source-registration-v1/manifest.json',
        '109b6ab29e88c75e0743feb627f462e19fb4955a119883b14fe12c435103779a')
    proof_path = data.BASE / 'PG9762-outbox-quality-source-post-v1/manifest.json'
    proof = data.read_checked(proof_path, '8b9963b22aac0b2d9dc1241c35cc07537980cd670a616854ca46a8c2cb0dc6c9')
    assert proof['source'] == SOURCE and proof['actualExit'] == 0 and proof['actualSelectedTests'] == 13
    normal = data.read_checked(data.BASE / 'PG9750-outbox-report-six-compile-v1/manifest.json',
        '7b1c2b2e67dab622cc3e905e1c04ac5819a587f90992c404cf6cab3f0ceebb96')
    assert normal['source'] == SOURCE and normal['actualExit'] == 0 and normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)
    assert all(data.sha((ROOT / p).read_bytes()) == h for p,h in hashes.items())
    inventory = data.read_checked(ROOT / 'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json',
        '2db77dcc547729899f4e9b969ed56367b7b8f33f93112fb6bc3083cb0a378a83')
    logical = {r['path']:r for r in inventory['artifacts']}
    assert len(logical) == 941 and reviewed.TEST not in logical
    old = copy.deepcopy(prior['sourceRows'])
    assert len(old) == 958 and reviewed.TEST not in {r['path'] for r in old}
    assert all(hashes[r['path']] == r['sha256'] for r in old)
    row = dict(path=reviewed.TEST,sha256=hashes[reviewed.TEST],owner='WBS-P006-02',
        canonicalOwner='WBS-P006-02',canonicalCostOwner='WBS-P006-02',changeOwner='WBS-G13.07',
        basis='EXPLICIT_OVF001_003_1971_1972_ORIGINAL_MAIN_P00602_9762',
        ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',legacyReportedOwner=None,
        legacyTraceOwnerMeaning='ENGINEERING_CHANGE_GROUP_NOT_CANONICAL_ARTIFACT_OWNER',
        actualAllocatedPp=None,additionalSharedCostPp=0,currentSourcePtQualificationInferred=False,
        historicalCostsReallocated=False,historicalRunReassigned=False,
        referenceRelatedOwners=[],runtimeUncertainty=[],
        independentSpec='evidence/01_PT/018_NK-OPS-001/1971_API_Outbox値型・集計overflow_単体テスト仕様書.md',
        methodTestIds=['PT-IDEM-REPORT-OVF001','PT-IDEM-REPORT-OVF002','PT-IDEM-REPORT-OVF003'],ownerProofManifest=str(proof_path.relative_to(ROOT)),
        ownerProofSha256=data.sha(proof_path.read_bytes()))
    rows = old + [row]
    def valid(value):
        return value == old + [row] and len({r['path'] for r in value}) == len(value)
    rejected = []
    for label,key,value in [('owner','canonicalOwner','WBS-G13.07'),('cost','canonicalCostOwner','WBS-G13.07'),
            ('hash','sha256','0'*64),('accepted','ownershipStatus','ACCEPTED')]:
        altered = copy.deepcopy(rows)
        altered[-1][key] = value
        assert not valid(altered)
        rejected.append(label)
    assert not valid(rows[:-1]) and not valid(rows + [row])
    rejected += ['missing','duplicate']
    universe = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    main = {p for p in universe if '/src/main/java/' in p}
    tests = universe - main
    registered = universe & (set(logical) | {r['path'] for r in rows})
    unresolved = sorted(universe - registered)
    prior_unresolved = prior['unregisteredJavaPaths']
    assert len(universe) == 1792 and len(main) == 965 and len(tests) == 827 and len(registered) == 1784
    assert unresolved == prior_unresolved and len(unresolved) == 8
    original_main = logical[reviewed.MAIN]
    assert original_main['owner'] == original_main['costOwner'] == 'WBS-P006-02'
    modified_main_binding = dict(path=reviewed.MAIN,sha256=hashes[reviewed.MAIN],
        originalLogicalSha256=original_main['sha256'],canonicalOwner=original_main['owner'],
        canonicalCostOwner=original_main['costOwner'],originalLogicalRowModified=False,
        proofManifest=str(proof_path.relative_to(ROOT)),proofSha256=data.sha(proof_path.read_bytes()),
        oldDynamicResultsTransferred=False)
    command = [sys.executable,'-B',str(ROOT / 'tools/quality/wbs_progress_audit.py')]
    audit = subprocess.run(command,cwd=ROOT,capture_output=True,timeout=60,check=False)
    error = audit.stderr.decode().splitlines()[-1]
    assert audit.returncode == 1 and not audit.stdout and error == 'ValueError: current physical candidate exact Git/worktree scope'
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json',dict(actualExit=0,source=SOURCE,previousSource=prior['source'],
        timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
        sourceRows=rows,sourceCount=len(rows),registered=len(registered),javaPaths=len(universe),
        registeredMain=len(registered & main),totalMain=len(main),registeredTest=len(registered & tests),totalTest=len(tests),
        unregisteredJavaPaths=unresolved,unregisteredTest=len(unresolved),old958AllFieldsPreserved=True,currentModifiedLogicalBindings=[modified_main_binding],
        wholeWbsAuditBefore=dict(command=command,actualExit=audit.returncode,lastError=error,passed=False),
        old941LogicalAndHistorical943Unchanged=True,newSourceOwnerCandidates=1,
        independentPostManifest=str(proof_path.relative_to(ROOT)),independentPostSha256=data.sha(proof_path.read_bytes()),
        normalManifestSha256='7b1c2b2e67dab622cc3e905e1c04ac5819a587f90992c404cf6cab3f0ceebb96',
        metadataCounterexamples=rejected,productTestsExecuted=0,newTestIds=0,newMain=0,newAccepted=0,
        formalUpdated=False,wholeG13Accepted=False,whole451Accepted=False,coverage=None,effortPercent=None))
    print(json.dumps(dict(actualExit=0,registered=len(registered),javaPaths=len(universe),unregistered=len(unresolved),
        manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
