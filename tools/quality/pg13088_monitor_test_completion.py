"""Program018 binding for all original81 corrected-source cases, no new PT IDs or rerun."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = '42ae92a74d57a9e1d031613d5b558af3ebe2925c'
OUT = data.BASE/'PG13088-monitor-test-completion-v1'
DOCUMENTS = ['evidence/01_PT/018_NK-OPS-001/'+name for name in ['2412_監視Test十_命名・fixture規約是正仕様.md','2413_監視Test十_命名・fixture規約是正結果.md','001_NK-OPS-001_検査起動wrapper・unit単体テスト仕様書.md','002_NK-OPS-001_検査起動wrapper・unit実行結果.md']]

def main():
    invocation = capture(__file__); assert not OUT.exists()
    p = data.read_checked(data.BASE/'PG13082-monitor-test-post-v1/manifest.json','911c0f6768b0672873c942d4d2a9e7e89c92c18f4a16d39ee9b4515ed4a44fcc')
    plan = data.read_checked(data.BASE/'PG13074-monitor-test-plan-v1/manifest.json','26c3c4fd22d61e6bd8dc26ddbf4c47baee7b98c3963352123a0fac1d80f88a09')
    h = data.read_checked(data.BASE/'PG13078-monitor-test-host-v1/manifest.json','28f76d37bfd46dd38535f7418aafc31046fa3e40697956d85d9951d537cbdd6d')
    t = data.read_checked(data.BASE/'PG13087-monitor-test-trace-post-v1/manifest.json','f4916614816f5af487cc4cccd55158d5cb6b4e9b41614becbd3f484033c89d25')
    assert p['source'] == plan['source'] == h['source'] == t['source'] == SOURCE
    assert p['actualExit'] == plan['actualExit'] == h['actualExit'] == t['actualExit'] == 0
    expected = {(r['className'],r['method']) for r in plan['cases']}
    assert len(expected) == len(h['cases']) == 81 and expected == {(r['classname'],r['name']) for r in h['cases']} and not any(r['nonPass'] for r in h['cases'])
    assert plan['newTests'] == p['newTestIds'] == 0 and p['observedTestExecutions'] == 81 and p['suites'] == 10
    assert p['rawStatic'] == 20 and p['staticGateExit'] == 1 and p['spotbugsSixExit'] == 0
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in h['begin']['sourceInputHashes'].items())
    assert t['wholeWbsAudit']['actualExit'] == 1 and not t['wholeWbsAudit']['passed']
    parent = data.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence'; target = parent/'monitor-test-name-regression'
    assert parent.is_dir() and not parent.is_symlink() and not target.exists()
    item = dict(actualExit=0,source=SOURCE,cases=plan['cases'],existingMethodIds=[r['className']+'#'+r['method'] for r in plan['cases']],
        observedOwnTests=81,suites=10,newUniqueTestIds=0,sessionId=h['sessionId'],oldExecUnion=False,
        selectedMain=p['selectedMain'],monitorGroups=p['monitorGroups'],selectedMainClosureCoverage100=False,
        proofManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13082-monitor-test-post-v1/manifest.json',
        proofManifestSha256='911c0f6768b0672873c942d4d2a9e7e89c92c18f4a16d39ee9b4515ed4a44fcc',
        documentHashes={path:data.sha((data.ROOT/path).read_bytes()) for path in DOCUMENTS},
        sourceDerivedRaw=8461,totalPriorCorrections=964,scopeRaw=20,staticGateExit=1,spotbugsSixExit=0,
        relatedBugs=['BUG-2023','BUG-2024'],relatedYkt=['YKT-1771','YKT-1772'],relatedSsc=[],
        inputExpectedActual='Original immutable source/oracles preserved in PG13070; token inverse52 negatives; all original81 XML cases SUCCESSFUL',
        sourceMainUnchanged=1843,changedTestPhysical=11,allOtherTestUnchanged=1961,newPhysicalClasses=0,
        newAccepted=0,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,effortPercent=None)
    verify(invocation); target.mkdir();data.write(target/'manifest.json',item);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        programIndex=str((target/'manifest.json').relative_to(data.ROOT)),programIndexSha256=data.sha((target/'manifest.json').read_bytes()),
        observedTests=81,suites=10,newUniqueTestIds=0,runDuplicated=False,productReruns=0,newAccepted=0,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__': main()
