"""Independent exact Test responsibility and changed logical Main binding; no product rerun."""
import copy
import json
from pathlib import Path
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

ROOT = data.ROOT
BASE = data.BASE
SOURCE = '21d7c30425e7aa9ce435e808035a94fa4d75c93b'
OUT = BASE/'PG9882-snapshot-nonce-trace-post-v1'
MAIN = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec.java'
TEST = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/idempotency/ResponseSnapshotNonceFailureTest.java'


def validate(joined, prior, hashes, logical):
    rows = joined['sourceRows']
    if rows[:-1] != prior['sourceRows'] or len(rows) != len({r['path'] for r in rows}) or len(rows) != 969:
        raise ValueError('exact old968 plusone, full prior fields preserved')
    row = rows[-1]
    if row['path'] != TEST or row['sha256'] != hashes[TEST]:
        raise ValueError('exact new source path/hash')
    if any(row[k] != 'WBS-P006-01' for k in ('owner','canonicalOwner','canonicalCostOwner')) or row['changeOwner'] != 'WBS-G13.07':
        raise ValueError('canonical/cost are original Main owner, not change owner')
    if row['ownershipStatus'] != 'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED' or row['actualAllocatedPp'] is not None or row['additionalSharedCostPp'] != 0:
        raise ValueError('candidate only, no invented cost or acceptance')
    if any(row[k] for k in ('historicalCostsReallocated','historicalRunReassigned','currentSourcePtQualificationInferred')):
        raise ValueError('no historic success/cost reassignment')
    bindings = joined['currentModifiedLogicalBindings']
    if bindings[:-1] != prior['currentModifiedLogicalBindings'] or len(bindings) != 2:
        raise ValueError('prior Outbox current binding preserved')
    current = bindings[-1]
    if current['path'] != MAIN or current['sha256'] != hashes[MAIN] or current['originalLogicalSha256'] != logical[MAIN]['sha256']:
        raise ValueError('current and original logical hash are separate')
    if current['canonicalOwner'] != current['canonicalCostOwner'] or current['canonicalOwner'] != logical[MAIN]['owner']:
        raise ValueError('original Main/cost owner preserved')
    if current['originalLogicalRowModified'] or current['oldDynamicResultsTransferred']:
        raise ValueError('no old snapshot or success mutation')
    universe = {p for p in hashes if p.endswith('.java') and '/java/' in p}
    registered = universe & (set(logical) | {r['path'] for r in rows})
    if len(universe) != 1796 or len(registered) != 1794 or sorted(universe-registered) != prior['unregisteredJavaPaths']:
        raise ValueError('full exact denominator, two UNKNOWN retained')
    if joined['unregisteredJavaPaths'] != prior['unregisteredJavaPaths'] or joined['registered'] != 1794:
        raise ValueError('unknown not erased in report')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    joined_sha = 'dd8c2590f9962bdcaa9f37c4f3ebf67c2940af14829b2b365ca8073b2ae15012'
    joined = data.read_checked(BASE/'PG9880-snapshot-nonce-trace-v1/manifest.json',joined_sha)
    prior = data.read_checked(BASE/'PG9834-shared-probe-owner-v1/manifest.json',joined['priorRegistrySha256'])
    normal = data.read_checked(BASE/'PG9866-snapshot-nonce-six-compile-v1/manifest.json',joined['normalManifestSha256'])
    assert joined['actualExit'] == normal['actualExit'] == 0 and joined['source'] == normal['source'] == SOURCE
    invpath = ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json'
    logical = {r['path']:r for r in json.loads(invpath.read_bytes())['artifacts']}
    hashes = normal['begin']['inputHashes']
    validate(joined,prior,hashes,logical)
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in {**hashes,**joined['wbsMetadataHashesUnchanged']}.items())
    body = (ROOT/TEST).read_text()
    methods = re.findall(r'@Test\s+void\s+(\w+)\s*\(\)',body)
    assert methods == ['rngscope001RuntimeFailureClearsOwnedNonceAndPreservesIdentity','rngscope002ErrorClearsOwnedNonceAndPreservesIdentity']
    assert 'new ResponseSnapshotCodec(' in body and 'ResponseSnapshotIdentity.authenticated(' in body
    assert joined['sourceRows'][-1]['mainSourceSubjects'] == [MAIN,MAIN.replace('ResponseSnapshotCodec.java','ResponseSnapshotIdentity.java')]
    assert all(logical[p]['owner'] == logical[p]['costOwner'] == 'WBS-P006-01' for p in joined['sourceRows'][-1]['mainSourceSubjects'])
    proof = data.read_checked(BASE/'PG9876-snapshot-nonce-quality-source-post-v1/manifest.json',joined['independentPostSha256'])
    assert proof['actualExit'] == 0 and proof['source'] == SOURCE and proof['selectedTests'] == 9 and proof['targetUnitFour100']
    audit = joined['wholeWbsAuditBefore']
    assert audit['actualExit'] == 1 and not audit['passed'] and audit['lastError'] == 'ValueError: current physical candidate exact Git/worktree scope'
    guards = {}
    for path in ('tools/quality/wbs_progress_audit.py','tools/quality/wbs_candidate_trace.py','tools/quality/wbs_component_overlay.py'):
        raw = (ROOT/path).read_bytes()
        assert raw == subprocess.check_output(['git','show','aba4a202b:'+path],cwd=ROOT)
        guards[path] = data.sha(raw)
    negatives = []
    for label,edit in (
        ('owner',lambda j:j['sourceRows'][-1].update(canonicalOwner='WBS-G13.07')),
        ('cost',lambda j:j['sourceRows'][-1].update(canonicalCostOwner='WBS-G03')),
        ('old-row-mutated',lambda j:j['sourceRows'][0].update(sha256='0'*64)),
        ('new-source-hash',lambda j:j['sourceRows'][-1].update(sha256='0'*64)),
        ('missing-row',lambda j:j['sourceRows'].pop()),
        ('duplicate-row',lambda j:j['sourceRows'].append(copy.deepcopy(j['sourceRows'][-1]))),
        ('old-binding-removed',lambda j:j['currentModifiedLogicalBindings'].pop(0)),
        ('original-rebound',lambda j:j['currentModifiedLogicalBindings'][-1].update(originalLogicalSha256=j['currentModifiedLogicalBindings'][-1]['sha256'])),
        ('unknown-erased',lambda j:j.update(registered=1796,unregisteredJavaPaths=[])),
        ('accepted',lambda j:j['sourceRows'][-1].update(ownershipStatus='ACCEPTED'))):
        changed = copy.deepcopy(joined)
        edit(changed)
        try:
            validate(changed,prior,hashes,logical)
        except ValueError:
            negatives.append(label)
        else:
            raise AssertionError('invalid responsibility accepted: '+label)
    assert len(negatives) == 10
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=joined_sha,
        registryPath='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9880-snapshot-nonce-trace-v1/manifest.json',
        sourceRows=969,newCandidates=1,registered=1794,javaPaths=1796,unregistered=2,
        main=dict(total=965,registered=965,unregistered=0),test=dict(total=831,registered=829,unregistered=2),
        modifiedLogicalBindings=joined['currentModifiedLogicalBindings'],old968AllFieldsPreserved=True,
        canonicalOwner='WBS-P006-01',canonicalCostOwner='WBS-P006-01',metadataNegativeVectors=negatives,
        wholeWbsAuditBefore=audit,originalCurrentAuditReusedNoReplay=True,auditSourceHashes=guards,
        wbsMetadataBeforeHashes=joined['wbsMetadataHashesUnchanged'],productTestsExecuted=0,actualExternalOperations=0,
        newAccepted=0,formalUpdated=False,wholeG13Accepted=False,whole451Accepted=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,registered=1794,javaPaths=1796,unknown=2,metadataNegatives=10,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
