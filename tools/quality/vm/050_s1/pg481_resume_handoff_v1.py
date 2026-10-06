"""BUG773/SSC191 exact pre-mutation Java only pidfd handoff; historical close remains unknown."""
import ast,hashlib,json,os,pathlib,select,signal,stat,subprocess,sys,time
import dbus
PID=3568101;TICKS=23013792;CLASS='2dec8706d6a1681868b385ff8e4d5f807f1d0ff8490a9df9219b1d6b2da6b4e2'
CHILD=3568130;CHILD_TICKS=23013918;CHILD_HASH='cc1706eb00d671ed52eefa7022a406d9029438634a5ef44eb5d36a2c3d167aa2'
BOOT='e07aa706-1acd-4e65-b309-d7f330f79d54'
ROOT=pathlib.Path('/var/lib/pgpt-s1-preservation/pg481-resume-handoff-v1')
SOURCE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg481-resume-tools-v1/pg481_resume_refs.py')
def require(v):
 if not v:raise ValueError('exact Backup tool handoff refused')
def tick():return int((pathlib.Path('/proc')/str(PID)/'stat').read_text().rpartition(')')[2].split()[19])
def actor(child_present=True):
 require(tick()==TICKS);p=pathlib.Path('/proc')/str(PID);args=(p/'cmdline').read_bytes().split(b'\0')
 require(len(args)==7 and args[0]==b'/opt/jdk-25.0.4/bin/java' and args[1:3]==[b'--enable-native-access=ALL-UNNAMED',b'-cp'] and args[-3:]==[b'Pg481ResumePreparation',b'prepare',b''])
 require(hashlib.sha256(SOURCE.with_name('Pg481ResumePreparation.class').read_bytes()).hexdigest()==CLASS)
 tasks=sorted(p.joinpath('task').iterdir());children=[v for t in tasks for v in t.joinpath('children').read_text().split()];require(tasks and children==([str(CHILD)] if child_present else []) and tick()==TICKS)
 targets=[]
 for fd in p.joinpath('fd').iterdir():
  try:targets.append(str(fd.readlink()))
  except FileNotFoundError:continue
 for name in ['maintenance.lock','startup-admission.lock']:
  path=pathlib.Path('/run/schubert-nk')/name;s=path.lstat();require(s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1 and str(path) in targets)
  matches=[]
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)>=8 and f[1:5]==['FLOCK','ADVISORY','WRITE',str(PID)]:
    d=f[5].split(':')
    if len(d)==3 and tuple(int(x,16) for x in d[:2])+(int(d[2]),)==(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino):matches.append(line)
  require(len(matches)==1)
 old=pathlib.Path('/var/lib/pgpt-s1-preservation/pg481-resume-preparation');m=old.lstat();require(stat.S_ISDIR(m.st_mode) and m.st_uid==m.st_gid==0 and stat.S_IMODE(m.st_mode)==0o700 and set(p.name for p in old.iterdir())=={'before.private.json','native-dropin-before.private'})
def snapshot():
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
 units={}
 for u in UNITS:
  v=show(u,FIELDS);require(v==previous['units'][u] and v['MainPID']==v['ControlPID']=='0' and not v['Job']);kernel(u);units[u]=v
 require(command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-q','-A','-t','-d','schubert_nk','-c',"select count(*) from pg_stat_activity where datname='schubert_nk' and usename in ('schubert_batch','schubert_api','schubert_web','schubert_inspector');"],4096).strip()==b'0')
 paths=['/var/lib/schubert-nk/maintenance','/srv/schubert-nk/backup','/srv/schubert-nk/data/transfer','/run/schubert-nk/startup','/run/schubert-nk/backup-request','/run/schubert-nk/cleanup-request','/run/schubert-nk/expiry-request','/run/schubert-nk/pt-coverage','/etc/schubert-nk','/run/systemd/system/schubert-nk-morning-controller.service.d','/var/lib/pgpt-s1-preservation/pg481-resume-preparation']
 configuration={}
 for u in UNITS:
  old=previous['configuration'][u];got=show(u,set(old));require(all(got[k]==old[k] for k in set(old)-{'ExecStart','DropInPaths'}))
  a=exec_record(old['ExecStart']);b=exec_record(got['ExecStart']);require(a is not None and b is not None)
  if u=='schubert-nk-morning-controller.service':
   require(b[:3]==(a[0],a[1]+' --resume 49437eda-1681-43a9-883a-424eb55a6166',a[2]))
   require(got['DropInPaths']==old['DropInPaths']+' /run/systemd/system/schubert-nk-morning-controller.service.d/pg481-once-resume.conf')
  else:require(a[:3]==b[:3] and got['DropInPaths']==old['DropInPaths'])
  configuration[u]=got
 return {'units':units,'configuration':configuration,'rows':rows(),'trees':{p:tree(pathlib.Path(p)) for p in paths},'current':str(pathlib.Path('/opt/schubert-nk/current').readlink())}
def save(name,value):
 with (ROOT/name).open('x') as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 fd=os.open(ROOT,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
phase='PREFLIGHT';bus=None;refs=[]
try:
 require(os.geteuid()==0 and sys.argv[1:]==['handoff'] and not ROOT.exists());os.umask(0o077)
 code=ast.parse(pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py').read_text());definitions=[n for n in code.body if isinstance(n,ast.FunctionDef) and n.name in ['command','metadata','tree','show','rows','kernel']]
 require(len(definitions)==6);exec(compile(ast.Module(body=definitions,type_ignores=[]),'<fixed readonly witness>','exec'),globals())
 previous=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg481-resume-preparation/before.private.json').read_text())
 import re
 policy=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/pg477_unit_references.py').read_bytes();require(hashlib.sha256(policy).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
 parse=next(n for n in ast.parse(policy).body if isinstance(n,ast.FunctionDef) and n.name=='exec_record');exec(compile(ast.Module(body=[parse],type_ignores=[]),'<fixed declaration>','exec'),globals())
 UNITS=list(previous['units']);FIELDS=set(next(iter(previous['units'].values())));actor();ROOT.mkdir(mode=0o700)
 bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
 phase='REF_ACQUIRE'
 for u in UNITS:manager.RefUnit(u);refs.append(u)
 before=snapshot();actor();save('before.private.json',before)
 child=pathlib.Path('/proc')/str(CHILD);require(int(child.joinpath('stat').read_text().rpartition(')')[2].split()[19])==CHILD_TICKS and int(child.joinpath('stat').read_text().rpartition(')')[2].split()[1])==PID)
 require(child.joinpath('cmdline').read_bytes().split(b'\0')==[b'/usr/bin/python3',b'-B',str(SOURCE).encode(),b'prepare',b'3568128',b''] and hashlib.sha256(SOURCE.read_bytes()).hexdigest()==CHILD_HASH)
 require(not any(t.joinpath('children').read_text().strip() for t in child.joinpath('task').iterdir()))
 childfd=os.pidfd_open(CHILD,0)
 try:
  actor();require(snapshot()==before);signal.pidfd_send_signal(childfd,signal.SIGTERM);poll=select.poll();poll.register(childfd,select.POLLIN);require(poll.poll(5000))
 finally:os.close(childfd)
 end=time.monotonic()+5
 while child.exists() and time.monotonic()<end:time.sleep(.01)
 require(not child.exists());actor(False)
 fd=os.pidfd_open(PID,0)
 try:
  actor(False);require(snapshot()==before);phase='EXACT_PIDFD_TERM';signal.pidfd_send_signal(fd,signal.SIGTERM)
  poll=select.poll();poll.register(fd,select.POLLIN);require(poll.poll(5000))
 finally:os.close(fd)
 end=time.monotonic()+5
 while pathlib.Path('/proc',str(PID)).exists() and time.monotonic()<end:time.sleep(.01)
 require(not pathlib.Path('/proc',str(PID)).exists());phase='AFTER_HANDOFF';after=snapshot();require(after==before);save('after.private.json',after)
 require(not any(r.split()[4:5]==[str(PID)] for r in pathlib.Path('/proc/locks').read_text().splitlines()))
 phase='REF_RELEASE'
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close();save('interrupted.private.json',{'oldPid':PID,'oldTicks':TICKS,'oldClass':CLASS,'oldCloseUnknown':True,'oldSuccessInferred':False,'allOldValuesUnchanged':True,'newScopeReturnedNormally':True,'newOwnershipRequired':True})
 print('PG481_RESUME_HANDOFF exactPidfdTerm=true allOldValuesUnchanged=true oldCloseUnknown=true newScopeReturnedNormally=true starts0=true')
except Exception:
 print('PG481_RESUME_HANDOFF_UNKNOWN phase='+phase+' refsRetained=true',file=sys.stderr,flush=True)
 while True:time.sleep(1)
