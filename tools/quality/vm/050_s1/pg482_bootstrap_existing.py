"""BOOT482001..004 fixed new-only synthetic bootstrap; under fresh Java M/A.
Exclusive DB exists only in prepare/post, never held across Bootstrap's shared TX.
"""
import ast,datetime,hashlib,json,os,pathlib,re,secrets,stat,subprocess,sys,time
import dbus
from pg457_stable_actor import stable_actor,ENTRIES
ENTRY='dev.codex.schubert.nk.api.bootstrap.BootstrapAdminMain';ENTRIES.add(ENTRY)
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg482-bootstrap-existing')
UNIT='schubert-nk-bootstrap-admin.service';CREDS=pathlib.Path('/etc/schubert-nk/credentials')
SOURCES={'bootstrap-admin-username','bootstrap-admin-password'};BOOT='e07aa706-1acd-4e65-b309-d7f330f79d54'
UNITS=['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service','schubert-nk-morning-controller.service',UNIT]
FIELDS=set('Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,InvocationID,Type,Restart,RemainAfterExit,Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,KillMode,SendSIGKILL'.split(','))
def require(v):
 if not v:raise ValueError('fixed synthetic bootstrap refused')
def normal20(v):
 return isinstance(v,dict) and set(v)==FIELDS and all(isinstance(x,str) for x in v.values()) and v['Id']==UNIT and v['LoadState']=='loaded' and v['Type']=='oneshot' and v['Restart']=='no' and v['RemainAfterExit']=='no' and v['KillMode']=='control-group' and v['SendSIGKILL']=='no' and v['MainPID']==v['ControlPID']=='0' and v['Job']=='' and v['ActiveState']=='inactive' and v['SubState']=='dead' and v['Result']=='success' and v['ExecMainCode']=='1' and v['ExecMainStatus']=='20' and re.fullmatch('[0-9a-f]{32}',v['InvocationID']) is not None and v['InvocationID']!='0'*32 and v['ExecMainStartTimestampMonotonic'].isdigit() and v['ExecMainExitTimestampMonotonic'].isdigit() and 0<int(v['ExecMainStartTimestampMonotonic'])<=int(v['ExecMainExitTimestampMonotonic'])<=int(v['ExecMainStartTimestampMonotonic'])+30000000
def command(args,limit=33554432):
 r=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=30);require(r.returncode==0 and len(r.stdout)<=limit);return r.stdout
def show(unit=UNIT):
 d=dict(line.split('=',1) for line in command(['/usr/bin/systemctl','show',unit,'--property='+','.join(sorted(FIELDS))],1048576).decode('ascii').splitlines());require(set(d)==FIELDS and d['Id']==unit);return d
def save(name,value):
 with (SAVE/name).open('x') as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
def sql(query):return command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',query])
phase='PREFLIGHT';refs=[];bus=None
try:
 require(os.geteuid()==0 and sys.argv[1]=='execute' and len(sys.argv)==3 and sys.argv[2].isdigit());backend=int(sys.argv[2]);os.umask(0o077)
 witness=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes();require(hashlib.sha256(witness).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
 nodes=[n for n in ast.parse(witness).body if isinstance(n,ast.FunctionDef) and n.name in ('metadata','tree','strict','owner','kernel','locked_database')]
 class Fixed(ast.NodeTransformer):
  def visit_Constant(self,n):
   if n.value==b'Pg480BackupRecovery':return ast.copy_location(ast.Constant(b'Pg482BootstrapExisting'),n)
   if isinstance(n.value,str) and "a.application_name='PG480-fixed-recovery'" in n.value:return ast.copy_location(ast.Constant(n.value.replace("a.application_name='PG480-fixed-recovery'","a.application_name='PG482-bootstrap-guard'")),n)
   return n
 bound=Fixed().visit(ast.Module(body=nodes,type_ignores=[]));ast.fix_missing_locations(bound);exec(compile(bound,'<fixed ownership capture>','exec'),globals())
 policy=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/pg477_unit_references.py').read_bytes();require(hashlib.sha256(policy).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
 definition=next(n for n in ast.parse(policy).body if isinstance(n,ast.FunctionDef) and n.name=='exec_record');exec(compile(ast.Module(body=[definition],type_ignores=[]),'<signed declaration parser>','exec'),globals())
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT and not SAVE.exists() and all(not (CREDS/n).exists() and not (CREDS/n).is_symlink() for n in SOURCES))
 require(pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG479'))
 require(hashlib.sha256(pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='a1c34cddba7d02cc479ccbe311a7ef7210f31f8aa1070f7685a2985d5503f286')
 held=owner();locked_database();bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
 for u in UNITS:manager.RefUnit(u);refs.append(u)
 tables=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg478-newrun-preflight-v2/before.private.json').read_text())['rows']
 def snapshot():
  require(owner()==held)
  units={u:show(u) for u in UNITS}
  for u,v in units.items():require(v['MainPID']==v['ControlPID']=='0' and v['Job']=='' and v['ActiveState'] in ('inactive','failed'));kernel(u)
  query="begin isolation level repeatable read read only;set local timezone='UTC';"
  for t in tables:query+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from (select to_jsonb(t) j from "+t+" t) q;"
  query+='commit;';rows={}
  for line in sql(query).splitlines():
   v=json.loads(line);require(v['table'] not in rows);rows[v['table']]=v['rows']
  require(set(rows)==set(tables) and len(rows['schubert.app_users'])==1 and rows['schubert.app_users'][0]['role']=='ADMIN')
  roots=['/var/lib/schubert-nk/maintenance','/srv/schubert-nk/backup','/srv/schubert-nk/data/transfer','/run/schubert-nk/startup','/etc/schubert-nk','/var/lib/pgpt-s1-preservation/pg468-bootstrap-retired-v1']
  trees={r:tree(pathlib.Path(r)) for r in roots};native=tree(pathlib.Path('/run/schubert-nk/pt-coverage'))
  config={}
  for u in UNITS:
   v=dict(line.split('=',1) for line in command(['/usr/bin/systemctl','show',u,'--property=ExecStart,DropInPaths,ReadWritePaths,User,Group,SupplementaryGroups,NoNewPrivileges,CapabilityBoundingSet,AmbientCapabilities,ProtectSystem,SuccessExitStatus'],1048576).decode().splitlines());decl=exec_record(v['ExecStart']);require(decl is not None);v['ExecStart']=decl[:3];config[u]=v
  return {'units':units,'rows':rows,'trees':trees,'native':native,'config':config}
 before=snapshot();SAVE.mkdir(mode=0o700);save('before.private.json',before);synthetic={};native_path=None;terminal=None
 def unchanged(post,credentials_present,native_added):
  require(post['rows']==before['rows'] and all(post['units'][u]==before['units'][u] for u in UNITS if u!=UNIT) and post['config']==before['config'])
  for root,old in before['trees'].items():
   got=post['trees'][root]
   if root!='/etc/schubert-nk':require(got==old);continue
   expected_new={str(CREDS/n) for n in SOURCES} if credentials_present else set();require(set(got)==set(old)|expected_new)
   for p,v in old.items():
    if p==str(CREDS):require(got[p]['metadata'][:6]==v['metadata'][:6])
    else:require(got[p]==v)
   for n in SOURCES:
    if credentials_present:require(strict(CREDS/n,0o400,256)==synthetic[n])
  old=before['native'];got=post['native'];require(set(got)==set(old)|({str(native_path)} if native_added else set()))
  for p,v in old.items():
   if native_added and p=='/run/schubert-nk/pt-coverage/ordinary-bootstrap196':require(got[p]['metadata'][:6]==v['metadata'][:6])
   else:require(got[p]==v)
 print('REF_READY',flush=True)
 for line in sys.stdin.buffer:
  action=line.rstrip(b'\n').decode('ascii');phase=action
  if action=='prepare':
   locked_database();require(snapshot()==before);synthetic={'bootstrap-admin-username':b'pgpt_bootstrap_482_synthetic','bootstrap-admin-password':secrets.token_urlsafe(32).encode('ascii')}
   for n,data in synthetic.items():
    fd=os.open(CREDS/n,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o400)
    with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
   fd=os.open(CREDS,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd);unchanged(snapshot(),True,False);print('REF_CHECKED',flush=True)
  elif action=='run':
   require(sql('select count(*) from pg_stat_activity where datname=\'schubert_nk\' and usename in (\'schubert_batch\',\'schubert_api\',\'schubert_web\',\'schubert_inspector\')').strip()==b'0')
   unchanged(snapshot(),True,False);save('start-reserved.private.json',{'oneExistingOnlyStart':True,'at':datetime.datetime.now(datetime.timezone.utc).isoformat()});require(owner()==held)
   command(['/usr/bin/systemctl','start','--no-block',UNIT],4096);deadline=time.monotonic()+35;actor=None;inv=None;states=[]
   while time.monotonic()<deadline:
    state=stable_actor('bootstrap',lambda role:show());states.append(state)
    if state.get('race'):time.sleep(.01);continue
    if state['InvocationID']:
     if inv is None:inv=state['InvocationID']
     require(inv==state['InvocationID'])
    if int(state['MainPID']) and state.get('entry')==ENTRY and actor is None:
     try:
      p=pathlib.Path('/proc')/state['MainPID'];status={k:v.strip() for k,v in (x.split(':',1) for x in (p/'status').read_text().splitlines())};tick=(p/'stat').read_text().rpartition(')')[2].split()[19]
      require(status['Uid'].split()==['999']*4 and status['Gid'].split()==['981']*4 and sorted(set(status['Groups'].split()),key=int)==sorted(set(command(['id','-G','schubert-api'],4096).decode().split()),key=int) and status['NoNewPrivs']=='1' and all(int(status[k],16)==0 for k in ('CapInh','CapPrm','CapEff','CapBnd','CapAmb')) and (p/'cgroup').read_text()=='0::/system.slice/'+UNIT+'\n')
      require(show()['MainPID']==state['MainPID'] and show()['InvocationID']==inv);actor={'pid':state['MainPID'],'ticks':tick,'invocation':inv,'zeroCapabilities':True};save('actor.private.json',actor)
     except FileNotFoundError:pass
    if inv and state['MainPID']==state['ControlPID']=='0' and not state['Job'] and state['ActiveState'] in ('inactive','failed'):break
    time.sleep(.01)
   save('states.private.json',states);require(actor is not None and normal20(state) and not pathlib.Path('/proc',actor['pid']).exists());kernel(UNIT);require(not pathlib.Path('/run/credentials',UNIT).exists());terminal=show();require(normal20(terminal) and terminal['InvocationID']==inv)
   journal=command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_SYSTEMD_INVOCATION_ID='+inv,'-o','json','--no-pager'],4194304);records=[json.loads(r) for r in journal.splitlines()];messages=[r.get('MESSAGE') for r in records]
   require(messages.count('Initial ADMIN bootstrap finished')==1 and messages.count('Bootstrap fixed PT native capture complete')==1 and 'Initial ADMIN bootstrap failed' not in messages)
   with (SAVE/'journal.private.jsonl').open('xb') as f:os.fchmod(f.fileno(),0o600);f.write(journal);f.flush();os.fsync(f.fileno())
   native_path=pathlib.Path('/run/schubert-nk/pt-coverage/ordinary-bootstrap196')/(inv+'.terminal.exec');s=native_path.lstat();require(stat.S_ISREG(s.st_mode) and s.st_uid==999 and s.st_gid==981 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1 and s.st_size>0);unchanged(snapshot(),True,True);save('terminal.private.json',terminal);print('REF_CHECKED',flush=True)
  elif re.fullmatch('retire:[1-9][0-9]*',action):
   backend=int(action.split(':')[1]);locked_database();require(show()==terminal and normal20(terminal));unchanged(snapshot(),True,True)
   for n in sorted(SOURCES):require(strict(CREDS/n,0o400,256)==synthetic[n]);os.rename(CREDS/n,SAVE/(n+'.retired.private'))
   for d in (CREDS,SAVE):fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
   unchanged(snapshot(),False,True);save('after.private.json',snapshot());print('REF_CHECKED',flush=True)
  elif action=='release':
   require(all(not (CREDS/n).exists() and strict(SAVE/(n+'.retired.private'),0o400,256)==synthetic[n] for n in SOURCES));unchanged(snapshot(),False,True)
   for u in reversed(refs):manager.UnrefUnit(u)
   bus.close();print('REF_RELEASED',flush=True);sys.exit(0)
  else:raise ValueError('fixed command required')
 raise ValueError('owner channel ended early')
except Exception as failure:
 import traceback
 print('REF_FAILED',flush=True);print('PG482_BOOTSTRAP_UNKNOWN phase='+phase+' type='+type(failure).__name__,file=sys.stderr,flush=True)
 for frame in traceback.extract_tb(failure.__traceback__):
  if frame.filename==__file__:print('PG482_BOOTSTRAP_FRAME method='+frame.name+' line='+str(frame.lineno),file=sys.stderr,flush=True)
 while True:time.sleep(1)
