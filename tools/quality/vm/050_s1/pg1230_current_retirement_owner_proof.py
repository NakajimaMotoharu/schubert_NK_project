"""Full current readonly proof of fixed failed retire cohort, no signals/actions."""
import inspect
import pg1222_completed_retirement_preflight as transport
import pg1229_actual_runtime_schema_preflight_v2 as previous

def payload():
    s=previous.payload()
    a="require(len(lines)==26 and lines[-2:]==[b'0',b'0'])"
    if s.count(a)!=1:raise ValueError('fixed one backend aggregate insertion rejected')
    s=s.replace(a,"require(len(lines)==26 and lines[-2:]==[b'1',b'1'])")
    a="require((int(d[0],16),int(d[1],16),s.st_ino))"
    old="require((int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino))"
    if s.count(old)!=1:raise ValueError('fixed maintenance holder insertion rejected')
    s=s.replace(old,"\n     if (int(d[0],16),int(d[1],16),int(d[2]))==(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino):require(f[1:5]==['FLOCK','ADVISORY','WRITE','560237'])")
    marker=' native=snapshot();require(native==snapshot())'
    if s.count(marker)!=1:raise ValueError('fixed whole owner observation join rejected')
    s=s.replace(marker," fixed=fixed_owner();native=snapshot();require(native==snapshot()and fixed==fixed_owner())")
    pos=s.index('try:\n for u in UNITS:');s=s[:pos]+OWNER+'\n'+s[pos:]
    s=s.replace("'run':'PG1229-runtime-schema-preflight-v2'","'run':'PG1230-current-retirement-owner-proof-v1'")
    s=s.replace('print(json.dumps(result))',SAVE)
    compile(s,'<fixed completed current owner proof>','exec');return s

OWNER=r'''
COHORT={560237:(5931043,'a2a6e372a802b53532507516ca880eff09efc0f6bf6f86aa27b70047c110d13f','/opt/jdk-25.0.4/bin/java',560235),560266:(5931153,'36d743b2577c621d0d6ae368d691e9555c7010d08af35b07628f7c470c330a01','/usr/bin/python3.14',560237)}
def fixed_owner():
 value={}
 for pid,(ticks,argv,exe,ppid)in COHORT.items():
  proc=pathlib.Path('/proc')/str(pid);status=dict(x.split(':',1)for x in(proc/'status').read_text().splitlines()if ':'in x)
  require(int((proc/'stat').read_text().rpartition(')')[2].split()[19])==ticks and hashlib.sha256((proc/'cmdline').read_bytes()).hexdigest()==argv and str((proc/'exe').readlink())==exe)
  require(status['Uid'].split()==status['Gid'].split()==['0']*4 and status['Groups'].split()==['0']and int(status['PPid'])==ppid)
  kids={x for t in(proc/'task').iterdir()for x in(t/'children').read_text().split()};require(kids==({'560266'}if pid==560237 else set()))
  d=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus');names=[str(n)for n in d.ListNames()if str(n).startswith(':')and int(d.GetConnectionUnixProcessID(n))==pid]
  require(names==([':1.312146']if pid==560266 else []));value[str(pid)]={'ticks':ticks,'argvSha256':argv,'children':sorted(kids),'bus':names}
 java=pathlib.Path('/proc/560237');links=[];sockets=set()
 for f in(java/'fd').iterdir():
  try:t=str(f.readlink())
  except FileNotFoundError:continue
  links.append(t)
  if t.startswith('socket:[')and t.endswith(']'):sockets.add(t[8:-1])
 locks={}
 for name in ['maintenance.lock','startup-admission.lock']:
  p=pathlib.Path('/run/schubert-nk')/name;m=metadata(p);require(m[2:6]==[0,0,stat.S_IFREG|0o600,1]and str(p)in links)
  found=[]
  for row in pathlib.Path('/proc/locks').read_text().splitlines():
   f=row.split()
   if len(f)>=8 and f[1:5]==['FLOCK','ADVISORY','WRITE','560237']:
    a=f[5].split(':')
    if (int(a[0],16),int(a[1],16),int(a[2]))==(os.major(m[0]),os.minor(m[0]),m[1]):found.append(row)
  require(len(found)==1);locks[name]={'metadata':m,'record':found[0]}
 require((java/'ns/net').stat().st_ino==pathlib.Path('/proc/self/ns/net').stat().st_ino)
 network=[]
 for name in ['tcp','tcp6']:network.extend(row.split()for row in(java/'net'/name).read_text().splitlines()[1:])
 local={'0100007F:C868','0000000000000000FFFF00000100007F:C868'};remote={'0100007F:1538','0000000000000000FFFF00000100007F:1538'}
 require(len([r for r in network if len(r)>=10 and r[1]in local and r[2]in remote and r[3]=='01'and r[9]in sockets])==1)
 q="select count(*)from pg_stat_activity a where pid=560264 and datname='schubert_nk'and usename='schubert_batch'and application_name='PG998-native-stop'and state='idle in transaction'and client_addr=inet '127.0.0.1'and client_port=51304 and exists(select 1 from pg_locks l where l.pid=a.pid and l.locktype='advisory'and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.mode='ExclusiveLock'and l.granted);"
 require(command(['sudo','-n','-u','postgres','psql','-X','-qAt','-d','schubert_nk','-c',q]).strip()==b'1')
 root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1224-native-stop-v1');require(set(p.name for p in root.iterdir())=={'refs-prepare.private.log'})
 log=(root/'refs-prepare.private.log').read_bytes();require(hashlib.sha256(log).hexdigest()=='1a4fd823822d72e100c46fa991653dcb1a2f2f3b21cf0c223231183c94890ff2')
 value.update(locks=locks,backend=560264,clientPort=51304,failureFiles=tree(root));return value
'''

SAVE=r'''
root=base/'pg1230-current-retirement-owner-proof-v1';require(not os.path.lexists(root))
bus=dbus.SystemBus(private=True)
try:require(fixed==fixed_owner())
finally:bus.close()
root.mkdir(mode=0o700)
observed={'current':after,'native':native,'owner':fixed}
blob=json.dumps(observed,sort_keys=True).encode()
with(root/'before.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(blob);f.flush();os.fsync(f.fileno())
for p in (root,root.parent):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
result.update(fixedOwnerPeerAndLocksPinned=True,privateBeforeSha256=hashlib.sha256(blob).hexdigest(),currentOwnedBackend=560264,oldNormalClose=False,signalsAttempted=0)
result['allClientAdvisoryFlock0']=False
print(json.dumps(result))
'''

def main():
    entry=inspect.getsource(transport.main).replace('pg1222-completed-retirement-preflight-v1','pg1230-current-retirement-owner-proof-v1')
    env=dict(transport.__dict__);env['payload']=payload
    exec(compile(entry,'<current fixed whole owner transport>','exec'),env);return env['main']()

if __name__=='__main__':raise SystemExit(main())
