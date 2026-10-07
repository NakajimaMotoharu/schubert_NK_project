"""SSC210/PT-OPS-PG517: fixed new ownership/tenRef, full originals, owned stops only."""
import ast, hashlib, json, os, pathlib, stat, subprocess, sys, time
import dbus

BOOT='cc9ed874-7f4f-450e-a188-8de1e42c8441'
ROOT=pathlib.Path('/var/lib/pgpt-s1-preservation/pg517-terminal-api-recovery-v1')
BASE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg516-terminal-issued-handoff-v1/before.private.json')
BASE_HASH='36362db410eb99db610dc896adf95bb2c9f485c9c81518da0c99cdd353758a80'
STARTUP='/run/schubert-nk/startup'
ORDER=['schubert-nk-expiry-cleanup.service','schubert-nk-cleanup.service','artemis.service']
PINS={
 '/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py':('0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7',{'command','show','metadata','tree','configuration_fields','kernel'}),
 '/var/lib/pgpt-s1-preservation/pg496-timeout-tools-v6/pg481_native_owned_stop.py':('99b24d0b0169fd8e7c6075f01096b6efeedaa953ee759e63eaa0e33f64fcb865',{'terminal','same_generation','normal_terminal','broker_witness'}),
 '/var/lib/pgpt-s1-preservation/pg496-timeout-tools-v6/pg466_term_witness.py':('e257ac5b9dea23ba91f68231717ee787b839f5d08d95fd67d62ac3c20b568a78',{'unique'})}

def require(value):
 if not value:raise ValueError('fixed single API recovery refused')
def load_definitions():
 for p,(digest,wanted) in PINS.items():
  raw=pathlib.Path(p).read_bytes();require(hashlib.sha256(raw).hexdigest()==digest)
  parsed=ast.parse(raw);defs=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in wanted]
  require(len(defs)==len(wanted))
  if 'show' in wanted:
   defs=[n for n in parsed.body if isinstance(n,ast.Assign) and all(isinstance(t,ast.Name) and t.id in {'UNITS','FIELDS'} for t in n.targets)]+defs
  exec(compile(ast.Module(body=defs,type_ignores=[]),'<fixed readonly/witness primitives>','exec'),globals())
def tick(pid):return int((pathlib.Path('/proc')/str(pid)/'stat').read_text().rpartition(')')[2].split()[19])
def holder(released=False):
 pid=os.getppid();p=pathlib.Path('/proc')/str(pid);args=(p/'cmdline').read_bytes().split(b'\0')
 require(args[0]==b'/opt/jdk-25.0.4/bin/java' and args[-3:]==[b'Pg517TerminalApiRecovery',b'recover',b''])
 require((p/'status').read_text().split('Uid:')[1].splitlines()[0].split()==['0']*4)
 ids={};links=[]
 for f in (p/'fd').iterdir():
  try:links.append(str(f.readlink()))
  except FileNotFoundError:pass
 for name in ['maintenance.lock','startup-admission.lock']:
  path=pathlib.Path('/run/schubert-nk')/name;m=metadata(path)
  require(m[2:7]==[0,0,stat.S_IFREG|0o600,1,0] and str(path) in links and not os.listxattr(path))
  matches=[]
  for row in pathlib.Path('/proc/locks').read_text().splitlines():
   v=row.split()
   if len(v)>=8 and v[1:5]==['FLOCK','ADVISORY','WRITE',str(pid)]:
    d=v[5].split(':')
    if len(d)==3 and (int(d[0],16),int(d[1],16),int(d[2]))==(os.major(m[0]),os.minor(m[0]),m[1]):matches.append(row)
  require(len(matches)==1);ids[name]=m
 sql="select count(*) from pg_stat_activity a where a.pid="+str(backend)+" and a.usename='schubert_batch' and a.application_name='PG517-fixed-recovery' and a.datname='schubert_nk' and exists(select 1 from pg_locks l where l.pid=a.pid and l.locktype='advisory' and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.granted);select count(*) from pg_stat_activity where datname='schubert_nk' and usename in ('schubert_batch','schubert_app','schubert_web_session','schubert_backup','schubert_inbox_inspector') and pid<>"+str(backend)+";"
 require(command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-d','schubert_nk','-c',sql]).splitlines()==([b'0',b'0'] if released else [b'1',b'0']))
 return pid,tick(pid),ids
def identity():
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
 require(str(pathlib.Path('/opt/schubert-nk/current').readlink())=='/opt/schubert-nk/releases/0.1.0-PG495')
 v=show('schubert-nk-morning-controller.service',FIELDS)
 require(v==baseline['units']['schubert-nk-morning-controller.service'] and not pathlib.Path('/proc/5872').exists())
 kernel('schubert-nk-morning-controller.service')
def namespace_failure_proof():
 raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg512-api-namespace-v1/api-journal.private.jsonl').read_bytes()
 require(hashlib.sha256(raw).hexdigest()=='151a73820d0344d9f123e4f5b0ab884a51f7663dea6efd61f59456d25eb408ff')
 rows=[json.loads(r,object_pairs_hook=unique) for r in raw.splitlines()]
 require(len(rows)==33 and all(r.get('_BOOT_ID')==BOOT.replace('-','') for r in rows))
 failed=[r for r in rows if '/run/schubert-nk/pt-coverage/ordinary-api193' in r.get('MESSAGE','') and 'No such file or directory' in r.get('MESSAGE','')]
 require(len(failed)==5 and all(r.get('_UID')=='0' for r in failed))
 require(sum('Failed at step NAMESPACE' in r.get('MESSAGE','') for r in rows)==5)
 require(not pathlib.Path('/run/schubert-nk/pt-coverage/ordinary-api193').exists())
def cohort():
 units={u:show(u,FIELDS) for u in UNITS}
 require(units==baseline['units'])
 for u,v in units.items():require(terminal(v));kernel(u)
 require(units=={u:show(u,FIELDS) for u in UNITS})
def startup_preserved(actual,previous):
 if not isinstance(actual,dict) or not isinstance(previous,dict):return False
 markers=[p for p in previous if p.endswith('.API.start.intent')]
 if len(previous)!=5 or len(markers)!=1:return False
 marker=markers[0]
 if set(actual) not in (set(previous),set(previous)-{marker}):return False
 if actual[STARTUP]['metadata'][:6]!=previous[STARTUP]['metadata'][:6]:return False
 if actual[STARTUP]['sha256']!=previous[STARTUP]['sha256']:return False
 current=STARTUP+'/epoch.current'
 if not revoked_phase:return all(actual[p]==previous[p] for p in actual if p!=STARTUP)
 if current not in actual or current not in previous:return False
 a=actual[current];b=previous[current]
 if a['metadata'][0]!=b['metadata'][0] or a['metadata'][2:6]!=b['metadata'][2:6]:return False
 if a['sha256']!=invalid_hash or a['metadata'][6]!=invalid_length:return False
 return all(actual[p]==previous[p] for p in actual if p not in [STARTUP,current])
def values():
 identity();require(holder()==owner);cohort()
 sql="begin isolation level repeatable read read only;set local timezone='UTC';";rows={}
 for table in baseline['rows']:
  sql+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from (select to_jsonb(t) j from "+table+" t) q;"
 for line in command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql+'commit;']).splitlines():
  v=json.loads(line);require(v['table'] not in rows);rows[v['table']]=v['rows']
 require(rows==baseline['rows'])
 roots={p:tree(pathlib.Path(p)) for p in baseline['trees']}
 for p in roots:require(startup_preserved(roots[p],baseline['trees'][p]) if p==STARTUP else roots[p]==baseline['trees'][p])
 require({u:show(u,configuration_fields()) for u in UNITS}==baseline['configuration'])
 identity();require(holder()==owner)
 return {'rows':rows,'trees':roots}
def save(name,data):
 require('/' not in name)
 with (ROOT/name).open('xb') as f:os.fchmod(f.fileno(),0o600);f.write(data);f.flush();os.fsync(f.fileno())
 fd=os.open(ROOT,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
def actor(unit,v):
 require(unit=='artemis.service');p=pathlib.Path('/proc')/v['MainPID']
 status={r.split(':',1)[0]:r.split(':',1)[1].strip() for r in (p/'status').read_text().splitlines() if ':' in r}
 a={'pid':v['MainPID'],'invocation':v['InvocationID'],'ticks':tick(v['MainPID']),
  'authority':{k:status[k] for k in ['Uid','Gid','Groups','CapInh','CapPrm','CapEff','CapBnd','CapAmb','NoNewPrivs']},
  'cgroup':(p/'cgroup').read_text(),'argvSha256':hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()}
 require(a==baseline['actors'][unit] and a['pid']=='38602' and a['ticks']==396578)
 control=show(unit,{'ControlGroup','Delegate','Slice'})
 require(control=={'ControlGroup':'/system.slice/artemis.service','Delegate':'no','Slice':'system.slice'})
 cg=pathlib.Path('/sys/fs/cgroup/system.slice/artemis.service');require(cg.is_dir())
 processes=[]
 for group in [cg,*[g for g in cg.rglob('*') if g.is_dir()]]:
  require(stat.S_ISDIR(group.lstat().st_mode));processes+=group.joinpath('cgroup.procs').read_text().splitlines()
 children=[t.joinpath('children').read_text().strip() for t in p.joinpath('task').iterdir()]
 require(kernel_actor(processes,children) and tick(v['MainPID'])==396578)
 require(control==show(unit,{'ControlGroup','Delegate','Slice'}))
 require(v==show(unit,FIELDS))
def kernel_actor(processes,children):
 return isinstance(processes,list) and processes==['38602'] and isinstance(children,list) and bool(children) and all(c=='' for c in children)
def broker_stop(before,after):
 raw=command(['/usr/bin/journalctl','--boot','_SYSTEMD_INVOCATION_ID='+before['InvocationID'],'-o','json','--no-pager'])
 vendor=[json.loads(r,object_pairs_hook=unique) for r in raw.splitlines()]
 uid=baseline['actors']['artemis.service']['authority']['Uid'].split()[0]
 require(vendor and all(r.get('_PID')==before['MainPID'] and r.get('_UID')==uid for r in vendor))
 result=broker_witness(before,after,raw);save('broker-vendor.private.jsonl',raw)
 pid1=command(['/usr/bin/journalctl','--boot','_PID=1','UNIT=artemis.service','-o','json','--no-pager'])
 rows=[json.loads(r,object_pairs_hook=unique) for r in pid1.splitlines()]
 ended=[r for r in rows if r.get('INVOCATION_ID')==before['InvocationID'] and r.get('MESSAGE_ID')=='9d1aaa27d60140bd96365438aad20286']
 require(len(ended)==1)
 e=ended[0];require(e.get('_BOOT_ID')==BOOT.replace('-','') and e.get('_UID')=='0' and e.get('_COMM')=='systemd'
  and e.get('JOB_TYPE')=='stop' and e.get('JOB_RESULT')=='done' and int(e['__MONOTONIC_TIMESTAMP'])>=int(after['ExecMainExitTimestampMonotonic']))
 save('broker-manager.private.jsonl',pid1);save('broker-witness.private.json',json.dumps(result,sort_keys=True).encode())
def all_terminal():
 cohort();return {u:show(u,FIELDS) for u in UNITS}
def canonical_invalid(raw):
 require(isinstance(raw,bytes) and len(raw)<2048)
 lines=raw.decode('ascii').splitlines(keepends=True)
 require(len(lines)==8 and lines[0]=='NKEPOCH1\n' and lines[1]=='state=ISSUED\n'
  and [v.split('=',1)[0] for v in lines[2:]]==['boot_id','epoch_id','run_id','cutoff_utc','activation_id','permit_sha256']
  and all(v.endswith('\n') for v in lines))
 require(len(lines[-1])==79 and all(c in '0123456789abcdef' for c in lines[-1][14:-1]))
 # Independent SS343 textual vector, not production serializer.
 return (lines[0]+'state=INVALID\n'+''.join(lines[2:-1])+'permit_sha256=-\n').encode('ascii')
def execute():
 global backend,baseline,owner,revoked_phase,invalid_hash,invalid_length
 require(os.geteuid()==0 and len(sys.argv)==2 and sys.argv[1].isdigit());os.umask(0o077)
 load_definitions();raw=BASE.read_bytes();require(hashlib.sha256(raw).hexdigest()==BASE_HASH);baseline=json.loads(raw)
 require(set(baseline)=={'units','rows','trees','configuration'})
 original_raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg505-parent-failure-v1/observed.private.json').read_bytes()
 require(hashlib.sha256(original_raw).hexdigest()=='d60070bd92c13b10b129e2793edb39a2436dad730e3dae6d4d7733c5e5ffd21d')
 original=json.loads(original_raw)
 require(baseline['rows']==original['rows'] and baseline['trees']==original['trees'])
 receipt=pathlib.Path('/var/lib/pgpt-s1-preservation/pg516-terminal-issued-handoff-v1/complete.private.json').read_bytes()
 require(hashlib.sha256(receipt).hexdigest()=='d1609b932980f852f94149e8f0726fdae8959b717ba03f33b882a22c1cb6b2ad')
 require(json.loads(receipt)=={'ownedChildThenJavaTERM':True,'rawUnchangedTwice':True,'currentStillIssued':True,'businessCohortUnchanged':True,'peersLocks0':True,'oldCloseUNKNOWN':True,'businessActions0':True})
 for leaf,digest in {'broker-vendor.private.jsonl':'80a915f03aaccd50cf00615113e50aa1b4e54219eb79af36a9b523d5dbf5d33b','broker-manager.private.jsonl':'87ab69fec569541ea8b76118e4692a4b03fdc7dcbc50e91557fa81614b9b3889','broker-witness.private.json':'1c697a99098f72a985ea657e91968e6f636a004ab1314d7b7e1feac444f21ddb'}.items():
  require(hashlib.sha256(pathlib.Path('/var/lib/pgpt-s1-preservation/pg516-terminal-issued-handoff-v1',leaf).read_bytes()).hexdigest()==digest)
 require(all(not pathlib.Path('/proc',str(pid)).exists() for pid in [310706,310735]))
 namespace_failure_proof()
 revoked_phase=False
 raw_current=pathlib.Path(STARTUP+'/epoch.current').read_bytes()
 require(hashlib.sha256(raw_current).hexdigest()=='87a7556e280c58a61d1390d69f5ecde78c430fd807f8a025c401af8bd17dd21e')
 invalid=canonical_invalid(raw_current);invalid_hash=hashlib.sha256(invalid).hexdigest();invalid_length=len(invalid)
 save('issued-current.private',raw_current);save('expected-invalid.private',invalid)
 backend=int(sys.argv[1]);owner=holder();identity()
 bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
 for u in UNITS:manager.RefUnit(u)
 require({u:show(u,FIELDS) for u in UNITS}==baseline['units']);cohort()
 v=values();require(v==values());save('before.private.json',json.dumps(v,sort_keys=True).encode())
 print('REF_READY',flush=True)
 retired=False
 for rawline in sys.stdin.buffer:
  action=rawline.rstrip(b'\n').decode('ascii');require(action in ['before','terminal','ownership','revoked','retired','release'])
  if action=='release':
   require(retired);identity();require(holder(True)==owner);all_terminal()
   # DB has closed. Full originals were independently captured before close; reread rows via RO.
   original_holder=holder
   globals()['holder']=lambda released=False: original_holder(True)
   v=values();require(v==values());save('after.private.json',json.dumps(v,sort_keys=True).encode())
   for u in reversed(UNITS):manager.UnrefUnit(u)
   bus.close();print('REF_RELEASED',flush=True);return
  require(holder()==owner);identity()
  if action=='before':require({u:show(u,FIELDS) for u in UNITS}==baseline['units']);v=values();require(v==values())
  elif action=='ownership':pass
  else:
   if action=='revoked':
    require(not revoked_phase);revoked_phase=True
   all_terminal();v=values();require(v==values())
   if action=='retired':
    require(not any(p.endswith('.API.start.intent') for p in v['trees'][STARTUP]));retired=True
    save('retired.private.json',json.dumps(v,sort_keys=True).encode())
  print('REF_CHECKED',flush=True)
 raise ValueError('owned channel ended')
if __name__=='__main__':
 try:execute()
 except Exception as failure:
  import traceback
  print('REF_FAILED',flush=True);print('PG517_REF_UNKNOWN type='+type(failure).__name__,file=sys.stderr,flush=True)
  for f in traceback.extract_tb(failure.__traceback__):
   if f.filename==__file__:print('PG517_FRAME method='+f.name+' line='+str(f.lineno),file=sys.stderr,flush=True)
  while True:time.sleep(1)
