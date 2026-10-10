"""Fixed failed-stop full24/full32/187/proc/DB/Ref/FD proof, signal0."""
import inspect
import pg1222_completed_retirement_preflight as transport
from pg1246_fresh_completed_capture_v3 import payload as previous
from pg1247_fresh_owned_stop_sources import GUEST_BEFORE,BEFORE

def payload():
    s=previous().replace('fresh-completed-capture-v3','fresh-stop-failed-owner-v1')
    s=s[:s.index('bus=dbus.SystemBus(private=True);manager=')]
    s+='\nBASELINE='+repr(GUEST_BEFORE)+'\nBASELINE_SHA='+repr(BEFORE)+'\n'+OWNER+'\n'+BODY
    compile(s,'<fixed failed stop complete owner proof>','exec');return s

OWNER=r'''
COHORT={691075:(6303152,'672b75588b7097cbd4edca1798498b5ab6e91664b5c7ea71b206284795198700','/opt/jdk-25.0.4/bin/java',691073),691104:(6303259,'26ec215f65f3e8eb78a4093424ad61ef625d3dc502ea5037b1ac4b5e7c8131ce','/usr/bin/python3.14',691075)}
def fixed_owner():
 values={}
 daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus')
 for pid,(ticks,digest,exe,ppid)in COHORT.items():
  p=pathlib.Path('/proc')/str(pid);fields=(p/'stat').read_text().rpartition(')')[2].split();a=(p/'cmdline').read_bytes();status=dict(x.split(':',1)for x in(p/'status').read_text().splitlines()if ':'in x)
  require(int(fields[19])==ticks and int(fields[1])==ppid and hashlib.sha256(a).hexdigest()==digest and str((p/'exe').readlink())==exe)
  require(status['Uid'].split()==status['Gid'].split()==['0']*4 and status['Groups'].split()==['0'])
  kids=sorted({int(x)for t in(p/'task').iterdir()for x in(t/'children').read_text().split()});require(kids==([691104]if pid==691075 else []))
  names=[str(n)for n in daemon.ListNames()if str(n).startswith(':')and int(daemon.GetConnectionUnixProcessID(n))==pid];require(names==([':1.463495']if pid==691104 else []))
  values[str(pid)]={'ticks':ticks,'argvSha256':digest,'children':kids,'bus':names}
 java=pathlib.Path('/proc/691075');links=[];sockets=set()
 for fd in(java/'fd').iterdir():
  try:value=str(fd.readlink())
  except FileNotFoundError:continue
  links.append(value)
  if value.startswith('socket:[')and value.endswith(']'):sockets.add(value[8:-1])
 locks={}
 for name in ['maintenance.lock','startup-admission.lock']:
  path=pathlib.Path('/run/schubert-nk')/name;st=path.lstat();require(stat.S_ISREG(st.st_mode)and(st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode),st.st_nlink)==(0,0,0o600,1)and str(path)in links)
  found=[]
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   fields=line.split()
   if len(fields)>=8 and fields[1:5]==['FLOCK','ADVISORY','WRITE','691075']:
    dev=fields[5].split(':')
    if tuple([int(dev[0],16),int(dev[1],16),int(dev[2])])==(os.major(st.st_dev),os.minor(st.st_dev),st.st_ino):found.append(line)
  require(len(found)==1);locks[name]={'metadata':md(path),'record':found[0]}
 require('/run/schubert-nk/startup'in links and(java/'ns/net').stat().st_ino==pathlib.Path('/proc/self/ns/net').stat().st_ino)
 local={'0100007F:8DCE','0000000000000000FFFF00000100007F:8DCE'};remote={'0100007F:1538','0000000000000000FFFF00000100007F:1538'}
 network=[line.split()for name in ['tcp','tcp6']for line in(java/'net'/name).read_text().splitlines()[1:]]
 require(len([r for r in network if len(r)>=10 and r[1]in local and r[2]in remote and r[3]=='01'and r[9]in sockets])==1)
 q="select count(*)from pg_stat_activity a where pid=691102 and datname='schubert_nk'and usename='schubert_batch'and application_name='PG998-native-stop'and state='idle in transaction'and client_addr=inet '127.0.0.1'and client_port=36302 and exists(select 1 from pg_locks l where l.pid=a.pid and l.locktype='advisory'and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.mode='ExclusiveLock'and l.granted);select count(*)from pg_stat_activity where datname='schubert_nk'and usename in ('schubert_batch','schubert_backup','schubert_inbox_inspector')and pid<>691102;"
 require(command(['sudo','-n','-u','postgres','psql','-X','-qAt','-d','schubert_nk','-c',q]).splitlines()==[b'1',b'0'])
 root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1247-native-stop-v1');require({p.name for p in root.iterdir()}=={'before.private.json','parent.normal.private','parent.private.jsonl','refs-prepare.private.log','stops-before.private','ticks-before.private'})
 values.update(locks=locks,backend=691102,clientPort=36302,failureFiles=tree(root));return values
'''

BODY=r'''
raw=pathlib.Path(BASELINE).read_bytes();require(hashlib.sha256(raw).hexdigest()==BASELINE_SHA);prior=json.loads(raw)
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for u in units:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)
 owner=fixed_owner();current=capture();require(current==prior and current==capture()and owner==fixed_owner())
 SAVE.mkdir(mode=0o700);blob=json.dumps({'current':current,'owner':owner},sort_keys=True).encode()
 with(SAVE/'before.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(blob);f.flush();os.fsync(f.fileno())
 require(current==capture()and owner==fixed_owner())
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'privateBeforeSha256':hashlib.sha256(blob).hexdigest(),'fixedOwnerCompletePeerAndFlockProven':True,'full24Full32Signed187CurrentUnchanged':True,'businessStops0':True,'signals0':True,'oldNormalClose':False,'formalAccepted':False}))
'''

def main():
    entry=inspect.getsource(transport.main).replace('pg1222-completed-retirement-preflight-v1','pg1251-fresh-stop-failed-owner-v1')
    env=dict(transport.__dict__);env['payload']=payload
    exec(compile(entry,'<new-only fixed failed stop proof transport>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
