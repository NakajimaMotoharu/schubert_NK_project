"""Bind the three new snapshot cases to Program008; no Product execution."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = '5c378e064f0f8a7366316d4afa28fbb2cd9cec81'
OUT = data.BASE/'PG13120-snapshot-completion-v1'
PINS = {
    'plan': ('PG13104-snapshot-corrected-plan-v1','03bc1cd8dc48f66167728284be8e5a5d04f32aea515ff3d07119dec4c66f9cd8'),
    'host': ('PG13108-snapshot-corrected-host-v1','776be8fff9f5c812c557a02f2198313adf8f506f2f88fea1c809e200911b525a'),
    'proof': ('PG13112-snapshot-corrected-post-v1','2e506ef62e654842ad448b38aa0a61f90b26ebaa98e3b84f42df50d221f07c9d'),
    'trace': ('PG13119-snapshot-max-trace-post-v3','388e6b5195ae17954975db2b46a78fed7a436dafc9b35e88484a272a95dbabb1'),
}
FAILED_ENTRIES = {
    'tools/quality/pg13114_snapshot_max_trace.py':'99760b7fe2bd3ce97350d006d20ca2ad82a54685676390a59a8a402bc611eebf',
    'tools/quality/pg13116_snapshot_max_trace.py':'5e17cba03461ba80cac80e74a50244e2b5cfce6afa6ec0b9c8f6e006b9302290',
}
DOCUMENTS = [
    'evidence/01_PT/018_NK-OPS-001/2414_Scenario最大snapshot純memory_単体テスト仕様.md',
    'evidence/01_PT/018_NK-OPS-001/2415_Scenario最大snapshot純memory_実行結果.md',
    'evidence/01_PT/008_NK-SCN-001/001_NK-SCN-001_単体テスト仕様書.md',
    'evidence/01_PT/008_NK-SCN-001/002_NK-SCN-001_実行結果.md',
]

def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    inputs = {key:data.read_checked(data.BASE/name/'manifest.json',sha) for key,(name,sha) in PINS.items()}
    assert all(x['source'] == SOURCE and x['actualExit'] == 0 for x in inputs.values())
    p,h,proof,t = (inputs[k] for k in ('plan','host','proof','trace'))
    expected = {(r['className'],r['method']) for r in p['cases']}
    assert len(expected) == p['newTests'] == proof['newTestIds'] == proof['observedTestExecutions'] == h['observedTestExecutions'] == 3
    assert expected == {(r['classname'],r['name']) for r in h['cases']} and not any(r['nonPass'] for r in h['cases'])
    assert proof['suites'] == 1 and proof['allMainClassesUnchanged'] == 1843 and proof['oldTestPhysicalUnchanged'] == 1972 and proof['newTestPhysical'] == 1
    assert proof['rawStatic'] == proof['staticGateExit'] == proof['spotbugsSixExit'] == proof['forbiddenProbeHits'] == 0
    assert not proof['selectedMainCoverage100'] and not proof['wholeArtifactCoverage100'] and not proof['oldCandidateSuccessTransferred']
    assert t['metadataNegativeVectors'] == 9 and t['wholeWbsAudit']['actualExit'] == 1 and not t['wholeWbsAudit']['passed']
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in FAILED_ENTRIES.items())
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in h['begin']['sourceInputHashes'].items())
    parent = data.ROOT/'evidence/01_PT/008_NK-SCN-001/evidence'
    target = parent/'snapshot-max-memory'
    assert parent.is_dir() and not parent.is_symlink() and not target.exists()
    item = dict(actualExit=0,source=SOURCE,primaryWbs='WBS-P008-05',cases=p['cases'],
        testIds=['PT-SCN-SNAPSHOTMAX-'+f'{n:03d}' for n in range(1,4)],
        observedOwnTests=3,suites=1,newUniqueTestIds=3,sessionId=h['sessionId'],oldExecUnion=False,
        selectedMain=proof['selectedMain'],selectedMainCoverage100=False,wholeArtifactCoverage100=False,
        inputPins={k:dict(path=str((data.BASE/name/'manifest.json').relative_to(data.ROOT)),sha256=sha) for k,(name,sha) in PINS.items()},
        documentHashes={path:data.sha((data.ROOT/path).read_bytes()) for path in DOCUMENTS},
        failedEntries=FAILED_ENTRIES,rawStatic=0,spotbugsSixExit=0,sourceMainUnchanged=1843,oldTestUnchanged=1972,newPhysicalClasses=1,
        relatedBugs=['BUG-2025','BUG-2026','BUG-2027'],relatedYkt=['YKT-1773','YKT-1774','YKT-1775'],
        oldCandidateExit=1,oldCandidateSuccessTransferred=False,additionalSourceQualificationCycles=1,
        newAccepted=0,whole451Accepted=False,formalUpdated=False,effortPercent=None)
    verify(invocation)
    target.mkdir(); data.write(target/'manifest.json',item); OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        programIndex=str((target/'manifest.json').relative_to(data.ROOT)),programIndexSha256=data.sha((target/'manifest.json').read_bytes()),
        observedTests=3,suites=1,newUniqueTestIds=3,productReruns=0,newAccepted=0,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__': main()
