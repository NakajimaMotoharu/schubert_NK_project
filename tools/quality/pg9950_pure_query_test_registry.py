"""Add one explicitly owned pure Test and refresh two hashes without cost/runtime reassignment."""
import copy
import json
from pathlib import Path
import subprocess

import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9880_snapshot_nonce_trace import audit

ROOT = data.ROOT
SOURCE = '35b059820f010ddca25cba5b6d496a65a99e8887'
OUT = data.BASE/'PG9950-pure-query-test-registry-v1'
PRIOR_SHA = '42899a03f8ddd657805f55c053cfb0f64616356c2ff889a912c8d77505303b0b'
PROOF_SHA = 'a550992985be1edc6712e3b08ceea3f6836a3958fa131f6190c3eda2c88dbd0c'
PREFIX = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/'
NEW = PREFIX+'admin/UserQueryResponseBoundaryTest.java'
SUBJECT_OWNERS = {PREFIX+'admin/UserQueryRequestTest.java':'WBS-P010-01',PREFIX+'log/LogRequestTest.java':'WBS-P018-09'}
MAIN = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/admin/UserQueryRequest.java'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    prior = data.read_checked(data.BASE/'PG9916-user-query-changed-test-trace-v1/manifest.json',PRIOR_SHA)
    proof_path = data.BASE/'PG9946-query-boundary-quality-post-v1/manifest.json'
    proof = data.read_checked(proof_path,PROOF_SHA)
    normal_path = data.BASE/'PG9944-log-style-six-compile-v1/manifest.json'
    normal = data.read_checked(normal_path,'9bd924d4baa1720b896451c96eee53c42f885afa213b8bca618ea4c4f9cd262d')
    assert prior['actualExit'] == proof['actualExit'] == normal['actualExit'] == 0
    assert proof['source'] == normal['source'] == SOURCE and proof['currentSourceProductTestsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in hashes.items())
    invpath = ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json'
    logical = {r['path']:r for r in json.loads(invpath.read_bytes())['artifacts']}
    assert len(logical) == 941 and logical[MAIN]['owner'] == logical[MAIN]['costOwner'] == 'WBS-P010-01'
    assert logical[MAIN]['sha256'] == hashes[MAIN] and NEW not in logical
    rows = copy.deepcopy(prior['sourceRows'])
    assert len(rows) == 969 and NEW not in {r['path'] for r in rows}
    changes = []
    for row in rows:
        path = row['path']
        if path in SUBJECT_OWNERS:
            assert row['canonicalOwner'] == row['canonicalCostOwner'] == SUBJECT_OWNERS[path]
            assert row['sha256'] != hashes[path]
            changes.append(dict(path=path,previousSha256=row['sha256'],currentSha256=hashes[path],
                canonicalOwner=row['canonicalOwner'],canonicalCostOwner=row['canonicalCostOwner'],source=SOURCE,
                previousRegistrySha256=PRIOR_SHA,staticProofManifest=str(proof_path.relative_to(ROOT)),staticProofSha256=PROOF_SHA,
                currentSourceRuntimeQualificationInferred=False,additionalAllocatedCostPp=0))
            row['sha256'] = hashes[path]
        else:
            assert row['sha256'] == hashes[path]
    row = dict(path=NEW,sha256=hashes[NEW],owner='WBS-P010-01',canonicalOwner='WBS-P010-01',canonicalCostOwner='WBS-P010-01',
        changeOwner='WBS-G13.07',basis='EXPLICIT_2008_VAL001_004_AND_ORIGINAL_LOGICAL_USER_QUERY_MAIN_P01001',
        ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',legacyReportedOwner=None,
        actualAllocatedPp=None,additionalSharedCostPp=0,historicalCostsReallocated=False,historicalRunReassigned=False,
        currentSourcePtQualificationInferred=False,referenceRelatedOwners=[],runtimeUncertainty=['CURRENT_SOURCE_WHOLE_QUALIFICATION_NOT_RUN'],
        independentSpec='evidence/01_PT/018_NK-OPS-001/2008_User応答境界4_単体テスト仕様書.md',
        methodTestIds=['PT-ADM-VAL001','PT-ADM-VAL002','PT-ADM-VAL003','PT-ADM-VAL004'],mainSourceSubjects=[MAIN],
        ownerProofManifest=str(proof_path.relative_to(ROOT)),ownerProofSha256=PROOF_SHA,
        sourceSpecificRuntimeProof=dict(source='7cdcf0029cf111d63498ba4de383bbbf494f91a1',tests=4,suites=1,
            manifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9938-user-query-response-post-v1/manifest.json',
            sha256='bfc77cc75a8f7764ad4c64a7955481f3e1cd7f10031c508b6f3e1902271062c3',reassignedToCurrentSource=False))
    rows.append(row)
    assert len(changes) == 2 and len(rows) == len({r['path'] for r in rows}) == 970
    universe = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    mains = {p for p in universe if '/src/main/java/' in p}
    registered = universe & (set(logical)|{r['path'] for r in rows})
    unknown = sorted(universe-registered)
    assert (len(universe),len(registered),len(mains)) == (1797,1795,965)
    assert unknown == prior['unregisteredJavaPaths'] and len(unknown) == 2
    assert not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)
    before = audit()
    assert before['actualExit'] == 1 and before['lastError'] == 'ValueError: current physical candidate exact Git/worktree scope'
    verify(invocation)
    OUT.mkdir()
    value = dict(actualExit=0,source=SOURCE,invocation=invocation,priorRegistrySha256=PRIOR_SHA,staticProofSha256=PROOF_SHA,
        sourceRows=rows,sourceCount=970,newLogicalCandidates=sum(r.get('ownershipStatus') == 'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED' for r in rows),
        currentModifiedLogicalBindings=prior['currentModifiedLogicalBindings'],previousChangedTestBindings=prior['changedTestBindings'],
        changedTestBindings=changes,newTestPaths=[NEW],registered=1795,javaPaths=1797,registeredMain=965,totalMain=965,
        registeredTest=830,totalTest=832,unregisteredJavaPaths=unknown,newPathsAdded=1,
        allOriginalRowsPreservedExceptTwoSha256=True,canonicalOwnerAndCostPreserved=True,
        relatedLogDaoOwner='WBS-P010-04',logRequestAndTestCanonicalOwner='WBS-P018-09',
        wholeWbsAuditBefore=before,productTestsExecuted=0,dynamicQualificationInferred=False,
        newAccepted=0,formalUpdated=False,effortPercent=None)
    data.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,registered=1795,unknown=2,newTestPaths=1,reboundTestHashes=2,
        wholeAudit=1,newLogicalCandidates=value['newLogicalCandidates'],manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
