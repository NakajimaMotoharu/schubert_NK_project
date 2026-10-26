"""One independent uppercase UUID fixture; no Main changes or target execution."""
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical

OUT = data.BASE/'PG10732-protocol-uppercase-fixture-plan-v1'
TEST = 'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/layout/SemanticFieldValueTest.java'
VALUE = '123E4567-E89B-12D3-A456-426614174000'
DECLARATION = '  private static final String UUID_UPPERCASE_TEXT = "'+VALUE+'";\n'


def transformed(before):
    anchor = '  private static final String UUID_TEXT = "123e4567-e89b-12d3-a456-426614174000";\n'
    assert before.count(anchor) == before.count('UUID_TEXT.toUpperCase()') == 1 and 'UUID_UPPERCASE_TEXT' not in before
    return before.replace(anchor,anchor+DECLARATION,1).replace('UUID_TEXT.toUpperCase()','UUID_UPPERCASE_TEXT',1)


def validate(before,after):
    if canonical(after) != canonical(transformed(before)):
        raise ValueError('one explicit fixed UUID declaration and input substitution only')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal_path = data.BASE/'PG10714-graph-constants-six-compile-v1/manifest.json'
    normal = data.read_checked(normal_path,'b24ac5ef1f85b9ed935e0772ef04040acbd12b78f573a88aa4d9420ae4995676')
    assert normal['source'] == '68278a0402137b8f27c3714d6d3c00848ccf0f49' and normal['actualExit'] == normal['testsExecuted'] == 0
    snapshot = Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    before = (snapshot/TEST).read_text()
    after = (data.ROOT/TEST).read_text()
    assert data.sha(before.encode()) == normal['begin']['inputHashes'][TEST]
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p != TEST)
    validate(before,after)
    assert len(VALUE.encode('ascii')) == 36 and re.fullmatch(r'[0-9A-F]{8}(?:-[0-9A-F]{4}){3}-[0-9A-F]{12}',VALUE)
    assert VALUE.lower() == '123e4567-e89b-12d3-a456-426614174000'
    negatives = 0
    for invalid in (after.replace(VALUE,'923E4567-E89B-12D3-A456-426614174000',1),
        after.replace('20260230000000000L','20260228000000000L',1),
        after.replace('UUID_UPPERCASE_TEXT','UNREVIEWED_UUID',1)):
        assert invalid != after
        try:
            validate(before,invalid)
        except ValueError:
            negatives += 1
        else:
            raise AssertionError('changed oracle/fixture/source accepted')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,baseSource=normal['source'],invocation=invocation,
        sourceChanges=[dict(path=TEST,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),
            canonicalOwner='WBS-P001-03',canonicalCostOwner='WBS-P001-03')],fixtureAsciiBytes=36,
        independentUppercaseUuidLiteral=VALUE,metadataNegativeVectors=negatives,mainAndOtherInputBytesUnchanged=True,
        productTestsExecuted=0,externalActions=0,coverage=None,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
