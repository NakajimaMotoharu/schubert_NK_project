"""SSC290 fixed local read-only manager. No starts/stops/reload or cached state/owner acceptance."""
import re
import time

NAMES=frozenset(['artemis.service','caddy.service']+['schubert-nk-'+n+'.service'for n in ['morning-controller','api','web','backup','bootstrap-admin','cleanup','expiry-cleanup','inbox-inspector']])
UNIT_FIELDS=('Id','LoadState','ActiveState','SubState','Job','InvocationID')
SERVICE_TEXT=('Type','Restart','KillMode','Result')
SERVICE_BOOL=('RemainAfterExit','SendSIGKILL')
SERVICE_INT=('MainPID','ControlPID','ExecMainCode','ExecMainStatus','ExecMainStartTimestampMonotonic','ExecMainExitTimestampMonotonic')


def projection(name,unit,service):
    if name not in NAMES or type(unit)is not dict or type(service)is not dict:raise ValueError('fixed complete manager interfaces required')
    def text(value):
        if type(value)is not str or len(value)>4096 or any(not 32<=ord(c)<=126 for c in value):raise ValueError('bounded ASCII systemd string required')
        return value
    if any(k not in unit for k in UNIT_FIELDS)or any(k not in service for k in SERVICE_TEXT+SERVICE_BOOL+SERVICE_INT):raise ValueError('all eighteen fields required')
    result={k:text(unit[k])for k in UNIT_FIELDS if k not in {'Job','InvocationID'}}
    if result['Id']!=name or result['LoadState']!='loaded':raise ValueError('fixed loaded unit required')
    job=unit['Job']
    if type(job)is not tuple or len(job)!=2 or type(job[0])is not int or not 0<=job[0]<=4294967295 or type(job[1])is not str:raise ValueError('fixed systemd Job signature required')
    if job[0]==0:
        if job[1]!='/':raise ValueError('empty job path required')
    elif job[1]!='/org/freedesktop/systemd1/job/'+str(job[0]):raise ValueError('same job number/path required')
    result['Job']=''if job[0]==0 else str(job[0])
    inv=unit['InvocationID']
    if type(inv)is not bytes or len(inv)not in (0,16):raise ValueError('fixed invocation bytes required')
    result['InvocationID']=''if not inv or inv==bytes(16)else inv.hex()
    result.update({k:text(service[k])for k in SERVICE_TEXT})
    for key in SERVICE_BOOL:
        if type(service[key])is not bool:raise ValueError('fixed boolean signature required')
        result[key]='yes'if service[key]else'no'
    for key in SERVICE_INT:
        value=service[key]
        if type(value)is not int or not 0<=value<=18446744073709551615:raise ValueError('nonnegative exact integer required')
        result[key]=str(value)
    return result


class NativeReader:
    def __init__(self):
        import dbus
        self.bus=dbus.bus.BusConnection('unix:path=/run/dbus/system_bus_socket')
        self.closed=False

    def rpc(self,destination,path,interface,method,signature,args,deadline):
        remaining=deadline-time.monotonic()
        if self.closed or not 0<remaining<=5:raise ValueError('same five-second read budget required')
        return self.bus.call_blocking(destination,path,interface,method,signature,args,timeout=remaining)

    def peer(self,deadline):
        args=('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus')
        name=str(self.rpc(*args,'GetNameOwner','s',('org.freedesktop.systemd1',),deadline))
        if len(name)>64 or re.fullmatch(r':[0-9]+\.[0-9]+',name)is None:raise ValueError('fixed systemd unique peer required')
        pid=int(self.rpc(*args,'GetConnectionUnixProcessID','s',(name,),deadline))
        uid=int(self.rpc(*args,'GetConnectionUnixUser','s',(name,),deadline))
        if (pid,uid)!=(1,0):raise ValueError('same kernel PID1/root peer required')
        return name,pid,uid

    def manager_call(self,method,name):
        if name not in NAMES or method not in {'LoadUnit','RefUnit','UnrefUnit'}:raise ValueError('metadata-only fixed operation')
        deadline=time.monotonic()+5;peer=self.peer(deadline)
        result=self.rpc(peer[0],'/org/freedesktop/systemd1','org.freedesktop.systemd1.Manager',method,'s',(name,),deadline)
        if self.peer(deadline)!=peer:raise ValueError('metadata reference peer changed')
        return result

    def LoadUnit(self,name):return self.manager_call('LoadUnit',name)
    def RefUnit(self,name):return self.manager_call('RefUnit',name)
    def UnrefUnit(self,name):return self.manager_call('UnrefUnit',name)

    def read(self,name):
        if name not in NAMES:raise ValueError('fixed observed unit required')
        deadline=time.monotonic()+5;before=self.peer(deadline)
        path=str(self.rpc(before[0],'/org/freedesktop/systemd1','org.freedesktop.systemd1.Manager','GetUnit','s',(name,),deadline))
        expected='/org/freedesktop/systemd1/unit/'+name.replace('_','_5f').replace('-','_2d').replace('.','_2e')
        if path!=expected:raise ValueError('fixed unit object path required')
        unit=self.rpc(before[0],path,'org.freedesktop.DBus.Properties','GetAll','s',('org.freedesktop.systemd1.Unit',),deadline)
        service=self.rpc(before[0],path,'org.freedesktop.DBus.Properties','GetAll','s',('org.freedesktop.systemd1.Service',),deadline)
        import dbus
        result=native_projection(name,unit,service,dbus)
        if self.peer(deadline)!=before:raise ValueError('same peer before/after required')
        return result

    def close(self):
        if self.closed:raise ValueError('private connection already closed')
        self.bus.close();self.closed=True


def native_projection(name,unit,service,types):
    if not isinstance(unit,types.Dictionary)or not isinstance(service,types.Dictionary):raise ValueError('typed property dictionaries required')
    if any(type(unit[k])is not types.String for k in UNIT_FIELDS if k not in {'Job','InvocationID'})or any(type(service[k])is not types.String for k in SERVICE_TEXT):raise ValueError('typed string properties required')
    job=unit['Job'];inv=unit['InvocationID']
    if type(job)is not types.Struct or len(job)!=2 or type(job[0])is not types.UInt32 or type(job[1])is not types.ObjectPath:raise ValueError('typed Job required')
    if not(type(inv)is types.ByteArray or type(inv)is types.Array and str(inv.signature)=='y'and all(type(v)is types.Byte for v in inv)):raise ValueError('typed invocation byte array required')
    if any(type(service[k])is not types.Boolean for k in SERVICE_BOOL):raise ValueError('typed bool properties required')
    for key in SERVICE_INT:
        expected=types.UInt32 if key in {'MainPID','ControlPID'}else types.Int32 if key in {'ExecMainCode','ExecMainStatus'}else types.UInt64
        if type(service[key])is not expected:raise ValueError('typed integer property required')
    u={k:((int(job[0]),str(job[1]))if k=='Job'else bytes(inv)if k=='InvocationID'else str(unit[k]))for k in UNIT_FIELDS}
    s={**{k:str(service[k])for k in SERVICE_TEXT},**{k:bool(service[k])for k in SERVICE_BOOL},**{k:int(service[k])for k in SERVICE_INT}}
    return projection(name,u,s)
