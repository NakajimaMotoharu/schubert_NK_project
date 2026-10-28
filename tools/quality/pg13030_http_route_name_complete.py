"""Fixed original six Test IDs and current six-class qualification; no Product replay."""
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = '2f4290e7e511ea30224d087f78d44964d3488919'
PINS = {
    'PG13012-http-route-name-preflight-v1':'27e0ab042507d1aac7757ee543a38523976f0441a5f3a9d2b6ea16df3f45e394',
    'PG13013-http-route-originals-v1':'e558144f2b09a2ffabd8476a518c4d6bdef43461266e59773677b8fb973e4875',
    'PG13014-http-route-name-preflight-v2':'70461a031e27a8c36a6fb1ffb36d7d4d9e1567ea5d79f092ddaf6fc7d3a41c7d',
    'PG13016-http-route-name-plan-v1':'5a886111e837fb871087f4777e32580c9e834bb169fd89e742006a2a9d4a253e',
    'PG13018-http-route-name-six-compile-v1':'66360a6446a271767118ed3ff4d734701f55a010638dc7676490409a0c488351',
    'PG13020-http-route-name-host-v1':'647c3c5306e93d3402c8fc135e5ecfe1acf4a4dab245d4488d7e39e76cd561f4',
    'PG13022-http-route-name-static-v1':'c4e96da7639188621b5e4477fca68d6bd10d17e09c7a6bdce23ca375249bf21c',
    'PG13024-http-route-name-post-v1':'6d4088dfc5b7b254ef4aaa652c41a3dd0e49d0106a0cfdc7759c5d1cffe19a1c',
    'PG13026-http-route-name-context-v1':'e9a90bad3af371bf236ab3a54a29a5d6ea852038514195177a939dc93c4c46b1',
    'PG13027-http-route-name-context-post-v1':'02dbb794f004b6492165b876537461b70a02731cd4fd875f9278188ff7e17f9f',
    'PG13028-http-route-name-trace-v1':'8cc4b73e1470a67b8e458abb89afb2284cc34fe8c5a3660f57dd16e339e41637',
    'PG13029-http-route-name-trace-post-v1':'4a7ad578a598547bd449dc643e06f317d5828c517e0337257f1b2c084ed657f8'}

def main():
    invocation = capture(__file__); out = data.BASE/'PG13030-http-route-name-completion-v1'
    index = data.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/http-route-private-name'
    assert not out.exists() and not index.exists() and index.parent.is_dir() and not index.parent.is_symlink()
    values = {name:data.read_checked(data.BASE/name/'manifest.json',sha) for name,sha in PINS.items()}
    for name,value in values.items():
        if name in list(PINS)[:3]:
            if 'originals' in name: assert value['source'] == '94eeea264b449e5826f292c746a9cd4655b3122a'
            else: assert value['source'] is None and value['baseSource'] == '94eeea264b449e5826f292c746a9cd4655b3122a'
        else: assert value['source'] == SOURCE
        assert value['actualExit'] == (1 if name in ['PG13012-http-route-name-preflight-v1','PG13014-http-route-name-preflight-v2','PG13022-http-route-name-static-v1'] else 0)
    host = values['PG13020-http-route-name-host-v1']; proof = values['PG13024-http-route-name-post-v1']
    assert host['observedTestExecutions'] == proof['observedTestExecutions'] == 6 and proof['selectedMainCoverage100']
    assert len(proof['selectedMain']) == 6 and proof['rawStatic'] == 4 and proof['spotbugsSixExit'] == 0
    assert proof['mainChangedPhysical'] == 5 and proof['oldTestPhysicalUnchanged'] == 1969 and proof['changedTestPhysical'] == 1
    docs = [data.ROOT/'evidence/01_PT/018_NK-OPS-001'/name for name in ['2404_HTTP私有index命名_製造単体仕様.md','2405_HTTP私有index命名_実行結果.md']]
    assert all(sha in docs[1].read_text() for sha in PINS.values())
    cases = host['begin']['cases']; assert len(cases) == 6 and len({r['className'] for r in cases}) == 1
    assert all(r['method'].startswith('httpMetric'+str(i).zfill(3)) for i,r in enumerate(cases,1))
    verify(invocation); out.mkdir(); index.mkdir()
    data.write(index/'manifest.json',dict(actualExit=0,program='NK-OPS-001',source=SOURCE,run=host['sessionId'],invocation=invocation,
        hostManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13020-http-route-name-host-v1/manifest.json',hostSha256=PINS['PG13020-http-route-name-host-v1'],
        postManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13024-http-route-name-post-v1/manifest.json',postSha256=PINS['PG13024-http-route-name-post-v1'],
        observedProductTests=6,newUniqueTestIds=0,existingTestIdMappings=[dict(testId='HTTPMETRIC'+str(i).zfill(3),className=row['className'],method=row['method'],actual='PASS') for i,row in enumerate(cases,1)],
        selectedMain=proof['selectedMain'],scopeSixMainCoverage100=True,rawStatic=4,scopeStaticExit=1,
        fullProgramAccepted=False,newAccepted=0,whole451Accepted=False,oldExecUnion=False))
    data.write(out/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,manifests=PINS,
        documents={str(p.relative_to(data.ROOT)):data.sha(p.read_bytes()) for p in docs},
        programIndexPath=str((index/'manifest.json').relative_to(data.ROOT)),programIndexSha256=data.sha((index/'manifest.json').read_bytes()),
        observedProductTests=6,newTestIds=0,scopeSixMainFourCounters100=True,scopeStaticExit=1,
        fullArtifactCoverage100=False,whole451Accepted=False,newAccepted=0,externalActions=0))
    print(json.dumps(dict(completionSha256=data.sha((out/'manifest.json').read_bytes()))))

if __name__ == '__main__': main()
