"""SSC190 read-only old peer/HTTP/socket/journal check. Runs under the tool's M/A.
No start, authority reconstruction, permit, credentials, or logged response body.
"""
import http.client, json, pathlib, socket, ssl, subprocess, sys
from pg457_stable_actor import stable_actor
from pg462_observer_identity import authenticate_ready
FIELDS='Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,InvocationID,Type,Restart,RemainAfterExit,Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,KillMode,SendSIGKILL'
UNITS={'api':'schubert-nk-api.service','web':'schubert-nk-web.service','caddy':'caddy.service','broker':'artemis.service'}
INFO={'commit':'bbb244e5191e68adee2f6251dfdbbba53e9b64b4','app':'0.1.0-SNAPSHOT','config':'1','schema':'027','protocol':'0.1.0-SNAPSHOT'}
EXPECTED={'api':('1747577','385f36f479ee4033b76453f01aea13e3','999','981',['980','981','982','986']),
          'web':('1749706','ba1c5cd71ee7407a8ebd2fcc2f4724fb','997','980',['980','982','986']),
          'caddy':('1754706','d62f9435d4824b199009b62e52464e06'),
          'broker':('1633918','993d2a8c8e89469aa862e56b5223531c')}
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
def check():
    assert len(sys.argv)==1 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
    # Actual same-boot manager events, not absence/GC alone. Parent original and all
    # completion fields are independently held/rechecked by the enclosing Java scope.
    raw=subprocess.check_output(['/usr/bin/journalctl','--boot=e07aa7061acd4e65b309d7f330f79d54','--since=2026-10-05 05:21:12 UTC','--until=2026-10-05 05:51:13 UTC','UNIT=schubert-nk-morning-controller.service','-o','json','--no-pager'],timeout=5)
    assert len(raw)<=1048576
    events=[json.loads(line) for line in raw.splitlines()]
    assert any(v.get('MESSAGE_ID')=='39f53479d3a045ac8e11786248231fbf' and v.get('JOB_RESULT')=='done' and v.get('JOB_ID')=='142470' and 1791177672000000<=int(v['__REALTIME_TIMESTAMP'])<=1791179473000000 for v in events)
    for role,port in [('api',8091),('web',8081)]:
        a=peer(role);assert a['entry']==f'dev.codex.schubert.nk.{role}.bootstrap.{role.capitalize()}ProcessMain';owned=sockets(a,port);assert owned
        h=get(port,'/actuator/health/readiness');i=get(port,'/actuator/info');b=peer(role)
        assert authenticate_ready(a['process'],b['process'],h,(i[0],json.loads(i[1])),INFO,*EXPECTED[role][2:]) and same(a,b) and owned&sockets(b,port)
    a=peer('caddy');owned=sockets(a,55160,'0F02000A');assert owned
    assert a['process']['NoNewPrivs']=='1' and all(a['process'][k]=='0000000000000000' for k in ('CapInh','CapPrm','CapEff','CapBnd','CapAmb'))
    # Do not generate an anonymous session/log immediately before the full DB freeze.
    # A fresh CA-verified handshake binds the current owned socket; historical login200
    # remains PG468's own evidence, never inferred from this handshake.
    ca=pathlib.Path('/var/lib/caddy/.local/share/caddy/pki/authorities/local/root.crt');before=ca.stat()
    with socket.create_connection(('10.0.2.15',55160),timeout=1) as raw_socket:
        with ssl.create_default_context(cafile=str(ca)).wrap_socket(raw_socket,server_hostname='10.0.2.15') as secured:
            assert secured.getpeercert() and ca.stat()==before and same(a,peer('caddy')) and owned&sockets(peer('caddy'),55160,'0F02000A')
    a=peer('broker');owned=sockets(a,61616);assert owned
    assert a['process']['Uid'].split()==['994']*4 and a['process']['Gid'].split()==['979']*4 and a['process']['Groups'].split()==['979']
    assert a['process']['NoNewPrivs']=='1' and all(a['process'][k]=='0000000000000000' for k in ('CapInh','CapPrm','CapEff','CapBnd','CapAmb'))
    assert same(a,peer('broker')) and owned&sockets(peer('broker'),61616)
    print('PG469_OLD_PEERS_VERIFIED sameGeneration=true ordinaryZeroCaps=true ownedSockets=true info5=true tlsHandshake=true originalParentDone=true')
if __name__=='__main__':check()
