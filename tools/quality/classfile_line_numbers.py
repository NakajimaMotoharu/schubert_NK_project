"""Mask only u2 line_number values at parsed Code/LineNumberTable coordinates, in memory.

All CP bytes, instructions, exception tables, stack maps, flags, other attributes and offsets
remain intact. This is a byte-difference classifier, not JVM verification or code execution.
"""
import hashlib
import struct


def normalized(raw):
    position=0;names={};result=bytearray(raw);lines=[]
    def take(length):
        nonlocal position
        if length<0 or position+length>len(raw):raise ValueError('truncated class structure')
        value=raw[position:position+length];position+=length;return value
    def u2():return struct.unpack('>H',take(2))[0]
    def u4():return struct.unpack('>I',take(4))[0]
    if take(4)!=b'\xca\xfe\xba\xbe':raise ValueError('class magic required')
    take(4);count=u2();index=1
    while index<count:
        tag=take(1)[0]
        if tag==1:names[index]=take(u2())
        elif tag in(3,4,9,10,11,12,17,18):take(4)
        elif tag in(5,6):take(8);index+=1
        elif tag in(7,8,16,19,20):take(2)
        elif tag==15:take(3)
        else:raise ValueError('unknown constant-pool tag')
        index+=1
    take(6);take(2*u2())
    def attributes(number,method=None,code_length=None):
        for _ in range(number):
            name=names.get(u2());length=u4();end=position+length
            if end>len(raw):raise ValueError('attribute outside class bytes')
            if name==b'Code'and method is not None and code_length is None:
                take(4);size=u4();take(size);take(8*u2());attributes(u2(),method,size)
            elif name==b'LineNumberTable'and code_length is not None:
                entries=u2()
                if length!=2+4*entries:raise ValueError('exact LineNumberTable length')
                for _ in range(entries):
                    start=u2();offset=position;line=u2()
                    if start>=code_length:raise ValueError('line start outside code')
                    result[offset:offset+2]=b'\0\0'
                    lines.append(dict(method=method,startPc=start,lineNumber=line,offset=offset))
            else:take(length)
            if position!=end:raise ValueError('attribute length/recursive structure mismatch')
    for _ in range(u2()):
        take(6);attributes(u2())
    for _ in range(u2()):
        u2();name=u2();descriptor=u2()
        method=(names[name]+names[descriptor]).decode('utf-8','backslashreplace')
        attributes(u2(),method)
    attributes(u2())
    if position!=len(raw):raise ValueError('trailing class bytes')
    return bytes(result),lines


def compare(before,after):
    a,alines=normalized(before);b,blines=normalized(after)
    digest=lambda raw:hashlib.sha256(raw).hexdigest()
    return dict(rawEqual=before==after,lineNumberNormalizedEqual=a==b,
        beforeSha256=digest(before),afterSha256=digest(after),
        normalizedBeforeSha256=digest(a),normalizedAfterSha256=digest(b),
        beforeLineNumbers=alines,afterLineNumbers=blines,productionClassesExecuted=0,
        onlyParsedLineNumberU2Masked=True)
