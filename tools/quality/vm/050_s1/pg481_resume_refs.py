"""SSC198 fixed one-run runtime preparation, under new outer M/A/DB/ten references."""
import ast,hashlib,json,os,pathlib,re,stat,subprocess,sys,time
import dbus
WITNESS=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py')
WITNESS_SHA='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7'
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg481-resume-preparation')
RUNTIME=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d')
NAME='pg481-once-resume.conf';MORNING='schubert-nk-morning-controller.service'
NATIVE=pathlib.Path('/etc/systemd/system')/(MORNING+'.d')/'pg477-native-coverage.conf'
RUN_ID='49437eda-1681-43a9-883a-424eb55a6166'
def require(v):
 if not v:raise ValueError('fixed once-resume preparation refused')
def fixed_dropin(base,native):
 if not isinstance(base,bytes) or not isinstance(native,bytes):raise ValueError('fixed signed base required')
 starts=[r.removeprefix(b'ExecStart=') for r in base.splitlines() if r.startswith(b'ExecStart=')]
 require(len(starts)==1 and starts[0].endswith(b' dev.codex.schubert.nk.batch.file.MorningProcessMain') and b'--resume' not in starts[0] and b'-javaagent' not in starts[0])
 agent=b'/usr/bin/java -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=destfile=/run/schubert-nk/pt-coverage/parent/parent.exec,append=false '
 argv=starts[0].replace(b'/usr/bin/java ',agent,1);require(argv!=starts[0])
 expected=b'# PGPT only: same entry/byte/owners; JaCoCo and explicit same-run resume.\n[Service]\nExecStart=\nExecStart='+argv+b'\nReadWritePaths=/run/schubert-nk/pt-coverage/parent\n'
 require(native==expected)
 return b'# SSC198: fixed one-run same-cutoff resume; retire only after genuine terminal.\n[Service]\nExecStart=\nExecStart='+argv+b' --resume '+RUN_ID.encode()+b'\n'
def private_json(name,value):
 with (SAVE/name).open('x') as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 sync(SAVE)
def sync(p):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
def compare(actual,changed):
 require(set(actual)==set(before) and all(actual[k]==before[k] for k in before if k!='configuration'))
 if not changed:require(actual==before);return
 for unit,conf in before['configuration'].items():
  if unit==MORNING:
   got=actual['configuration'][unit]
   require(all(got[k]==conf[k] for k in CONFIG-{'ExecStart','DropInPaths'}))
   require(exec_record(got['ExecStart'])[:3]==('/usr/bin/java',new_argv,'no'))
   require(got['DropInPaths']==str(NATIVE)+' '+str(RUNTIME/NAME))
  else:
   got=actual['configuration'][unit]
   require(all(got[k]==conf[k] for k in CONFIG-{'ExecStart'}))
   old_decl=exec_record(conf['ExecStart']);new_decl=exec_record(got['ExecStart'])
   require(old_decl is not None and new_decl is not None and old_decl[:3]==new_decl[:3])
 require(strict(RUNTIME/NAME,0o644,4096)==dropin)
 require(set(p.name for p in RUNTIME.iterdir())=={NAME})
phase='PREFLIGHT';bus=None;refs=[];changed=False
try:
 require(os.geteuid()==0 and len(sys.argv)==3 and sys.argv[1]=='prepare' and sys.argv[2].isdigit());backend=int(sys.argv[2]);require(backend>1)
 os.umask(0o077);require(not SAVE.exists() and not RUNTIME.exists())
 complete=pathlib.Path('/var/lib/pgpt-s1-preservation/pg481-pending-codeonly/complete.private').read_bytes()
 require(hashlib.sha256(complete).hexdigest()=='2978f79f537db1a690ed9e46df94138048748af9572f428a62157378e1c7b230')
 st=WITNESS.lstat();require(stat.S_ISREG(st.st_mode) and st.st_uid==st.st_gid==0 and stat.S_IMODE(st.st_mode)==0o400 and st.st_nlink==1 and 'system.posix_acl_access' not in os.listxattr(WITNESS))
 raw=WITNESS.read_bytes();require(st==WITNESS.lstat() and hashlib.sha256(raw).hexdigest()==WITNESS_SHA)
 code=ast.parse(raw);nodes=[n for n in code.body if isinstance(n,ast.FunctionDef)]
 constants=[n for n in code.body if isinstance(n,ast.Assign) and all(isinstance(t,ast.Name) and t.id in ['BOOT','RUN','PARENT','BACKUP','UNITS','FIELDS','MARKER'] for t in n.targets)]
 class FixedBinding(ast.NodeTransformer):
  def visit_Constant(self,node):
   if node.value==b'Pg480BackupRecovery':return ast.copy_location(ast.Constant(b'Pg481ResumePreparation'),node)
   if node.value=='/opt/schubert-nk/releases/0.1.0-PG477':return ast.copy_location(ast.Constant('/opt/schubert-nk/releases/0.1.0-PG479'),node)
   if isinstance(node.value,str) and "a.application_name='PG480-fixed-recovery'" in node.value:return ast.copy_location(ast.Constant(node.value.replace("a.application_name='PG480-fixed-recovery'","a.application_name='PG481-fixed-resume'")),node)
   return node
 bound=FixedBinding().visit(ast.Module(body=constants+nodes,type_ignores=[]));ast.fix_missing_locations(bound);exec(compile(bound,'<fixed original witness>','exec'),globals())
 previous=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg479-archive-diagnosis/after-terminal.private.json').read_text());CONFIG=configuration_fields();held=owner()
 policy=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/pg477_unit_references.py').read_bytes();require(hashlib.sha256(policy).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
 definition=next(n for n in ast.parse(policy).body if isinstance(n,ast.FunctionDef) and n.name=='exec_record');exec(compile(ast.Module(body=[definition],type_ignores=[]),'<pinned declaration>','exec'),globals())
 approved_before=approved_configuration
 def approved_configuration(unit,conf):
  if changed and unit==MORNING:
   old=before['configuration'][unit];require(all(conf[k]==old[k] for k in CONFIG-{'ExecStart','DropInPaths'}))
   parsed=exec_record(conf['ExecStart']);require(parsed is not None and parsed[:3]==('/usr/bin/java',new_argv,'no') and conf['DropInPaths']==str(NATIVE)+' '+str(RUNTIME/NAME))
  else:approved_before(unit,conf)
 native=strict(NATIVE,0o644,4096)
 base=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG479/systemd')/MORNING
 dropin=fixed_dropin(base.read_bytes(),native);new_argv=next(r.removeprefix(b'ExecStart=') for r in dropin.splitlines() if r.startswith(b'ExecStart=') and r!=b'ExecStart=').decode('ascii')
 parent=RUNTIME.parent;s=parent.lstat();require(stat.S_ISDIR(s.st_mode) and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o755 and 'system.posix_acl_access' not in os.listxattr(parent))
 bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
 phase='REF_ACQUIRE'
 for unit in UNITS:manager.RefUnit(unit);refs.append(unit)
 before=snapshot('RETIRED');saved=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg481-pending-codeonly/after.private.json').read_text());require(before==saved)
 old=exec_record(before['configuration'][MORNING]['ExecStart']);require(old is not None and old[:3]==('/usr/bin/java',new_argv.removesuffix(' --resume '+RUN_ID),'no'))
 require(before['configuration'][MORNING]['DropInPaths']==str(NATIVE))
 SAVE.mkdir(mode=0o700);private_json('before.private.json',before)
 with (SAVE/'native-dropin-before.private').open('xb') as f:os.fchmod(f.fileno(),0o600);f.write(native);f.flush();os.fsync(f.fileno())
 sync(SAVE);print('REF_READY',flush=True)
 for line in sys.stdin.buffer:
  name=line.rstrip(b'\n').decode('ascii');require(name in ['before','prepare','release']);phase=name
  if name=='prepare':
   require(not changed);compare(snapshot('RETIRED'),False)
   RUNTIME.mkdir(mode=0o755);os.chmod(RUNTIME,0o755);sync(parent)
   target=RUNTIME/NAME;fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o644)
   with os.fdopen(fd,'wb') as f:os.fchmod(f.fileno(),0o644);f.write(dropin);f.flush();os.fsync(f.fileno())
   sync(RUNTIME);require(strict(target,0o644,4096)==dropin);phase='ONE_RELOAD';command(['/usr/bin/systemctl','daemon-reload'],4096);changed=True
  if name=='release':
   require(changed);actual=snapshot('RETIRED',False);compare(actual,True);private_json('after.private.json',actual)
   for unit in reversed(refs):manager.UnrefUnit(unit)
   bus.close();print('REF_RELEASED',flush=True);sys.exit(0)
  else:compare(snapshot('RETIRED'),changed);print('REF_CHECKED',flush=True)
 raise ValueError('owner channel ended early')
except Exception as failure:
 import traceback
 print('REF_FAILED',flush=True);print('PG481_RESUME_REFERENCE_FAILURE type='+type(failure).__name__+' phase='+phase,file=sys.stderr,flush=True)
 for frame in traceback.extract_tb(failure.__traceback__):
  if frame.filename==__file__:print('PG481_RESUME_REFERENCE_FRAME method='+frame.name+' line='+str(frame.lineno),file=sys.stderr,flush=True)
 while True:time.sleep(1)
