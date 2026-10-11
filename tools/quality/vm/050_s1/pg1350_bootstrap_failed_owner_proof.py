"""Read-only current fullscope and exact failed Bootstrap Java/DB/socket/M-A proof."""
import ast
import inspect
import pg1340_published_stop_independent_post_v4 as prior
from pg1334_published_owned_stop_sources_v2 import SOURCE

OWNER = r'''
def fixed_owner():
 candidates=[]
 for p in pathlib.Path('/proc').iterdir():
  if p.name.isdigit():
   try:a=(p/'cmdline').read_bytes()
   except(FileNotFoundError,ProcessLookupError,PermissionError):continue
   if b'Pg1348BootstrapExisting\x00verify\x00' in a:candidates.append((p,a))
 require(len(candidates)==1);p,argv=candidates[0];pid=int(p.name)
 status=dict(x.split(':',1)for x in(p/'status').read_text().splitlines()if ':'in x)
 fields=(p/'stat').read_text().rpartition(')')[2].split();ticks=int(fields[19])
 require(status['Uid'].split()==status['Gid'].split()==['0']*4 and status['Groups'].split()==['0'])
 require(str((p/'exe').readlink())=='/opt/jdk-25.0.4/bin/java'and b'/var/lib/pgpt-s1-preservation/pg1348-bootstrap-tools-v3:'in argv and b'/opt/schubert-nk/releases/0.1.0-PG1292/'in argv)
 kids={x for t in(p/'task').iterdir()for x in(t/'children').read_text().split()};require(not kids)
 q="select json_build_object('pid',pid,'clientPort',client_port)from pg_stat_activity a where datname='schubert_nk'and usename='schubert_batch'and application_name='PG1348-bootstrap-guard'and state='idle in transaction'and client_addr=inet '127.0.0.1'and exists(select 1 from pg_locks l where l.pid=a.pid and l.locktype='advisory'and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.mode='ExclusiveLock'and l.granted);"
 rows=command(['sudo','-n','-u','postgres','psql','-X','-qAt','-d','schubert_nk','-c',q]).splitlines();require(len(rows)==1);peer=json.loads(rows[0]);require(set(peer)=={'pid','clientPort'}and all(type(v)is int and v>1 for v in peer.values()))
 links=[];sockets=set()
 for fd in(p/'fd').iterdir():
  try:value=str(fd.readlink())
  except FileNotFoundError:continue
  links.append(value)
  if value.startswith('socket:[')and value.endswith(']'):sockets.add(value[8:-1])
 require((p/'ns/net').stat().st_ino==pathlib.Path('/proc/self/ns/net').stat().st_ino)
 local={'0100007F:'+format(peer['clientPort'],'04X'),'0000000000000000FFFF00000100007F:'+format(peer['clientPort'],'04X')};remote={'0100007F:1538','0000000000000000FFFF00000100007F:1538'}
 network=[line.split()for name in ['tcp','tcp6']for line in(p/'net'/name).read_text().splitlines()[1:]]
 require(len([r for r in network if len(r)>=10 and r[1]in local and r[2]in remote and r[3]=='01'and r[9]in sockets])==1)
 locks={}
 for name in ['maintenance.lock','startup-admission.lock']:
  path=pathlib.Path('/run/schubert-nk')/name;st=path.lstat();require(stat.S_ISREG(st.st_mode)and(st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode),st.st_nlink)==(0,0,0o600,1)and str(path)in links)
  found=[]
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)>=8 and f[1:5]==['FLOCK','ADVISORY','WRITE',str(pid)]:
    d=f[5].split(':')
    if (int(d[0],16),int(d[1],16),int(d[2]))==(os.major(st.st_dev),os.minor(st.st_dev),st.st_ino):found.append(line)
  require(len(found)==1);locks[name]=metadata9(st)
 root=base/'pg1348-bootstrap-verify-v3';require({x.name for x in root.iterdir()}==set())
 return {'pid':pid,'ticks':ticks,'ppid':int(status['PPid']),'argvSha256':hashlib.sha256(argv).hexdigest(),'backend':peer['pid'],'clientPort':peer['clientPort'],'locks':locks,'failedSave':tree(root)}
'''

def payload(seals):
    raw = prior.payload(seals)
    marker = 'bus=dbus.SystemBus(private=True);'
    if raw.count(marker) != 1:
        raise ValueError('one actual independent manager scope required')
    raw = raw.replace(marker, OWNER + '\n' + marker)
    raw = raw.replace("lines[-2:]==[b'0',b'0']", "lines[-2:]==[b'1',b'1']")
    old = "require((int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino))"
    if raw.count(old) != 1:
        raise ValueError('one fixed owner FLOCK boundary required')
    raw = raw.replace(old, "\n     if (int(d[0],16),int(d[1],16),int(d[2]))==(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino):require(f[1:5]==['FLOCK','ADVISORY','WRITE',str(owner['pid'])])")
    marker = ' native=snapshot();require(native==snapshot())'
    if raw.count(marker) != 1:
        raise ValueError('one complete two-read snapshot required')
    raw = raw.replace(marker, " owner=fixed_owner();native=snapshot();require(native==snapshot()and owner==fixed_owner())")
    raw = raw.replace('pg1340-published-terminal-post-v4', 'pg1350-bootstrap-failed-owner-v1').replace('PG1340-published-terminal-post-v4', 'PG1350-bootstrap-failed-owner-v1')
    marker = "with(save/'result.safe.json').open('x')as f:"
    raw = raw.replace(marker, "blob=json.dumps({'current':after,'native':native,'owner':owner},sort_keys=True).encode()\nwith(save/'before.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(blob);f.flush();os.fsync(f.fileno())\nresult.update(privateBeforeSha256=hashlib.sha256(blob).hexdigest(),fixedOwner=owner,allClientAdvisoryFlock0=False,oldNormalClose=False,signals0=True)\n" + marker)
    ast.parse(raw)
    return raw

def source():
    return prior.source().replace('pg1340-published-terminal-post-v4', 'pg1350-bootstrap-failed-owner-v1')

def main():
    env = dict(prior.previous.transport.__dict__, SOURCE=SOURCE, payload=payload)
    exec(compile(source(), '<actual fixed failed owner proof>', 'exec'), env)
    return env['main']()

if __name__ == '__main__':
    raise SystemExit(main())
