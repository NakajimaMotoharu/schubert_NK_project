"""SSC198 R03 fixed runtime retirement witness; only exact outer typed unlink allowed."""
import ast,hashlib,json,os,pathlib,re,stat,subprocess,sys,time
import dbus
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg521-runtime-resume-v2')
RUNTIME=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d')
NAME='pg492-once-resume.conf';MORNING='schubert-nk-morning-controller.service'
NATIVE=pathlib.Path('/etc/systemd/system')/(MORNING+'.d')/'pg477-native-coverage.conf'
def require(v):
 if not v:raise ValueError('fixed fresh runtime resume refused')
def compare(before,actual,changed):
 require(set(actual)==set(before) and all(actual[k]==before[k] for k in before if k!='configuration'))
 for unit,old in before['configuration'].items():
  new=actual['configuration'][unit];require(set(old)==set(new))
  exclusions={'ExecStart','DropInPaths'} if unit==MORNING and changed else {'ExecStart'}
  require(all(old[k]==new[k] for k in old if k not in exclusions))
  left=exec_record(old['ExecStart']);right=exec_record(new['ExecStart']);require(left is not None and right is not None)
  expected=(left[0],left[1]+' --resume 91a748b4-1abe-484c-9682-44f46429b324',left[2]) if unit==MORNING and changed else left[:3]
  require(right[:3]==expected)
  if unit==MORNING and changed:require('--resume' not in left[1] and new['DropInPaths']==str(NATIVE)+' '+str(RUNTIME/NAME))
phase='PREFLIGHT';bus=None;refs=[]
try:
 require(os.geteuid()==0 and len(sys.argv)==3 and sys.argv[1]=='prepare' and sys.argv[2].isdigit());backend=int(sys.argv[2]);os.umask(0o077)
 witness=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py');w=witness.read_bytes()
 require(hashlib.sha256(w).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
 parsed=ast.parse(w);names={'command','show','metadata','tree','strict','owner','locked_database','kernel','configuration_fields'}
 constants=[n for n in parsed.body if isinstance(n,ast.Assign) and all(isinstance(t,ast.Name) and t.id in {'BOOT','UNITS','FIELDS'} for t in n.targets)]
 definitions=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in names];require(len(definitions)==len(names))
 class Fixed(ast.NodeTransformer):
  def visit_Constant(self,n):
   if n.value==b'Pg480BackupRecovery':return ast.copy_location(ast.Constant(b'Pg521RuntimeResume'),n)
   if isinstance(n.value,str) and "a.application_name='PG480-fixed-recovery'" in n.value:return ast.copy_location(ast.Constant(n.value.replace("a.application_name='PG480-fixed-recovery'","a.application_name='PG521-runtime-resume'").replace("'schubert_batch','schubert_api','schubert_web','schubert_inspector'","'schubert_batch','schubert_app','schubert_web_session','schubert_inbox_inspector','schubert_backup'").replace("l.objsubid=1 and l.granted","l.objsubid=1 and l.mode='ExclusiveLock' and l.granted")),n)
   return n
 code=Fixed().visit(ast.Module(body=constants+definitions,type_ignores=[]));ast.fix_missing_locations(code);exec(compile(code,'<fixed ownership witness>','exec'),globals())
 BOOT='cc9ed874-7f4f-450e-a188-8de1e42c8441' # Explicit current profile, never old BOOT.
 policy=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/pg477_unit_references.py').read_bytes();require(hashlib.sha256(policy).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
 definition=next(n for n in ast.parse(policy).body if isinstance(n,ast.FunctionDef) and n.name=='exec_record');exec(compile(ast.Module(body=[definition],type_ignores=[]),'<signed declaration parser>','exec'),globals())
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT and SAVE.is_dir() and metadata(SAVE)[2:6]==[0,0,stat.S_IFDIR|0o700,2] and set(p.name for p in SAVE.iterdir())=={'refs-prepare.private.log'})
 target=RUNTIME/NAME;require(not target.exists() and not target.is_symlink());native=strict(NATIVE,0o644,4096)
 runtime_directory=metadata(RUNTIME);require(runtime_directory[2:5]==[0,0,stat.S_IFDIR|0o755] and 'system.posix_acl_access' not in os.listxattr(RUNTIME))
 require(set(p.name for p in RUNTIME.iterdir())==set())
 definition_source=pathlib.Path('/var/lib/pgpt-s1-preservation/pg492-resume-tools-v3/pg492_resume_refs.py').read_bytes();require(hashlib.sha256(definition_source).hexdigest()=='a80954c1c05c22edde852dc07bd886641f77155be45fb0d0fbf2477a0fd937d3')
 fixed_definition=next(n for n in ast.parse(definition_source).body if isinstance(n,ast.FunctionDef) and n.name=='fixed_dropin');env={'require':require,'RUN_ID':'91a748b4-1abe-484c-9682-44f46429b324'};exec(compile(ast.Module(body=[fixed_definition],type_ignores=[]),'<exact prepared file>','exec'),env)
 dropin=env['fixed_dropin'](pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG495/systemd/schubert-nk-morning-controller.service').read_bytes(),native)
 owner_before=owner();locked_database();bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
 for unit in UNITS:manager.RefUnit(unit);refs.append(unit)
 def snapshot(db_required=True):
  require(owner()==owner_before)
  require(metadata(RUNTIME)[:6]==runtime_directory[:6])
  if db_required:locked_database()
  else:
   sql="select count(*) from pg_stat_activity where datname='schubert_nk' and usename in ('schubert_batch','schubert_app','schubert_backup','schubert_inbox_inspector','schubert_web_session');select count(*) from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and granted;"
   require(command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-d','schubert_nk','-c',sql],4096).splitlines()==[b'0',b'0'])
  units={u:show(u,FIELDS) for u in UNITS}
  for u,v in units.items():
   require(v['MainPID']==v['ControlPID']=='0' and v['Job']=='' and v['ActiveState'] in ('inactive','failed'));kernel(u)
  baseline_raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg520-runtime-retirement-v1/after.private.json').read_bytes()
  require(hashlib.sha256(baseline_raw).hexdigest()=='c758d3316b1b10605d44d1caecca3c93cdf1d0cb1897348d95b57daf2c424b96')
  baseline=json.loads(baseline_raw);require(set(baseline)=={'units','configuration','rows','trees','current','unitFiles'})
  complete=pathlib.Path('/var/lib/pgpt-s1-preservation/pg520-runtime-retirement-v1/complete.private').read_bytes()
  require(hashlib.sha256(complete).hexdigest()=='7c85d7e84504a514c54981de3d6c4689dc33f04f172eaf3c0211db9a822e5e0b')
  tables=baseline['rows'];require(len(tables)==24 and len(tables['schubert.batch_runs'])==452)
  require(hashlib.sha256(pathlib.Path('/run/schubert-nk/startup/epoch.current').read_bytes()).hexdigest()=='85776ad116f8f506a97a51a092afee8d2da2378bbe682c5cbf183ab3672f4da3')
  sql="begin isolation level repeatable read read only;set local timezone='UTC';"
  for t in tables:sql+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from (select to_jsonb(t) j from "+t+" t) q;"
  sql+='commit;';data={}
  for line in command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql]).splitlines():
   v=json.loads(line);require(v['table'] not in data);data[v['table']]=v['rows']
  require(data==tables and units==baseline['units'])
  trees={p:tree(pathlib.Path(p)) for p in set(baseline['trees'])|{'/run/schubert-nk/pt-coverage'}}
  require(all(trees[p]==v for p,v in baseline['trees'].items()))
  configuration={u:show(u,configuration_fields()) for u in UNITS};unit_files={}
  for u in UNITS:
   fragment=command(['/usr/bin/systemctl','show',u,'--property=FragmentPath','--value'],4096).decode().strip();require(fragment.startswith(('/etc/systemd/system/','/usr/lib/systemd/system/','/lib/systemd/system/')))
   for name in [fragment,*configuration[u]['DropInPaths'].split()]:
    if name==str(target):continue
    p=pathlib.Path(name);m=metadata(p);require(stat.S_ISREG(m[4]) and m[2]==0 and m[5]==1);unit_files[name]={'metadata':m,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};require(m==metadata(p))
  return {'units':units,'configuration':configuration,'rows':data,'trees':trees,'unitFiles':unit_files,'current':str(pathlib.Path('/opt/schubert-nk/current').readlink())}
 before=snapshot();require(before==snapshot())
 previous=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg520-runtime-retirement-v1/after.private.json').read_bytes())
 require(before==previous)
 for root,values in before['trees'].items():require(tree(pathlib.Path(root))==values)
 require(SAVE.is_dir()) # Java created only the fixed private SAVE before the child.
 def save(name,value):
  with (SAVE/name).open('x') as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 save('before.private.json',before)
 with (SAVE/'new-runtime.private').open('xb') as f:os.fchmod(f.fileno(),0o600);f.write(dropin);f.flush();os.fsync(f.fileno())
 print('REF_READY',flush=True);changed=False
 for line in sys.stdin.buffer:
  action=line.rstrip(b'\n').decode('ascii');require(action in ('before','prepare','release'));phase=action
  if action=='before':
   require(not changed and not target.exists() and not target.is_symlink());compare(before,snapshot(),False)
  elif action=='prepare':
   require(not changed and not target.exists() and not target.is_symlink());compare(before,snapshot(),False)
   fd=os.open(RUNTIME,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
   try:
    s=os.fstat(fd);require([s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]==runtime_directory)
    file=os.open(NAME,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=fd)
    try:
     os.fchmod(file,0o644)
     written=0
     while written<len(dropin):
      count=os.write(file,dropin[written:]);require(count>0);written+=count
     os.fsync(file)
    finally:os.close(file)
    os.fsync(fd)
   finally:os.close(fd)
   require(strict(target,0o644,4096)==dropin);command(['/usr/bin/systemctl','daemon-reload']);changed=True
   compare(before,snapshot(),True)
  else:
   require(changed and strict(target,0o644,4096)==dropin and set(p.name for p in RUNTIME.iterdir())=={NAME})
   compare(before,snapshot(False),True)
  if action=='release':
   save('after.private.json',snapshot(False))
   for unit in reversed(refs):manager.UnrefUnit(unit)
   bus.close();print('REF_RELEASED',flush=True);sys.exit(0)
  print('REF_CHECKED',flush=True)
 raise ValueError('owner channel ended early')
except Exception as failure:
 import traceback
 print('REF_FAILED',flush=True);print('PG521_RETIRE_REF_UNKNOWN phase='+phase+' type='+type(failure).__name__,file=sys.stderr,flush=True)
 for frame in traceback.extract_tb(failure.__traceback__):
  if frame.filename==__file__:print('PG521_RETIRE_REF_FRAME method='+frame.name+' line='+str(frame.lineno),file=sys.stderr,flush=True)
 while True:time.sleep(1)
