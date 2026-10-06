"""DONE486 fixed normal-completed code-only witness; no starts/DB/original mutation.
CLI source/digest are comparison demands, never ownership or signing authority.
"""
import ast,hashlib,json,os,pathlib,re,stat,subprocess,sys,time,uuid,shutil
import dbus
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg486-completed-codeonly')
OLD='/opt/schubert-nk/releases/0.1.0-PG479';NEXT='/opt/schubert-nk/releases/0.1.0-PG486'
STARTUP='/run/schubert-nk/startup';EPOCH=STARTUP+'/epoch.current'
CONFIG='/etc/schubert-nk';APPROVAL=CONFIG+'/release-approval/current'
def require(v):
 if not v:raise ValueError('fixed completed deployment refused')
def epoch_transition(old,new):
 def parse(raw):
  require(isinstance(raw,bytes) and len(raw)<=4096)
  parts=raw.decode('ascii').split('\n');require(len(parts)==9 and parts[0]=='NKEPOCH1' and parts[-1]=='')
  keys=['state','boot_id','epoch_id','run_id','cutoff_utc','activation_id','permit_sha256'];v={}
  for part,key in zip(parts[1:-1],keys):
   require(part.startswith(key+'='));v[key]=part[len(key)+1:]
  for key in ['boot_id','epoch_id','run_id','activation_id']:
   value=uuid.UUID(v[key]);require(value.int!=0 and str(value)==v[key])
  require(v['boot_id']=='e07aa706-1acd-4e65-b309-d7f330f79d54' and v['run_id']=='49437eda-1681-43a9-883a-424eb55a6166' and v['cutoff_utc']=='2026-10-06T06:28:43.734078Z')
  return v
 before=parse(old);after=parse(new)
 require(before['state']=='ISSUED' and re.fullmatch('[0-9a-f]{64}',before['permit_sha256']) is not None)
 require(after['state']=='INVALID' and after['permit_sha256']=='-' and uuid.UUID(after['epoch_id']).version==4 and after['epoch_id']!=before['epoch_id'])
 require(all(before[k]==after[k] for k in before if k not in ['state','epoch_id','permit_sha256']))
def changed_only(before,after,approval,old_epoch,new_epoch):
 require(set(after)==set(before) and after['current']==NEXT and before['current']==OLD)
 require(after['units']==before['units'] and after['configuration']==before['configuration'] and after['unitFiles']==before['unitFiles'] and after['rows']==before['rows'])
 require(set(after['trees'])==set(before['trees']))
 for root,old in before['trees'].items():
  new=after['trees'][root];require(set(old)==set(new))
  for name,value in old.items():
   actual=new[name]
   if name in [EPOCH,APPROVAL]:
    raw=new_epoch if name==EPOCH else approval;mode=0o600 if name==EPOCH else 0o400
    require(actual['sha256']==hashlib.sha256(raw).hexdigest() and actual['metadata'][0]==value['metadata'][0] and actual['metadata'][1]!=value['metadata'][1])
    require(actual['metadata'][2:7]==[0,0,stat.S_IFREG|mode,1,len(raw)])
   elif name in [STARTUP,CONFIG+'/release-approval']:
    require(value['metadata'][:7]==actual['metadata'][:7] and value['sha256']==actual['sha256'])
   else:require(value==actual)
 epoch_transition(old_epoch,new_epoch)
phase='PREFLIGHT';bus=None;refs=[]
def execute():
 global phase,bus,refs,backend,source,digest,BOOT,UNITS,FIELDS
 require(os.geteuid()==0 and len(sys.argv)==5 and sys.argv[1]=='activate' and sys.argv[2].isdigit());backend=int(sys.argv[2]);source=sys.argv[3];digest=sys.argv[4]
 require(backend>1 and re.fullmatch('[0-9a-f]{40}',source) is not None and re.fullmatch('[0-9a-f]{64}',digest) is not None);os.umask(0o077)
 witness=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py');raw=witness.read_bytes()
 require(hashlib.sha256(raw).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
 parsed=ast.parse(raw);names={'command','show','metadata','tree','strict','locked_database','kernel','configuration_fields'}
 nodes=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in names];require(len(nodes)==len(names))
 constants=[n for n in parsed.body if isinstance(n,ast.Assign) and all(isinstance(t,ast.Name) and t.id in {'BOOT','UNITS','FIELDS'} for t in n.targets)]
 class Binding(ast.NodeTransformer):
  def visit_Constant(self,n):
   if isinstance(n.value,str) and "a.application_name='PG480-fixed-recovery'" in n.value:return ast.copy_location(ast.Constant(n.value.replace("a.application_name='PG480-fixed-recovery'","a.application_name='PG486-completed-codeonly'")),n)
   return n
 code=Binding().visit(ast.Module(body=constants+nodes,type_ignores=[]));ast.fix_missing_locations(code);exec(compile(code,'<immutable ownership primitives>','exec'),globals())
 def owner():
  pid=os.getppid();p=pathlib.Path('/proc')/str(pid);args=(p/'cmdline').read_bytes().split(b'\0')
  require(args[0]==b'/opt/jdk-25.0.4/bin/java' and args[-5:]==[b'Pg486CompletedDeployment',b'activate',source.encode(),digest.encode(),b''])
  ticks=int((p/'stat').read_text().rpartition(')')[2].split()[19]);fds=[]
  for fd in (p/'fd').iterdir():
   try:fds.append(str(fd.readlink()))
   except FileNotFoundError:continue
  for name in ['maintenance.lock','startup-admission.lock']:
   path=pathlib.Path('/run/schubert-nk')/name;strict(path,0o600,0);s=path.lstat();require(str(path) in fds);found=[]
   for line in pathlib.Path('/proc/locks').read_text().splitlines():
    fields=line.split()
    if len(fields)>=8 and fields[1:5]==['FLOCK','ADVISORY','WRITE',str(pid)]:
     dev=fields[5].split(':')
     if len(dev)==3 and (int(dev[0],16),int(dev[1],16),int(dev[2]))==(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino):found.append(line)
   require(len(found)==1)
  return pid,ticks
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT and not SAVE.exists())
 for stem,expected in [('pg481-native-stop-v1','63118252463ee0895763efff82e079d604f8edbd9e5e9904ad04a211e15105e9'),('pg481-runtime-retirement','713c40cdb939f9fcf9f7130a4fabfff66d4d4e40127e8d138a3770954ae7cd61'),('pg482-bootstrap-existing','633b89135d5dfe738a9ee9dee098976e6855ff2c555e2b9d7a6122c358e03a43')]:
  require(hashlib.sha256(strict(pathlib.Path('/var/lib/pgpt-s1-preservation')/stem/'complete.private',0o600,4096)).hexdigest()==expected)
 saved_raw=strict(pathlib.Path('/var/lib/pgpt-s1-preservation/pg482-bootstrap-existing/after.private.json'),0o600,33554432);require(hashlib.sha256(saved_raw).hexdigest()=='8e579ef0b853e243130a43daf28171e9564f50196dabcd7833d7da60e7fb21a1')
 previous=json.loads(saved_raw);require(len(previous['rows'])==24 and len(previous['rows']['schubert.batch_runs'])==423)
 config_raw=strict(pathlib.Path('/var/lib/pgpt-s1-preservation/pg481-runtime-retirement/after.private.json'),0o600,33554432);require(hashlib.sha256(config_raw).hexdigest()=='c09135bc9eaf20398b5642d5d62b3aeb26d7e974176655c5a5fd809ad1d60096');prior_config=json.loads(config_raw)
 policy=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/pg477_unit_references.py').read_bytes();require(hashlib.sha256(policy).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
 definition=next(n for n in ast.parse(policy).body if isinstance(n,ast.FunctionDef) and n.name=='exec_record');env={'re':re};exec(compile(ast.Module(body=[definition],type_ignores=[]),'<immutable declaration parser>','exec'),env)
 held=owner();locked_database();bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
 for unit in UNITS:manager.RefUnit(unit);refs.append(unit)
 def snapshot(db_required=True):
  require(owner()==held)
  if db_required:locked_database()
  else:
   count=command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',"select count(*) from pg_stat_activity where datname='schubert_nk' and usename in ('schubert_batch','schubert_api','schubert_web','schubert_inspector')"],4096)
   require(count.strip()==b'0')
  units={u:show(u,FIELDS) for u in UNITS}
  for u,v in units.items():require(v['Id']==u and v['LoadState']=='loaded' and v['MainPID']==v['ControlPID']=='0' and v['Job']=='' and v['ActiveState'] in ('inactive','failed'));kernel(u)
  query="begin isolation level repeatable read read only;set local timezone='UTC';"
  for table in previous['rows']:query+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from (select to_jsonb(t) j from "+table+" t) q;"
  query+='commit;';rows={}
  for line in command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',query]).splitlines():
   v=json.loads(line);require(v['table'] not in rows);rows[v['table']]=v['rows']
  require(rows==previous['rows'])
  requests=['/run/schubert-nk/'+n for n in ['backup-request','cleanup-request','expiry-request']]
  for name in requests:require(not list(pathlib.Path(name).iterdir()))
  roots=list(previous['trees'])+['/run/schubert-nk/pt-coverage',*requests];trees={p:tree(pathlib.Path(p)) for p in roots};configuration={u:show(u,configuration_fields()) for u in UNITS};unitFiles={}
  for u,v in configuration.items():
   fragment=command(['/usr/bin/systemctl','show',u,'--property=FragmentPath','--value'],4096).decode().strip();require(fragment.startswith(('/etc/systemd/system/','/usr/lib/systemd/system/','/lib/systemd/system/')))
   for name in [fragment,*v['DropInPaths'].split()]:
    p=pathlib.Path(name);m=metadata(p);require(stat.S_ISREG(m[4]) and m[2]==0 and m[5]==1);unitFiles[name]={'metadata':m,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};require(m==metadata(p))
  return {'units':units,'configuration':configuration,'unitFiles':unitFiles,'trees':trees,'rows':rows,'current':str(pathlib.Path('/opt/schubert-nk/current').readlink())}
 before=snapshot();require(before==snapshot() and before['current']==OLD and before['unitFiles']==prior_config['unitFiles'])
 require(set(before['configuration'])==set(prior_config['configuration']))
 for unit,value in before['configuration'].items():
  old=prior_config['configuration'][unit];require(set(value)==set(old) and all(value[k]==old[k] for k in old if k!='ExecStart'))
  left=env['exec_record'](old['ExecStart']);right=env['exec_record'](value['ExecStart']);require(left is not None and right is not None and left[:3]==right[:3])
 require(all(before['trees'][k]==v for k,v in previous['trees'].items()) and before['trees']['/run/schubert-nk/pt-coverage']==previous['native'])
 old_epoch=strict(pathlib.Path(EPOCH),0o600,4096);approval=('NKRELEASEAPPROVAL1\nversion=0.1.0-PG486\nmanifest_sha256='+digest+'\n').encode('ascii')
 SAVE.mkdir(mode=0o700)
 def save(name,value):
  with (SAVE/name).open('x') as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
  fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
 save('before.private.json',before)
 native=SAVE/'native-before-private';native.mkdir(mode=0o700)
 for name,item in before['trees']['/run/schubert-nk/pt-coverage'].items():
  if item['sha256'] is None:continue
  p=pathlib.Path(name);target=native/p.relative_to('/run/schubert-nk/pt-coverage');target.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
  with p.open('rb') as inp,target.open('xb') as out:os.fchmod(out.fileno(),0o600);shutil.copyfileobj(inp,out);out.flush();os.fsync(out.fileno())
  require(hashlib.sha256(target.read_bytes()).hexdigest()==item['sha256'])
 for directory in [p for p in native.rglob('*') if p.is_dir()]+[native,SAVE]:
  fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
 require(snapshot()==before);print('REF_READY',flush=True);changed=False
 for line in sys.stdin.buffer:
  action=line.rstrip(b'\n').decode('ascii');phase=action;require(action in ['before','after','release'])
  if action=='before':require(not changed and snapshot()==before)
  else:
   require(action!='release' or changed);new_epoch=strict(pathlib.Path(EPOCH),0o600,4096);changed_only(before,snapshot(action!='release'),approval,old_epoch,new_epoch);require(strict(pathlib.Path(APPROVAL),0o400,192)==approval);changed=True
  if action=='release':
   save('after.private.json',snapshot(False))
   for unit in reversed(refs):manager.UnrefUnit(unit)
   bus.close();print('REF_RELEASED',flush=True);return
  print('REF_CHECKED',flush=True)
 raise ValueError('owner channel ended early')
if __name__=='__main__':
 try:execute()
 except Exception as failure:
  print('REF_FAILED',flush=True);print('PG486_REFERENCE_UNKNOWN phase='+phase+' type='+type(failure).__name__,file=sys.stderr,flush=True)
  import traceback
  for frame in traceback.extract_tb(failure.__traceback__):
   if frame.filename==__file__:print('PG486_REFERENCE_FRAME method='+frame.name+' line='+str(frame.lineno),file=sys.stderr,flush=True)
  while True:time.sleep(1)
