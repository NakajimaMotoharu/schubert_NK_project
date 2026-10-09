"""Fixed pending9de2 runtime preparation from fresh802, no old operation replay."""
import ast
from pathlib import Path
R=Path(__file__).resolve().parent
SOURCE='102cdf1d365ab321f74b523237590eee764ae858'
DIGEST='c48af3ada5e2f00b1704f65fdb4625d6220bed29b6cecbbd23d7354cf708880d'
RUN='9de2d03c-28c7-4647-97d9-c66ace06048c'

def java():
 raw=(R/'Pg521RuntimeResume.java').read_text().replace('Pg521RuntimeResume','Pg805RuntimeResume').replace('pg521','pg805').replace('PG521','PG805').replace('pg805-resume-tools-v2','pg805-resume-tools-v1').replace('pg805-runtime-resume-v2','pg805-runtime-resume-v1').replace('PG495','PG796').replace('a2e98ce9e96c42425921e3686e8ae7a94bff9e6c',SOURCE).replace('f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44',DIGEST)
 raw=raw.replace('static String phase="PREFLIGHT";',r'''static String phase="PREFLIGHT";
  static Pg797OwnedDatabase lease;
  static long lastPulse,maxGap;
  static void pulse()throws Exception{
    if(lease==null)return;long now=System.nanoTime();if(lastPulse!=0)maxGap=Math.max(maxGap,now-lastPulse);
    if(lastPulse!=0&&now-lastPulse>=TimeUnit.SECONDS.toNanos(30))throw new java.sql.SQLException("owned database observation interval exceeded");
    lease.verify();lastPulse=now;
  }
''')
 raw=raw.replace('for(;;)try{Thread.sleep(1000);}catch(InterruptedException notification){Thread.interrupted();}',r'''boolean lost=false;
    for(;;){if(lease!=null&&!lost)try{pulse();}catch(Exception|Error failure2){System.err.println("PG805_DB_NOT_CONFIRMED ownershipNotInferred=true");lost=true;}try{Thread.sleep(1000);}catch(InterruptedException notification){Thread.interrupted();}}
''')
 raw=raw.replace('while(System.nanoTime()<deadline){while(input.available()>0)', 'while(System.nanoTime()<deadline){if(!phase.equals("REF_CLOSE"))pulse();while(input.available()>0)')
 raw=raw.replace('phase="REFERENCE_SCOPE";var refs=new References(pid,db);','lease=new Pg797OwnedDatabase(db,new Pg797OwnedDatabase.Expected(pid,"schubert_batch","PG805-runtime-resume","schubert_nk",true,true));pulse();phase="REFERENCE_SCOPE";var refs=new References(pid,db);')
 raw=raw.replace('phase="DB_CLOSE";db.rollback();db.close();','pulse();phase="DB_CLOSE";db.rollback();db.close();lease.confirmClosed();')
 return raw

def fixed_dropin_source():
 raw=(R/'pg492_resume_refs.py').read_text();node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='fixed_dropin')
 return ast.unparse(ast.Module(body=[node],type_ignores=[]))

HELPER=r'''
import pathlib,sys,os,json,hashlib,stat,time,ast,re
import pg805_snapshot as h
from pg777_reference_capability import CaptureReferences
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg805-runtime-resume-v1')
RUNTIME=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d')
NAME='pg805-once-resume.conf';MORNING='schubert-nk-morning-controller.service'
NATIVE=pathlib.Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/pg477-native-coverage.conf')
RUN_ID='9de2d03c-28c7-4647-97d9-c66ace06048c';phase='initial'
def require(v):
 if not v:raise ValueError('fixed805 resume refused')
def persist(name,data):
 with(SAVE/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(data);f.flush();os.fsync(f.fileno())
 fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
def unit_files(configuration):
 value={}
 for unit,config in configuration.items():
  fragment=h.command(['/usr/bin/systemctl','show',unit,'--property=FragmentPath','--value']).decode().strip()
  require(fragment.startswith(('/etc/systemd/system/','/usr/lib/systemd/system/','/lib/systemd/system/')))
  for name in[fragment,*config['DropInPaths'].split()]:
   if name==str(RUNTIME/NAME):continue
   p=pathlib.Path(name);m=h.metadata(p);require(stat.S_ISREG(m[4])and m[2]==0 and m[5]==1)
   value[name]={'metadata':m,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};require(m==h.metadata(p))
 return value
def snapshot(changed,db_required):
 owner=h.holder(db_required);h.parent();baseline=h.baseline();units={u:h.show(u)for u in h.ORDER+h.EXTRA}
 for u,v in units.items():require(v['MainPID']==v['ControlPID']=='0'and not v['Job']);h.kernel_empty(u)
 rows=h.rows();trees={root:h.tree(pathlib.Path(root))for root in baseline['trees']};configuration={}
 for u in units:
  value=h.complete_configuration(h.command(['/usr/bin/systemctl','show',u,'--property='+','.join(sorted(h.FIELDS_CONFIGURATION))]).decode(),u);expected=baseline['configuration'][u]
  before=exec_record(expected['ExecStart']);after=exec_record(value['ExecStart']);require(before is not None and after is not None)
  if changed and u==MORNING:
   require(after[:3]==(before[0],before[1]+' --resume '+RUN_ID,before[2])and value['DropInPaths']==expected['DropInPaths']+' '+str(RUNTIME/NAME))
   require(all(value[k]==expected[k]for k in value if k not in('ExecStart','DropInPaths')))
  else:
   require(after[:3]==before[:3]and all(value[k]==expected[k]for k in value if k!='ExecStart'))
  configuration[u]=value
 require(rows==baseline['rows']and trees==baseline['trees']and h.holder(db_required)==owner)
 require(unit_files(configuration)==baseline['unitFiles'])
 require(h.tree(pathlib.Path('/run/schubert-nk/pt-coverage'))==baseline['coverageBefore'])
 return {'units':units,'configuration':configuration,'rows':rows,'trees':trees,'unitFiles':unit_files(configuration),'current':str(pathlib.Path('/opt/schubert-nk/current').readlink()),'coverageBefore':baseline['coverageBefore']}
def prepare(target,dropin,expected):
 require(not os.path.lexists(target)and not list(RUNTIME.iterdir()))
 fd=os.open(RUNTIME,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  s=os.fstat(fd);require([s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]==expected)
  file=os.open(NAME,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=fd)
  try:
   os.fchmod(file,0o644);written=0
   while written<len(dropin):
    count=os.write(file,dropin[written:]);require(count>0);written+=count
   os.fsync(file)
  finally:os.close(file)
  os.fsync(fd)
 finally:os.close(fd)
 require(target.read_bytes()==dropin);h.command(['/usr/bin/systemctl','daemon-reload'])
def main():
 global phase,exec_record
 os.umask(0o077);require(os.geteuid()==0 and sys.argv[1]=='prepare'and len(sys.argv)==3 and sys.argv[2].isdigit());h.load_definitions()
 policy=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/pg477_unit_references.py').read_bytes();require(hashlib.sha256(policy).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
 node=next(n for n in ast.parse(policy).body if isinstance(n,ast.FunctionDef)and n.name=='exec_record');env={'re':re};exec(compile(ast.Module(body=[node],type_ignores=[]),'<fixed exec declaration>', 'exec'),env);exec_record=env['exec_record']
 directory=h.metadata(RUNTIME);require(directory[2:6]==[0,0,stat.S_IFDIR|0o755,2]and 'system.posix_acl_access'not in os.listxattr(RUNTIME)and not list(RUNTIME.iterdir()))
 dropin=fixed_dropin(pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG796/systemd/schubert-nk-morning-controller.service').read_bytes(),NATIVE.read_bytes());target=RUNTIME/NAME
 with CaptureReferences():
  try:
   before=snapshot(False,True);require(before==snapshot(False,True));persist('before.private.json',json.dumps(before,sort_keys=True).encode());persist('new-runtime.private',dropin)
   print('REF_READY',flush=True);changed=False
   for line in sys.stdin.buffer:
    phase=line.rstrip(b'\n').decode('ascii');require(phase in('before','prepare','release'))
    if phase=='before':require(not changed and before==snapshot(False,True))
    elif phase=='prepare':
     require(not changed and before==snapshot(False,True));prepare(target,dropin,directory);changed=True;snapshot(True,True)
    else:
     require(changed and target.read_bytes()==dropin and {p.name for p in RUNTIME.iterdir()}=={NAME});after=snapshot(True,False)
     q="select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;"
     require(h.command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]).splitlines()==[b'0',b'0'])
     persist('after.private.json',json.dumps(after,sort_keys=True).encode());break
    print('REF_CHECKED',flush=True)
   else:raise ValueError('owner channel ended early')
  except BaseException as failure:
   print('REF_FAILED',flush=True);print('PG805_UNKNOWN phase='+phase+' type='+type(failure).__name__,file=sys.stderr,flush=True)
   import traceback
   for frame in traceback.extract_tb(failure.__traceback__):
    if frame.filename==__file__:print('PG805_FRAME method='+frame.name+' line='+str(frame.lineno),file=sys.stderr,flush=True)
   while True:time.sleep(1)
 print('REF_RELEASED',flush=True)
if __name__=='__main__':main()
'''

def helper():return fixed_dropin_source()+'\n'+HELPER

def snapshot_library():
 from pg804_current_sources import helper as current
 raw=current();lines=raw.splitlines(keepends=True)
 for node in reversed(ast.parse(raw).body):
  if isinstance(node,ast.FunctionDef)and node.name=='main'or isinstance(node,ast.If)and '__name__'in ast.unparse(node.test):del lines[node.lineno-1:node.end_lineno]
 raw=''.join(lines).replace('pg803-published-handoff-v2/after.private.json','pg802-current-source-post-v1/after.private.json').replace('d82a4626f8b9a0cb00130087413d1dd227dd04ced4f9add680668f99b27c6a92','fc1fb69cbc9e6db2d5c246547a0181f1a1b41c7b89c1ac7198edb69f638e07c5')
 raw=raw.replace('def holder():','def holder(db_required=True):').replace("argv[-3]==b'Pg804CurrentReadback' and argv[-2] in (b'verify',b'recover') and argv[-1]==b''","argv[-3:]==[b'Pg805RuntimeResume',b'prepare',b'']").replace('PG804-fixed-recovery','PG805-runtime-resume')
 raw=raw.replace("require(command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql]).strip()==b'1')","if db_required:require(command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql]).strip()==b'1')")
 return raw
