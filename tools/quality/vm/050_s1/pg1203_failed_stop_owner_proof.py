"""Fixed pre-Ref stop-tool owner proof; no signal/DB/Unit mutation."""
import ast
import inspect
from pg1197_completed_current_capture import payload as previous
import pg1120_current_failed_capture as transport

PID=553547
TICKS=5550827
ARGV='8006b09714090a3298e90430da333e0a823d5e1ad504473fb0fdc6c2f8a63916'


def prefix():
    s=previous().replace("completed-current-before-v1'","failed-stop-owner-proof-v1'")
    t=ast.parse(s);node=next(n for n in reversed(t.body)if isinstance(n,ast.Try))
    s=s[:sum(len(x)for x in s.splitlines(keepends=True)[:node.lineno-1])]
    s+='\nPID='+repr(PID)+'\nTICKS='+repr(TICKS)+'\nARGV='+repr(ARGV)+'\n'+OWNER
    return s


OWNER=r'''
def fixed_owner():
 p=pathlib.Path('/proc')/str(PID);cmd=(p/'cmdline').read_bytes();status=dict(line.split(':',1)for line in(p/'status').read_text().splitlines()if ':'in line)
 require(int((p/'stat').read_text().rpartition(')')[2].split()[19])==TICKS and hashlib.sha256(cmd).hexdigest()==ARGV)
 require(str((p/'exe').readlink())=='/opt/jdk-25.0.4/bin/java'and cmd.split(b'\0')[-3:]==[b'Pg1198NativeStop',b'stop',b''])
 require(status['Uid'].split()==status['Gid'].split()==['0']*4 and status['Groups'].split()==['0']and status['PPid'].strip()=='553545')
 tasks={x.name:(x/'children').read_text()for x in(p/'task').iterdir()};require(tasks and all(not v.strip()for v in tasks.values()))
 fds=[]
 for fd in(p/'fd').iterdir():
  try:fds.append(str(fd.readlink()))
  except FileNotFoundError:continue
 locks={}
 for name in ['maintenance.lock','startup-admission.lock']:
  target=pathlib.Path('/run/schubert-nk')/name;a=md(target);require(a[2:6]==[0,0,stat.S_IFREG|0o600,1]and str(target)in fds)
  matches=[]
  for row in pathlib.Path('/proc/locks').read_text().splitlines():
   f=row.split()
   if len(f)>=8 and f[1:5]==['FLOCK','ADVISORY','WRITE',str(PID)]:
    d=f[5].split(':')
    if len(d)==3 and(int(d[0],16),int(d[1],16),int(d[2]))==(os.major(a[0]),os.minor(a[0]),a[1]):matches.append(row)
  require(len(matches)==1);locks[name]={'metadata':a,'record':matches[0]}
 daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus')
 for name in daemon.ListNames():
  if str(name).startswith(':'):require(int(daemon.GetConnectionUnixProcessID(name))!=PID)
 old_save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1198-native-stop-v1');require(md(old_save)[2:6]==[0,0,stat.S_IFDIR|0o700,2]and not list(old_save.iterdir()))
 return{'pid':PID,'ticks':TICKS,'argvSha256':ARGV,'tasks':tasks,'locks':locks,'oldEmptySave':entry(old_save),'noChildNoBus':True,'dbZeroCurrentlyNotOldNormal':True}
'''


def payload():
    s=prefix()+BODY
    ast.parse(s);return s


BODY=r'''
sealed=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/completed-current-before-v1/before.private.json').read_bytes()
require(hashlib.sha256(sealed).hexdigest()=='398324fdea98d2469067a1e93858cd292b4e0328da5712b709c7bb99cffeadfa');completed_current=json.loads(sealed)
try:
 for u in CAPTURE_UNITS:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)
 owner=fixed_owner();actual=capture();require(actual==completed_current and actual==capture()and owner==fixed_owner())
 SAVE.mkdir(mode=0o700)
 data=json.dumps({'current':actual,'owner':owner},sort_keys=True).encode()
 with(SAVE/'before.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(data);f.flush();os.fsync(f.fileno())
 require(actual==capture()and owner==fixed_owner())
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'beforePrivateSha256':hashlib.sha256(data).hexdigest(),'wholeCurrentIdentical':True,'fixedPreRefOwnerHeld':True,'currentDb0NotOldNormalClose':True,'signals0':True,'newMetadataReferencesNormalClose':True,'formalAccepted':False}))
'''


def main():
    s=inspect.getsource(transport.main).replace('pg1120-current-failed-capture-v1','pg1203-failed-stop-owner-proof-v1').replace('PG1120-current-failed-capture-v1','PG1203-failed-stop-owner-proof-v1')
    env=dict(transport.__dict__);env['PAYLOAD']=payload();exec(compile(s,'<fixed stop owner fullproof>','exec'),env);return env['main']()


if __name__=='__main__':raise SystemExit(main())
