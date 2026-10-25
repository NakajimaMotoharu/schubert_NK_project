"""Append one explicit DTO Test owner, retaining the prior registry and all WBS snapshots."""
import copy
import json
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

ROOT = data.ROOT
SOURCE = '8ba82083ec65abc6373b8454576dcbaee7d3e621'
OUT = data.BASE / 'PG9824-cleanup-test-owner-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    prior_sha = '0c9d2e5dc36b66b318e5351ee2e9e2463aab23a20c3cc2cd9917e60ae98af470'
    prior = data.read_checked(data.BASE / 'PG9806-batch-current-source-registration-v1/manifest.json',prior_sha)
    proof_sha = 'c81ac2d6af515934be47f6e9fb12ea34fc7355c6beeeb17b6998cd387bb240c0'
    proof = data.read_checked(data.BASE / 'PG9822-cleanup-quality-post-v1/manifest.json',proof_sha)
    normal = data.read_checked(data.BASE / 'PG9812-cleanup-values-six-compile-v1/manifest.json',
        'e074d972cbaf56b94ba4d25a77e7368b4f53ccd91489be0fbc27f07ef3975c95')
    assert prior['actualExit'] == proof['actualExit'] == normal['actualExit'] == 0 and proof['source'] == normal['source'] == SOURCE
    hashes = normal['begin']['inputHashes']
    invpath = ROOT / 'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json'
    snappath = ROOT / 'documents/400_PGPT/470_PMO/486_WBS現行実績.json'
    original_hashes = {str(p.relative_to(ROOT)):data.sha(p.read_bytes()) for p in (invpath,snappath)}
    logical = {r['path']:r for r in json.loads(invpath.read_bytes())['artifacts']}
    assert len(logical) == 941
    old = copy.deepcopy(prior['sourceRows'])
    assert len(old) == 961 and all(hashes[r['path']] == r['sha256'] for r in old)
    path,source_hash = next(iter(proof['changedSourceHashes'].items()))
    assert path not in logical and path not in {r['path'] for r in old}
    mains = ['src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/' + p for p in (
        'repository/CleanupReason.java','repository/CleanupChunk.java','repository/LogCleanupProgress.java','cleanup/LogCleanupSummary.java')]
    assert all(logical[p]['owner'] == logical[p]['costOwner'] == 'WBS-P017-07' for p in mains)
    addition = dict(path=path,sha256=source_hash,owner='WBS-P017-07',canonicalOwner='WBS-P017-07',canonicalCostOwner='WBS-P017-07',
        changeOwner='WBS-P017-07.01',basis='EXPLICIT_1981_FOUR_LOG_CLEANUP_VALUE_MAIN_CONTRACTS_AND_9822',
        ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',legacyReportedOwner=None,
        actualAllocatedPp=None,additionalSharedCostPp=0,currentSourcePtQualificationInferred=False,
        historicalCostsReallocated=False,historicalRunReassigned=False,referenceRelatedOwners=[],runtimeUncertainty=[],
        independentSpec='evidence/01_PT/018_NK-OPS-001/1981_LogCleanup値契約_独立単体テスト仕様書.md',
        methodTestIds=proof['newTestIds'],mainSourceSubjects=mains,ownerProofSha256=proof_sha)
    rows = old + [addition]
    assert len(rows) == len({r['path'] for r in rows}) == 962 and rows[:-1] == prior['sourceRows']
    universe = {p for p in hashes if p.endswith('.java') and '/java/' in p}
    registered = universe & (set(logical) | {r['path'] for r in rows})
    unresolved = sorted(universe - registered)
    assert len(universe) == 1795 and len(registered) == 1787 and unresolved == prior['unregisteredJavaPaths'] and len(unresolved) == 8
    assert all(data.sha((ROOT / p).read_bytes()) == h for p,h in hashes.items())
    assert all(data.sha((ROOT / p).read_bytes()) == h for p,h in original_hashes.items())
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,previousSource=prior['source'],
        priorRegistrySha256=prior_sha,sourceRows=rows,sourceCount=962,registered=1787,javaPaths=1795,
        registeredMain=965,totalMain=965,registeredTest=822,totalTest=830,unregisteredJavaPaths=unresolved,
        currentModifiedLogicalBindings=prior['currentModifiedLogicalBindings'],old961AllFieldsPreserved=True,
        independentPostSha256=proof_sha,wbsMetadataHashesUnchanged=original_hashes,
        canonicalWbsMetadataStillHistoricalSource=prior['source'],wholeWbsAuditNotReplayed=True,
        wholeWbsAuditHoldNotLifted=True,metadataUpdateDeferredNotQualified=True,productTestsExecuted=0,
        newTestIds=0,newAccepted=0,formalUpdated=False,wholeG13Accepted=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,registered=1787,javaPaths=1795,unregistered=8,
        manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
