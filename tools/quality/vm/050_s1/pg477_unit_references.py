"""SSC196: long-lived metadata-only sender under the actual Java M/A owner.
No start/stop/permit/DDL; unknown keeps this sender and the parent owner isolated.
"""
import os,pathlib,subprocess,json,stat,sys,time,hashlib,pwd
import dbus
os.umask(0o077)
BOOT='e07aa706-1acd-4e65-b309-d7f330f79d54'
SOURCE='cce61f63900b1479f9f8dbdc338e222b1c8c38a3'
DIGEST='613b71a06c2b215887219cd3502d3db34542fea957e0d88dbb9c54c8bab18667'
OLD=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG475')
NEXT=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG477')
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-stopped-deploy')
TOOLS=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-stopped-tools-v3')
UNITS=['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service','schubert-nk-morning-controller.service','schubert-nk-bootstrap-admin.service']
FIELDS=set('Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,InvocationID,Type,Restart,RemainAfterExit,Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,KillMode,SendSIGKILL'.split(','))
CONFIG=set('ExecStart,DropInPaths,ReadWritePaths,User,Group,SupplementaryGroups,NoNewPrivileges,ProtectSystem,ProtectHome,PrivateTmp,PrivateDevices,RestrictSUIDSGID,CapabilityBoundingSet,AmbientCapabilities,UMask,LimitCORE,TimeoutStartUSec,TimeoutStopUSec,MemoryMax,TasksMax'.split(','))
config_before=None
bus=None;manager=None;refs=[];before=None;owner=None;phase='PREFLIGHT';configured=False
def require(value):
 if not value:raise ValueError('fixed Unit metadata/configuration refused')
def command(args,timeout=5):
 p=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=timeout)
 require(p.returncode==0 and len(p.stdout)<=1048576);return p.stdout
def show(unit,fields=FIELDS):
 require(unit in UNITS);rows=command(['/usr/bin/systemctl','show',unit,'--property='+','.join(sorted(fields))]).decode('ascii').splitlines();value={}
 for row in rows:
  key,text=row.split('=',1);require(key not in value);value[key]=text
 require(set(value)==fields)
 if 'Id' in fields:require(value['Id']==unit and value['LoadState']=='loaded')
 return value
def kernel(unit):
 p=pathlib.Path('/sys/fs/cgroup/system.slice')/unit
 if p.exists():
  for d in [p,*[x for x in p.rglob('*') if x.is_dir()]]:
   require(not (d/'cgroup.procs').read_text().strip() and 'populated 0\n' in (d/'cgroup.events').read_text())
def holder():
 pid=os.getppid();p=pathlib.Path('/proc')/str(pid);args=(p/'cmdline').read_bytes().split(b'\0')
 require(args[0]==b'/opt/jdk-25.0.4/bin/java' and args[-3:]==[b'Pg477StoppedDeployment',sys.argv[1].encode(),b''])
 tick=int((p/'stat').read_text().rpartition(')')[2].split()[19]);fdpaths=[]
 for fd in (p/'fd').iterdir():
  try:fdpaths.append(str(fd.readlink()))
  except FileNotFoundError:continue
 for name in ['maintenance.lock','startup-admission.lock']:
  path=pathlib.Path('/run/schubert-nk')/name;s=path.lstat()
  require(stat.S_ISREG(s.st_mode) and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1 and str(path) in fdpaths)
  hits=[]
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   fs=line.split()
   if len(fs)>=8 and fs[1:5]==['FLOCK','ADVISORY','WRITE',str(pid)]:
    d=fs[5].split(':')
    if len(d)==3 and (int(d[0],16),int(d[1],16),int(d[2]))==(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino):hits.append(line)
  require(len(hits)==1)
 return pid,tick
def stopped():
 require(holder()==owner and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
 result={}
 for unit in UNITS:
  first=show(unit);require(first['MainPID']==first['ControlPID']=='0' and first['Job']=='' and first['ActiveState'] in ['inactive','failed'] and first['KillMode']=='control-group' and first['SendSIGKILL']=='no')
  kernel(unit);require(first==show(unit));result[unit]=first
 return result
def material(path):
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  s=os.fstat(fd);require(stat.S_ISREG(s.st_mode) and s.st_uid==0 and s.st_nlink==1 and s.st_size<=65536)
  data=os.read(fd,65537);require(len(data)==s.st_size);return data,s
 finally:os.close(fd)
def save(name,data):
 s=SAVE.lstat();require(stat.S_ISDIR(s.st_mode) and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o700)
 fd=os.open(SAVE/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
 with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
 sync(SAVE)
def sync(path):
 fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
def replace(path,data,prior):
 parent=path.parent;require(parent.is_dir() and not parent.is_symlink())
 old,s=material(path);require(old==prior);save('old-'+path.name,old)
 save('old-'+path.name+'-metadata.private',json.dumps([s.st_dev,s.st_ino,s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink]).encode())
 tmp=parent/('pg477-'+path.name+'.part');fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,stat.S_IMODE(s.st_mode))
 with os.fdopen(fd,'wb') as f:
  os.fchown(f.fileno(),s.st_uid,s.st_gid);os.fchmod(f.fileno(),stat.S_IMODE(s.st_mode));f.write(data);f.flush();os.fsync(f.fileno())
 require(material(path)[0]==old);os.replace(tmp,path);sync(parent);require(material(path)[0]==data)
def dropin_preview(unit):
 p=pathlib.Path('/etc/systemd/system')/(unit+'.d')/'pg390-native-coverage.conf'
 raw,s=material(p);require(raw.startswith(b'# PGPT only: same entry/byte/owners; JaCoCo and explicit same-run resume.\n[Service]\nExecStart=\nExecStart='))
 if 'morning' in unit:
  base=material(OLD/'systemd'/unit)[0].decode('ascii')
  starts=[x.removeprefix('ExecStart=') for x in base.splitlines() if x.startswith('ExecStart=')];require(len(starts)==1)
  argv=starts[0].replace('/usr/bin/java ','/usr/bin/java -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=destfile=/run/schubert-nk/pt-coverage/parent/parent.exec,append=false ',1)
  expected=b'# PGPT only: same entry/byte/owners; JaCoCo and explicit same-run resume.\n[Service]\nExecStart=\nExecStart='+argv.encode()+b' --resume 31100027-2222-4333-8444-555555555555\nReadWritePaths=/run/schubert-nk/pt-coverage/parent\n'
  require(raw==expected)
  tail=b' --resume 31100027-2222-4333-8444-555555555555\nReadWritePaths=/run/schubert-nk/pt-coverage/parent\n'
  require(raw.count(tail)==1);next_data=raw.replace(tail,b'\nReadWritePaths=/run/schubert-nk/pt-coverage/parent\n')
 else:
  require(raw==b'# PGPT only: same entry/byte/owners; JaCoCo and explicit same-run resume.\n[Service]\nExecStart=\nExecStart=/opt/pgpt-tools-pg390/schubert-nk-inbox-inspector\nReadWritePaths=/run/schubert-nk/pt-coverage/inspector\n');next_data=None
 return p,raw,s,next_data
def retire(unit):
 p,raw,s,next_data=dropin_preview(unit)
 save('old-'+unit+'-dropin.private',raw);save('old-'+unit+'-dropin-metadata.private',json.dumps([s.st_dev,s.st_ino,s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink]).encode())
 archived=SAVE/('retired-'+unit+'-pg390.conf');require(not archived.exists());os.rename(p,archived);sync(p.parent);sync(SAVE)
 if next_data is not None:
  q=p.parent/'pg477-native-coverage.conf';fd=os.open(q,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,stat.S_IMODE(s.st_mode))
  with os.fdopen(fd,'wb') as f:os.fchown(f.fileno(),s.st_uid,s.st_gid);os.fchmod(f.fileno(),stat.S_IMODE(s.st_mode));f.write(next_data);f.flush();os.fsync(f.fileno())
  sync(q.parent);require(material(q)[0]==next_data)
def configure():
 global configured
 require(sys.argv[1]=='activate' and not configured and stopped()==before)
 require(pathlib.Path('/opt/schubert-nk/current').readlink()==NEXT)
 raw=material(NEXT/'RELEASE-MANIFEST.json')[0];require(hashlib.sha256(raw).hexdigest()==DIGEST and json.loads(raw)['source']['commit']==SOURCE)
 top=pathlib.Path('/run/schubert-nk/pt-coverage');s=top.lstat();require(stat.S_ISDIR(s.st_mode) and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o755)
 for role,account in [('ordinary-inspector196','schubert-inbox-inspector'),('ordinary-bootstrap196','schubert-api')]:
  user=pwd.getpwnam(account);p=top/role;require(not p.exists() and not p.is_symlink());p.mkdir(mode=0o700);os.chown(p,user.pw_uid,user.pw_gid);sync(top)
  after=p.lstat();require((after.st_uid,after.st_gid,stat.S_IMODE(after.st_mode))==(user.pw_uid,user.pw_gid,0o700) and not list(p.iterdir()))
  require(command(['/usr/bin/stat','-f','-c','%T',str(p)]).strip()==b'tmpfs')
  acl=command(['/usr/bin/getfacl','-cpn',str(p)]).decode('ascii').strip();require(acl=='user::rwx\ngroup::---\nother::---')
 for unit in ['schubert-nk-inbox-inspector.service','schubert-nk-bootstrap-admin.service']:
  prior=material(OLD/'systemd'/unit)[0];target=material(NEXT/'systemd'/unit)[0]
  replace(pathlib.Path('/etc/systemd/system')/unit,target,prior)
 retire('schubert-nk-inbox-inspector.service');retire('schubert-nk-morning-controller.service')
 command(['/usr/bin/systemctl','daemon-reload'],30)
 require(stopped()==before)
 for unit in UNITS:
  after=show(unit,CONFIG)
  allowed={'ExecStart','DropInPaths','ReadWritePaths'} if unit in ['schubert-nk-inbox-inspector.service','schubert-nk-bootstrap-admin.service','schubert-nk-morning-controller.service'] else set()
  require(all(after[k]==config_before[unit][k] for k in CONFIG-allowed))
 for unit in ['schubert-nk-inbox-inspector.service','schubert-nk-bootstrap-admin.service','schubert-nk-morning-controller.service']:
  value=show(unit,FIELDS|{'ExecStart','DropInPaths','ReadWritePaths'})
  require('--resume' not in value['ExecStart'] and '/opt/pgpt-tools-pg390/schubert-nk-inbox-inspector' not in value['ExecStart'])
  if 'morning' in unit:require(value['DropInPaths']=='/etc/systemd/system/'+unit+'.d/pg477-native-coverage.conf' and value['ReadWritePaths']=='/run/schubert-nk/pt-coverage/parent')
  elif 'inspector' in unit:require(value['DropInPaths']=='' and value['ReadWritePaths']=='/run/schubert-nk/pt-coverage/ordinary-inspector196' and 'operations/bin/schubert-nk-inbox-inspector' in value['ExecStart'])
  else:require(value['DropInPaths']=='' and value['ReadWritePaths']=='/run/schubert-nk/pt-coverage/ordinary-bootstrap196' and 'sessionid=BOOTSTRAP-${INVOCATION_ID}-ordinary' in value['ExecStart'])
 save('unit-reference-after.private.json',json.dumps(stopped(),sort_keys=True).encode())
 save('unit-hardening-after.private.json',json.dumps({u:show(u,CONFIG) for u in UNITS},sort_keys=True).encode())
 save('unit-config.complete.private',b'sameTenStoppedGenerationsRetained=true\noldDropinsPreserved=true\nnewRolesOnly=true\nnoResume=true\nstarts0=true\n');configured=True
try:
 require(os.geteuid()==0 and sys.argv[1:] in [['verify'],['activate']]);owner=holder();before=stopped()
 bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
 phase='REF_ACQUIRE'
 for unit in UNITS:manager.RefUnit(unit);refs.append(unit)
 require(stopped()==before);config_before={u:show(u,CONFIG) for u in UNITS}
 require(config_before['schubert-nk-bootstrap-admin.service']['DropInPaths']=='')
 for u in ['schubert-nk-inbox-inspector.service','schubert-nk-morning-controller.service']:
  require(config_before[u]['DropInPaths']=='/etc/systemd/system/'+u+'.d/pg390-native-coverage.conf')
 proof=TOOLS/('refs-'+sys.argv[1]+'-before.private.json')
 fd=os.open(proof,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as f:f.write(json.dumps({'owner':owner,'stopped':before,'configuration':config_before},sort_keys=True).encode());f.flush();os.fsync(f.fileno())
 for u in ['schubert-nk-inbox-inspector.service','schubert-nk-bootstrap-admin.service']:
  require(material(pathlib.Path('/etc/systemd/system')/u)[0]==material(OLD/'systemd'/u)[0])
 for u in ['schubert-nk-inbox-inspector.service','schubert-nk-morning-controller.service']:dropin_preview(u)
 top=pathlib.Path('/run/schubert-nk/pt-coverage');s=top.lstat();require(stat.S_ISDIR(s.st_mode) and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o755)
 for role in ['ordinary-inspector196','ordinary-bootstrap196']:require(not (top/role).exists() and not (top/role).is_symlink())
 require(not SAVE.exists())
 sync(TOOLS);print('REF_READY',flush=True)
 for raw in sys.stdin.buffer:
  require(holder()==owner)
  if raw==b'check\n':require(stopped()==before);print('REF_CHECKED',flush=True)
  elif raw==b'configure\n':phase='CONFIGURE';configure();print('REF_CONFIGURED',flush=True)
  elif raw==b'release\n':
   phase='REF_RELEASE';require(stopped()==before)
   for unit in reversed(refs):manager.UnrefUnit(unit)
   bus.close();print('REF_RELEASED',flush=True);sys.exit(0)
  else:raise ValueError('fixed reference protocol refused')
 raise ValueError('reference owner channel ended early')
except Exception:
 print('REF_FAILED',flush=True);print('PG477_REFERENCE_UNKNOWN phase='+phase+' senderRetained=true',file=sys.stderr,flush=True)
 while True:time.sleep(1)
