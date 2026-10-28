"""Bind six source-local results, four independent IDs and limited public delta only."""
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg12706_scenario_writer_public as scan

SOURCE = '762568bb0338749c9549ec937cc2c79e84418836'
PINS = {
    'PG12970-query-binding-preflight-v1':'f8e2f65216af67ba757a4dce2e32bff48fb951587b6054dd29953650401f7f3d',
    'PG12972-query-binding-plan-v1':'d7c36bb6ed7a8833b89fb21dc7af8cf4095ee56db45b46e8f26743f2eff76f31',
    'PG12974-query-binding-six-compile-v1':'f3134ed6a743744068faa3c45142bb6a558ab5526aeccebad9e8d3d1b0ca005d',
    'PG12976-query-binding-host-v1':'f2fda8705ee7829e92f33e541bcc1db84558ffb0d2e770ac3b900bd0805a9f2d',
    'PG12978-query-binding-static-v1':'ab19f4ce69c070761a49c3aa5573566ca90b45d33bc068a1f3faecbf0831dd0f',
    'PG12979-query-helper-byte-recovery-v1':'bf8c7f18c8592abf9d35941c829ee7de21b735fca591dd4460f45dc604d80ee0',
    'PG12980-query-binding-post-v1':'a05f5898aeebabc5d5866e2fa85aa3b2263199667c4bc18533004733ae631a61',
    'PG12982-query-binding-trace-v1':'762b25517af68a865010d85af878ebd2b601f0db23645e16fba8a865cf1bda7a',
    'PG12983-query-binding-trace-post-v1':'5aa2a092c2075e3f63db09f86f19bd42c6a9e77b34d07c7548caa4fd5c9d9a91'}

def main():
    invocation = capture(__file__)
    out = data.BASE/'PG12984-query-binding-completion-v1'
    index = data.ROOT/'evidence/01_PT/013_NK-NTF-001/evidence/query-response-binding'
    assert not out.exists() and not index.exists()
    values = {name:data.read_checked(data.BASE/name/'manifest.json',sha) for name,sha in PINS.items()}
    for name,value in values.items():
        if 'preflight' in name:
            assert value['source'] is None and value['baseSource'] == 'c1d9b6e4b27b236ed8b40724f0701d2a2216237b'
        else: assert value['source'] == SOURCE
        assert value['actualExit'] == (1 if 'preflight' in name or 'static-v1' in name else 0)
    n = values['PG12974-query-binding-six-compile-v1']
    h = values['PG12976-query-binding-host-v1']; proof = values['PG12980-query-binding-post-v1']
    assert h['observedTestExecutions'] == proof['observedTestExecutions'] == 6 and not proof['selectedMainCoverage100']
    assert proof['rawStatic'] == 2 and proof['staticGateExit'] == 1 and proof['spotbugsSixExit'] == 0
    old = data.read_checked(data.BASE/'PG11038-api-request-six-compile-v1/manifest.json','5f2d2363b5d3ddaf1c61b59e096ffe5705725b332dcf4324381181c1c6c90e7b')
    path = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/question/QuestionQueryRequest.java'
    assert old['begin']['inputHashes'][path] == n['begin']['inputHashes'][path] == data.sha((data.ROOT/path).read_bytes())
    docs = [data.ROOT/'evidence/01_PT/018_NK-OPS-001'/x for x in ['2399_P013照会応答束縛_単体テスト仕様書.md','2400_P013照会応答束縛_実行結果.md']]
    assert all(sha in docs[1].read_text() for sha in PINS.values())
    selected = [row for row in h['begin']['cases'] if row['className'].endswith('.QuestionQueryResponseBindingTest')]
    assert len(selected) == 4
    verify(invocation); out.mkdir(); index.mkdir()
    data.write(index/'manifest.json',dict(actualExit=0,program='NK-NTF-001',source=SOURCE,run=h['sessionId'],invocation=invocation,
        hostManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG12976-query-binding-host-v1/manifest.json',hostSha256=PINS['PG12976-query-binding-host-v1'],
        postManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG12980-query-binding-post-v1/manifest.json',postSha256=PINS['PG12980-query-binding-post-v1'],
        observedProductTests=6,newUniqueTestIds=4,newTestIdMappings=[dict(testId='PT-QRY-BIND'+str(i).zfill(3),className=row['className'],method=row['method'],actual='PASS') for i,row in enumerate(selected,1)],
        selectedMain=proof['selectedMain'],fullProgramAccepted=False,newAccepted=0,whole451Accepted=False,oldExecUnion=False))
    data.write(out/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,manifests=PINS,
        documents={str(p.relative_to(data.ROOT)):data.sha(p.read_bytes()) for p in docs},
        programIndexPath=str((index/'manifest.json').relative_to(data.ROOT)),programIndexSha256=data.sha((index/'manifest.json').read_bytes()),
        observedProductTests=6,newBusinessTestIds=4,selectedMainFourCounters100=False,scopeStaticExit=1,
        historicalMainShaEqual=True,oldSuccessNotTransferred=True,fullArtifactCoverage100=False,whole451Accepted=False,newAccepted=0,externalActions=0))
    print(json.dumps(dict(completionSha256=data.sha((out/'manifest.json').read_bytes()))))
    scan.OUT = data.BASE/'PG12984-query-binding-public-v1'
    scan.BEFORE = '78aa0f6cae9c35bf1bd17b1e5c19a22d3326a80d'
    scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg129','tools/quality/architecture/QueryBindingJunitLauncher.java','tools/quality/architecture/QueryBindingArtifactCoverageMeasure.java')
    scan.main()

if __name__ == '__main__': main()
