"""SSC208/BUG811 fixed current-boot pre-namespace owner only; not normal close."""
import hashlib,importlib.util,json,os,pathlib,signal,time

PID=3262;TICKS=310103;CHILD=3291;CHILD_TICKS=310212
BOOT='cc9ed874-7f4f-450e-a188-8de1e42c8441'
ARGV='1416c7acc909846118faa7947e3cf1c5e1368bd945b2eba5d233a1c539a40287'
CHILD_ARGV='85c10c135c139c7757c0bb46840da1336d082297ac54678fe11f25a6d87248b5'
TOOLS=pathlib.Path('/var/lib/pgpt-s1-preservation/pg503-resume-tools-v1')
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg503-runtime-owned-handoff-v1')
PINS={'Pg503ResumePreparation.class':'5d11a1203cd05890350b9f20fcda59a6f69c3e2e56c49b856af5af4be500402f',
 'Pg503ResumePreparation$References.class':'86f26743deb3c28eb0391a50c2061c7b1c3fd524d3dd1445195c0af71e71bfc2',
 'Pg503ResumePreparationTest.class':'ebef84517820c91b7533d45d55c225db55ae009eaa2089ea1fe648782abf567f',
 'pg503_resume_refs.py':'b6d8b54b2d02721be93fdaf01fe5314a1fe6f7364458c435729466b956220c05'}

def require(value):
 if not value:raise ValueError('fixed cold handoff refused')
def identity(value,pid,ticks,argv,parent=None):
 return (isinstance(value,dict) and set(value)=={'pid','ticks','argv','uid','parent','children'}
  and type(value['pid']) is int and value['pid']==pid and type(value['ticks']) is int and value['ticks']==ticks
  and value['argv']==argv and value['uid']==['0']*4 and (parent is None or value['parent']==parent)
  and isinstance(value['children'],set))
def process(pid):
 p=pathlib.Path('/proc')/str(pid);s=(p/'stat').read_text().rpartition(')')[2].split()
 return {'pid':pid,'ticks':int(s[19]),'parent':int(s[1]),'argv':hashlib.sha256((p/'cmdline').read_bytes()).hexdigest(),
  'uid':(p/'status').read_text().split('Uid:')[1].splitlines()[0].split(),
  'children':{int(c) for t in (p/'task').iterdir() for c in (t/'children').read_text().split()}}
def owner(child_alive):
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
 parent=process(PID);require(identity(parent,PID,TICKS,ARGV) and parent['children']==({CHILD} if child_alive else set()))
 if child_alive:
  child=process(CHILD);require(identity(child,CHILD,CHILD_TICKS,CHILD_ARGV,PID) and not child['children'])
 locks=pathlib.Path('/proc/locks').read_text().splitlines()
 fdpaths={str(fd.readlink()) for fd in (pathlib.Path('/proc')/str(PID)/'fd').iterdir()}
 for name in ['maintenance.lock','startup-admission.lock']:
  p=pathlib.Path('/run/schubert-nk')/name;m=h.metadata(p)
  require(m==lock_baseline[name] and str(p) in fdpaths)
  matches=[]
  for line in locks:
   f=line.split()
   if len(f)>=8 and f[1:5]==['FLOCK','ADVISORY','WRITE',str(PID)]:
    d=f[5].split(':')
    if (int(d[0],16),int(d[1],16),int(d[2]))==(os.major(m[0]),os.minor(m[0]),m[1]):matches.append(line)
  require(len(matches)==1)
def raw():
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
 units={}
 for name,expected in before['units'].items():
  def show():
   pairs=[line.split('=',1) for line in h.command(['/usr/bin/systemctl','show',name,'--property='+','.join(sorted(h.FIELDS))],1048576).decode('ascii').splitlines()]
   v=dict(pairs);require(len(v)==len(pairs) and h.cold(v) and v==expected);return v
  first=show();c=pathlib.Path('/sys/fs/cgroup/system.slice')/name
  if c.exists():
   for p in [c,*[v for v in c.rglob('*') if v.is_dir()]]:
    require(not (p/'cgroup.procs').read_text().strip() and 'populated 0\n' in (p/'cgroup.events').read_text())
  require(first==show());units[name]=first
  config=dict(line.split('=',1) for line in h.command(['/usr/bin/systemctl','show',name,'--property='+','.join(sorted(before['configuration'][name]))],1048576).decode('ascii').splitlines());require(config==before['configuration'][name])
 sql="begin isolation level repeatable read read only;set local timezone='UTC';"
 for table in before['rows']:
  require(h.re.fullmatch(r'[a-z_]+\.[a-z_]+',table) is not None)
  sql+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from (select to_jsonb(t) j from "+table+" t) q;"
 sql+='commit;';rows={}
 for line in h.command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql]).splitlines():
  value=json.loads(line);require(value['table'] not in rows);rows[value['table']]=value['rows']
 require(rows==before['rows']);trees={}
 for name,expected in before['trees'].items():
  value=h.tree(pathlib.Path(name));require(value==expected and value==h.tree(pathlib.Path(name)));trees[name]=value
 require(str(pathlib.Path('/opt/schubert-nk/current').readlink())==baseline['current'])
 for path in ['/run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf']:
  require(not pathlib.Path(path).exists())
 peers="select count(*) from pg_stat_activity where datname='schubert_nk' and usename in ('schubert_batch','schubert_app','schubert_web_session','schubert_backup','schubert_inbox_inspector');select count(*) from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and granted;"
 require(h.command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-d','schubert_nk','-c',peers],4096).splitlines()==[b'0',b'0'])
 runtime=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d')
 require(h.metadata(runtime)==runtime_metadata and not list(runtime.iterdir()) and 'system.posix_acl_access' not in os.listxattr(runtime) and 'system.posix_acl_default' not in os.listxattr(runtime))
 require('ro' in h.command(['/usr/bin/findmnt','--target','/opt/schubert-nk/releases/0.1.0-PG495','--output','OPTIONS','--noheadings'],4096).decode().strip().split(','))
 return {'units':units,'rows':rows,'trees':trees}
def save(name,value):
 with (SAVE/name).open('x') as f:
  os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
def wait_gone(pid,seconds):
 end=time.monotonic()+seconds
 while pathlib.Path('/proc',str(pid)).exists() and time.monotonic()<end:time.sleep(.05)
 require(not pathlib.Path('/proc',str(pid)).exists())
def execute():
 global h,before,baseline,lock_baseline,runtime_metadata
 require(os.geteuid()==0 and not SAVE.exists());os.umask(0o077)
 for name,digest in PINS.items():
  p=TOOLS/name;s=p.lstat();require(s.st_uid==s.st_gid==0 and s.st_mode==0o100400 and s.st_nlink==1)
  require(hashlib.sha256(p.read_bytes()).hexdigest()==digest)
 helper=pathlib.Path('/var/lib/pgpt-s1-preservation/pg502-cold-tools-v1/pg502_cold_refs.py');require(hashlib.sha256(helper.read_bytes()).hexdigest()=='06cc9b07c617417493358b3cc485f39984238f46cef4cc3f81dc116fbd8b7f3f')
 spec=importlib.util.spec_from_file_location('fixed_pg502',helper);h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
 baseline_raw=h.BASE.read_bytes();require(hashlib.sha256(baseline_raw).hexdigest()==h.BASE_HASH);baseline=json.loads(baseline_raw)
 before=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg503-resume-preparation-v1/refs-before.private.json').read_bytes())
 cold_raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg502-cold-preparation-v1/refs-after.private.json').read_bytes();require(hashlib.sha256(cold_raw).hexdigest()=='07d74f8b4a5dbf99b801ff2f272e57d1e693dfba61d323800dc180fc6b6d2f49')
 lock_baseline=json.loads(cold_raw)['owner'][2]
 own=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg503-failure-owner-v1/owner.private.json').read_bytes())
 require(own['pid']==PID and own['ticks']==TICKS and own['argvSHA']==ARGV and own['children']==[CHILD]
  and own['child']['pid']==CHILD and own['child']['ticks']==CHILD_TICKS and own['child']['argvSHA']==CHILD_ARGV)
 runtime_metadata=own['runtimeMetadata'];require(runtime_metadata[2:5]==[0,0,0o40700] and own['runtimeNames']==[])
 require(len(before['units'])==10 and len(before['rows'])==24 and len(before['rows']['schubert.batch_runs'])==442
  and before['rows']==baseline['rows'] and all(before['trees'][k]==v for k,v in baseline['trees'].items() if not k.startswith('/run/')))
 owner(True);a=raw();owner(True);require(a==raw());owner(True)
 parent_fd=os.pidfd_open(PID);child_fd=os.pidfd_open(CHILD);owner(True)
 SAVE.mkdir(mode=0o700);save('before.private.json',a)
 save('term-reservation.private.json',{'boot':BOOT,'pid':PID,'ticks':TICKS,'argv':ARGV,'child':CHILD,'childTicks':CHILD_TICKS,'childArgv':CHILD_ARGV,'oldCloseUNKNOWN':True,'repeatForbidden':True})
 owner(True);signal.pidfd_send_signal(child_fd,signal.SIGTERM);os.close(child_fd);wait_gone(CHILD,5)
 owner(False);signal.pidfd_send_signal(parent_fd,signal.SIGTERM);os.close(parent_fd);wait_gone(PID,15)
 require(a==raw() and a==raw())
 for name in ['maintenance.lock','startup-admission.lock']:
  m=h.metadata(pathlib.Path('/run/schubert-nk')/name)
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)>=8 and f[1]=='FLOCK':
    d=f[5].split(':');require((int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(m[0]),os.minor(m[0]),m[1]))
 save('complete.private.json',{'ownedChildThenParentTERM':True,'rawUnchangedTwice':True,'businessPeers0':True,'advisory0':True,'locks0':True,'oldCloseUNKNOWN':True,'businessActions0':True})
 print('PG503_RUNTIME_HANDOFF ownedTERM=true fullRawUnchangedTwice=true peersLocks0=true oldCloseUNKNOWN=true')
if __name__=='__main__':execute()
