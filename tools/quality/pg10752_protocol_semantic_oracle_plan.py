"""One Test:9same-value literals,7primitive expected values,1uppercase redaction guard."""
import difflib
from pathlib import Path
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical
from public_java_digest_provenance import LEX

OUT = data.BASE/'PG10752-protocol-semantic-oracle-plan-v1'
TEST = 'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/layout/SemanticFieldValueTest.java'
CONSTANTS = (
    ('SAFE_TEXT','"safe"',7),('RELATIVE_PATH_TEXT','"scenario/game/file.txt"',4),
    ('DISPLAY_PATH_TEXT','"表示/台本"',4),('UNSET_FIELD_NAME','"unset"',8),('VALUE_FIELD_NAME','"value"',12),
    ('INVALID_SEMANTIC_TEXT','"invalid"',5),('ABSOLUTE_PATH_TEXT','"/absolute"',4),
    ('NFC_RELATIVE_PATH_TEXT','"scenario/é/file.txt"',5),('NFC_DISPLAY_PATH_TEXT','"表示/é"',5))
ASSERTIONS = (
    ('assertEquals(\n        Optional.of(authentication),\n        TypedFieldValues.optionalAuthenticationContext(fields, "authentication"));',
     'assertEquals(Optional.of(HEX_A), TypedFieldValues.optionalAuthenticationContext(fields, "authentication").map(AuthenticationContext::wireValue));'),
    ('assertEquals(sha256, TypedFieldValues.requiredSha256(fields, "sha"));',
     'assertEquals(HEX_A, TypedFieldValues.requiredSha256(fields, "sha").wireValue());'),
    ('assertEquals(Optional.of(sha256), TypedFieldValues.optionalSha256(fields, "sha"));',
     'assertEquals(Optional.of(HEX_A), TypedFieldValues.optionalSha256(fields, "sha").map(Sha256Hex::wireValue));'),
    ('assertEquals(relativePath, TypedFieldValues.requiredRelativePath(fields, "relative"));',
     'assertEquals(RELATIVE_PATH_TEXT, TypedFieldValues.requiredRelativePath(fields, "relative").wireValue());'),
    ('assertEquals(\n        Optional.of(relativePath), TypedFieldValues.optionalRelativePath(fields, "relative"));',
     'assertEquals(Optional.of(RELATIVE_PATH_TEXT), TypedFieldValues.optionalRelativePath(fields, "relative").map(RelativePath::wireValue));'),
    ('assertEquals(displayPath, TypedFieldValues.requiredDisplayPath(fields, "display"));',
     'assertEquals(DISPLAY_PATH_TEXT, TypedFieldValues.requiredDisplayPath(fields, "display").wireValue());'),
    ('assertEquals(Optional.of(displayPath), TypedFieldValues.optionalDisplayPath(fields, "display"));',
     'assertEquals(Optional.of(DISPLAY_PATH_TEXT), TypedFieldValues.optionalDisplayPath(fields, "display").map(DisplayPath::wireValue));'))
UPPER_GUARD = '    assertFalse(exception.getMessage().contains(UUID_UPPERCASE_TEXT));\n'


def transformed(before):
    for name,_,_ in CONSTANTS:
        assert not any(m.group() == name for m in LEX.finditer(before))
    result = before
    for old,new in ASSERTIONS:
        assert result.count(old) == 1
        result = result.replace(old,new,1)
    lower_guard = '    assertFalse(exception.getMessage().contains(UUID_TEXT));\n'
    assert result.count(lower_guard) == 1 and UPPER_GUARD not in result
    result = result.replace(lower_guard,lower_guard+UPPER_GUARD,1)
    table = {literal:name for name,literal,_ in CONSTANTS}
    tokens = list(LEX.finditer(result))
    for _,literal,count in CONSTANTS:
        assert sum(m.group() == literal for m in tokens) == count
    for match in reversed(tokens):
        if match.group() in table:
            result = result[:match.start()]+table[match.group()]+result[match.end():]
    header = 'class SemanticFieldValueTest {\n'
    assert result.count(header) == 1
    declarations = ''.join('  private static final String '+name+' = '+literal+';\n' for name,literal,_ in CONSTANTS)
    return result.replace(header,header+declarations,1)


def validate(before,after):
    if canonical(after) != canonical(transformed(before)):
        raise ValueError('exact9literal/7primitive assertions/1uppercase guard only')


def baseline():
    normal = data.read_checked(data.BASE/'PG10736-protocol-uppercase-six-compile-v1/manifest.json',
        '5bfb5e23af7295e2d163f7b8de21d2290c14ffb6eba8339e654ff4c56ae86492')
    assert normal['source'] == '21d275a74fb7ec8bb3a5d39f168d561f03c5b9a7' and normal['actualExit'] == normal['testsExecuted'] == 0
    return normal,Path(normal['jars']['protocol']['path']).parent.parent.parent.parent


def emit():
    _,snapshot = baseline()
    before = (snapshot/TEST).read_text()
    assert (data.ROOT/TEST).read_text() == before
    after = transformed(before)
    patch = '*** Begin Patch\n*** Update File: '+str(data.ROOT/TEST)+'\n'
    for line in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:]:
        patch += ('@@' if line.startswith('@@') else line)+'\n'
    return patch+'*** End Patch\n'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal,snapshot = baseline()
    before = (snapshot/TEST).read_text()
    after = (data.ROOT/TEST).read_text()
    assert data.sha(before.encode()) == normal['begin']['inputHashes'][TEST]
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p != TEST)
    validate(before,after)
    negatives = 0
    for invalid in (after.replace('SAFE_TEXT = "safe"','SAFE_TEXT = "wrong"',1),
        after.replace('.map(Sha256Hex::wireValue)','.map(Object::toString)',1),
        after.replace(UPPER_GUARD,''),after.replace('e\\u0301','é',1)):
        assert invalid != after
        try:
            validate(before,invalid)
        except ValueError:
            negatives += 1
        else:
            raise AssertionError('wrong value/oracle/redaction/normalization accepted')
    counts = {name:sum(m.group() == name for m in LEX.finditer(after))-1 for name,_,_ in CONSTANTS}
    assert sum(counts.values()) == 58 and counts['RELATIVE_PATH_TEXT'] == counts['DISPLAY_PATH_TEXT'] == 6
    assert negatives == 4 and after.count('contains(UUID_UPPERCASE_TEXT)') == 1
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,baseSource=normal['source'],invocation=invocation,
        sourceChanges=[dict(path=TEST,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),canonicalOwner='WBS-P001-03',canonicalCostOwner='WBS-P001-03')],
        constants=[dict(name=n,literal=v,originalReferences=c,currentReferences=counts[n]) for n,v,c in CONSTANTS],
        constantsAdded=9,originalLiteralReferencesReplaced=54,currentConstantReferences=58,
        expectedFactoryAssertionsReplaced=7,uppercaseRedactionAssertionsAdded=1,metadataNegativeVectors=4,
        allMainAndOtherInputBytesPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
