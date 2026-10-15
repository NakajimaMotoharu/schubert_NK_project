"""Bounds-checked public class-file SourceFile attribute; never decode arbitrary MUTF8 constants."""


def source_file(raw):
    if type(raw)is not bytes:raise ValueError('class bytes required')
    p=0;utf8={}
    def take(n):
        nonlocal p
        if type(n)is not int or n<0 or p+n>len(raw):raise ValueError('truncated class')
        value=raw[p:p+n];p+=n;return value
    def u2():return int.from_bytes(take(2),'big')
    def u4():return int.from_bytes(take(4),'big')
    if take(4)!=b'\xca\xfe\xba\xbe':raise ValueError('class magic')
    take(4);count=u2();i=1
    while i<count:
        tag=take(1)[0]
        if tag==1:utf8[i]=take(u2())
        elif tag in {7,8,16,19,20}:take(2)
        elif tag in {3,4,9,10,11,12,17,18}:take(4)
        elif tag in {5,6}:take(8);i+=1
        elif tag==15:take(3)
        else:raise ValueError('constant-pool tag')
        i+=1
    def attributes(n):
        result=[]
        for _ in range(n):result.append((utf8.get(u2()),take(u4())))
        return result
    take(6);take(2*u2())
    for _ in range(u2()):take(6);attributes(u2())
    for _ in range(u2()):take(6);attributes(u2())
    values=[v for name,v in attributes(u2())if name==b'SourceFile']
    if p!=len(raw)or len(values)!=1 or len(values[0])!=2:raise ValueError('unique complete SourceFile required')
    name=utf8.get(int.from_bytes(values[0],'big'),b'').decode('ascii')
    if not name.endswith('.java')or any(x in name for x in ['/', '\\', '\x00'])or name.startswith('.'):raise ValueError('SourceFile basename required')
    return name
