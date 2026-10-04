"""Read-only reattachment to current PG461 peers after failed external observer.
No retrospective Root claim, no application start/stop/permit/budget renewal.
"""
import hashlib,http.client,json,pathlib,ssl,subprocess,sys
sys.path.insert(0,'/var/lib/pgpt-s1-preservation/pg461-code-tools-v1')
from pg457_stable_actor import stable_actor
SOURCE='00785cf0698aecf1ace1e60b87e8849639e85b97'
DIGEST='1b7688de234ad15e39ffe578060019ff61fc21efd3c8e0c5aa62c39c95959b3c'
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
assert hashlib.sha256(pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()).hexdigest()==DIGEST
UNITS={'morning':'schubert-nk-morning-controller.service','api':'schubert-nk-api.service','web':'schubert-nk-web.service','caddy':'caddy.service'}
FIELDS='Id,MainPID,ControlPID,InvocationID,Job,ExecMainStartTimestampMonotonic,ActiveState,SubState,ExecMainStatus'
PINS={'morning':('628952','a93cd4cdb41a4709af0e976b37389598'),'api':('771339','bbf96d392f424aa195e8cceb80d02115'),'web':('773290','6c6d91f9022c47aa86cb9d7eea8f0bd7'),'caddy':('776564','9474a1839bd04ab090b45a74bb297128')}
def manager(role):
 return dict(x.split('=',1) for x in subprocess.check_output(['/usr/bin/systemctl','show',UNITS[role],'--property='+FIELDS],text=True).splitlines())
def actor(role):
 a=stable_actor(role,manager);assert not a.get('race') and (a['MainPID'],a['InvocationID'])==PINS[role];return a
def authority(a,account):
 p=a['process'];uid=subprocess.check_output(['id','-u',account],text=True).strip();gid=subprocess.check_output(['id','-g',account],text=True).strip()
 groups=sorted(set(subprocess.check_output(['id','-G',account],text=True).split()),key=int)
 return p['Uid'].split()==[uid]*4 and p['Gid'].split()==[gid]*4 and p['Groups'].split()==groups and p['NoNewPrivs']=='1' and all(p[k]=='0000000000000000' for k in ('CapInh','CapPrm','CapEff','CapBnd','CapAmb'))
def sockets(a,port,host):
 proc=pathlib.Path('/proc')/a['MainPID'];fds=set()
 for fd in (proc/'fd').iterdir():
  try:
   target=str(fd.readlink())
   if target.startswith('socket:['):fds.add(target[8:-1])
  except FileNotFoundError:pass
 found=set()
 for name,address in [('tcp',f'{host}:{port:04X}'),('tcp6',f'0000000000000000FFFF0000{host}:{port:04X}')]:
  for line in (proc/'net'/name).read_text().splitlines()[1:]:
   f=line.split()
   if len(f)>=10 and f[1]==address and f[3]=='0A' and f[9] in fds:found.add(f[9])
 return found
def get(c,path):
 try:c.request('GET',path);r=c.getresponse();b=r.read(65537);assert len(b)<=65536;return r.status,b
 finally:c.close()
before={r:actor(r) for r in UNITS};owned={r:sockets(before[r],8091 if r=='api' else 8081,'0100007F') for r in ('api','web')}
for r in ('api','web'):
 assert owned[r]
 assert get(http.client.HTTPConnection('127.0.0.1',8091 if r=='api' else 8081,timeout=2),'/actuator/health/readiness')==(200,b'{"status":"UP"}')
 status,body=get(http.client.HTTPConnection('127.0.0.1',8091 if r=='api' else 8081,timeout=2),'/actuator/info')
 assert status==200 and json.loads(body)=={'commit':SOURCE,'app':'0.1.0-SNAPSHOT','config':'1','schema':'027','protocol':'0.1.0-SNAPSHOT'}
ca=pathlib.Path('/var/lib/caddy/.local/share/caddy/pki/authorities/local/root.crt');metadata=ca.stat();assert metadata.st_mode&0o777==0o600
caddySocket=sockets(before['caddy'],55160,'0F02000A');assert caddySocket
status,body=get(http.client.HTTPSConnection('10.0.2.15',55160,timeout=2,context=ssl.create_default_context(cafile=str(ca))),'/login')
assert status==200 and b'schubert NK' in body and ca.stat()==metadata
after={r:actor(r) for r in UNITS}
for r in UNITS:
 assert all(before[r].get(k)==after[r].get(k) for k in ('MainPID','InvocationID','startTicks','process','entry'))
for r in ('api','web'):
 assert authority(after[r],'schubert-'+r) and owned[r].intersection(sockets(after[r],8091 if r=='api' else 8081,'0100007F'))
assert authority(after['caddy'],'caddy') and caddySocket.intersection(sockets(after['caddy'],55160,'0F02000A'))
print(json.dumps({'source':SOURCE,'sameCapturedCurrentPeers':True,'sameApiWeb':True,'sameCaddySocket':True,'publicCaValidated':True,'publicCaMode600':True,'caddyTlsLogin200':True,'rootWebExternalCaptureMissing':True,'wholeMorningAccepted':False,'bodyLogged':False,'starts0':True,'at':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()}))
