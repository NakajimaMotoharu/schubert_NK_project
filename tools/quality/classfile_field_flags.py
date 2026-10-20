"""Bounded Java ClassFile field access flag inspection,never loads or executes a class."""
import struct


def fields(raw):
    def u2(at):return struct.unpack_from('>H',raw,at)[0]
    def u4(at):return struct.unpack_from('>I',raw,at)[0]
    if len(raw)<10 or raw[:4]!=b'\xca\xfe\xba\xbe':raise ValueError('actual ClassFile magic')
    total=u2(8);at=10;cp={};index=1
    while index<total:
        tag=raw[at];at+=1
        if tag==1:
            size=u2(at);at+=2;cp[index]=raw[at:at+size];at+=size
        elif tag in(3,4,9,10,11,12,17,18):at+=4
        elif tag in(5,6):at+=8;index+=1
        elif tag in(7,8,16,19,20):at+=2
        elif tag==15:at+=3
        else:raise ValueError('known Java25 constant-pool tag')
        if at>len(raw):raise ValueError('complete constant-pool entry')
        index+=1
    at+=6;interfaces=u2(at);at+=2+2*interfaces;count=u2(at);at+=2;result={}
    for _ in range(count):
        offset=at;flags,name,descriptor,attributes=struct.unpack_from('>HHHH',raw,at);at+=8
        if name not in cp or descriptor not in cp or cp[name]in result:raise ValueError('unique declared UTF8 field name/descriptor')
        result[cp[name]]=dict(flags=flags,offset=offset,descriptor=cp[descriptor])
        for _ in range(attributes):
            size=u4(at+2);at+=6+size
            if at>len(raw):raise ValueError('complete field attribute')
    return result


def only_clear_private_volatile(before,after,name=b'closed'):
    old,new=fields(before),fields(after)
    if set(old)!=set(new)or name not in old:raise ValueError('same complete field inventory')
    a,b=old[name],new[name]
    if a['descriptor']!=b'Z'or b['descriptor']!=b'Z'or a['flags']!=0x0042 or b['flags']!=0x0002 or a['offset']!=b['offset']:
        raise ValueError('exact PRIVATE|VOLATILE boolean to PRIVATE at same field slot')
    expected=bytearray(before);struct.pack_into('>H',expected,a['offset'],0x0002)
    if bytes(expected)!=after:raise ValueError('all other ClassFile bytes unchanged,not only method names')
    return dict(fieldName=name.decode('ascii'),oldFlags=a['flags'],newFlags=b['flags'],fieldFlagsOffset=a['offset'],allOtherClassBytesIdentical=True)
