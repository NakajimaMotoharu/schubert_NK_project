"""Bound limited business result then explicit public delta scan, never whole451 acceptance."""
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg12706_scenario_writer_public as scan

PINS = {
    'PG12892-reply-terminal-six-compile-v1':'f018c19fbaabdc7de2253f8b12a57c86a532177ea40fc9b5448b461aa20ce532',
    'PG12894-reply-terminal-plan-v1':'5b7db8a9c0f9b54a64a7a7fa5503c5b7710a45a38804479848606870e7492243',
    'PG12896-reply-terminal-host-v1':'26389dbc5e120a4897d864c8f7e8496f401620cf0ff846eb824959a181726fb0',
    'PG12898-reply-terminal-static-v1':'1b6116f3dd3e95f3b75dca863c4055be4562cb4fa10fa6e142ac91d72535b64f',
    'PG12900-reply-terminal-post-v1':'b7618d0a1c1e8f15aa08fae490abd8ec584245dd19bfb37288c545026d55a99f',
    'PG12902-reply-terminal-trace-v1':'abc790d1356a461040d3dfe52c9db8ffb1cf9f6736a3ee200db4cb74c1d68590',
    'PG12903-reply-terminal-trace-post-v1':'e3f2afddff06f0825c4345a5ad23d2637c78391542b744ebfaf42e7b680a8a6a',
    'PG12904-reply-terminal-context-v1':'1be2332707417257212e82bd6693ba6233553fc4741a5ae57e4c3bbcb844533f',
    'PG12905-reply-terminal-context-post-v1':'daf29ad45be69a1158e12219396b998571ec88e12cdc48b0ca18d96611ed9070'}

def main():
    invocation = capture(__file__)
    out = data.BASE/'PG12906-reply-terminal-completion-v1'; assert not out.exists()
    for name,digest in PINS.items():
        v = data.read_checked(data.BASE/name/'manifest.json',digest)
        assert v['source'] == '5590eee0d766fdd48e56d95f6b33ce729accbd00'
        assert v['actualExit'] == (1 if 'static-v1' in name else 0)
    docs = [data.ROOT/'evidence/01_PT/018_NK-OPS-001'/name for name in ['2391_P005応答終端競合_単体テスト仕様書.md','2392_P005応答終端競合_実行結果.md']]
    for digest in PINS.values(): assert digest in docs[1].read_text()
    verify(invocation); out.mkdir()
    data.write(out/'manifest.json',dict(actualExit=0,source='5590eee0d766fdd48e56d95f6b33ce729accbd00',invocation=invocation,
        manifests=PINS,documents={str(p.relative_to(data.ROOT)):data.sha(p.read_bytes()) for p in docs},
        observedProductTests=9,newBusinessTestIds=4,selectedMainFourCounters100=True,
        fullArtifactCoverage100=False,staticGateExit=1,newAccepted=0,whole451Accepted=False,externalActions=0))
    print(json.dumps(dict(completionSha256=data.sha((out/'manifest.json').read_bytes()))))
    scan.OUT = data.BASE/'PG12906-reply-terminal-public-v1'
    scan.BEFORE = '4dd2d47bd292bc22ef4ae75fa54c4e0365ba4489'
    scan.PREFIXES = (*scan.PREFIXES,'tools/quality/pg128','tools/quality/pg129',
        'tools/quality/architecture/ReplyTerminalRaceJunitLauncher.java',
        'tools/quality/architecture/ReplyTerminalRaceArtifactCoverageMeasure.java')
    scan.main()

if __name__ == '__main__': main()
