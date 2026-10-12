"""Exact class byte equality except fixed LineNumberTable line +1, not an exclusion.

Code, constant pool, stack maps, attributes and line bytecode offsets must remain
byte-identical. Both actual class identities are retained for CRC/coverage.
"""
import struct

def positions(raw):
    if type(raw)is not bytes:raise ValueError('class bytes required')
    p=0;names={};lines=[]
    def take(n):
        nonlocal p
        if n<0 or p+n>len(raw):raise ValueError('truncated class')
        v=raw[p:p+n];p+=n;return v
    def u2():return int.from_bytes(take(2),'big')
    def u4():return int.from_bytes(take(4),'big')
    if take(4)!=b'\xca\xfe\xba\xbe':raise ValueError('class magic')
    take(4);count=u2();i=1
    while i<count:
        tag=take(1)[0]
        if tag==1:names[i]=take(u2()).decode('utf8')
        elif tag in [7,8,16,19,20]:take(2)
        elif tag in [3,4,9,10,11,12,17,18]:take(4)
        elif tag in [5,6]:take(8);i+=1
        elif tag==15:take(3)
        else:raise ValueError('class constant tag')
        i+=1
    def attributes(n, code=False):
        nonlocal p
        for _ in range(n):
            name=names.get(u2());size=u4();end=p+size
            if end>len(raw):raise ValueError('class attribute bounds')
            if code and name=='Code':
                take(4);take(u4());take(u2()*8)
                for _ in range(u2()):
                    name=names.get(u2());size=u4();child_end=p+size
                    if child_end>end:raise ValueError('Code attribute bounds')
                    if name=='LineNumberTable':
                        n=u2()
                        if size!=2+4*n:raise ValueError('line attribute bounds')
                        for _ in range(n):take(2);lines.append(p);take(2)
                    else:take(size)
                    if p!=child_end:raise ValueError('Code attribute length')
            else:take(size)
            if p!=end:raise ValueError('class attribute length')
    take(6);take(u2()*2)
    for _ in range(u2()):take(6);attributes(u2())
    for _ in range(u2()):take(6);attributes(u2(),True)
    attributes(u2())
    if p!=len(raw) or not lines:raise ValueError('class framing or missing line tables')
    return lines

def verify(old,new,offset=1):
    if type(offset)is not int or offset!=1 or type(old)is not bytes or type(new)is not bytes or len(old)!=len(new):
        raise ValueError('fixed source line delta required')
    before=positions(old);after=positions(new)
    if before!=after:raise ValueError('line table locations differ')
    normalized=bytearray(new)
    for p in before:
        a=struct.unpack_from('>H',old,p)[0];b=struct.unpack_from('>H',new,p)[0]
        if b!=a+offset:raise ValueError('foreign source line delta')
        normalized[p:p+2]=old[p:p+2]
    if bytes(normalized)!=old:raise ValueError('non-line class byte changed')
    return {'lineEntries':len(before),'lineOffset':1,'nonLineBytesIdentical':True}
