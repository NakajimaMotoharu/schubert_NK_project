"""Independent bounded binary classfile metadata decoder; never loads a class or executes code."""
import struct


class Reader:
    def __init__(self, raw):
        self.raw = raw
        self.pos = 0

    def take(self, count):
        if count < 0 or self.pos + count > len(self.raw):
            raise ValueError('truncated classfile metadata')
        result = self.raw[self.pos:self.pos + count]
        self.pos += count
        return result

    def u(self, width):
        return int.from_bytes(self.take(width),'big')

    def end(self):
        if self.pos != len(self.raw):
            raise ValueError('unconsumed classfile metadata')


def decode(raw, entry):
    r = Reader(raw)
    if r.u(4) != 0xcafebabe or r.u(2) != 0 or r.u(2) != 69:
        raise ValueError('fixed Java25 non-preview format required')
    count = r.u(2)
    if count < 2:
        raise ValueError('constant pool required')
    cp = [None] * count
    index = 1
    while index < count:
        tag = r.u(1)
        if tag == 1:
            cp[index] = (tag,r.take(r.u(2)))
        elif tag in (3,4):
            cp[index] = (tag,r.take(4))
        elif tag in (5,6):
            if index + 1 >= count:
                raise ValueError('two-slot constant overflows pool')
            cp[index] = (tag,r.take(8))
            index += 1
        elif tag in (7,8,16,19,20):
            cp[index] = (tag,r.u(2))
        elif tag in (9,10,11,12,17,18):
            cp[index] = (tag,r.take(4))
        elif tag == 15:
            cp[index] = (tag,r.take(3))
        else:
            raise ValueError('unknown constant pool tag')
        index += 1

    def item(i, kind):
        if not 0 < i < count or cp[i] is None or cp[i][0] != kind:
            raise ValueError('typed constant pool reference required')
        return cp[i][1]

    def text(i):
        try:
            return item(i,1).decode('ascii')
        except UnicodeDecodeError as ex:
            raise ValueError('ASCII structural identity required') from ex

    def attrs(reader):
        return [(text(reader.u(2)),reader.take(reader.u(4))) for _ in range(reader.u(2))]

    flags, this, superclass = r.u(2),r.u(2),r.u(2)
    name = text(item(this,7))
    if superclass:
        item(superclass,7)
    if entry != name + '.class':
        raise ValueError('binary identity differs from inventory')
    for _ in range(r.u(2)):
        item(r.u(2),7)
    fields = r.u(2)
    for _ in range(fields):
        r.u(2)
        text(r.u(2))
        text(r.u(2))
        attrs(r)
    methods = []
    for _ in range(r.u(2)):
        flag, method, descriptor = r.u(2),text(r.u(2)),text(r.u(2))
        codes = [value for label,value in attrs(r) if label == 'Code']
        if len(codes) > 1:
            raise ValueError('duplicate Code attribute')
        length = 0
        if codes:
            c = Reader(codes[0])
            c.u(2)
            c.u(2)
            length = c.u(4)
            if not 0 < length < 65536 or flag & (0x0100 | 0x0400):
                raise ValueError('Code length or native/abstract contract')
            c.take(length)
            for _ in range(c.u(2)):
                start,end,target,catch = [c.u(2) for _ in range(4)]
                if not 0 <= start < end <= length or not 0 <= target < length:
                    raise ValueError('exception table code bounds')
                if catch:
                    item(catch,7)
            attrs(c)
            c.end()
        elif not flag & (0x0100 | 0x0400):
            raise ValueError('concrete method missing Code')
        methods.append(dict(name=method,descriptor=descriptor,flags=flag,hasCode=bool(codes),codeLength=length))
    sources = [value for label,value in attrs(r) if label == 'SourceFile']
    if len(sources) != 1 or len(sources[0]) != 2:
        raise ValueError('one SourceFile required')
    source = text(int.from_bytes(sources[0],'big'))
    r.end()
    return dict(flags=flags,sourceFile=source,fields=fields,methods=methods)


def selftest():
    """Literal metadata only: no class definition, production fixture or invocation."""
    def utf(s):
        raw = s.encode('ascii')
        return b'\x01' + struct.pack('>H',len(raw)) + raw
    cp = utf('p/T') + b'\x07\x00\x01' + utf('SourceFile') + utf('T.java')
    prefix = bytes.fromhex('cafebabe000000450005') + cp
    # public interface; zero interfaces/fields/methods; one SourceFile attribute
    good = prefix + bytes.fromhex('06010002000000000000000000010003000000020004')
    assert decode(good,'p/T.class') == dict(flags=0x0601,sourceFile='T.java',fields=0,methods=[])
    negatives = [good[:cut] for cut in (0,4,8,10,len(good)-1)] + [good+b'\x00',b'\x00'+good[1:],good[:9]+b'\x01'+good[10:]]
    for bad in negatives:
        try:
            decode(bad,'p/T.class')
        except (ValueError,IndexError):
            pass
        else:
            raise AssertionError('invalid/truncated metadata accepted')
    try:
        decode(good,'p/Wrong.class')
    except ValueError:
        pass
    else:
        raise AssertionError('wrong class identity accepted')
    for tag,width in ((3,4),(4,4),(5,8),(6,8),(8,2),(9,4),(10,4),(11,4),(12,4),
                      (15,3),(16,2),(17,4),(18,4),(19,2),(20,2)):
        extra = bytes([tag]) + bytes(width)
        slots = 2 if tag in (5,6) else 1
        altered = good[:8] + struct.pack('>H',5+slots) + cp + extra + good[len(prefix):]
        assert decode(altered,'p/T.class')['sourceFile'] == 'T.java'
    bad_tag = good[:10] + b'\x02' + good[11:]
    try:
        decode(bad_tag,'p/T.class')
    except ValueError:
        pass
    else:
        raise AssertionError('unknown constant tag accepted')
    return 26


def code_vectors():
    """Static method-attribute vectors; byte arrays are never defined as Java classes."""
    def utf(s):
        raw = s.encode('ascii')
        return b'\x01' + struct.pack('>H',len(raw)) + raw
    cp = utf('p/T') + b'\x07\x00\x01' + utf('SourceFile') + utf('T.java') + utf('m') + utf('()V') + utf('Code')
    prefix = bytes.fromhex('cafebabe000000450008') + cp
    code = bytes.fromhex('0000000000000001b100000000')

    def build(flags, bodies, superclass=0):
        body = struct.pack('>7H',0x21,2,superclass,0,0,1,flags) + struct.pack('>3H',5,6,len(bodies))
        body += b''.join(struct.pack('>HI',7,len(value))+value for value in bodies)
        return prefix + body + bytes.fromhex('00010003000000020004')
    parsed = decode(build(9,[code]),'p/T.class')
    assert parsed['methods'] == [dict(name='m',descriptor='()V',flags=9,hasCode=True,codeLength=1)]
    assert decode(build(0x109,[]),'p/T.class')['methods'][0]['hasCode'] is False
    for raw in (build(9,[]),build(0x409,[code]),build(9,[code[:4]+bytes(4)+code[8:]]),
                build(9,[code[:-1]]),build(9,[code,code]),build(9,[code+b'\x00']),build(9,[code],superclass=1)):
        try:
            decode(raw,'p/T.class')
        except ValueError:
            pass
        else:
            raise AssertionError('invalid Code/superclass metadata accepted')
    return 9
