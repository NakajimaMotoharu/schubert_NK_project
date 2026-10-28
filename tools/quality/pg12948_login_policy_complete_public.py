"""Fixed pure policy outcome, Program007 TestID index and public delta only."""
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg12706_scenario_writer_public as scan

SOURCE = 'e49eb0cc84c62ace468cf389938b23f3e56ba520'
PINS = {
    'PG12934-login-policy-preflight-v1':'31453c489d31fc82eecac8b632865888c22476ccf94bd8cd2f1dfa567e9fe4b2',
    'PG12936-login-policy-plan-v1':'745d68510d587effc590ab73fce3db60fde883b7b518c6c69a361c93f06c67d2',
    'PG12938-login-policy-six-compile-v1':'f65a05a93b6a857e21602222b5a9f5287a92b185cf6b540792c5bf8d7a10cac2',
    'PG12940-login-policy-host-v1':'3cf0b7bab17d85a075c1ad007cf12ee7b2536706b062b3dac3dd32b17766dfca',
    'PG12942-login-policy-static-v1':'c2054cdf6d521ebbb32e3300768e72346cc62dd4f35ef35ecf212821cb5b402e',
    'PG12944-login-policy-post-v1':'a6d70118ffcbc9dc1ccbdf56e3ed711d1811561cc2043a1bf7a2af0ec771d426',
    'PG12946-login-policy-trace-v1':'81f56767211bba65e7493b8d9a6549ff4b4a2cf88a39c70f1618606cc0237366',
    'PG12947-login-policy-trace-post-v1':'b436f7fe9c7206388fa9cfef7466d200b5a1220909c64d2d60657007ffa34911'}

def main():
    invocation = capture(__file__)
    out = data.BASE/'PG12948-login-policy-completion-v1'
    index = data.ROOT/'evidence/01_PT/007_NK-AUT-001/evidence/pure-login-window-sequence'
    assert not out.exists() and not index.exists()
    for name,digest in PINS.items():
        v = data.read_checked(data.BASE/name/'manifest.json',digest); assert v['actualExit'] == 0
        if 'preflight' in name: assert v['source'] is None and v['baseSource'] == '4a3fad244f21530547fdc79b16f9ea3af0ca13af'
        else: assert v['source'] == SOURCE
    docs = [data.ROOT/'evidence/01_PT/018_NK-OPS-001'/n for n in ['2395_P007失敗窓時系列_単体テスト仕様書.md','2396_P007失敗窓時系列_実行結果.md']]
    for digest in PINS.values(): assert digest in docs[1].read_text()
    host = data.read_checked(data.BASE/'PG12940-login-policy-host-v1/manifest.json',PINS['PG12940-login-policy-host-v1'])
    proof = data.read_checked(data.BASE/'PG12944-login-policy-post-v1/manifest.json',PINS['PG12944-login-policy-post-v1'])
    assert host['observedTestExecutions'] == proof['observedTestExecutions'] == 9 and proof['selectedTwoMainCoverage100'] and proof['rawStatic'] == 0
    selected = [r for r in host['begin']['cases'] if r['className'].endswith('.LoginAttemptSequenceTest')]; assert len(selected) == 4
    verify(invocation); out.mkdir(); index.mkdir()
    data.write(index/'manifest.json',dict(actualExit=0,program='NK-AUT-001',source=SOURCE,run=host['sessionId'],invocation=invocation,
        hostManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG12940-login-policy-host-v1/manifest.json',hostSha256=PINS['PG12940-login-policy-host-v1'],
        postManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG12944-login-policy-post-v1/manifest.json',postSha256=PINS['PG12944-login-policy-post-v1'],
        observedProductTests=9,newUniqueTestIds=4,newTestIdMappings=[dict(testId='PT-AUT-WINDOW-'+str(i).zfill(3),className=r['className'],method=r['method'],actual='PASS') for i,r in enumerate(selected,1)],
        selectedTwoMain=proof['selectedTwoMain'],fullProgramAccepted=False,newAccepted=0,whole451Accepted=False,oldExecUnion=False))
    data.write(out/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,manifests=PINS,
        documents={str(p.relative_to(data.ROOT)):data.sha(p.read_bytes()) for p in docs},
        programIndexPath=str((index/'manifest.json').relative_to(data.ROOT)),programIndexSha256=data.sha((index/'manifest.json').read_bytes()),
        observedProductTests=9,newBusinessTestIds=4,selectedTwoMainFourCounters100=True,scopeStaticExit=0,
        fullArtifactCoverage100=False,whole451Accepted=False,newAccepted=0,externalActions=0))
    print(json.dumps(dict(completionSha256=data.sha((out/'manifest.json').read_bytes()))))
    scan.OUT = data.BASE/'PG12948-login-policy-public-v1'; scan.BEFORE = 'de95d1e9669f7a1c0e90573f83250aac913ae9fa'
    scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg129','tools/quality/architecture/LoginWindowJunitLauncher.java','tools/quality/architecture/LoginWindowArtifactCoverageMeasure.java')
    scan.main()

if __name__ == '__main__': main()
