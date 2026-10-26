"""Independent five-source reverse contract with eight negative metadata vectors; no PT."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical
from pg10339_result_profile_oracle_post_v2 import folded

OUT = data.BASE/'PG10796-protocol-residual-source-post-v1'


def replace_one(values,old,new):
    needle,replacement = canonical(old),canonical(new)
    positions = [i for i in range(len(values)-len(needle)+1) if values[i:i+len(needle)] == needle]
    if len(positions) != 1:
        raise ValueError('exact approved correction required')
    i = positions[0]
    return values[:i]+replacement+values[i+len(needle):]


def ending(values,start,left,right):
    assert values[start] == left
    depth = 0
    for index in range(start,len(values)):
        if values[index] == left: depth += 1
        elif values[index] == right:
            depth -= 1
            if depth == 0: return index
    raise ValueError('unbalanced source tokens')


def check(name,before,after):
    values = canonical(after)
    if name == 'HeaderModelTest.java':
        names = ('protocol','headerVersion','layoutId','layoutVersion','kind','interaction','correlationId','sentAt',
            'context','headerLength','dataLength','recordLength','recordCount','totalLength','result')
        for old in names:
            if values.count(old+'Value') != 3:
                raise ValueError('one declaration/assignment/build argument per private field')
            values = [old if token == old+'Value' else token for token in values]
    if name == 'LargeResultRecordCodecTest.java':
        values = replace_one(values,'import java.security.NoSuchAlgorithmException;','')
        if values.count('NoSuchAlgorithmException') != 2:
            raise ValueError('exact narrowed JCA catch pair required')
        values = ['Exception' if token == 'NoSuchAlgorithmException' else token for token in values]
        owners = []
        while True:
            candidates = [i for i in range(len(values)-1) if values[i:i+2] == ['try','(']]
            if not candidates: break
            start = candidates[-1]
            end = ending(values,start+1,'(',')')
            assert values[end+1] == '{'
            close = ending(values,end+1,'{','}')
            declaration = values[start+2:end]
            assert len(declaration) > 3
            owners.append((declaration[0],declaration[1]))
            values = values[:start]+declaration+[';']+values[end+2:close]+values[close+1:]
        if sorted(owners) != sorted([('CountingOutputStream','output'),('OutputStream','broken'),('InputStream','broken'),('InputStream','zeroThenEof')]):
            raise ValueError('all four exact fixture owners require TWR')
        for method in ('acceptsTheDocumentedTenThousandRecordFortyEightMillionByteMaximum',
            'writeRejectsNullCountLengthAndIoFailure','decodeRejectsTruncationExtraHashAndIoFailure'):
            values = replace_one(values,'void '+method+'() throws IOException {','void '+method+'() {')
        values = replace_one(values,'if (offset >= value.length) return -1; int next = Byte.toUnsignedInt(value[offset]); offset++; return next;',
            'return offset >= value.length ? -1 : Byte.toUnsignedInt(value[offset++]);')
    if name in ('PayloadGoldenVectorTest.java','PayloadTypeCatalogTest.java'):
        values = replace_one(values,'for (String line = reader.readLine(); line != null; line = reader.readLine()) {',
            'for (String line; (line = reader.readLine()) != null; ) {')
    if name == 'IndependentNamedFieldOracle.java':
        values = replace_one(values,'index++; FieldValue wire = independentWire(field, scalar, index);',
            'FieldValue wire = independentWire(field, scalar, ++index);')
        values = replace_one(values,'private static final int JST_WIRE_DIGITS = 17;','')
        if values.count('JST_WIRE_DIGITS') != 1:
            raise ValueError('one independent JST length predicate')
        values = [part for token in values for part in (canonical('17') if token == 'JST_WIRE_DIGITS' else [token])]
    if name in ('IndependentNamedFieldOracle.java','PayloadTypeCatalogTest.java'):
        values = replace_one(values,'private static final int UUID_TEXT_LENGTH = 36;','')
        if values.count('UUID_TEXT_LENGTH') != 1:
            raise ValueError('one independent UUID length predicate')
        values = [part for token in values for part in (canonical('36') if token == 'UUID_TEXT_LENGTH' else [token])]
    if folded(values) != canonical(before):
        raise ValueError('unrelated assertion/fixture/owner order changed')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    plan = data.read_checked(data.BASE/'PG10794-protocol-residual-plan-v1/manifest.json',
        'b506b8f013e48e2c1c4f93161fe08f0eb3f44bd29f69f1ca8af1f23de69196ab')
    normal = data.read_checked(data.BASE/'PG10778-protocol-fixture-batch-six-compile-v1/manifest.json',
        'f0b3a2df7892710085ec00739c49c8d0a6d0a7da8d3dc9d4ccee8d75b6214462')
    snapshot = Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    changed = {r['path'] for r in plan['sourceChanges']}
    assert len(changed) == 5 and plan['actualExit'] == 0
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p not in changed)
    texts = {}
    for row in plan['sourceChanges']:
        before,after = (snapshot/row['path']).read_text(),(data.ROOT/row['path']).read_text()
        assert data.sha(before.encode()) == row['beforeSha256'] and data.sha(after.encode()) == row['sha256']
        name = Path(row['path']).name
        check(name,before,after)
        texts[name] = (before,after)
    vectors = [
        ('HeaderModelTest.java','protocolValue','protocolWrong'),
        ('LargeResultRecordCodecTest.java','catch (NoSuchAlgorithmException','catch (Exception'),
        ('LargeResultRecordCodecTest.java','try (CountingOutputStream output','try (OutputStream output'),
        ('IndependentNamedFieldOracle.java','JST_WIRE_DIGITS = 17','JST_WIRE_DIGITS = 18'),
        ('IndependentNamedFieldOracle.java','index++;',''),
        ('PayloadGoldenVectorTest.java','reader.readLine()','reader.skip(1)'),
        ('PayloadTypeCatalogTest.java','@Test','@Disabled'),
        ('LargeResultRecordCodecTest.java','offset++;','offset--;')]
    for name,old,new in vectors:
        before,after = texts[name]
        assert old in after
        bad = after.replace(old,new,1)
        assert bad != after
        try:
            check(name,before,bad)
        except ValueError:
            pass
        else:
            raise AssertionError('wrong order/value/TWR/assertion accepted')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,sourceBefore=normal['source'],sourceChanges=plan['sourceChanges'],
        metadataNegativeVectors=len(vectors),allMainAndOtherInputBytesPreserved=True,productTestsExecuted=0,coverage=None,
        correctedFindingCount=28,preservedContextCandidates=10,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
