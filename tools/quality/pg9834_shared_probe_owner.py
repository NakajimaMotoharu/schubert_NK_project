"""Register six explicitly reviewed oracle support definitions; never execute delegated callbacks."""
import copy
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import g07_host_class_provenance_inputs as data
import trace_owner_join as owner
from host_tool_invocation import capture, verify

ROOT = data.ROOT
SOURCE = '8ba82083ec65abc6373b8454576dcbaee7d3e621'
SLOT = ROOT.parent / 'pgpt-runs/PG379/pg9834-shared-probe-owner-v1'
OUT = data.BASE / 'PG9834-shared-probe-owner-v1'
EXPECTED = {
    'UserCommandFaults':{'WBS-P010-01','WBS-P010-02'},
    'LogJdbcFaults':{'WBS-P006-01','WBS-P010-04'},
    'UserQueryFaults':{'WBS-P010-01','WBS-P010-04'},
    'ServiceJdbcProbe':{'WBS-P017-07','WBS-P017-12'},
    'MaintenanceJdbcProbe':{'WBS-P004-02','WBS-P004-04','WBS-P019-01'},
    'CallerMonitorProbe':{'WBS-P017-06','WBS-P018-03','WBS-P018-04','WBS-P018-06'}}


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    prior_sha = 'ac07bdb3152cb171996e913c48d01b63cf1ea75583a5a7584008b646756d456c'
    prior = data.read_checked(data.BASE / 'PG9824-cleanup-test-owner-v1/manifest.json',prior_sha)
    normal_sha = 'e074d972cbaf56b94ba4d25a77e7368b4f53ccd91489be0fbc27f07ef3975c95'
    normal = data.read_checked(data.BASE / 'PG9812-cleanup-values-six-compile-v1/manifest.json',normal_sha)
    assert prior['source'] == normal['source'] == SOURCE and prior['actualExit'] == normal['actualExit'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT / p).read_bytes()) == h for p,h in hashes.items())
    pmo = ROOT / 'documents/400_PGPT/470_PMO'
    metadata_hashes = {str(p.relative_to(ROOT)):data.sha(p.read_bytes()) for p in (pmo / '485_WBS網羅性・受入対応.json',pmo / '486_WBS現行実績.json')}
    logical = {r['path']:r for r in json.loads((pmo / '485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    rows = copy.deepcopy(prior['sourceRows'])
    assert len(rows) == 962 and all(hashes[r['path']] == r['sha256'] for r in rows)
    known = {**{p:r['owner'] for p,r in logical.items()},**{r['path']:r['canonicalOwner'] for r in rows}}
    candidates = sorted(p for p in prior['unregisteredJavaPaths'] if Path(p).stem in EXPECTED)
    assert len(candidates) == 6
    java = {p:(ROOT / p).read_text() for p in hashes if p.endswith('.java') and '/java/' in p}
    consumers,added = {},[]
    for path in candidates:
        simple = Path(path).stem
        text = java[path]
        package = re.search(r'^package ([\w.]+);',text,re.MULTILINE).group(1)
        fqname = package + '.' + simple
        assert sum(Path(p).stem == simple for p in java) == 1
        assert not re.search(r'@Test\b|^import (?:static )?dev\.codex\.',text,re.MULTILINE)
        assert 'dev.codex.' not in re.sub(r'^package [^;]+;','',text,count=1,flags=re.MULTILINE)
        assert owner.canonical(path,logical)['canonicalOwner'] == 'WBS-G03' and path not in known
        matches = []
        for caller,body in java.items():
            if caller == path or not re.search(r'\b' + simple + r'\b',body):
                continue
            assert '/src/test/java/' in caller and caller in known
            caller_package = re.search(r'^package ([\w.]+);',body,re.MULTILINE).group(1)
            assert caller_package == package or fqname in body
            lines = [n for n,line in enumerate(body.splitlines(),1) if re.search(r'\b' + simple + r'\b',line)]
            matches.append(dict(path=caller,sha256=hashes[caller],canonicalOwner=known[caller],referenceLines=lines,
                referenceKind='SAME_PACKAGE_OR_EXPLICIT_FQN_TEXT_NOT_CALLEE_RESOLUTION'))
        assert {r['canonicalOwner'] for r in matches} == EXPECTED[simple]
        consumers[path] = matches
        proposal = owner.canonical(path,logical)
        added.append(dict(path=path,sha256=hashes[path],owner=proposal['canonicalOwner'],**proposal,
            changeOwner='WBS-G13.07',legacyReportedOwner=None,additionalSharedCostPp=0,actualAllocatedPp=None,
            historicalCostsReallocated=False,historicalRunReassigned=False,currentSourcePtQualificationInferred=False,
            referenceRelatedOwners=sorted(EXPECTED[simple]),runtimeUncertainty=[],
            responsibility='SHARED_ORACLE_SUPPORT_DEFINITION_ONLY_NOT_CONSUMER_BUSINESS_OWNERSHIP',
            independentSpec='evidence/01_PT/018_NK-OPS-001/1985_G13汎用oracle補助六件_担当候補仕様.md',
            consumerSourcePaths=sorted(r['path'] for r in matches),executabilityOrPermissionNotInferred=True))
    assert sum(map(len,consumers.values())) == 25
    os.umask(0o077)
    SLOT.mkdir()
    command = [sys.executable,'-B','-m','unittest','trace_owner_probe_policy_test','-v']
    began = dt.datetime.now(dt.timezone.utc).isoformat()
    run = subprocess.run(command,cwd=ROOT,stdin=subprocess.DEVNULL,capture_output=True,timeout=30,check=False)
    assert run.returncode == 0 and not run.stdout and 'Ran 4 tests' in run.stderr.decode() and run.stderr.decode().rstrip().endswith('OK')
    with (SLOT / 'tool-unittest.log').open('xb') as stream:
        stream.write(run.stderr)
    result_rows = rows + added
    universe = set(java)
    registered = universe & (set(logical) | {r['path'] for r in result_rows})
    unregistered = sorted(universe - registered)
    assert len(result_rows) == len({r['path'] for r in result_rows}) == 968
    assert len(registered) == 1793 and len(universe) == 1795
    assert {Path(p).stem for p in unregistered} == {'BorrowedJdbcFatal329Test','TargetBusinessControllerTest'}
    assert result_rows[:-6] == prior['sourceRows']
    assert all(data.sha((ROOT / p).read_bytes()) == h for p,h in {**hashes,**metadata_hashes}.items())
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'consumers.json',consumers)
    result = dict(actualExit=0,source=SOURCE,invocation=invocation,priorRegistrySha256=prior_sha,normalManifestSha256=normal_sha,
        sourceRows=result_rows,sourceCount=968,registered=1793,javaPaths=1795,registeredMain=965,totalMain=965,
        registeredTest=828,totalTest=830,unregisteredJavaPaths=unregistered,
        currentModifiedLogicalBindings=prior['currentModifiedLogicalBindings'],old962AllFieldsPreserved=True,
        canonicalNewOwner='WBS-G03',canonicalNewCostOwner='WBS-G03',primaryDecision='PG-D673',
        sourceOwnerCandidatesAdded=6,consumerReferences=25,consumersSha256=data.sha((OUT / 'consumers.json').read_bytes()),
        ruleSha256=data.sha((ROOT / 'tools/quality/trace_owner_join.py').read_bytes()),
        specSha256=data.sha((ROOT / 'evidence/01_PT/018_NK-OPS-001/1985_G13汎用oracle補助六件_担当候補仕様.md').read_bytes()),
        toolUnittest=dict(command=command,startUTC=began,endUTC=dt.datetime.now(dt.timezone.utc).isoformat(),actualExit=run.returncode,
            testsRun=4,productTestCredit=0,logSha256=data.sha(run.stderr),testSourceSha256=data.sha((ROOT / 'tools/quality/trace_owner_probe_policy_test.py').read_bytes())),
        wbsMetadataHashesUnchanged=metadata_hashes,metadataStillHistoricalSource='58913ab374ef54d138fa3fad8c80cccd03d87c10',
        original23MethodTraceNotReplayed=True,productTestsExecuted=0,actualExternalOperations=0,graph9Operations=0,
        wholeG03Accepted=False,wholeG13Accepted=False,wholeWbsAuditHoldNotLifted=True,newAccepted=0,formalUpdated=False,effortPercent=None)
    data.write(OUT / 'manifest.json',result)
    print(json.dumps(dict(actualExit=0,sourceOwnerCandidatesAdded=6,registered=1793,javaPaths=1795,unregistered=2,
        manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
