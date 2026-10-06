"""SSC198 exact pending code-only witness. Borrow fixed immutable PG480 witness definitions.
No general empty/DONE/Pair gate relaxation. Raw DB/native remain private.
"""
import ast,hashlib,json,os,pathlib,stat,subprocess,sys,time,shutil
import dbus
WITNESS=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py')
WITNESS_SHA='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7'
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg481-pending-codeonly')
BEFORE='/opt/schubert-nk/releases/0.1.0-PG477'
AFTER='/opt/schubert-nk/releases/0.1.0-PG479'
NEW_APPROVAL=b'NKRELEASEAPPROVAL1\nversion=0.1.0-PG479\nmanifest_sha256=a1c34cddba7d02cc479ccbe311a7ef7210f31f8aa1070f7685a2985d5503f286\n'
APPROVAL='/etc/schubert-nk/release-approval/current';APPROVAL_ROOT='/etc/schubert-nk/release-approval'
def require(v):
 if not v:raise ValueError('fixed pending code-only witness refused')
def configuration_changed_only_approval(old,new):
 if set(old)!=set(new):return False
 for name,value in old.items():
  if name==APPROVAL:
   actual=new[name]
   if actual['sha256']!=hashlib.sha256(NEW_APPROVAL).hexdigest() or actual['metadata'][2:7]!=[0,0,stat.S_IFREG|0o400,1,len(NEW_APPROVAL)]:return False
  elif name==APPROVAL_ROOT:
   if value['metadata'][:7]!=new[name]['metadata'][:7] or value['sha256']!=new[name]['sha256']:return False
  elif value!=new[name]:return False
 return True
def compare(actual,changed):
 if not changed:require(actual==before);return
 require(set(actual)==set(before) and all(actual[k]==before[k] for k in before if k!='config'))
 require(configuration_changed_only_approval(before['config'],actual['config']))
 require(strict(pathlib.Path(APPROVAL),0o400,192)==NEW_APPROVAL)
def private_json(name,value):
 with (SAVE/name).open('x') as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
phase='PREFLIGHT';bus=None;refs=[];changed=False
try:
 require(os.geteuid()==0 and len(sys.argv)==3 and sys.argv[1] in ['verify','activate'] and sys.argv[2].isdigit());backend=int(sys.argv[2]);require(backend>1)
 os.umask(0o077);require(not SAVE.exists())
 receipt=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-recovery-v3/complete.private').read_bytes()
 require(hashlib.sha256(receipt).hexdigest()=='13fa981a3c8d3748d878785e038acd45ddd0335eaa2b3a3afd75f481ccf1a466')
 pinned=WITNESS.lstat();require(stat.S_ISREG(pinned.st_mode) and pinned.st_uid==pinned.st_gid==0 and stat.S_IMODE(pinned.st_mode)==0o400 and pinned.st_nlink==1 and 'system.posix_acl_access' not in os.listxattr(WITNESS))
 raw=WITNESS.read_bytes();require(pinned==WITNESS.lstat() and hashlib.sha256(raw).hexdigest()==WITNESS_SHA)
 code=ast.parse(raw);nodes=[n for n in code.body if isinstance(n,ast.FunctionDef)]
 constants=[n for n in code.body if isinstance(n,ast.Assign) and all(isinstance(t,ast.Name) and t.id in ['BOOT','RUN','PARENT','BACKUP','UNITS','FIELDS','MARKER'] for t in n.targets)]
 class FixedBinding(ast.NodeTransformer):
  def visit_Constant(self,node):
   if node.value==b'Pg480BackupRecovery':return ast.copy_location(ast.Constant(b'Pg481PendingDeployment'),node)
   if node.value==BEFORE:return ast.copy_location(ast.Name('selectedRelease',ast.Load()),node)
   if isinstance(node.value,str) and "a.application_name='PG480-fixed-recovery'" in node.value:return ast.copy_location(ast.Constant(node.value.replace("a.application_name='PG480-fixed-recovery'","a.application_name='PG481-fixed-pending'")),node)
   return node
 bound=FixedBinding().visit(ast.Module(body=constants+nodes,type_ignores=[]));ast.fix_missing_locations(bound);exec(compile(bound,'<pinned fixed Backup witness>','exec'),globals())
 # execute above retains the closed native owner implementation, not caller-supplied authority.
 previous=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg479-archive-diagnosis/after-terminal.private.json').read_text());CONFIG=configuration_fields();held=owner();selectedRelease=BEFORE
 bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
 phase='REF_ACQUIRE'
 for unit in UNITS:manager.RefUnit(unit);refs.append(unit)
 before=snapshot('RETIRED');saved=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-recovery-v3/before.private.json').read_text());require(before==saved)
 SAVE.mkdir(mode=0o700);private_json('before.private.json',before)
 native=SAVE/'native-before-private';native.mkdir(mode=0o700)
 for name,item in before['native'].items():
  if item['sha256'] is None:continue
  path=pathlib.Path(name);relative=path.relative_to('/run/schubert-nk/pt-coverage');target=native/relative
  target.parent.mkdir(mode=0o700,parents=True,exist_ok=True);require(not target.exists())
  with path.open('rb') as source,target.open('xb') as out:
   os.fchmod(out.fileno(),0o600);shutil.copyfileobj(source,out);out.flush();os.fsync(out.fileno())
  require(hashlib.sha256(target.read_bytes()).hexdigest()==item['sha256'])
 for directory in [p for p in native.rglob('*') if p.is_dir()]+[native,SAVE]:
  fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
 compare(snapshot('RETIRED'),False);print('REF_READY',flush=True)
 for line in sys.stdin.buffer:
  name=line.rstrip(b'\n').decode('ascii');require(name in ['before','after','release'])
  phase=name
  if name=='after':require(sys.argv[1]=='activate');selectedRelease=AFTER;changed=True
  if name=='release':
   compare(snapshot('RETIRED',False),changed);private_json('after.private.json',snapshot('RETIRED',False))
   for unit in reversed(refs):manager.UnrefUnit(unit)
   bus.close();print('REF_RELEASED',flush=True);sys.exit(0)
  else:compare(snapshot('RETIRED'),changed);print('REF_CHECKED',flush=True)
 raise ValueError('owner channel ended early')
except Exception as failure:
 import traceback
 print('REF_FAILED',flush=True);print('PG481_REFERENCE_FAILURE type='+type(failure).__name__+' phase='+phase,file=sys.stderr,flush=True)
 for frame in traceback.extract_tb(failure.__traceback__):
  if frame.filename==__file__:print('PG481_REFERENCE_FRAME method='+frame.name+' line='+str(frame.lineno),file=sys.stderr,flush=True)
 while True:time.sleep(1)
