"""Independent six support-definition responsibility audit; no probe/Java/JDBC execution."""
import json
from pathlib import Path
import re
import subprocess
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

ROOT = data.ROOT
SOURCE = '8ba82083ec65abc6373b8454576dcbaee7d3e621'
OUT = data.BASE / 'PG9836-shared-probe-owner-post-v1'
EXPECTED = {'UserCommandFaults','LogJdbcFaults','UserQueryFaults','ServiceJdbcProbe','MaintenanceJdbcProbe','CallerMonitorProbe'}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    joined_sha = '0d361ca974427a14e3feab9ae8be3c55b704268da3576bd70cdfa52bd4bcf200'
    joined = data.read_checked(data.BASE / 'PG9834-shared-probe-owner-v1/manifest.json',joined_sha)
    prior = data.read_checked(data.BASE / 'PG9824-cleanup-test-owner-v1/manifest.json',joined['priorRegistrySha256'])
    normal = data.read_checked(data.BASE / 'PG9812-cleanup-values-six-compile-v1/manifest.json',joined['normalManifestSha256'])
    assert joined['actualExit'] == prior['actualExit'] == normal['actualExit'] == 0 and joined['source'] == prior['source'] == normal['source'] == SOURCE
    rows = joined['sourceRows']
    assert rows[:-6] == prior['sourceRows'] and len(rows) == len({r['path'] for r in rows}) == 968
    new = rows[-6:]
    assert {Path(r['path']).stem for r in new} == EXPECTED
    hashes = normal['begin']['inputHashes']
    assert all(hashes[r['path']] == r['sha256'] == data.sha((ROOT / r['path']).read_bytes()) for r in rows)
    invpath = ROOT / 'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json'
    logical = {r['path']:r for r in json.loads(invpath.read_bytes())['artifacts']}
    known = {**{p:r['owner'] for p,r in logical.items()},**{r['path']:r['canonicalOwner'] for r in prior['sourceRows']}}
    consumers = data.read_checked(data.BASE / 'PG9834-shared-probe-owner-v1/consumers.json',joined['consumersSha256'])
    assert set(consumers) == {r['path'] for r in new} and sum(map(len,consumers.values())) == 25
    for row in new:
        path = row['path']
        body = (ROOT / path).read_text()
        assert not re.search(r'@Test\b|^import (?:static )?dev\.codex\.',body,re.MULTILINE)
        assert 'dev.codex.' not in re.sub(r'^package [^;]+;','',body,count=1,flags=re.MULTILINE)
        assert row['owner'] == row['canonicalOwner'] == row['canonicalCostOwner'] == 'WBS-G03'
        assert row['changeOwner'] == 'WBS-G13.07' and path not in known
        assert not row['historicalCostsReallocated'] and not row['currentSourcePtQualificationInferred'] and row['executabilityOrPermissionNotInferred']
        assert row['actualAllocatedPp'] is None and row['additionalSharedCostPp'] == 0
        assert sorted({known[c['path']] for c in consumers[path]}) == row['referenceRelatedOwners']
        for caller in consumers[path]:
            assert caller['sha256'] == hashes[caller['path']] == data.sha((ROOT / caller['path']).read_bytes())
            assert caller['canonicalOwner'] == known[caller['path']]
            lines = (ROOT / caller['path']).read_text().splitlines()
            assert caller['referenceLines'] and all(re.search(r'\b' + Path(path).stem + r'\b',lines[n-1]) for n in caller['referenceLines'])
    universe = {p for p in hashes if p.endswith('.java') and '/java/' in p}
    registered = universe & (set(logical) | {r['path'] for r in rows})
    assert len(universe) == 1795 and len(registered) == 1793
    assert sorted(universe - registered) == joined['unregisteredJavaPaths']
    assert {Path(p).name for p in joined['unregisteredJavaPaths']} == {'BorrowedJdbcFatal329Test.java','TargetBusinessControllerTest.java'}
    old = '64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
    assert all(subprocess.check_output(['git','show',old + ':' + p],cwd=ROOT) == (ROOT / p).read_bytes() for p in prior['unregisteredJavaPaths'])
    assert all(data.sha((ROOT / p).read_bytes()) == h for p,h in joined['wbsMetadataHashesUnchanged'].items())
    assert joined['toolUnittest']['testsRun'] == 4 and joined['toolUnittest']['actualExit'] == joined['toolUnittest']['productTestCredit'] == 0
    assert joined['currentModifiedLogicalBindings'] == prior['currentModifiedLogicalBindings']
    command = [sys.executable,'-B',str(ROOT / 'tools/quality/wbs_progress_audit.py')]
    audit = subprocess.run(command,cwd=ROOT,capture_output=True,timeout=60,check=False)
    last = audit.stderr.decode().splitlines()[-1]
    assert audit.returncode == 1 and not audit.stdout and last == 'ValueError: current physical candidate exact Git/worktree scope'
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=joined_sha,
        registryPath='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9834-shared-probe-owner-v1/manifest.json',
        sourceRows=968,registered=1793,javaPaths=1795,main=dict(total=965,registered=965,unregistered=0),
        test=dict(total=830,registered=828,unregistered=2),canonicalOwner='WBS-G03',newCandidates=6,consumerReferences=25,
        old962AllFieldsPreserved=True,allEightPriorSourceBytesUnchanged=True,original23MethodTraceNotReplayed=True,
        decision='PG-D673',ruleSha256=joined['ruleSha256'],specSha256=joined['specSha256'],
        wholeWbsAuditBefore=dict(command=command,actualExit=1,lastError=last,passed=False,
            stdoutSha256=data.sha(audit.stdout),stderrSha256=data.sha(audit.stderr)),
        wbsMetadataBeforeHashes=joined['wbsMetadataHashesUnchanged'],productTestsExecuted=0,actualExternalOperations=0,
        newAccepted=0,formalUpdated=False,wholeG03Accepted=False,wholeG13Accepted=False,wholeWbsAuditHoldNotLifted=True,effortPercent=None))
    print(json.dumps(dict(actualExit=0,registered=1793,unregistered=2,wholeWbsAudit='HOLD_ACTUAL_EXIT1',
        manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
