"""Current949 normal recovery completed: existing805 runtime only, typed unlink/reload.
No start/stop/revoke/DB mutation; SSC198/235/238 fixed current bindings.
"""
import ast
from pathlib import Path
import pg813_sources as recovery
R=Path(__file__).resolve().parent
SOURCE=recovery.SOURCE;DIGEST=recovery.DIGEST
SNAPSHOT='d6f9deea19d305cf445847afed7194ef427e0c6dd4bb94a8104605bd1fb37a26'
def java():
 raw=(R/'Pg520RuntimeRetirement.java').read_text().replace('Pg520RuntimeRetirement','Pg815RuntimeRetirement').replace('pg520','pg815').replace('PG520','PG815').replace('pg492-once-resume.conf','pg805-once-resume.conf').replace('PG495','PG796').replace('a2e98ce9e96c42425921e3686e8ae7a94bff9e6c',SOURCE).replace('f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44',DIGEST)
 old='Pg464CodeOnlyDeployment.configure("PG796","'+SOURCE+'",Path.of("/opt/schubert-nk/releases/0.1.0-PG796"));'
 assert raw.count(old)==1;raw=raw.replace(old,'Pg387TrustedDeployment.LABEL="PG796";Pg387TrustedDeployment.STEM="pg796";Pg387TrustedDeployment.SOURCE="'+SOURCE+'";Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG796");')
 raw=raw.replace('require(args.length==1','require(args!=null && args.length==1')
 raw=raw.replace('static String phase="PREFLIGHT";',r'''static String phase="PREFLIGHT";
  static Pg797OwnedDatabase lease;
  static void pulse()throws Exception{if(lease!=null)lease.verify();}
''')
 raw=raw.replace('while(System.nanoTime()<deadline){while(input.available()>0)','while(System.nanoTime()<deadline){if(!phase.equals("REF_CLOSE"))pulse();while(input.available()>0)')
 raw=raw.replace('phase="REFERENCE_SCOPE";var refs=', 'lease=new Pg797OwnedDatabase(db,new Pg797OwnedDatabase.Expected(pid,"schubert_batch","PG815-runtime-retirement","schubert_nk",true,true));pulse();phase="REFERENCE_SCOPE";var refs=')
 raw=raw.replace('db.rollback();db.close();phase="REF_CLOSE";', 'pulse();db.rollback();db.close();lease.confirmClosed();phase="REF_CLOSE";')
 raw=raw.replace('for(;;)try{Thread.sleep(1000);}catch(InterruptedException notification){Thread.interrupted();}',r'''boolean lost=false;
    for(;;){if(lease!=null&&!lost)try{lease.verify();}catch(Exception|Error secondary){lost=true;System.err.println("PG815_DB_NOT_CONFIRMED ownershipNotInferred=true");}try{Thread.sleep(1000);}catch(InterruptedException notification){Thread.interrupted();}}
''')
 return raw

def java_test():return r'''public final class Pg815RuntimeRetirementTest {
  public static void main(String[] ignored)throws Exception{
    int count=0;
    for(String[] argv:new String[][]{null,{}, {"prepare"},{"retire","foreign"},{"unknown"}}){
      try{Pg815RuntimeRetirement.main(argv);throw new AssertionError("bad arguments admitted");}
      catch(IllegalStateException expected){count++;}
    }
    if(count!=5)throw new AssertionError("five independent argv vectors required");
    System.out.println("PG815_CLI actual0=true badArgv5=true authority0=true");
  }
}
'''
def snapshot_library():
 raw=recovery.helper();tree=ast.parse(raw);lines=raw.splitlines(keepends=True)
 for n in reversed(tree.body):
  if isinstance(n,ast.FunctionDef)and n.name in('baseline','main','actor','stop_one','verify_live','snapshot','configuration')or isinstance(n,ast.If)and '__name__'in ast.unparse(n.test):del lines[n.lineno-1:n.end_lineno]
 raw=''.join(lines).replace("b'Pg813FailedRecovery'","b'Pg815RuntimeRetirement'").replace("argv[-2] in (b'verify',b'recover')","argv[-2]==b'retire'").replace('PG813-fixed-recovery','PG815-runtime-retirement')
 raw=raw.replace('def holder():','def holder(db_required=True):').replace(" require(command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql]).strip()==b'1')"," if db_required:require(command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql]).strip()==b'1')")
 return raw+r'''
def baseline():
 path=pathlib.Path('/var/lib/pgpt-s1-preservation/pg814-recovered949-post-v1/after.private.json');raw=path.read_bytes()
 require(hashlib.sha256(raw).hexdigest()=='d6f9deea19d305cf445847afed7194ef427e0c6dd4bb94a8104605bd1fb37a26');return json.loads(raw)
'''

HELPER=r'''
import ast,hashlib,json,os,pathlib,re,stat,sys,time
import pg815_snapshot as h
from pg777_reference_capability import CaptureReferences
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg815-runtime-retirement-v1')
RUNTIME=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d')
NAME='pg805-once-resume.conf';MORNING='schubert-nk-morning-controller.service'
NATIVE=pathlib.Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/pg477-native-coverage.conf')
RUN_ID='9de2d03c-28c7-4647-97d9-c66ace06048c'
def require(v):
 if not v:raise ValueError('fixed815 retirement refused')
def persist(name,raw):
 with(SAVE/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(raw);f.flush();os.fsync(f.fileno())
 fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
def snapshot(changed,db_required):
 owner=h.holder(db_required);h.parent();baseline=h.baseline();units={u:h.show(u)for u in h.ORDER+h.EXTRA};configuration={};files={}
 for u,v in units.items():
  require(v['MainPID']==v['ControlPID']=='0'and not v['Job']);h.kernel_empty(u)
  value=h.complete_configuration(h.command(['/usr/bin/systemctl','show',u,'--property='+','.join(sorted(h.FIELDS_CONFIGURATION))]).decode(),u);expected=baseline['configuration'][u]
  old=exec_record(expected['ExecStart']);new=exec_record(value['ExecStart']);require(old is not None and new is not None)
  if changed and u==MORNING:
   require(new[:3]==(old[0],old[1].removesuffix(' --resume '+RUN_ID),old[2])and new[1]!=old[1])
   require(value['DropInPaths']==expected['DropInPaths'].removesuffix(' '+str(RUNTIME/NAME)))
   require(all(value[k]==expected[k]for k in value if k not in('ExecStart','DropInPaths')))
  else:require(new[:3]==old[:3]and all(value[k]==expected[k]for k in value if k!='ExecStart'))
  configuration[u]=value
  fragment=h.command(['/usr/bin/systemctl','show',u,'--property=FragmentPath','--value']).decode().strip();require(fragment.startswith(('/etc/systemd/system/','/usr/lib/systemd/system/','/lib/systemd/system/')))
  for name in[fragment,*value['DropInPaths'].split()]:
   if name==str(RUNTIME/NAME):continue
   p=pathlib.Path(name);m=h.metadata(p);require(stat.S_ISREG(m[4])and m[2]==0 and m[5]==1)
   files[name]={'metadata':m,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};require(m==h.metadata(p))
 require(files=={name:value for name,value in baseline['unitFiles'].items()if name!=str(RUNTIME/NAME)})
 rows=h.rows();trees={name:h.tree(pathlib.Path(name))for name in baseline['trees']}
 require(rows==baseline['rows']and trees==baseline['trees']and h.holder(db_required)==owner)
 require(h.tree(pathlib.Path('/run/schubert-nk/pt-coverage'))==baseline['coverageAfter'])
 return {'units':units,'configuration':configuration,'rows':rows,'trees':trees,'unitFiles':files,'current':baseline['current'],'coverageAfter':baseline['coverageAfter']}
def main():
 global exec_record
 os.umask(0o077);require(os.geteuid()==0 and len(sys.argv)==3 and sys.argv[1]=='retire'and sys.argv[2].isdigit());h.load_definitions()
 policy=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/pg477_unit_references.py').read_bytes();require(hashlib.sha256(policy).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
 node=next(n for n in ast.parse(policy).body if isinstance(n,ast.FunctionDef)and n.name=='exec_record');env={'re':re};exec(compile(ast.Module(body=[node],type_ignores=[]),'<fixed exec parser>','exec'),env);exec_record=env['exec_record']
 target=RUNTIME/NAME;m=h.metadata(target);directory=h.metadata(RUNTIME)
 require(m[2:6]==[0,0,stat.S_IFREG|0o644,1]and directory[2:5]==[0,0,stat.S_IFDIR|0o755]and 'system.posix_acl_access'not in os.listxattr(target)and {p.name for p in RUNTIME.iterdir()}=={NAME})
 expected=fixed_dropin(pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG796/systemd/schubert-nk-morning-controller.service').read_bytes(),NATIVE.read_bytes());require(target.read_bytes()==expected and hashlib.sha256(expected).hexdigest()=='eb600f61cdc75089d2cc66da426ff69efe8b644806e8b21684ae5ebc88466911')
 with CaptureReferences():
  try:
   before=snapshot(False,True);require(before==snapshot(False,True));persist('before.private.json',json.dumps(before,sort_keys=True).encode());persist('runtime-before.private',expected);print('REF_READY',flush=True);changed=False
   for line in sys.stdin.buffer:
    action=line.rstrip(b'\n').decode('ascii');require(action in('before','removed','release'))
    if action=='before':require(not changed and h.metadata(target)==m and target.read_bytes()==expected and h.metadata(RUNTIME)==directory);require(before==snapshot(False,True))
    else:
     require(not os.path.lexists(target)and not list(RUNTIME.iterdir())and h.metadata(RUNTIME)[:6]==directory[:6]);after=snapshot(True,action!='release');changed=True
    if action=='release':
     sql="select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;"
     require(h.command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql]).splitlines()==[b'0',b'0']);persist('after.private.json',json.dumps(after,sort_keys=True).encode());break
    print('REF_CHECKED',flush=True)
   else:raise ValueError('owner channel ended early')
  except BaseException as failure:
   print('REF_FAILED',flush=True);print('PG815_UNKNOWN type='+type(failure).__name__,file=sys.stderr,flush=True)
   import traceback
   for frame in traceback.extract_tb(failure.__traceback__):
    if frame.filename==__file__:print('PG815_FRAME method='+frame.name+' line='+str(frame.lineno),file=sys.stderr,flush=True)
   while True:time.sleep(1)
 print('REF_RELEASED',flush=True)
if __name__=='__main__':main()
'''
def helper():
 from pg805_resume_sources import fixed_dropin_source
 return fixed_dropin_source()+'\n'+HELPER
