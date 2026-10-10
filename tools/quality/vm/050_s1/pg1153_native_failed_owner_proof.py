"""Read-only full original and exact current UNKNOWN operator ownership proof."""
import ast
import inspect
import json
from pg1147_terminal_management_post import payload as previous
from pg1041_cold_policy_diagnostic import W
import pg1120_current_failed_capture as transport


def payload():
    raw=previous();raw=raw[:raw.index('COMPLETE=pathlib.Path(')]
    raw=raw.replace('terminal-management-post-v1','native-failed-owner-proof-v1')
    frozen=json.loads((W/'pg1151-native-five-frozen-v3.safe.json').read_bytes())
    if frozen['actualExit']!=0:raise ValueError('fixed new operator closure refused')
    raw='FILES='+repr(frozen['fileHashes'])+'\n'+raw+BODY
    ast.parse(raw);return raw


BODY=r'''
PRIOR=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/terminal-management-post-v1/after.private.json')
prior=PRIOR.read_bytes();require(hashlib.sha256(prior).hexdigest()=='cfd139237f179e7531b94d28c1570c07af9612b476857f3eb479d9a732a7c0b9')
CURRENT=json.loads(prior)
JAVA=410279;CHILD=410308
def tick(pid):return int((pathlib.Path('/proc')/str(pid)/'stat').read_text().rpartition(')')[2].split()[19])
def actor(pid,ticks,digest,exe,children):
 p=pathlib.Path('/proc')/str(pid);require(tick(pid)==ticks and str((p/'exe').readlink())==exe and hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()==digest)
 require((p/'status').read_text().split('Uid:')[1].splitlines()[0].split()==['0']*4)
 require({int(v)for t in(p/'task').iterdir()for v in(t/'children').read_text().split()}==children)
 return {'pid':pid,'ticks':ticks,'argvSha256':digest,'exe':exe,'children':sorted(children)}
def lock_proof():
 result={};proc=pathlib.Path('/proc')/str(JAVA)
 for name in ['maintenance.lock','startup-admission.lock']:
  p=pathlib.Path('/run/schubert-nk')/name;m=md(p);s=p.stat();require(m[2:7]==[0,0,stat.S_IFREG|0o600,1,0]and not os.listxattr(p))
  fds={}
  for f in(proc/'fd').iterdir():
   try:
    if str(f.readlink())==str(p):
     held=f.stat();require([held.st_dev,held.st_ino,held.st_uid,held.st_gid,held.st_mode,held.st_nlink,held.st_size,held.st_mtime_ns,held.st_ctime_ns]==m)
     fds[f.name]=(proc/'fdinfo'/f.name).read_text().split('flags:')[1].splitlines()[0].strip()
   except FileNotFoundError:pass
  require(bool(fds));matches=[]
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   v=line.split()
   if len(v)>=8 and len(v[5].split(':'))==3:
    d=v[5].split(':')
    if(int(d[0],16),int(d[1],16),int(d[2]))==(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino):matches.append(v)
  require(len(matches)==1 and matches[0][1:5]==['FLOCK','ADVISORY','WRITE',str(JAVA)])
  result[name]={'metadata':m,'fds':fds}
 return result
def resource_zero():
 live=pathlib.Path('/proc',str(JAVA)).exists()
 sql="select count(*)from pg_stat_activity where datname='schubert_nk'and usename in('schubert_batch','schubert_app','schubert_web_session','schubert_backup','schubert_inbox_inspector');select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and granted;"
 require(command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-d','schubert_nk','-c',sql]).splitlines()==([b'1',b'1']if live else[b'0',b'0']))
 if live:
  sql="select count(*)from pg_stat_activity a where a.datname='schubert_nk'and a.usename='schubert_batch'and a.application_name='PG1148-fixed-recovery'and exists(select 1 from pg_locks l where l.pid=a.pid and l.locktype='advisory'and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.mode='ExclusiveLock'and l.granted);"
  require(command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-d','schubert_nk','-c',sql]).splitlines()==[b'1'])
def current():
 v=capture();require(v==CURRENT);return v
def owner():
 java=actor(JAVA,4653404,'98f1a3a4ae2d298e8eae985059cf6a30f3f203fbb5ede0ec95350b3ab9f15791','/opt/jdk-25.0.4/bin/java',{CHILD})
 child=actor(CHILD,4653520,'48eb3b90dae4122879878b95aa6a7db29aff1a052c6b7cfddc4f981c8d262b3c','/usr/bin/python3.14',set())
 require(int((pathlib.Path('/proc',str(CHILD),'stat').read_text().rpartition(')')[2].split()[1]))==JAVA)
 root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1148-native-five-tools-v3');dirs={p.as_posix()for n in FILES for p in pathlib.PurePosixPath(n).parents if p.as_posix()!='.'}
 require({p.relative_to(root).as_posix()for p in root.rglob('*')}==set(FILES)|dirs)
 for p in[root,*root.rglob('*')]:
  s=p.lstat();require(not p.is_symlink()and s.st_uid==s.st_gid==0 and not os.listxattr(p))
  if p.is_dir():require(stat.S_IMODE(s.st_mode)==0o700)
  else:require(stat.S_ISREG(s.st_mode)and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o400 and hashlib.sha256(p.read_bytes()).hexdigest()==FILES[p.relative_to(root).as_posix()])
 error=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1148-native-five-recovery-v1/refs.private.err').read_bytes();require(hashlib.sha256(error).hexdigest()=='f9790b619e2420ce980281c7ef5317e93b9efd93b787c063cdd7e3961cde2094')
 names=[]
 for n in daemon.ListNames():
  if str(n).startswith(':'):
   try:
    if int(daemon.GetConnectionUnixProcessID(n))==CHILD:names.append(str(n))
   except dbus.DBusException:pass
 require(len(names)==1 and int(daemon.GetConnectionUnixUser(names[0]))==0)
 resource_zero();return {'java':java,'child':child,'locks':lock_proof(),'childBus':names[0],'oldNormalClose':False}
def whole():return {'current':current(),'owner':owner()}
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus');refs=[]
try:
 for u in units:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)
 owned_snapshot=whole();require(owned_snapshot==whole());SAVE.mkdir(mode=0o700)
 with(SAVE/'observed.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(owned_snapshot,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 require(owned_snapshot==whole())
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'privateSnapshotSha256':hashlib.sha256((SAVE/'observed.private.json').read_bytes()).hexdigest(),'fixedNativeOwner':True,'allOriginalsUnchanged':True,'nativeMutation0':True,'signals0':True,'newMetadataNormalClose':True,'oldOperationNormalClose':False,'formalAccepted':False}))
'''


def main():
    text=inspect.getsource(transport.main).replace('pg1120-current-failed-capture-v1','pg1153-native-failed-owner-proof-v1').replace('PG1120-current-failed-capture-v1','PG1153-native-failed-owner-proof-v1')
    env=dict(transport.__dict__);env['PAYLOAD']=payload();exec(compile(text,'<fixed current native owner proof>','exec'),env);return env['main']()


if __name__=='__main__':raise SystemExit(main())
