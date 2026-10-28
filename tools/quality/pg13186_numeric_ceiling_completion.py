"""Program002 new one/eight related scope binding; field codec local four100, not whole Program."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from quality_scope_dimensions import bind

OUT = data.BASE/'PG13186-numeric-ceiling-completion-v1'
SOURCE = '80ba5f783432c84b6facd83bcd3a80774f4e4665'
DOCUMENTS = [
    'evidence/01_PT/018_NK-OPS-001/2424_FieldCodec数値semantic上限_単体テスト仕様.md',
    'evidence/01_PT/018_NK-OPS-001/2425_FieldCodec数値semantic上限_実行結果.md',
    'evidence/01_PT/002_NK-PRO-002/001_NK-PRO-002_単体テスト仕様書.md',
    'evidence/01_PT/002_NK-PRO-002/002_NK-PRO-002_実行結果.md',
]

def main():
    invocation = capture(__file__);assert not OUT.exists()
    p = data.read_checked(data.BASE/'PG13182-numeric-ceiling-post-v1/manifest.json','c62b307ca85ddf0b5a7e505817115eb41b4a3ce04bff9e9272aee1f3bdc0b4a5')
    plan = data.read_checked(data.BASE/'PG13174-numeric-ceiling-plan-v1/manifest.json','7cb6dbf4fb9b2532cd9e170dc18a71fcb6732a04314c693dc812ffea66c2a40d')
    h = data.read_checked(data.BASE/'PG13178-numeric-ceiling-host-v1/manifest.json','b1d058359df9b2d989b30a66b07f19a0125a2e2cbc6ae1dc6ae0e955030a56a1')
    t = data.read_checked(data.BASE/'PG13185-numeric-ceiling-trace-post-v1/manifest.json','3e22b6be57bafec8f5be703ba2b49b1ae4ffd88afcd391438dc618d2de4fdb19')
    assert p['source'] == plan['source'] == h['source'] == t['source'] == SOURCE and t['actualExit'] == 0
    d = bind(plan,h,p);assert d.public() == p['dimensions'] and d.observed_cases == 9 and d.new_test_ids == 1 and d.suites == 2
    assert p['selectedMainCoverage100'] is True and p['changedTestPhysical'] == 1 and p['newTestPhysical'] == 0
    assert p['rawStatic'] == p['staticGateExit'] == p['spotbugsSixExit'] == 0 and t['wholeWbsAudit']['actualExit'] == 1 and not t['wholeWbsAudit']['passed']
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in h['begin']['sourceInputHashes'].items())
    parent = data.ROOT/'evidence/01_PT/002_NK-PRO-002/evidence';target = parent/'field-numeric-ceiling'
    assert parent.is_dir() and not parent.is_symlink() and not target.exists()
    new_cases = [r for r in plan['cases'] if r['className']+'#'+r['method'] in plan['newMethodIds']];assert len(new_cases) == 1
    item = dict(actualExit=0,source=SOURCE,primaryWbs='WBS-P002-01',cases=plan['cases'],newTestIdBindings={'PT-CODEC-NUMMAX001':new_cases[0]},
        observedOwnTests=9,suites=2,newUniqueTestIds=1,existingRelatedMethodIds=[r['className']+'#'+r['method'] for r in plan['cases'] if r not in new_cases],
        sessionId=h['sessionId'],oldExecUnion=False,dimensions=d.public(),selectedMain=p['selectedMain'],selectedMainCoverage100=True,wholeArtifactCoverage100=False,
        proofManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13182-numeric-ceiling-post-v1/manifest.json',proofManifestSha256='c62b307ca85ddf0b5a7e505817115eb41b4a3ce04bff9e9272aee1f3bdc0b4a5',
        documentHashes={path:data.sha((data.ROOT/path).read_bytes()) for path in DOCUMENTS},relatedRd=['MSG-004'],relatedUi=['232'],relatedSs=['322§4.2','322§5','322§11'],
        relatedBugs=[],relatedYkt=[],rawStatic=0,spotbugsSixExit=0,newAccepted=0,whole451Accepted=False,formalUpdated=False,effortPercent=None)
    verify(invocation);target.mkdir();data.write(target/'manifest.json',item);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,programIndex=str((target/'manifest.json').relative_to(data.ROOT)),
        programIndexSha256=data.sha((target/'manifest.json').read_bytes()),observedTests=9,suites=2,newUniqueTestIds=1,productReruns=0,newAccepted=0,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
