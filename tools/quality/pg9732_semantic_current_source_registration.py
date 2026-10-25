"""Add one explicitly reviewed Test responsibility, keep historical source and qualification separate."""
import copy
import datetime as dt
import json
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
import pg9702_semantic_fixed_quality_source_post as reviewed
from host_tool_invocation import capture, verify

ROOT = data.ROOT
OUT = data.BASE / 'PG9732-semantic-current-source-registration-v1'
SOURCE = reviewed.SOURCE


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    prior = data.read_checked(data.BASE / 'PG9674-page-current-source-registration-v1/manifest.json',
        '52bb8cb2514dc0308543de65af37f0261e546aca840e50ec0c4a00d179aeece5')
    proof_path = reviewed.BASE / 'PG9702-semantic-fixed-quality-source-post-v1/manifest.json'
    proof = data.read_checked(proof_path, '4b5478aefdf326b64aec579988cf4fd53795b0013715de1fc60d3eaddcc1d749')
    assert proof['source'] == SOURCE and proof['actualExit'] == 0 and proof['actualTestsInCurrentRun'] == 15
    normal = data.read_checked(data.BASE / 'PG9694-semantic-direct-fixed-six-compile-v1/manifest.json',
        '7d2e18f86d2bc9e5c61473da8b8924aa7c6668bf8903541d5502902d2dac1d7a')
    assert normal['source'] == SOURCE and normal['actualExit'] == 0 and normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)
    assert all(data.sha((ROOT / p).read_bytes()) == h for p,h in hashes.items())
    inventory = data.read_checked(ROOT / 'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json',
        'ab329a7e851f66d9f32dc40826da481e3c7f1438b28724c67ab46d48b71977f2')
    logical = {r['path']:r for r in inventory['artifacts']}
    assert len(logical) == 941 and reviewed.TEST not in logical
    old = copy.deepcopy(prior['sourceRows'])
    assert len(old) == 957 and reviewed.TEST not in {r['path'] for r in old}
    assert all(hashes[r['path']] == r['sha256'] for r in old)
    row = dict(path=reviewed.TEST,sha256=hashes[reviewed.TEST],owner='WBS-P002-02',
        canonicalOwner='WBS-P002-02',canonicalCostOwner='WBS-P002-02',changeOwner='WBS-G13.07',
        basis='EXPLICIT_SEM001_003_PROGRAM002_011_AND_ORIGINAL_MAIN_OWNER_9702',
        ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',legacyReportedOwner=None,
        legacyTraceOwnerMeaning='ENGINEERING_CHANGE_GROUP_NOT_CANONICAL_ARTIFACT_OWNER',
        actualAllocatedPp=None,additionalSharedCostPp=0,currentSourcePtQualificationInferred=False,
        historicalCostsReallocated=False,historicalRunReassigned=False,
        referenceRelatedOwners=[],runtimeUncertainty=[],
        independentSpec='evidence/01_PT/002_NK-PRO-002/011_Semantic未網羅条件_単体テスト仕様書.md',
        methodTestIds=proof['methods'],ownerProofManifest=str(proof_path.relative_to(ROOT)),
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
    assert len(universe) == 1791 and len(main) == 965 and len(tests) == 826 and len(registered) == 1783
    assert unresolved == prior_unresolved and len(unresolved) == 8
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json',dict(actualExit=0,source=SOURCE,previousSource=prior['source'],
        timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
        sourceRows=rows,sourceCount=len(rows),registered=len(registered),javaPaths=len(universe),
        registeredMain=len(registered & main),totalMain=len(main),registeredTest=len(registered & tests),totalTest=len(tests),
        unregisteredJavaPaths=unresolved,unregisteredTest=len(unresolved),old957AllFieldsPreserved=True,
        old941LogicalAndHistorical943Unchanged=True,newSourceOwnerCandidates=1,
        independentPostManifest=str(proof_path.relative_to(ROOT)),independentPostSha256=data.sha(proof_path.read_bytes()),
        normalManifestSha256='7d2e18f86d2bc9e5c61473da8b8924aa7c6668bf8903541d5502902d2dac1d7a',
        metadataCounterexamples=rejected,productTestsExecuted=0,newTestIds=0,newMain=0,newAccepted=0,
        formalUpdated=False,wholeG13Accepted=False,whole451Accepted=False,coverage=None,effortPercent=None))
    print(json.dumps(dict(actualExit=0,registered=len(registered),javaPaths=len(universe),unregistered=len(unresolved),
        manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
