"""WBS-G07/3021: declared JaCoCo execution format only. No value-bearing strings are returned."""
import struct

from jacoco_readonly_exec_subset import validate_modified_utf

COMMON=('bytes','headers','sessions','classes','probes','hits','sessionUnits','classUnits','asciiSessions','asciiClasses','orderedSessions')

def parse(raw):
    if not isinstance(raw,bytes) or not 5<=len(raw)<=1_048_576:
        raise ValueError('bounded bytes required')
    pos=0
    result={k:0 for k in COMMON};result['bytes']=len(raw);result['unusedPaddingSetBits']=0
    def take(count):
        nonlocal pos
        if count<0 or count>len(raw)-pos:raise ValueError('truncated declared field')
        part=raw[pos:pos+count];pos+=count;return part
    def number(fmt):
        return struct.unpack(fmt,take(struct.calcsize(fmt)))[0]
    def utf_units():
        encoded=take(number('>H'))
        validate_modified_utf(encoded)
        units=[];index=0
        while index<len(encoded):
            first=encoded[index];index+=1
            if first<=0x7f:units.append(first)
            elif first>>4 in (12,13):
                if index>=len(encoded) or encoded[index]&0xc0!=0x80:raise ValueError('invalid modified UTF')
                units.append(((first&31)<<6)|(encoded[index]&63));index+=1
            elif first>>4==14:
                if index+1>=len(encoded) or encoded[index]&0xc0!=0x80 or encoded[index+1]&0xc0!=0x80:raise ValueError('invalid modified UTF')
                units.append(((first&15)<<12)|((encoded[index]&63)<<6)|(encoded[index+1]&63));index+=2
            else:raise ValueError('invalid modified UTF')
        return units
    def varint():
        value=0
        for shift in range(0,35,7):
            part=number('>B');value|=(part&127)<<shift
            if part&128==0:
                if value>8*len(raw):raise ValueError('probe allocation exceeds bounded input')
                return value
        raise ValueError('overlong probe varint')
    first=True
    while pos<len(raw):
        tag=number('>B')
        if first and tag!=1:raise ValueError('header must be first')
        first=False
        if tag==1:
            if number('>H')!=0xc0c0 or number('>H')!=0x1007:raise ValueError('unsupported header/version')
            result['headers']+=1
        elif tag==16:
            units=utf_units();start=number('>q');end=number('>q')
            result['sessions']+=1;result['sessionUnits']+=len(units)
            result['asciiSessions']+=int(all(32<=v<=126 for v in units))
            result['orderedSessions']+=int(0<=start<=end)
        elif tag==17:
            take(8);units=utf_units();count=varint();packed=take((count+7)//8)
            result['classes']+=1;result['classUnits']+=len(units)
            result['asciiClasses']+=int(all(32<=v<=126 for v in units));result['probes']+=count
            result['hits']+=sum((packed[n//8]>>(n%8))&1 for n in range(count))
            if count%8:result['unusedPaddingSetBits']+=(packed[-1]>>(count%8)).bit_count()
        else:raise ValueError('unknown format block')
    if result['headers']<1:raise ValueError('missing header')
    result['consumedBytes']=pos
    return result

def fixtures():
    # Public, manually encoded metadata vectors. No product class, real session or key.
    header=bytes.fromhex('01c0c01007')
    session=bytes.fromhex('1000065055424c494300000000000000010000000000000002')
    item=bytes.fromhex('110123456789abcdef000e7075626c69632f46697874757265090501')
    basic=header+session+item
    unicode_session=bytes.fromhex('10000bc080e38182eda0bdedb88000000000000000010000000000000002')
    def expected(size,headers=1,sessions=0,classes=0,probes=0,hits=0,sessionUnits=0,classUnits=0,asciiSessions=0,asciiClasses=0,orderedSessions=0,padding=0):
        return dict(bytes=size,headers=headers,sessions=sessions,classes=classes,probes=probes,hits=hits,sessionUnits=sessionUnits,classUnits=classUnits,asciiSessions=asciiSessions,asciiClasses=asciiClasses,orderedSessions=orderedSessions,unusedPaddingSetBits=padding,consumedBytes=size)
    positives=[
      ('header-only',header,expected(5)),
      ('two-headers',header+header,expected(10,headers=2)),
      ('ascii-metadata',basic,expected(58,sessions=1,classes=1,probes=9,hits=3,sessionUnits=6,classUnits=14,asciiSessions=1,asciiClasses=1,orderedSessions=1)),
      ('modified-utf-nul-and-surrogates',header+unicode_session+item,expected(63,sessions=1,classes=1,probes=9,hits=3,sessionUnits=4,classUnits=14,asciiClasses=1,orderedSessions=1)),
      ('unused-padding-is-not-hidden',basic[:-1]+bytes([0x81]),expected(58,sessions=1,classes=1,probes=9,hits=3,sessionUnits=6,classUnits=14,asciiSessions=1,asciiClasses=1,orderedSessions=1,padding=1))]
    negatives=[
      ('empty',b''),('not-header-first',basic[5:]),('bad-magic',bytes.fromhex('01c0c11007')+basic[5:]),
      ('bad-version',bytes.fromhex('01c0c01008')+basic[5:]),('truncated-header',basic[:4]),
      ('truncated-session-length',basic[:7]),('truncated-session-timestamp',basic[:29]),
      ('invalid-modified-utf',header+bytes.fromhex('100001ff')+bytes(16)),
      ('truncated-class-name',basic[:45]),('truncated-probe-varint',basic[:55]+bytes([0x80])),
      ('truncated-probes',basic[:-1]),('unknown-trailing-block',basic+bytes([0x7f])),
      ('truncated-appended-header',basic+bytes([1])),('truncated-large-utf-field',header+bytes.fromhex('10ffff'))]
    return positives,negatives
