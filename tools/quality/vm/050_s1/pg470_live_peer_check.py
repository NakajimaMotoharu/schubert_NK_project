"""SSC190 read-only old peer/HTTP/socket/journal check. Runs under the tool's M/A.
No start, authority reconstruction, permit, credentials, or logged response body.
"""
import http.client, json, pathlib, socket, ssl, subprocess, sys
from pg457_stable_actor import stable_actor
from pg462_observer_identity import authenticate_ready
FIELDS='Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,InvocationID,Type,Restart,RemainAfterExit,Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,KillMode,SendSIGKILL'
UNITS={'api':'schubert-nk-api.service','web':'schubert-nk-web.service','caddy':'caddy.service','broker':'artemis.service'}
INFO={'commit':'d3bba6db6eb9fec13e4847a10541cf337f575731','app':'0.1.0-SNAPSHOT','config':'1','schema':'027','protocol':'0.1.0-SNAPSHOT'}
EXPECTED={'api':('2004047','5382161425dd4edcac8758357f747c0e','999','981',['980','981','982','986']),
          'web':('2006107','88e5d93fbeb443f9a1c3c769105c6c4d','997','980',['980','982','986']),
          'caddy':('2011228','9aa28af50ac74d84a6c6067f26619356'),
          'broker':('1887227','0c97d581cb0d460389c777b8052c3284')}
def manager(role):
    raw=subprocess.check_output(['/usr/bin/systemctl','show',UNITS[role],'--property='+FIELDS],text=True,timeout=5)
    result={}
    for line in raw.splitlines():
        k,v=line.split('=',1);assert k not in result;result[k]=v
    assert set(result)==set(FIELDS.split(','));return result
def peer(role):
    a=stable_actor(role,manager)
    assert not a.get('race') and (a['MainPID'],a['InvocationID'])==EXPECTED[role][:2]
    assert a['LoadState']=='loaded' and a['ActiveState']=='active' and a['SubState']=='running' and a['ControlPID']=='0' and a['Job']==''
    assert (pathlib.Path('/proc')/a['MainPID']/'cgroup').read_text()==f'0::/system.slice/{UNITS[role]}\n'
    return a
def same(a,b):
    return all(a[k]==b[k] for k in ('MainPID','InvocationID','startTicks','process','entry'))
def sockets(a,port,host='0100007F'):
    proc=pathlib.Path('/proc')/a['MainPID'];fds=set()
    for fd in (proc/'fd').iterdir():
        try:
            target=str(fd.readlink())
            if target.startswith('socket:['):fds.add(target[8:-1])
        except FileNotFoundError:pass
    owned=set()
    for name,address in [('tcp',f'{host}:{port:04X}'),('tcp6',f'0000000000000000FFFF0000{host}:{port:04X}')]:
        for line in (proc/'net'/name).read_text().splitlines()[1:]:
            f=line.split()
            if len(f)>=10 and f[1]==address and f[3]=='0A' and f[9] in fds:owned.add(f[9])
    return owned
def get(port,path):
    c=http.client.HTTPConnection('127.0.0.1',port,timeout=1)
    try:
        c.request('GET',path);r=c.getresponse();b=r.read(4097);assert len(b)<=4096;return r.status,b
    finally:c.close()
def parent_done(row):
    if not isinstance(row,dict):return False
    expected={'_BOOT_ID':'e07aa7061acd4e65b309d7f330f79d54','_PID':'1','_UID':'0','_COMM':'systemd','MESSAGE_ID':'39f53479d3a045ac8e11786248231fbf','UNIT':'schubert-nk-morning-controller.service','INVOCATION_ID':'aabcc2c3ef1444a7bb07b3183b220c14','JOB_ID':'162935','JOB_TYPE':'start','JOB_RESULT':'done'}
    if any(row.get(k)!=v for k,v in expected.items()):return False
    for key in ['__REALTIME_TIMESTAMP','_SOURCE_REALTIME_TIMESTAMP']:
        value=row.get(key)
        if not isinstance(value,str) or len(value)!=16 or not value.isascii() or not value.isdigit() or not 1791218060000000<=int(value)<=1791219861000000:return False
    return True
def check():
    assert len(sys.argv)==1 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
    # Actual same-boot manager events, not absence/GC alone. Parent original and all
    # completion fields are independently held/rechecked by the enclosing Java scope.
    raw=subprocess.check_output(['/usr/bin/journalctl','--boot=e07aa7061acd4e65b309d7f330f79d54','--since=2026-10-05 16:34:20 UTC','--until=2026-10-05 17:04:21 UTC','UNIT=schubert-nk-morning-controller.service','-o','json','--no-pager'],timeout=5)
    assert len(raw)<=1048576
    events=[json.loads(line) for line in raw.splitlines()]
    assert sum(parent_done(v) for v in events)==1
    for role,port in [('api',8091),('web',8081)]:
        a=peer(role);assert a['entry']==f'dev.codex.schubert.nk.{role}.bootstrap.{role.capitalize()}ProcessMain';owned=sockets(a,port);assert owned
        h=get(port,'/actuator/health/readiness');i=get(port,'/actuator/info');b=peer(role)
        assert authenticate_ready(a['process'],b['process'],h,(i[0],json.loads(i[1])),INFO,*EXPECTED[role][2:]) and same(a,b) and owned&sockets(b,port)
    a=peer('caddy');owned=sockets(a,55160,'0F02000A');assert owned
    assert a['process']['NoNewPrivs']=='1' and all(a['process'][k]=='0000000000000000' for k in ('CapInh','CapPrm','CapEff','CapBnd','CapAmb'))
    # Do not generate an anonymous session/log immediately before the full DB freeze.
    # A fresh CA-verified handshake binds the current owned socket; historical login200
    # remains PG469's own evidence, never inferred from this handshake.
    ca=pathlib.Path('/var/lib/caddy/.local/share/caddy/pki/authorities/local/root.crt');before=ca.stat()
    with socket.create_connection(('10.0.2.15',55160),timeout=1) as raw_socket:
        with ssl.create_default_context(cafile=str(ca)).wrap_socket(raw_socket,server_hostname='10.0.2.15') as secured:
            assert secured.getpeercert() and ca.stat()==before and same(a,peer('caddy')) and owned&sockets(peer('caddy'),55160,'0F02000A')
    a=peer('broker');owned=sockets(a,61616);assert owned
    assert a['process']['Uid'].split()==['994']*4 and a['process']['Gid'].split()==['979']*4 and a['process']['Groups'].split()==['979']
    assert a['process']['NoNewPrivs']=='1' and all(a['process'][k]=='0000000000000000' for k in ('CapInh','CapPrm','CapEff','CapBnd','CapAmb'))
    assert same(a,peer('broker')) and owned&sockets(peer('broker'),61616)
    print('PG470_OLD_PEERS_VERIFIED sameGeneration=true ordinaryZeroCaps=true ownedSockets=true info5=true tlsHandshake=true originalParentDone=true')
if __name__=='__main__':check()
