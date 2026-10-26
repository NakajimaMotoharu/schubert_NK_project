"""Five Test/helper sources:28specific static corrections, no Main/oracle change."""
import difflib
from pathlib import Path
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical

OUT = data.BASE/'PG10794-protocol-residual-plan-v1'
PREFIX = 'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/'
FILES = ('header/HeaderModelTest.java','file/LargeResultRecordCodecTest.java',
    'codec/PayloadGoldenVectorTest.java','layout/IndependentNamedFieldOracle.java','layout/PayloadTypeCatalogTest.java')
FIELDS = ('protocol','headerVersion','layoutId','layoutVersion','kind','interaction','correlationId','sentAt',
    'context','headerLength','dataLength','recordLength','recordCount','totalLength','result')


def once(text,old,new):
    assert text.count(old) == 1,(old,text.count(old))
    return text.replace(old,new,1)


def wrapped(text,declaration):
    # Only the existing owner declaration through this fixed JUnit method tail.
    start = text.index(declaration)
    line_start = text.rfind('\n',0,start)+1
    assert text[line_start:start].strip() == ''
    indent = text[line_start:start]
    depth,end = 0,None
    for match in LEX.finditer(text,start):
        token = match.group()
        if token in ('{','(','['): depth += 1
        elif token in ('}',')',']'): depth -= 1
        elif token == ';' and depth == 0:
            end = match.end()
            break
    assert end is not None
    finish = text.index('\n  }',end)
    statement = text[start:end-1]
    body = text[end:finish]
    body = '\n'.join('  '+line if line else line for line in body.split('\n'))
    return text[:line_start]+indent+'try ('+statement+') {'+body+'\n'+indent+'}'+text[finish:]


def transformed(name,text):
    if name == 'HeaderModelTest.java':
        start = text.index('  private static final class HeaderBuilder {')
        before,tail = text[:start],text[start:]
        tokens = list(LEX.finditer(tail))
        for index in range(len(tokens)-1,-1,-1):
            match = tokens[index]
            if match.group() in FIELDS and (index+1 == len(tokens) or tokens[index+1].group() != '('):
                tail = tail[:match.start()]+match.group()+'Value'+tail[match.end():]
        return before+tail
    if name == 'LargeResultRecordCodecTest.java':
        text = once(text,'import java.security.MessageDigest;','import java.security.MessageDigest;\nimport java.security.NoSuchAlgorithmException;')
        assert text.count('catch (Exception exception)') == 2
        text = text.replace('catch (Exception exception)','catch (NoSuchAlgorithmException exception)')
        text = once(text,'      return offset >= value.length ? -1 : Byte.toUnsignedInt(value[offset++]);',
            '      if (offset >= value.length) return -1;\n      int next = Byte.toUnsignedInt(value[offset]);\n      offset++;\n      return next;')
        for declaration in ('CountingOutputStream output = new CountingOutputStream();',
            'OutputStream broken =','InputStream zeroThenEof =','InputStream broken ='):
            text = wrapped(text,declaration)
        for method in ('acceptsTheDocumentedTenThousandRecordFortyEightMillionByteMaximum',
            'writeRejectsNullCountLengthAndIoFailure','decodeRejectsTruncationExtraHashAndIoFailure'):
            text = once(text,'void '+method+'() {','void '+method+'() throws IOException {')
        return text
    if name in ('PayloadGoldenVectorTest.java','PayloadTypeCatalogTest.java'):
        text = once(text,'for (String line; (line = reader.readLine()) != null; ) {',
            'for (String line = reader.readLine(); line != null; line = reader.readLine()) {')
    if name == 'IndependentNamedFieldOracle.java':
        text = once(text,'FieldValue wire = independentWire(field, scalar, ++index);',
            'index++;\n      FieldValue wire = independentWire(field, scalar, index);')
        text = once(text,'class IndependentNamedFieldOracle {\n',
            'class IndependentNamedFieldOracle {\n  private static final int JST_WIRE_DIGITS = 17;\n  private static final int UUID_TEXT_LENGTH = 36;\n')
        text = once(text,'field.length() == 17','field.length() == JST_WIRE_DIGITS')
        text = once(text,'field.length() == 36','field.length() == UUID_TEXT_LENGTH')
    if name == 'PayloadTypeCatalogTest.java':
        text = once(text,'class PayloadTypeCatalogTest {\n',
            'class PayloadTypeCatalogTest {\n  private static final int UUID_TEXT_LENGTH = 36;\n')
        text = once(text,'field.length() == 36','field.length() == UUID_TEXT_LENGTH')
    return text


def inputs():
    normal = data.read_checked(data.BASE/'PG10778-protocol-fixture-batch-six-compile-v1/manifest.json',
        'f0b3a2df7892710085ec00739c49c8d0a6d0a7da8d3dc9d4ccee8d75b6214462')
    assert normal['actualExit'] == normal['testsExecuted'] == 0
    return normal,Path(normal['jars']['protocol']['path']).parent.parent.parent.parent


def emit():
    _,snapshot = inputs()
    patch = '*** Begin Patch\n'
    for relative in FILES:
        path = PREFIX+relative
        before = (snapshot/path).read_text()
        assert (data.ROOT/path).read_text() == before
        after = transformed(Path(path).name,before)
        assert before != after
        patch += '*** Update File: '+str(data.ROOT/path)+'\n'
        patch += '\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal,snapshot = inputs()
    paths = {PREFIX+p for p in FILES}
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p not in paths)
    rows = []
    for path in sorted(paths):
        before,after = (snapshot/path).read_text(),(data.ROOT/path).read_text()
        assert canonical(after) == canonical(transformed(Path(path).name,before)),path
        rows.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode())))
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,sourceBefore=normal['source'],sourceChanges=rows,
        privateFieldRenames=15,narrowedCatchTypes=2,separatedOperandUpdates=4,independentLengthConstants=3,
        ownerTryWithResources=4,expectedRawFindingsRemoved=28,remainingContextCandidates=10,
        allMainAndOtherInputBytesPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
