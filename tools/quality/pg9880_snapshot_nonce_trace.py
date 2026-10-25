"""Add one explicitly reviewed Test and one current Main binding; preserve historical rows and costs."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

ROOT = data.ROOT
BASE = data.BASE
SOURCE = '21d7c30425e7aa9ce435e808035a94fa4d75c93b'
OUT = BASE/'PG9880-snapshot-nonce-trace-v1'
MAIN = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec.java'
TEST = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/idempotency/ResponseSnapshotNonceFailureTest.java'


def audit():
    command = [sys.executable,'-B',str(ROOT/'tools/quality/wbs_progress_audit.py')]
    result = subprocess.run(command,cwd=ROOT,capture_output=True,timeout=60,check=False)
    error = result.stderr.decode().splitlines()[-1] if result.stderr else None
    return dict(command=command,actualExit=result.returncode,passed=result.returncode==0,
        lastError=error,stdoutSha256=data.sha(result.stdout),stderrSha256=data.sha(result.stderr))


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    prior_sha = '0d361ca974427a14e3feab9ae8be3c55b704268da3576bd70cdfa52bd4bcf200'
    prior = data.read_checked(BASE/'PG9834-shared-probe-owner-v1/manifest.json',prior_sha)
    proof_sha = '00eb2fb3eb8d9cb763e7a2a91eb0aa0352eff63ba17725b5f305d75a7e939f48'
    proof_path = BASE/'PG9876-snapshot-nonce-quality-source-post-v1/manifest.json'
    proof = data.read_checked(proof_path,proof_sha)
    normal_sha = '2b00918c64ac9dfc7e9b4d648c93ef8ef0bee293ae1faa65cc280c3dd21ab535'
    normal = data.read_checked(BASE/'PG9866-snapshot-nonce-six-compile-v1/manifest.json',normal_sha)
    assert prior['actualExit'] == proof['actualExit'] == normal['actualExit'] == 0
    assert proof['source'] == normal['source'] == SOURCE and proof['selectedTests'] == 9
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in hashes.items())
    invpath = ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json'
    snappath = ROOT/'documents/400_PGPT/470_PMO/486_WBS現行実績.json'
    original = {str(p.relative_to(ROOT)):data.sha(p.read_bytes()) for p in (invpath,snappath)}
    logical = {r['path']:r for r in json.loads(invpath.read_bytes())['artifacts']}
    old = copy.deepcopy(prior['sourceRows'])
    assert len(logical) == 941 and len(old) == 968 and all(hashes[r['path']] == r['sha256'] for r in old)
    subjects = [MAIN,MAIN.replace('ResponseSnapshotCodec.java','ResponseSnapshotIdentity.java')]
    assert all(logical[p]['owner'] == logical[p]['costOwner'] == 'WBS-P006-01' for p in subjects)
    assert TEST not in logical and TEST not in {r['path'] for r in old}
    row = dict(path=TEST,sha256=hashes[TEST],owner='WBS-P006-01',canonicalOwner='WBS-P006-01',canonicalCostOwner='WBS-P006-01',
        changeOwner='WBS-G13.07',basis='EXPLICIT_1993_RNGSCOPE001_002_AND_CANONICAL_CODEC_IDENTITY_P00601',
        ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',legacyReportedOwner=None,
        actualAllocatedPp=None,additionalSharedCostPp=0,historicalCostsReallocated=False,historicalRunReassigned=False,
        currentSourcePtQualificationInferred=False,referenceRelatedOwners=[],runtimeUncertainty=[],
        independentSpec='evidence/01_PT/018_NK-OPS-001/1993_Snapshot乱数異常時buffer消去_単体テスト仕様書.md',
        methodTestIds=['PT-IDEM-RNGSCOPE001','PT-IDEM-RNGSCOPE002'],mainSourceSubjects=subjects,
        ownerProofManifest=str(proof_path.relative_to(ROOT)),ownerProofSha256=proof_sha)
    rows = old+[row]
    old_binding = copy.deepcopy(prior['currentModifiedLogicalBindings'])
    main_row = logical[MAIN]
    binding = dict(path=MAIN,sha256=hashes[MAIN],originalLogicalSha256=main_row['sha256'],
        canonicalOwner=main_row['owner'],canonicalCostOwner=main_row['costOwner'],originalLogicalRowModified=False,
        proofManifest=str(proof_path.relative_to(ROOT)),proofSha256=proof_sha,oldDynamicResultsTransferred=False)
    bindings = old_binding+[binding]
    universe = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    mains = {p for p in universe if '/src/main/java/' in p}
    tests = universe-mains
    registered = universe & (set(logical) | {r['path'] for r in rows})
    unknown = sorted(universe-registered)
    assert len(rows) == len({r['path'] for r in rows}) == 969 and len(universe) == 1796 and len(registered) == 1794
    assert len(mains) == 965 and len(tests) == 831 and unknown == prior['unregisteredJavaPaths'] and len(unknown) == 2
    assert len(bindings) == 2 and len({r['path'] for r in bindings}) == 2
    negatives = []
    for label,key,value in (('owner','canonicalOwner','WBS-G13.07'),('cost','canonicalCostOwner','WBS-G13.07'),
        ('hash','sha256','0'*64),('acceptance','ownershipStatus','ACCEPTED')):
        changed = copy.deepcopy(rows)
        changed[-1][key] = value
        assert changed != old+[row]
        negatives.append(label)
    assert rows[:-1] == prior['sourceRows'] and bindings[:-1] == prior['currentModifiedLogicalBindings']
    observed_audit = audit()
    assert observed_audit['actualExit'] == 1 and not observed_audit['passed']
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in {**hashes,**original}.items())
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,previousSource=prior['source'],invocation=invocation,
        priorRegistrySha256=prior_sha,normalManifestSha256=normal_sha,independentPostSha256=proof_sha,
        sourceRows=rows,sourceCount=969,registered=1794,javaPaths=1796,registeredMain=965,totalMain=965,
        registeredTest=829,totalTest=831,unregisteredJavaPaths=unknown,currentModifiedLogicalBindings=bindings,
        old968AllFieldsPreserved=True,oldCurrentModifiedLogicalBindingsPreserved=True,sourceOwnerCandidatesAdded=1,
        newLogicalCandidates=sum(r.get('ownershipStatus')=='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED' for r in rows),
        newTestCanonicalOwner='WBS-P006-01',newTestCanonicalCostOwner='WBS-P006-01',metadataCounterexamples=negatives,
        wholeWbsAuditBefore=observed_audit,wbsMetadataHashesUnchanged=original,productTestsExecuted=0,
        newAccepted=0,formalUpdated=False,wholeG13Accepted=False,whole451Accepted=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,registered=1794,javaPaths=1796,unregistered=2,
        wholeAudit=observed_audit['actualExit'],manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
