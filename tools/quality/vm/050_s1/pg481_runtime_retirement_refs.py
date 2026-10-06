"""SSC198 R03 fixed runtime retirement witness; only exact outer typed unlink allowed."""
import ast,hashlib,json,os,pathlib,re,stat,subprocess,sys,time
import dbus
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg481-runtime-retirement')
RUNTIME=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d')
NAME='pg481-once-resume.conf';MORNING='schubert-nk-morning-controller.service'
NATIVE=pathlib.Path('/etc/systemd/system')/(MORNING+'.d')/'pg477-native-coverage.conf'
def require(v):
 if not v:raise ValueError('fixed runtime retirement refused')
def compare(before,actual,changed):
 require(set(actual)==set(before) and all(actual[k]==before[k] for k in before if k!='configuration'))
 for unit,old in before['configuration'].items():
  new=actual['configuration'][unit];require(set(old)==set(new))
  exclusions={'ExecStart','DropInPaths'} if unit==MORNING and changed else {'ExecStart'}
  require(all(old[k]==new[k] for k in old if k not in exclusions))
  left=exec_record(old['ExecStart']);right=exec_record(new['ExecStart']);require(left is not None and right is not None)
  expected=(left[0],left[1].removesuffix(' --resume 49437eda-1681-43a9-883a-424eb55a6166'),left[2]) if unit==MORNING and changed else left[:3]
  require(right[:3]==expected)
  if unit==MORNING and changed:require(left[1]!=expected[1] and new['DropInPaths']==str(NATIVE))
phase='PREFLIGHT';bus=None;refs=[]
try:
 require(os.geteuid()==0 and len(sys.argv)==3 and sys.argv[1]=='retire' and sys.argv[2].isdigit());backend=int(sys.argv[2]);os.umask(0o077)
 witness=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py');w=witness.read_bytes()
 require(hashlib.sha256(w).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
 parsed=ast.parse(w);names={'command','show','metadata','tree','strict','owner','locked_database','kernel','configuration_fields'}
 constants=[n for n in parsed.body if isinstance(n,ast.Assign) and all(isinstance(t,ast.Name) and t.id in {'BOOT','UNITS','FIELDS'} for t in n.targets)]
 definitions=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in names];require(len(definitions)==len(names))
 class Fixed(ast.NodeTransformer):
  def visit_Constant(self,n):
   if n.value==b'Pg480BackupRecovery':return ast.copy_location(ast.Constant(b'Pg481RuntimeRetirement'),n)
   if isinstance(n.value,str) and "a.application_name='PG480-fixed-recovery'" in n.value:return ast.copy_location(ast.Constant(n.value.replace("a.application_name='PG480-fixed-recovery'","a.application_name='PG481-runtime-retirement'")),n)
   return n
 code=Fixed().visit(ast.Module(body=constants+definitions,type_ignores=[]));ast.fix_missing_locations(code);exec(compile(code,'<fixed ownership witness>','exec'),globals())
 policy=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/pg477_unit_references.py').read_bytes();require(hashlib.sha256(policy).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
 definition=next(n for n in ast.parse(policy).body if isinstance(n,ast.FunctionDef) and n.name=='exec_record');exec(compile(ast.Module(body=[definition],type_ignores=[]),'<signed declaration parser>','exec'),globals())
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT and not SAVE.exists())
 target=RUNTIME/NAME;original=strict(target,0o644,4096);runtime_meta=metadata(target);native=strict(NATIVE,0o644,4096)
 runtime_directory=metadata(RUNTIME);require(runtime_directory[2:5]==[0,0,stat.S_IFDIR|0o755] and 'system.posix_acl_access' not in os.listxattr(RUNTIME))
 expected=pathlib.Path('/var/lib/pgpt-s1-preservation/pg481-resume-preparation/native-dropin-before.private').read_bytes();require(native==expected and set(p.name for p in RUNTIME.iterdir())=={NAME})
 definition_source=pathlib.Path('/var/lib/pgpt-s1-preservation/pg481-prepared-resume-tools-v1/pg481_prepared_resume_refs.py').read_bytes();require(hashlib.sha256(definition_source).hexdigest()=='7fa3b5ac4e5461e4450d81d30dc91d2b36fbaa60bdebfc0c2a6a1ddf3e01e2bd')
 fixed_definition=next(n for n in ast.parse(definition_source).body if isinstance(n,ast.FunctionDef) and n.name=='fixed_dropin');env={'require':require,'RUN_ID':'49437eda-1681-43a9-883a-424eb55a6166'};exec(compile(ast.Module(body=[fixed_definition],type_ignores=[]),'<exact prepared file>','exec'),env)
 require(original==env['fixed_dropin'](pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG479/systemd/schubert-nk-morning-controller.service').read_bytes(),native))
 owner_before=owner();locked_database();bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
 for unit in UNITS:manager.RefUnit(unit);refs.append(unit)
 def snapshot(db_required=True):
  require(owner()==owner_before)
  require(metadata(RUNTIME)[:6]==runtime_directory[:6])
  if db_required:locked_database()
  units={u:show(u,FIELDS) for u in UNITS}
  for u,v in units.items():
   require(v['MainPID']==v['ControlPID']=='0' and v['Job']=='' and v['ActiveState'] in ('inactive','failed'));kernel(u)
  tables=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg478-newrun-preflight-v2/before.private.json').read_text())['rows']
  sql="begin isolation level repeatable read read only;set local timezone='UTC';"
  for t in tables:sql+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from (select to_jsonb(t) j from "+t+" t) q;"
  sql+='commit;';data={}
  for line in command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql]).splitlines():
   v=json.loads(line);require(v['table'] not in data);data[v['table']]=v['rows']
  require(set(data)==set(tables))
  trees={p:tree(pathlib.Path(p)) for p in ['/var/lib/schubert-nk/maintenance','/srv/schubert-nk/backup','/srv/schubert-nk/data/transfer','/run/schubert-nk/startup','/run/schubert-nk/pt-coverage','/etc/schubert-nk']}
  configuration={u:show(u,configuration_fields()) for u in UNITS};unit_files={}
  for u in UNITS:
   fragment=command(['/usr/bin/systemctl','show',u,'--property=FragmentPath','--value'],4096).decode().strip();require(fragment.startswith(('/etc/systemd/system/','/usr/lib/systemd/system/','/lib/systemd/system/')))
   for name in [fragment,*configuration[u]['DropInPaths'].split()]:
    if name==str(target):continue
    p=pathlib.Path(name);m=metadata(p);require(stat.S_ISREG(m[4]) and m[2]==0 and m[5]==1);unit_files[name]={'metadata':m,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};require(m==metadata(p))
  return {'units':units,'configuration':configuration,'rows':data,'trees':trees,'unitFiles':unit_files,'current':str(pathlib.Path('/opt/schubert-nk/current').readlink())}
 before=snapshot();SAVE.mkdir(mode=0o700)
 def save(name,value):
  with (SAVE/name).open('x') as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 save('before.private.json',before)
 with (SAVE/'runtime-before.private').open('xb') as f:os.fchmod(f.fileno(),0o600);f.write(original);f.flush();os.fsync(f.fileno())
 print('REF_READY',flush=True);changed=False
 for line in sys.stdin.buffer:
  action=line.rstrip(b'\n').decode('ascii');require(action in ('before','removed','release'));phase=action
  if action=='before':require(not changed and metadata(target)==runtime_meta and strict(target,0o644,4096)==original);compare(before,snapshot(),False)
  else:
   require(not target.exists() and not target.is_symlink() and strict(NATIVE,0o644,4096)==native and set(p.name for p in RUNTIME.iterdir())==set());compare(before,snapshot(action!='release'),True);changed=True
  if action=='release':
   save('after.private.json',snapshot(False))
   for unit in reversed(refs):manager.UnrefUnit(unit)
   bus.close();print('REF_RELEASED',flush=True);sys.exit(0)
  print('REF_CHECKED',flush=True)
 raise ValueError('owner channel ended early')
except Exception as failure:
 import traceback
 print('REF_FAILED',flush=True);print('PG481_RETIRE_REF_UNKNOWN phase='+phase+' type='+type(failure).__name__,file=sys.stderr,flush=True)
 for frame in traceback.extract_tb(failure.__traceback__):
  if frame.filename==__file__:print('PG481_RETIRE_REF_FRAME method='+frame.name+' line='+str(frame.lineno),file=sys.stderr,flush=True)
 while True:time.sleep(1)
