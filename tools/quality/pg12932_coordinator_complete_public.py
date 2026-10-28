"""Bound source-separated business results and append-only spec history; public delta only."""
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg12706_scenario_writer_public as scan

PINS = {
    'PG12908-coordinator-six-compile-v1':'89a56682397935ccc954426df91a99be29797e40fec05c23bca7551889bfcf1e',
    'PG12910-coordinator-plan-v1':'60ead5eb8019fd1b82015663168127b6e3ef6802909d9995f373b091c04f3968',
    'PG12912-coordinator-host-v1':'37cd5a69c4570664ffccb77366a0b4e1d72f644a519f335cddca18905ba18554',
    'PG12914-coordinator-static-v1':'032eab4fc9aecc313a5412621821f5942b1d05ea9137d95fecd2aac653034ece',
    'PG12916-coordinator-post-v1':'302c87f33df40c5204561c1e58e556e04768f1b78ff34950825927cd4f2ede21',
    'PG12918-coordinator-corrected-plan-v1':'3491b6d92468eee54d6aba15e1efe500fa82676ac5bdc4bdfdcf53fbe58953c3',
    'PG12920-coordinator-corrected-six-compile-v1':'14e6f1dce556fe58dc1ecdea73c0b65ab6dbc45d82625601eae1732378e239cc',
    'PG12922-coordinator-corrected-host-v1':'1aa4cded3c135470f100f246770ebf77424b9689f991511a9ff37e63a7af0ba2',
    'PG12924-coordinator-corrected-static-v1':'6b939db5f3785efd4296d055692e0a3f038069924ed07c31abd8524b70b2f694',
    'PG12926-coordinator-corrected-post-v1':'b3904e8e05c97c403ff65e65793dae5d3e447c564c61cbd7150262e7041ea3f9',
    'PG12928-coordinator-context-v1':'9c8e7149fb87f628d3c37f217e66ddc5f4a0cec98a4f0326bfd17450e162705c',
    'PG12929-coordinator-context-post-v1':'5a683d236436f04ae85d914cab91b8e93c332cb2f94885cdc3ae015d2975004c',
    'PG12930-coordinator-trace-v1':'b984b53514914c24fde1c36eb638c660f5e1cf95ce0c2a819ec620eebb6045d3',
    'PG12931-coordinator-trace-post-v1':'f32417c8cf6eb9dcc971cca40bdaad90f6ea4c6c0230b571dc83906d19ee9e0a'}
CURRENT = '4a3fad244f21530547fdc79b16f9ea3af0ca13af'

def main():
    invocation = capture(__file__)
    out = data.BASE/'PG12932-coordinator-completion-v1'
    index = data.ROOT/'evidence/01_PT/005_NK-MSG-001/evidence/reply-registry-recovery'
    assert not out.exists() and not index.exists()
    old_names = set(list(PINS)[:5])
    for name,digest in PINS.items():
        v = data.read_checked(data.BASE/name/'manifest.json',digest)
        assert v['source'] == ('a501a917bdb2b5086da503df41710b099975fbc1' if name in old_names else CURRENT)
        assert v['actualExit'] == (1 if 'static-v1' in name else 0)
    docs = [data.ROOT/'evidence/01_PT/018_NK-OPS-001'/x for x in ['2393_P005同期失敗後回復_単体テスト仕様書.md','2394_P005同期失敗後回復_実行結果.md']]
    for digest in PINS.values(): assert digest in docs[1].read_text()
    lines = docs[0].read_text().splitlines(keepends=True)
    assert lines[2].startswith('追加是正（BUG2010/2011') and lines[3] == '\n'
    original = ''.join(lines[:2]+lines[4:]).encode()
    oldplan = data.read_checked(data.BASE/'PG12910-coordinator-plan-v1/manifest.json',PINS['PG12910-coordinator-plan-v1'])
    assert data.sha(original) == oldplan['specificationSha256'] == '647b2dd2006ac27f1ffe5fae19344395cae4fd18b6b348fb6400a2c5460a79ca'
    records = []
    for source,name,digest,proof,proofsha,label,classname,count in [
        ('5590eee0d766fdd48e56d95f6b33ce729accbd00','PG12896-reply-terminal-host-v1','26389dbc5e120a4897d864c8f7e8496f401620cf0ff846eb824959a181726fb0','PG12900-reply-terminal-post-v1','b7618d0a1c1e8f15aa08fae490abd8ec584245dd19bfb37288c545026d55a99f','TERM','ReplyCorrelationTerminalRaceTest',9),
        (CURRENT,'PG12922-coordinator-corrected-host-v1',PINS['PG12922-coordinator-corrected-host-v1'],'PG12926-coordinator-corrected-post-v1',PINS['PG12926-coordinator-corrected-post-v1'],'RECOVERY','JmsRequestReplyCleanupTest',17)]:
        host = data.read_checked(data.BASE/name/'manifest.json',digest)
        post = data.read_checked(data.BASE/proof/'manifest.json',proofsha)
        assert host['source'] == post['source'] == source and host['actualExit'] == post['actualExit'] == 0
        assert host['observedTestExecutions'] == count and not host['oldExecUnion']
        selected = [r for r in host['begin']['cases'] if r['className'].endswith('.'+classname)]
        assert len(selected) == 4
        records.append(dict(source=source,run=host['sessionId'],hostManifest=name+'/manifest.json',hostSha256=digest,
            postManifest=proof+'/manifest.json',postSha256=proofsha,observedTestExecutions=count,
            newTestIdMappings=[dict(testId='PT-JMS-'+label+'-'+str(i).zfill(3),className=r['className'],method=r['method'],actual='PASS') for i,r in enumerate(selected,1)],
            noCrossSourceCoverageUnion=True))
    verify(invocation); out.mkdir(); index.mkdir()
    with (out/'2393-original-spec-before-erratum.md').open('xb') as stream: stream.write(original)
    data.write(index/'manifest.json',dict(actualExit=0,program='NK-MSG-001',records=records,newUniqueTestIds=8,
        aggregateProductPassCount=None,aggregateCoverage=None,metadataProductExecutions=0,fullProgramAccepted=False,
        formalUpdated=False,newAccepted=0,whole451Accepted=False,sourceDomainsSeparated=True,
        reason='Two historical source domains; test counts and coverage not added across runs',invocation=invocation))
    data.write(out/'manifest.json',dict(actualExit=0,source=CURRENT,invocation=invocation,manifests=PINS,
        documents={str(p.relative_to(data.ROOT)):data.sha(p.read_bytes()) for p in docs},
        originalSpecificationPath=str((out/'2393-original-spec-before-erratum.md').relative_to(data.ROOT)),originalSpecificationSha256=data.sha(original),
        programIndexPath=str((index/'manifest.json').relative_to(data.ROOT)),programIndexSha256=data.sha((index/'manifest.json').read_bytes()),
        currentProductTests=17,newBusinessTestIds=4,selectedMainFourCounters100=True,
        fullArtifactCoverage100=False,staticGateExit=1,newAccepted=0,whole451Accepted=False,externalActions=0))
    print(json.dumps(dict(completionSha256=data.sha((out/'manifest.json').read_bytes()))))
    scan.OUT = data.BASE/'PG12932-coordinator-public-v1'
    scan.BEFORE = '67ed1d10307e9ec86c3712e8dfcf99a9bd1f72ca'
    scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg129',
        'tools/quality/architecture/CoordinatorRecoveryJunitLauncher.java',
        'tools/quality/architecture/CoordinatorRecoveryArtifactCoverageMeasure.java')
    scan.main()

if __name__ == '__main__': main()
