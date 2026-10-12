"""BUG1156 pre-Ref immutable retain: current whole proof, no signal/start.

This is a diagnosed failed-phase read-only connection, not an observer in a
fresh handoff guard. The original host job retains its management exclusion.
"""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import SSH, W
from pg1718_current_bootstrap_before import payload as before_payload
from pg1719_current_bootstrap_sources import TOOLS, SOURCE

SLOT = 'pg1722-bootstrap-db-owner-proof-v1'
PID = 383695
TICKS = 7281859

ACTOR = r'''
P=pathlib.Path('/proc/383695')
def actor():
 require(P.exists() and int((P/'stat').read_text().rpartition(')')[2].split()[19])==7281859)
 require(os.readlink(P/'exe')=='/opt/jdk-25.0.4/bin/java' and (P/'cmdline').read_bytes()==EXPECTED_ARGV)
 status=dict(line.split(':',1)for line in(P/'status').read_text().splitlines()if ':'in line)
 require(status['Uid'].split()==status['Gid'].split()==['0']*4 and status['PPid'].strip()=='383693')
 children={int(c)for t in(P/'task').iterdir()for c in(t/'children').read_text().split()};require(not children)
 fds={f.name:{'metadata':metadata9(f.stat()),'target':os.readlink(f)}for f in(P/'fd').iterdir()}
 require(len(fds)==99)
 return {'pid':383695,'ticks':7281859,'argvSha256':hashlib.sha256(EXPECTED_ARGV).hexdigest(),'authority':{k:status[k].strip()for k in ['Uid','Gid','Groups','NoNewPrivs','CapInh','CapPrm','CapEff','CapBnd','CapAmb','PPid']},'cgroup':(P/'cgroup').read_text(),'fds':fds}
def owned_lock(name):
 p=pathlib.Path('/run/schubert-nk')/name;s=p.lstat()
 require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(p))
 hits=[]
 for line in pathlib.Path('/proc/locks').read_text().splitlines():
  f=line.split()
  if len(f)<8:continue
  d=f[5].split(':')
  if len(d)==3 and(int(d[0],16),int(d[1],16),int(d[2]))==(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino):hits.append(f)
 require(len(hits)==1 and hits[0][1:5]==['FLOCK','ADVISORY','WRITE','383695'])
 actual=actor();linked=sorted([n for n,v in actual['fds'].items()if tuple(v['metadata'][:2])==(s.st_dev,s.st_ino)],key=int)
 locking=[]
 for n in linked:
  lines=[l.split()for l in(P/'fdinfo'/n).read_text().splitlines()if l.startswith('lock:')]
  require(len(lines)<=1)
  if lines:
   require(lines[0][2:6]==['FLOCK','ADVISORY','WRITE','383695']and lines[0][6:]==[f'{os.major(s.st_dev):02x}:{os.minor(s.st_dev):02x}:{s.st_ino}','0','EOF']);locking.append(n)
 require(bool(locking))
 import ctypes
 libc=ctypes.CDLL(None,use_errno=True);relations=[]
 for i,a in enumerate(linked):
  for b in linked[i+1:]:
   ctypes.set_errno(0);v=libc.syscall(312,383695,383695,0,int(a),int(b));require(v>=0 and ctypes.get_errno()==0)
   require((v==0)==(a in locking and b in locking))
   relations.append({'a':a,'b':b,'sameOfd':v==0})
 return {'name':name,'metadata':metadata9(s),'fds':linked,'lockingFds':locking,'relations':relations}
def same_peer():
 q="begin read only;select json_build_object('pid',pid,'port',client_port,'address',host(client_addr),'role',usename,'app',application_name,'database',datname,'state',state,'backendStart',backend_start)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and mode='ExclusiveLock'and granted;commit;"
 lines=command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],4096).splitlines();require(len(lines)==2 and lines[1]==b'1')
 peer=json.loads(lines[0]);require(type(peer['pid'])is int and peer['pid']>0 and peer['address']=='127.0.0.1'and type(peer['port'])is int and 1<=peer['port']<=65535 and peer['role']=='schubert_batch'and peer['app']=='PG1719-bootstrap-guard'and peer['database']=='schubert_nk'and peer['state']=='idle in transaction')
 q="begin read only;select count(*)from pg_locks where pid="+str(peer['pid'])+" and locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;commit;"
 require(command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],4096).strip()==b'1')
 def sockets(pid):return {os.readlink(f)[8:-1]for f in(pathlib.Path('/proc')/str(pid)/'fd').iterdir()if os.readlink(f).startswith('socket:[')}
 def endpoint(v):
  import ipaddress
  a,p=v.split(':');r=bytes.fromhex(a);ip=ipaddress.ip_address(b''.join(r[i:i+4][::-1]for i in range(0,len(r),4)))
  if isinstance(ip,ipaddress.IPv6Address):ip=ip.ipv4_mapped
  return str(ip),int(p,16)
 rows=[l.split()for n in ['tcp','tcp6']for l in pathlib.Path('/proc/net',n).read_text().splitlines()[1:]]
 c=sockets(383695);s=sockets(peer['pid']);local=('127.0.0.1',peer['port']);database=('127.0.0.1',5432)
 left=[r for r in rows if len(r)>=10 and r[3]=='01'and r[9]in c and endpoint(r[1])==local and endpoint(r[2])==database]
 right=[r for r in rows if len(r)>=10 and r[3]=='01'and r[9]in s and endpoint(r[1])==database and endpoint(r[2])==local]
 require(len(left)==len(right)==1)
 return {'activity':peer,'clientInode':left[0][9],'serverInode':right[0][9]}
'''

TAIL = r'''
tool=base/TOOL_NAME
require({p.relative_to(tool).as_posix()for p in tool.rglob('*')if p.is_file()}==set(TOOL_HASHES)|{'payload-sha256.json'})
for n,h in TOOL_HASHES.items():
 p=tool/n;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(p)and hashlib.sha256(p.read_bytes()).hexdigest()==h)
require(json.loads((tool/'payload-sha256.json').read_bytes())==TOOL_HASHES)
failure=base/'pg1719-bootstrap-verify-v3';require(failure.is_dir()and not list(failure.iterdir()))
a=actor();require(a==actor());locks=[owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']];peer=same_peer();require(peer==same_peer())
save=base/SLOT;require(not os.path.lexists(save));save.mkdir(mode=0o700)
value={'actor':a,'locks':locks,'peer':peer,'native':native,'toolHashes':TOOL_HASHES,'productionSource':SOURCE,'all24And32And187Unchanged':True,'allTenKernelEmpty':True,'noRefChildOrUnitStart':True,'signals0':True,'oldCloseUnknown':True}
encoded=json.dumps(value,sort_keys=True).encode()
with(save/'proof.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'proofSha256':hashlib.sha256(encoded).hexdigest(),'productionSource':SOURCE,'parentPid':383695,'ticks':7281859,'backendPid':peer['activity']['pid'],'fdCount':99,'child0':True,'samePeer':True,'ownedLocks':2,'allOriginalValuesUnchanged':True,'signals0':True,'oldCloseUnknown':True,'formalAccepted':False}))
'''

def payload():
    fixed=json.loads((W/'pg1720-frozen-v1.safe.json').read_bytes())
    if fixed['actualExit']!=0 or fixed['productionSource']!=SOURCE:raise ValueError('actual frozen111 source required')
    raw=before_payload();raw=raw[:raw.index('dependency_fields=')]+"\nfinally:\n for u in reversed(refs):manager.UnrefUnit(u)\n bus.close()\n"
    raw=raw.replace("lines[-2:]==[b'0',b'0']","lines[-2:]==[b'1',b'1']")
    start=raw.index("  for name in ('maintenance.lock','startup-admission.lock'):")
    end=raw.index("  require(tree(pathlib.Path('/run/systemd/system'))",start)
    raw=raw[:start]+"  for name in ('maintenance.lock','startup-admission.lock'):owned_lock(name)\n"+raw[end:]
    marker='bus=dbus.SystemBus(private=True);manager='
    at=raw.index(marker);raw=raw[:at]+ACTOR+'\n'+raw[at:]
    # Capture all-current Unit Ref scope first; no artificial business changes.
    cp='/var/lib/pgpt-s1-preservation/'+TOOLS+':/opt/schubert-nk/releases/0.1.0-PG1638/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG1638/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG1638/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG1638/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
    argv=['/opt/jdk-25.0.4/bin/java','--enable-native-access=ALL-UNNAMED','-cp',cp,'Pg1719BootstrapExisting','verify']
    raw='EXPECTED_ARGV='+repr(b'\0'.join(s.encode()for s in argv)+b'\0')+'\nTOOL_HASHES='+repr(fixed['fileHashes'])+'\nTOOL_NAME='+repr(TOOLS)+'\nSLOT='+repr(SLOT)+'\n'+raw+TAIL
    from pyflakes.api import check
    if check(raw,'<preRef current soleDB whole proof>'):raise ValueError('generated static refused')
    compile(raw,'<preRef current soleDB whole proof>','exec');return raw

def main():
    log=(W/'pg1721-verify-v1.private.log').read_bytes()
    if b'PG1719_BOOTSTRAP_RETIRE_UNKNOWN phase=PREPARE_DATABASE_SCOPE type=java.lang.IllegalArgumentException ownershipRetained=true oldCloseNotInferred=true\n'not in log or b'FRAME method=open line=53\n'not in log or (W/'pg1721-verify-v1.exit').exists():
        raise ValueError('actual immutable preRef retained phase required')
    java=(W/TOOLS/'Pg1719BootstrapExisting.java').read_text()
    if 'try(var database=open()){\n            refs=new References(backend(database),database);'not in java:
        raise ValueError('constructor refusal must precede Ref and business actions')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode();(out/'payload.private.py').write_bytes(raw)
    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=90)
    (out/'stderr.private.log').write_bytes(r.stderr)
    v={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'signals0':True,'formalAccepted':False}
    if r.returncode==0:v['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(v,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(v));return r.returncode

if __name__=='__main__':raise SystemExit(main())
