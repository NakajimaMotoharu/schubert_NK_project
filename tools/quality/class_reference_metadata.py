"""ClassFile source/CP symbol reader only; no JVM or target runtime, strings never references."""
import re
import struct

SYMBOL=re.compile(r'[A-Za-z0-9_/$-]+')

def read(raw):
    at=0
    def take(size):
        nonlocal at
        if size<0 or at+size>len(raw):raise ValueError('complete bounded ClassFile required')
        value=raw[at:at+size];at+=size;return value
    def u2():return struct.unpack('>H',take(2))[0]
    def u4():return struct.unpack('>I',take(4))[0]
    if take(4)!=b'\xca\xfe\xba\xbe':raise ValueError('ClassFile magic required')
    minor=u2();major=u2()
    if major!=69 or minor not in (0,65535):raise ValueError('pinned Java25 class format required')
    count=u2();cp={};index=1
    while index<count:
        tag=take(1)[0]
        if tag==1:value=take(u2())
        elif tag in (3,4):value=take(4)
        elif tag in (5,6):value=take(8)
        elif tag in (7,8,16,19,20):value=u2()
        elif tag in (9,10,11,12,17,18):value=(u2(),u2())
        elif tag==15:value=(take(1)[0],u2())
        else:raise ValueError('known ClassFile constant tag required')
        cp[index]=(tag,value);index+=2 if tag in (5,6) else 1
    if index!=count:raise ValueError('wide constant cannot overrun pool')
    def item(index,tag):
        value=cp.get(index)
        if value is None or value[0]!=tag:raise ValueError('typed valid constant-pool index required')
        return value[1]
    def utf(index):
        try:return item(index,1).decode('ascii')
        except UnicodeDecodeError as exc:raise ValueError('ASCII structural symbol required') from exc
    def class_name(index):
        value=utf(item(index,7))
        if value.startswith('['):
            value=value.lstrip('[')
            if value in ('B','C','D','F','I','J','S','Z'):return None
            if not(value.startswith('L') and value.endswith(';')):raise ValueError('valid object array descriptor required')
            value=value[1:-1]
        if not SYMBOL.fullmatch(value):raise ValueError('bounded class symbol required')
        return value
    u2();identity=class_name(u2());super_class=u2()
    if super_class:class_name(super_class)
    for _ in range(u2()):class_name(u2())
    def attributes(number,top=False):
        sources=[]
        for _ in range(number):
            name=utf(u2());size=u4()
            if top and name=='SourceFile':
                if size!=2:raise ValueError('exact SourceFile payload required')
                sources.append(utf(u2()))
            else:take(size)
        return sources
    for _ in range(2):
        for _ in range(u2()):take(6);attributes(u2())
    sources=attributes(u2(),top=True)
    if at!=len(raw) or len(sources)!=1 or not re.fullmatch(r'[A-Za-z0-9_$-]+\.java',sources[0]):
        raise ValueError('one exact SourceFile and complete class bytes required')
    references={class_name(i) for i,(tag,_) in cp.items() if tag==7}-{None}
    reflective=any(name.startswith('java/lang/reflect/') for name in references)
    for _,(tag,value) in cp.items():
        if tag in (9,10,11):
            owner,name_type=value;declaring=class_name(owner);name,_=item(name_type,12)
            if declaring=='java/lang/Class' and utf(name) in ('forName','getMethod','getDeclaredMethod','getDeclaredMethods','getConstructor','getDeclaredConstructor','getField','getDeclaredField'):
                reflective=True
            if declaring.startswith(('java/lang/invoke/MethodHandles','java/lang/invoke/MethodHandle')) and utf(name).startswith(('lookup','privateLookup','find','unreflect','invoke')):
                reflective=True
    return dict(className=identity,sourceFile=sources[0],references=sorted(references),reflectiveOrDynamicLookup=reflective)

def source_closure(direct,edges,unresolved):
    if set(direct)!=set(edges) or set(direct)!=set(unresolved):raise ValueError('same graph source domain required')
    if any(not set(v)<=set(direct) for v in edges.values()):raise ValueError('closed helper graph required')
    owners={key:set(value) for key,value in direct.items()};unknown={key:set(value) for key,value in unresolved.items()}
    for _ in range(len(direct)+1):
        changed=False
        for key,dependencies in edges.items():
            a=set().union(owners[key],*(owners[d] for d in dependencies))
            b=set().union(unknown[key],*(unknown[d] for d in dependencies))
            if a!=owners[key] or b!=unknown[key]:changed=True;owners[key]=a;unknown[key]=b
        if not changed:return owners,unknown
    raise ValueError('finite monotone source graph must converge')

def vectors():
    def fixture(target_tag=7,duplicate_source=False,trailer=b'',target='p/Target'):
        constants=[]
        def utf(value):
            raw=value.encode();constants.append(b'\1'+struct.pack('>H',len(raw))+raw);return len(constants)
        def single(tag,index):constants.append(bytes([tag])+struct.pack('>H',index));return len(constants)
        identity=single(7,utf('p/Fixture'));source_name=utf('SourceFile');source=utf('Fixture.java')
        single(target_tag,utf(target))
        attrs=struct.pack('>HIH',source_name,2,source)
        header=b'\xca\xfe\xba\xbe'+struct.pack('>HHH',0,69,len(constants)+1)+b''.join(constants)
        return header+struct.pack('>HHHHHHH',0,identity,0,0,0,0,2 if duplicate_source else 1)+attrs+(attrs if duplicate_source else b'')+trailer
    assert 'p/Target' in read(fixture())['references']
    assert 'p/Target' not in read(fixture(8))['references']
    assert 'p/package-info' in read(fixture(target='p/package-info'))['references']
    assert 'p/package-info' not in read(fixture(8,target='p/package-info'))['references']
    assert 'p/Target' in read(fixture(target='[[Lp/Target;'))['references']
    assert read(fixture(target='[[I'))['references']==['p/Fixture']
    assert read(fixture(target='java/lang/reflect/Method'))['reflectiveOrDynamicLookup'] is True
    assert read(fixture(target='java/lang/invoke/MethodHandles$Lookup'))['reflectiveOrDynamicLookup'] is False
    for raw in (fixture()[:-1],fixture(duplicate_source=True),fixture(trailer=b'x'),b'bad'):
        try:read(raw)
        except ValueError:pass
        else:raise AssertionError('malformed ClassFile accepted')
    direct={'a':{'WBS-P001-01'},'b':set(),'c':{'WBS-P002-01'},'d':set()}
    edges={'a':{'b'},'b':{'a'},'c':{'b'},'d':{'b'}};unknown={key:set() for key in direct}
    owners,held=source_closure(direct,edges,unknown)
    assert owners['a']==owners['b']==owners['d']=={'WBS-P001-01'} and owners['c']=={'WBS-P001-01','WBS-P002-01'}
    unknown['a']={'MISSING'};owners,held=source_closure(direct,edges,unknown)
    assert all(held[key]=={'MISSING'} for key in direct)
    return 14
