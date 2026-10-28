"""Stage-specific public record/source schema; no target test or historical helper replay."""
import re
import g07_host_class_provenance_inputs as data
import pg13480_positioned_literal_config as original
import pg13481_positioned_literal_config_v2 as recovery
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG13498-positioned-record-path-schema-post-v1'
ACTUAL = 'evidence/01_PT/018_NK-OPS-001/2470_位置bound22Test91件_製造静的結果.md'
SOURCE = 'ff8149dd27decbe683b48d1cbb5f2cb59ecca83a'
EXPECTED = {number:original.BASE_SOURCE if number in (13482,13483) else None if number == 13485 else SOURCE
            for number in (13482,13483,13485,13486,13488,13490,13491,13492,13493,13495)}

def validate(number,value):
    assert number in EXPECTED and 'source' in value and value['source'] == EXPECTED[number]
    assert type(value['actualExit']) is int and value['actualExit'] == 0

def main():
    invocation = capture(__file__)
    assert not OUT.exists() and original.RECORD == recovery.RECORD and original.RECORD != ACTUAL
    planned,actual = data.ROOT/original.RECORD,data.ROOT/ACTUAL
    assert planned.is_file() and actual.is_file() and not planned.is_symlink() and not actual.is_symlink()
    index,body = planned.read_text(),actual.read_text()
    assert ']('+actual.name+')' in index and 'BUG2059/YKT1807' in index and SOURCE in index and SOURCE in body
    rows = re.findall(r'\| (PG\S+) \| ([a-f0-9]{64}) \|',body)
    assert len(rows) == len({name for name,_ in rows}) == 10
    manifests = []
    for name,pin in rows:
        value = data.read_checked(data.BASE/name/'manifest.json',pin)
        number = int(re.match(r'PG([0-9]+)-',name).group(1))
        validate(number,value)
        manifests.append(dict(run=name,sha256=pin,source=value['source']))
    for number,value in [(13486,dict(source=None,actualExit=0)),(13485,dict(actualExit=0)),
                         (13483,dict(source=SOURCE,actualExit=0)),(13485,dict(source=None,actualExit=True))]:
        try:
            validate(number,value)
        except AssertionError:
            pass
        else:
            raise AssertionError('incorrect stage/source schema accepted')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,plannedRecord=original.RECORD,
        plannedRecordSha256=data.sha(planned.read_bytes()),actualRecord=ACTUAL,actualRecordSha256=data.sha(actual.read_bytes()),
        linkedManifestCount=len(manifests),manifests=manifests,metadataNegativeVectors=4,original13497ActualExit=1,
        immutableConfigsNotModified=True,originalEventPreserved=True,productTestsExecuted=0,newAccepted=0,
        formalUpdated=False,wholeTraceAccepted=False,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
