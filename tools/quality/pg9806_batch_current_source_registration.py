"""Register two reviewed pure batch Test owners; preserve all historical mappings and results."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import g07_host_class_provenance_inputs as data
import pg9802_batch_boundary_quality_post as reviewed
from host_tool_invocation import capture, verify

ROOT = data.ROOT
SOURCE = reviewed.SOURCE
OUT = data.BASE / 'PG9806-batch-current-source-registration-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    prior = data.read_checked(data.BASE / 'PG9766-outbox-current-source-registration-v1/manifest.json',
        '180c761500bf3e7fc08326f26fcea2b020dd398bdaa4231b55bef4c20a1f5815')
    proof_path = data.BASE / 'PG9802-batch-boundary-quality-post-v1/manifest.json'
    proof_sha = '4578485d372283f2ad70a3a8b7a654d30d94c15a8e8443773e3fb3517435a883'
    proof = data.read_checked(proof_path,proof_sha)
    normal = data.read_checked(data.BASE / 'PG9792-batch-boundary-six-compile-v1/manifest.json',
        'aadb6fcfee66e10f1e6357493ac5c15d60babe72570dc506b87e522f9a238a86')
    assert proof['actualExit'] == normal['actualExit'] == 0 and proof['source'] == normal['source'] == SOURCE
    assert proof['actualSelectedTests'] == 20 and normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT / p).read_bytes()) == h for p,h in hashes.items())
    assert not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)
    inventory = data.read_checked(ROOT / 'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json',
        '354838e6c7d059f54385b05646d63d3929897895cdf95e8b1326e1cee60cf4f9')
    logical = {r['path']:r for r in inventory['artifacts']}
    assert len(logical) == 941
    old = copy.deepcopy(prior['sourceRows'])
    assert len(old) == 959 and all(hashes[r['path']] == r['sha256'] for r in old)
    subject_paths = {
        'BatchRunValueBoundaryTest':['BatchRun','MaintenanceActivation'],
        'CleanupValueBoundaryTest':['CleanupCounts','CleanupKind']}
    added = []
    for simple,(owner,methods) in reviewed.NEW.items():
        path = reviewed.PREFIX + simple + '.java'
        assert path not in logical and path not in {r['path'] for r in old}
        mains = ['src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/' + n + '.java' for n in subject_paths[simple]]
        assert all(logical[p]['owner'] == logical[p]['costOwner'] == owner for p in mains)
        added.append(dict(path=path,sha256=hashes[path],owner=owner,canonicalOwner=owner,canonicalCostOwner=owner,
            changeOwner='WBS-G13.07',basis='EXPLICIT_1978_RUNVALUE_CLEANVALUE_METHODS_AND_ORIGINAL_MAIN_PARENTS_9802',
            ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',legacyReportedOwner=None,
            legacyTraceOwnerMeaning='ENGINEERING_CHANGE_GROUP_NOT_CANONICAL_ARTIFACT_OWNER',
            actualAllocatedPp=None,additionalSharedCostPp=0,currentSourcePtQualificationInferred=False,
            historicalCostsReallocated=False,historicalRunReassigned=False,referenceRelatedOwners=[],runtimeUncertainty=[],
            independentSpec='evidence/01_PT/018_NK-OPS-001/1978_Batch値型16_途中結果・追加4仕様.md',
            methodTestIds=methods,mainSourceSubjects=mains,ownerProofManifest=str(proof_path.relative_to(ROOT)),ownerProofSha256=proof_sha))
    rows = old + added
    def valid(value):
        return value == old + added and len(value) == len({r['path'] for r in value})
    negatives = []
    for label,key,value in [('owner','canonicalOwner','WBS-G13.07'),('cost','canonicalCostOwner','WBS-G13.07'),
        ('hash','sha256','0'*64),('accepted','ownershipStatus','ACCEPTED')]:
        for index in range(len(added)):
            modified = copy.deepcopy(rows)
            modified[len(old) + index][key] = value
            assert not valid(modified)
        negatives.append(label)
    assert not valid(rows[:-1]) and not valid(rows + [added[0]])
    negatives += ['missing','duplicate']
    universe = {p for p in hashes if p.endswith('.java') and '/java/' in p}
    mains = {p for p in universe if '/src/main/java/' in p}
    tests = universe - mains
    registered = universe & (set(logical) | {r['path'] for r in rows})
    unresolved = sorted(universe - registered)
    assert len(universe) == 1794 and len(mains) == 965 and len(tests) == 829 and len(registered) == 1786
    assert unresolved == prior['unregisteredJavaPaths'] and len(unresolved) == 8
    modified_logical = copy.deepcopy(prior['currentModifiedLogicalBindings'])
    assert len(modified_logical) == 1 and all(hashes[r['path']] == r['sha256'] for r in modified_logical)
    command = [sys.executable,'-B',str(ROOT / 'tools/quality/wbs_progress_audit.py')]
    audit = subprocess.run(command,cwd=ROOT,capture_output=True,timeout=60,check=False)
    error = audit.stderr.decode().splitlines()[-1]
    assert audit.returncode == 1 and not audit.stdout and error == 'ValueError: current physical candidate exact Git/worktree scope'
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json',dict(actualExit=0,source=SOURCE,previousSource=prior['source'],invocation=invocation,
        sourceRows=rows,sourceCount=len(rows),registered=len(registered),javaPaths=len(universe),
        registeredMain=len(registered & mains),totalMain=len(mains),registeredTest=len(registered & tests),totalTest=len(tests),
        unregisteredJavaPaths=unresolved,unregisteredTest=len(unresolved),old959AllFieldsPreserved=True,
        old941LogicalAndHistorical943Unchanged=True,newSourceOwnerCandidates=2,currentModifiedLogicalBindings=modified_logical,
        currentModifiedLogicalBindingPreservedWithoutSourcePromotion=True,metadataCounterexamples=negatives,
        independentPostManifest=str(proof_path.relative_to(ROOT)),independentPostSha256=proof_sha,
        normalManifestSha256='aadb6fcfee66e10f1e6357493ac5c15d60babe72570dc506b87e522f9a238a86',
        wholeWbsAuditBefore=dict(command=command,actualExit=audit.returncode,lastError=error,passed=False),
        productTestsExecuted=0,newTestIds=0,newMain=0,newAccepted=0,formalUpdated=False,wholeG13Accepted=False,
        whole451Accepted=False,coverage=None,effortPercent=None))
    print(json.dumps(dict(actualExit=0,registered=1786,javaPaths=1794,unregistered=8,
        manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
