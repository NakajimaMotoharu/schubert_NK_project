"""Classfile Code/debug hashes only; CP indices are raw representation, never a semantic proof."""
import hashlib
import json
import struct
from classfile_code_metadata import Reader,decode

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def parts(raw,entry):
    model=decode(raw,entry);r=Reader(raw);r.take(8);count=r.u(2);pool={};i=1
    while i<count:
        tag=r.u(1)
        if tag==1:pool[i]=r.take(r.u(2))
        elif tag in (3,4):r.take(4)
        elif tag in (5,6):r.take(8);i+=1
        elif tag in (7,8,16,19,20):r.take(2)
        elif tag in (9,10,11,12,17,18):r.take(4)
        elif tag==15:r.take(3)
        else:raise ValueError('unsupported pool tag')
        i+=1
    def text(i):return pool[i].decode('ascii')
    def attrs(reader):return [(text(reader.u(2)),reader.take(reader.u(4))) for _ in range(reader.u(2))]
    r.take(6);r.take(2*r.u(2))
    for _ in range(r.u(2)):r.take(6);attrs(r)
    core,debug={},{}
    for _ in range(r.u(2)):
        flag,name,desc=r.u(2),text(r.u(2)),text(r.u(2));attributes=attrs(r);key=name+desc
        for label,body in attributes:
            if label!='Code':continue
            c=Reader(body);head=c.take(4);code=c.take(c.u(4));handlers=c.take(8*c.u(2));children=attrs(c);c.end();dbg=[(n,b.hex()) for n,b in children if n in ('LineNumberTable','LocalVariableTable','LocalVariableTypeTable')];other=[(n,b.hex()) for n,b in children if n not in ('LineNumberTable','LocalVariableTable','LocalVariableTypeTable')]
            assert key not in core;core[key]=digest(dict(flags=flag,head=head.hex(),instructions=code.hex(),handlers=handlers.hex(),otherAttributes=other));debug[key]=digest(dbg)
    attrs(r);r.end();assert len(core)==sum(m['hasCode'] for m in model['methods'])
    return dict(model=model,rawCodeRepresentationSha256=digest(core),debugTablesSha256=digest(debug),methodsRawCode=core,methodsDebugTables=debug)

def selftest():
    def utf(s):
        value=s.encode('ascii');return b'\x01'+struct.pack('>H',len(value))+value
    cp=b''.join(utf(s) if isinstance(s,str) else s for s in ('p/T',b'\x07\x00\x01','SourceFile','T.java','m','()V','Code','LineNumberTable'))
    def fixture(instructions,line):
        debug=struct.pack('>3H',1,0,line);code=struct.pack('>HHI',0,0,len(instructions))+instructions+struct.pack('>HHHI',0,1,8,len(debug))+debug
        return bytes.fromhex('cafebabe000000450009')+cp+struct.pack('>10H',0x21,2,0,0,0,1,9,5,6,1)+struct.pack('>HI',7,len(code))+code+struct.pack('>HHIH',1,3,2,4)
    good=fixture(b'\xb1',7);a=parts(good,'p/T.class');b=parts(fixture(b'\xb1',8),'p/T.class');c=parts(fixture(b'\x00\xb1',7),'p/T.class');assert a['rawCodeRepresentationSha256']==b['rawCodeRepresentationSha256'] and a['debugTablesSha256']!=b['debugTablesSha256'];assert a['rawCodeRepresentationSha256']!=c['rawCodeRepresentationSha256'] and a['debugTablesSha256']==c['debugTablesSha256'];assert len(a['methodsRawCode'])==1
    rejected=0
    for raw in (good[:-1],good+b'\0',b'\0'+good[1:]):
        try:parts(raw,'p/T.class')
        except ValueError:rejected+=1
        else:raise AssertionError('invalid classfile metadata accepted')
    try:parts(good,'p/Other.class')
    except ValueError:rejected+=1
    else:raise AssertionError('foreign binary metadata accepted')
    return dict(positiveVectors=3,negativeVectors=rejected,noClassDefined=True)
