"""SSC206 continuous current-boot M/A/DB/10Ref cold witness; private raw values only."""
import hashlib,json,os,pathlib,re,stat,subprocess,sys,time
import dbus

BOOT='cc9ed874-7f4f-450e-a188-8de1e42c8441'
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg501-cold-preparation-v1')
BASE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg498-pending-codeonly/refs-after.private.json')
BASE_HASH='1ef541deba93311f167df38135930dd1a935fddb7cc54d9cf2b02bfb1b77fdc3'
STARTUP=pathlib.Path('/run/schubert-nk/startup')
FIELDS=set('Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,InvocationID,Type,Restart,RemainAfterExit,Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,KillMode,SendSIGKILL'.split(','))
os.umask(0o077)

def require(value):
 if not value:raise ValueError('fixed cold witness refused')
def bounded(code,size,limit):
 return type(code) is int and code==0 and type(size) is int and type(limit) is int and 0<=size<=limit
def command(args,limit=32*1024*1024):
 p=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=30)
 require(bounded(p.returncode,len(p.stdout),limit));return p.stdout
def metadata(path):
 s=path.lstat();require(stat.S_ISDIR(s.st_mode) or stat.S_ISREG(s.st_mode))
 return [s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
def tree(root):
 values={}
 for p in [root,*sorted(root.rglob('*'))]:
  m=metadata(p);digest=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
  require(m==metadata(p));values[str(p)]={'metadata':m,'sha256':digest}
 return values
def cold(values):
 return (isinstance(values,dict) and set(values)==FIELDS and all(isinstance(v,str) for v in values.values()) and values['LoadState']=='loaded'
  and values['ActiveState']=='inactive' and values['SubState']=='dead' and values['Result']=='success'
  and values['MainPID']==values['ControlPID']=='0' and values['Job']==values['InvocationID']==''
  and values['KillMode']=='control-group' and values['SendSIGKILL']=='no'
  and all(values[k]=='0' for k in ['ExecMainCode','ExecMainStatus','ExecMainStartTimestampMonotonic','ExecMainExitTimestampMonotonic']))
def epoch_valid(raw,activation):
 if not isinstance(raw,bytes) or not isinstance(activation,bytes):return False
 try:
  active=activation.decode('ascii').splitlines();lines=raw.decode('ascii').splitlines()
  if len(active)!=4 or active[0]!='NKACT1' or len(lines)!=8 or lines[0]!='NKEPOCH1':return False
  fields={}
  for line in lines[1:]:
   k,v=line.split('=',1)
   if k in fields:return False
   fields[k]=v
  return (set(fields)==set('state boot_id epoch_id run_id cutoff_utc activation_id permit_sha256'.split())
    and fields['state']=='INVALID' and fields['boot_id']==BOOT
    and re.fullmatch(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',fields['epoch_id']) is not None
    and fields['epoch_id']!='00000000-0000-0000-0000-000000000000'
    and fields['run_id']==active[1] and fields['cutoff_utc']==active[2] and fields['activation_id']==active[3]
    and fields['permit_sha256']=='-' and raw.endswith(b'\n') and b'\r' not in raw)
 except (UnicodeDecodeError,ValueError):return False
def holder():
 pid=os.getppid();p=pathlib.Path('/proc')/str(pid);args=(p/'cmdline').read_bytes().split(b'\0')
 require(args[0]==b'/opt/jdk-25.0.4/bin/java' and args[-3:]==[b'Pg501ColdPreparation',b'prepare',b''])
 require((p/'status').read_text().split('Uid:')[1].splitlines()[0].split()==['0','0','0','0'])
 ticks=int((p/'stat').read_text().rpartition(')')[2].split()[19]);fdpaths=[]
 for fd in (p/'fd').iterdir():
  try:fdpaths.append(str(fd.readlink()))
  except FileNotFoundError:continue
 identities={}
 for name in ['maintenance.lock','startup-admission.lock']:
  path=pathlib.Path('/run/schubert-nk')/name;m=metadata(path)
  require(m[2:7]==[0,0,stat.S_IFREG|0o600,1,0] and str(path) in fdpaths)
  hits=[]
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   parts=line.split()
   if len(parts)>=8 and parts[1:5]==['FLOCK','ADVISORY','WRITE',str(pid)]:
    dev=parts[5].split(':')
    if len(dev)==3 and (int(dev[0],16),int(dev[1],16),int(dev[2]))==(os.major(m[0]),os.minor(m[0]),m[1]):hits.append(line)
  require(len(hits)==1);identities[name]=m
 return pid,ticks,identities
def snapshot(prepared=False,released=False):
 require(holder()==owner and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
 units={}
 for name in baseline['units']:
  def show():
   value={}
   for line in command(['/usr/bin/systemctl','show',name,'--property='+','.join(sorted(FIELDS))],1048576).decode('ascii').splitlines():
    key,text=line.split('=',1);require(key not in value);value[key]=text
   require(cold(value) and value['Id']==name)
   require(all(value[k]==baseline['units'][name][k] for k in ['Type','Restart','RemainAfterExit','KillMode','SendSIGKILL']))
   return value
  first=show();cgroup=pathlib.Path('/sys/fs/cgroup/system.slice')/name
  if cgroup.exists():
   for p in [cgroup,*[v for v in cgroup.rglob('*') if v.is_dir()]]:
    require(not (p/'cgroup.procs').read_text().strip() and 'populated 0\n' in (p/'cgroup.events').read_text())
  require(first==show());units[name]=first
 peers="select count(*) from pg_stat_activity a where a.pid="+str(backend)+" and a.usename='schubert_batch' and a.application_name='PG501-cold-preparation' and a.datname='schubert_nk' and exists(select 1 from pg_locks l where l.pid=a.pid and l.locktype='advisory' and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.mode='ExclusiveLock' and l.granted);select count(*) from pg_stat_activity where datname='schubert_nk' and usename in ('schubert_batch','schubert_app','schubert_web_session','schubert_backup','schubert_inbox_inspector') and pid<>"+str(backend)+";"
 require(command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-d','schubert_nk','-c',peers],4096).splitlines()==([b'0',b'0'] if released else [b'1',b'0']))
 sql="begin isolation level repeatable read read only;set local timezone='UTC';"
 for table in baseline['rows']:
  require(re.fullmatch(r'[a-z_]+\.[a-z_]+',table) is not None)
  sql+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from (select to_jsonb(t) j from "+table+" t) q;"
 sql+='commit;';rows={}
 for line in command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql]).splitlines():
  r=json.loads(line);require(r['table'] not in rows);rows[r['table']]=r['rows']
 require(rows==baseline['rows'])
 trees={}
 for name,expected in baseline['trees'].items():
  if name.startswith('/run/'):continue
  actual=tree(pathlib.Path(name));require(actual==expected and actual==tree(pathlib.Path(name)));trees[name]=actual
 require(str(pathlib.Path('/opt/schubert-nk/current').readlink())==baseline['current'])
 require(not pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf').exists())
 if prepared:
  require(set(p.name for p in STARTUP.iterdir())=={'epoch.current'})
  require(epoch_valid((STARTUP/'epoch.current').read_bytes(),pathlib.Path('/var/lib/schubert-nk/maintenance/active').read_bytes()))
  for name in ['backup-request','cleanup-request','expiry-request']:
   p=pathlib.Path('/run/schubert-nk')/name;m=metadata(p)
   require(m[2:5]==[0,0,stat.S_IFDIR|0o700] and not list(p.iterdir()))
 else:require(not STARTUP.exists() and not pathlib.Path('/run/schubert-nk/pt-coverage').exists())
 return {'units':units,'rows':rows,'trees':trees,'owner':owner,'prepared':prepared}
def execute():
 global baseline,owner,backend
 require(os.geteuid()==0 and len(sys.argv)==2 and sys.argv[1].isdigit())
 require(pathlib.Path('/var/lib/cloud/data/instance-id').read_text().strip()=='pgpt-r2-20260927-01')
 raw=BASE.read_bytes();require(hashlib.sha256(raw).hexdigest()==BASE_HASH);baseline=json.loads(raw)
 require(len(baseline['units'])==10 and len(baseline['rows'])==24 and len(baseline['rows']['schubert.batch_runs'])==442)
 backend=int(sys.argv[1]);owner=holder();bus=dbus.SystemBus(private=True)
 manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
 for name in baseline['units']:manager.RefUnit(name)
 before=snapshot();require(before==snapshot())
 with (SAVE/'refs-before.private.json').open('x') as f:os.fchmod(f.fileno(),0o600);json.dump(before,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 print('REF_READY',flush=True);prepared=False
 for line in sys.stdin.buffer:
  point=line.rstrip(b'\n').decode('ascii');require(point in ['before','frozen','prepared','release'])
  if point=='prepared':prepared=True
  value=snapshot(prepared,point=='release')
  if point in ['frozen','prepared','release']:
   options=command(['/usr/bin/findmnt','--target','/opt/schubert-nk/releases/0.1.0-PG495','--output','OPTIONS','--noheadings'],4096).decode().strip().split(',');require('ro' in options)
  if point=='release':
   require(prepared)
   with (SAVE/'refs-after.private.json').open('x') as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
   for name in reversed(list(baseline['units'])):manager.UnrefUnit(name)
   bus.close();print('REF_RELEASED',flush=True);return
  print('REF_CHECKED',flush=True)
 raise ValueError('owner channel ended')
if __name__=='__main__':
 try:execute()
 except Exception as failure:
  import traceback
  print('REF_FAILED',flush=True);print('PG501_COLD_REF_UNKNOWN type='+type(failure).__name__,file=sys.stderr,flush=True)
  for frame in traceback.extract_tb(failure.__traceback__):
   if frame.filename==__file__:print('PG501_COLD_REF_FRAME method='+frame.name+' line='+str(frame.lineno),file=sys.stderr,flush=True)
  while True:time.sleep(1)
