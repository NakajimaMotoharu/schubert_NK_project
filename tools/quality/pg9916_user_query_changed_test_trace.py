"""Rebind two existing Test hashes, preserve all canonical owners/cost and historical registry fields."""
import copy
import json
from pathlib import Path
import subprocess

import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9880_snapshot_nonce_trace import audit

ROOT = data.ROOT
SOURCE = '4c94a7d4665e4f3c27a7d39fb2b427bec663d903'
OUT = data.BASE/'PG9916-user-query-changed-test-trace-v1'
PRIOR_SHA = 'dd8c2590f9962bdcaa9f37c4f3ebf67c2940af14829b2b365ca8073b2ae15012'
PROOF_SHA = '4cc044a2095170ba4ff1484165180328ba1dc2c6e506d066cbefa61c6e656d04'
PREFIX = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/admin/'
SUBJECTS = {PREFIX+'UserQueryRequestTest.java',PREFIX+'UserQueryApplicationServiceTest.java'}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    prior_path = data.BASE/'PG9880-snapshot-nonce-trace-v1/manifest.json'
    proof_path = data.BASE/'PG9912-user-query-fixture-post-v1/manifest.json'
    prior,proof = data.read_checked(prior_path,PRIOR_SHA),data.read_checked(proof_path,PROOF_SHA)
    normal_path = data.BASE/'PG9908-user-query-fixture-six-compile-v1/manifest.json'
    normal = data.read_checked(normal_path,'82fa21a02cbd438e29d63a5260e206d71bf7c9df864448146866af5d73c91e34')
    assert prior['actualExit'] == proof['actualExit'] == normal['actualExit'] == 0
    assert proof['source'] == normal['source'] == SOURCE and proof['productTestsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in hashes.items())
    rows = copy.deepcopy(prior['sourceRows'])
    changed = []
    for row in rows:
        path = row['path']
        if path in SUBJECTS:
            assert row['canonicalOwner'] == row['canonicalCostOwner'] == 'WBS-P010-01'
            assert row['sha256'] != hashes[path]
            changed.append(dict(path=path,previousSha256=row['sha256'],currentSha256=hashes[path],
                canonicalOwner=row['canonicalOwner'],canonicalCostOwner=row['canonicalCostOwner'],
                source=SOURCE,previousRegistrySha256=PRIOR_SHA,staticProofManifest=str(proof_path.relative_to(ROOT)),
                staticProofSha256=PROOF_SHA,dynamicQualificationStatus='NOT_EXECUTED_DB_DEPENDENCY_HOLD',
                oldDynamicSuccessTransferred=False,additionalAllocatedCostPp=0))
            row['sha256'] = hashes[path]
        else:
            assert row['sha256'] == hashes[path]
    assert len(changed) == 2 and len(rows) == len({r['path'] for r in rows}) == 969
    invpath = ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json'
    logical = json.loads(invpath.read_bytes())['artifacts']
    assert len(logical) == 941
    universe = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    mains = {p for p in universe if '/src/main/java/' in p}
    registered = universe & ({r['path'] for r in logical}|{r['path'] for r in rows})
    unknown = sorted(universe-registered)
    assert len(universe) == 1796 and len(registered) == 1794 and len(mains) == 965
    assert unknown == prior['unregisteredJavaPaths'] and len(unknown) == 2
    assert not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)
    before = audit()
    assert before['actualExit'] == 1 and before['lastError'] == 'ValueError: current physical candidate exact Git/worktree scope'
    verify(invocation)
    OUT.mkdir()
    value = dict(actualExit=0,source=SOURCE,invocation=invocation,priorRegistrySha256=PRIOR_SHA,staticProofSha256=PROOF_SHA,
        sourceRows=rows,sourceCount=969,currentModifiedLogicalBindings=prior['currentModifiedLogicalBindings'],
        changedTestBindings=changed,registered=1794,javaPaths=1796,registeredMain=965,totalMain=965,
        registeredTest=829,totalTest=831,unregisteredJavaPaths=unknown,newPathsAdded=0,
        allOriginalRowFieldsPreservedExceptTwoSha256=True,canonicalOwnerAndCostPreserved=True,
        wholeWbsAuditBefore=before,productTestsExecuted=0,dynamicQualificationInferred=False,
        newAccepted=0,formalUpdated=False,effortPercent=None)
    data.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,registered=1794,unknown=2,reboundTestHashes=2,wholeAudit=1,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
