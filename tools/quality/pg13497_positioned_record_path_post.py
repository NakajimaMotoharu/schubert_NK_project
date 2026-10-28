"""Independent planned/actual public record path and complete manifest-table binding; no PT."""
import re
import g07_host_class_provenance_inputs as data
import pg13480_positioned_literal_config as original
import pg13481_positioned_literal_config_v2 as recovery
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG13497-positioned-record-path-post-v1'
ACTUAL = 'evidence/01_PT/018_NK-OPS-001/2470_位置bound22Test91件_製造静的結果.md'

def main():
    invocation = capture(__file__)
    assert not OUT.exists() and original.RECORD == recovery.RECORD and original.RECORD != ACTUAL
    planned,actual = data.ROOT/original.RECORD,data.ROOT/ACTUAL
    assert planned.is_file() and actual.is_file() and not planned.is_symlink() and not actual.is_symlink()
    index,body = planned.read_text(),actual.read_text()
    assert ']('+actual.name+')' in index and 'BUG2059/YKT1807' in index
    source = 'ff8149dd27decbe683b48d1cbb5f2cb59ecca83a'
    assert source in index and source in body
    rows = re.findall(r'\| (PG\S+) \| ([a-f0-9]{64}) \|',body)
    assert len(rows) == len({name for name,_ in rows}) == 10
    manifests = []
    for name,pin in rows:
        value = data.read_checked(data.BASE/name/'manifest.json',pin)
        assert value['actualExit'] == 0
        if 'source' in value:
            assert value['source'] in (source,original.BASE_SOURCE)
        manifests.append(dict(run=name,sha256=pin))
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=source,invocation=invocation,plannedRecord=original.RECORD,
        plannedRecordSha256=data.sha(planned.read_bytes()),actualRecord=ACTUAL,actualRecordSha256=data.sha(actual.read_bytes()),
        linkedManifestCount=len(manifests),manifests=manifests,immutableConfigsNotModified=True,originalEventPreserved=True,
        productTestsExecuted=0,newAccepted=0,formalUpdated=False,wholeTraceAccepted=False,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
