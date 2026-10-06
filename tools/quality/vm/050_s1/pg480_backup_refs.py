"""SSC198 fixed interrupted Backup witness and continuous private metadata sender.
No service/DB/request mutation. Raw snapshots are Root private; replies contain no material.
"""
import ast,hashlib,json,os,pathlib,stat,subprocess,sys,time
import dbus
TOOLS=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3')
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-recovery-v3')
BOOT='e07aa706-1acd-4e65-b309-d7f330f79d54'
RUN='49437eda-1681-43a9-883a-424eb55a6166'
PARENT='795eec6b633244148b40b26d0251a8ed'
BACKUP='e5a9480ba99847779d30d3c4a321284d'
UNITS=['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service','schubert-nk-morning-controller.service','schubert-nk-bootstrap-admin.service']
FIELDS=set('Id,LoadState,ActiveState,SubState,MainPID,ControlPID,Job,InvocationID,ExecMainCode,ExecMainStatus,Result,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,KillMode,SendSIGKILL,Restart,Type,RemainAfterExit'.split(','))
MARKER='/run/schubert-nk/backup-request/backup-start.intent'
def require(v):
 if not v:raise ValueError('fixed Backup recovery witness refused')
def command(args,limit=33554432):
 p=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=30)
 require(p.returncode==0 and len(p.stdout)<=limit);return p.stdout
def show(unit,fields):
 require(unit in UNITS);v={}
 for row in command(['/usr/bin/systemctl','show',unit,'--property='+','.join(sorted(fields))],1048576).decode('utf-8').splitlines():
  k,s=row.split('=',1);require(k not in v);v[k]=s
 require(set(v)==fields);return v
def metadata(p):
 s=p.lstat();require(stat.S_ISREG(s.st_mode) or stat.S_ISDIR(s.st_mode))
 return [s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
def tree(root):
 result={}
 for p in [root,*sorted(root.rglob('*'))]:
  m=metadata(p);h=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
  require(m==metadata(p));result[str(p)]={'metadata':m,'sha256':h}
 return result
def strict(p,mode,limit):
 m=metadata(p);require(m[2:6]==[0,0,stat.S_IFREG|mode,1] and 0<=m[6]<=limit and 'system.posix_acl_access' not in os.listxattr(p))
 raw=p.read_bytes();require(m==metadata(p));return raw
def owner():
 pid=os.getppid();p=pathlib.Path('/proc')/str(pid);args=(p/'cmdline').read_bytes().split(b'\0')
 require(args[0]==b'/opt/jdk-25.0.4/bin/java' and args[-3:]==[b'Pg480BackupRecovery',sys.argv[1].encode(),b''])
 ticks=int((p/'stat').read_text().rpartition(')')[2].split()[19]);paths=[]
 for fd in (p/'fd').iterdir():
  try:paths.append(str(fd.readlink()))
  except FileNotFoundError:continue
 for name in ['maintenance.lock','startup-admission.lock']:
  path=pathlib.Path('/run/schubert-nk')/name;strict(path,0o600,0);s=path.lstat();require(str(path) in paths)
  found=[]
  for row in pathlib.Path('/proc/locks').read_text().splitlines():
   f=row.split()
   if len(f)>=8 and f[1:5]==['FLOCK','ADVISORY','WRITE',str(pid)]:
    d=f[5].split(':')
    if len(d)==3 and tuple(int(x,16) for x in d[:2])+(int(d[2]),)==(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino):found.append(row)
  require(len(found)==1)
 return pid,ticks
def rows():
 sql="begin isolation level repeatable read read only; set local timezone='UTC';"
 for t in previous['rows']:sql+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from (select to_jsonb(t) j from "+t+" t) q;"
 sql+='commit;';v={}
 for row in command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-q','-A','-t','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql]).splitlines():
  j=json.loads(row);require(j['table'] not in v);v[j['table']]=j['rows']
 require(v==previous['rows']);return v
def locked_database():
 sql="select count(*) from pg_catalog.pg_stat_activity a where a.pid="+str(backend)+" and a.usename='schubert_batch' and a.datname='schubert_nk' and a.application_name='PG480-fixed-recovery' and exists(select 1 from pg_catalog.pg_locks l where l.pid=a.pid and l.locktype='advisory' and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.granted); select count(*) from pg_catalog.pg_stat_activity where datname='schubert_nk' and usename in ('schubert_batch','schubert_api','schubert_web','schubert_inspector') and pid<>"+str(backend)+";"
 out=command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-q','-A','-t','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],4096).splitlines()
 require(out==[b'1',b'0'])
def kernel(unit):
 p=pathlib.Path('/sys/fs/cgroup/system.slice')/unit
 if p.exists():
  for d in [p,*[x for x in p.rglob('*') if x.is_dir()]]:require(not (d/'cgroup.procs').read_text().strip() and 'populated 0\n' in (d/'cgroup.events').read_text())
def configuration_fields():
 return set('ExecStart,DropInPaths,ReadWritePaths,User,Group,SupplementaryGroups,NoNewPrivileges,ProtectSystem,ProtectHome,PrivateTmp,PrivateDevices,RestrictSUIDSGID,CapabilityBoundingSet,AmbientCapabilities,UMask,LimitCORE,TimeoutStartUSec,TimeoutStopUSec,MemoryMax,TasksMax'.split(','))
def approved_configuration(unit,conf):
 import re
 directory=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-stopped-tools-v3')
 policy=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/pg477_unit_references.py')
 require(hashlib.sha256(policy.read_bytes()).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
 source=ast.parse(policy.read_text());names=['exec_record','after_exec','same_declaration','signed_declaration','effective_rw']
 definitions=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in names];require(len(definitions)==5)
 env={'re':re};exec(compile(ast.Module(body=definitions,type_ignores=[]),'<fixed configuration policy>','exec'),env)
 # This immutable old policy expected no newer startup. Here declaration alone is compared;
 # exact real auxiliary history remains separately bound to full18 and PID1 receipts below.
 env['after_exec']=lambda value:env['exec_record'](value) is not None
 old=json.loads((directory/'refs-activate-before.private.json').read_text())['configuration'][unit]
 allowed={'ExecStart','DropInPaths','ReadWritePaths'} if unit in ['schubert-nk-inbox-inspector.service','schubert-nk-bootstrap-admin.service','schubert-nk-morning-controller.service'] else {'ExecStart'}
 require(all(conf[k]==old[k] for k in CONFIG-allowed) and env['signed_declaration'](unit,old['ExecStart'],conf['ExecStart']))
 if len(allowed)>1:
  require(env['effective_rw'](unit,old['ReadWritePaths'],conf['ReadWritePaths']))
  require(conf['DropInPaths']==('/etc/systemd/system/'+unit+'.d/pg477-native-coverage.conf' if 'morning' in unit else ''))
def epoch_ok(epoch):
 return (isinstance(epoch,bytes) and epoch.startswith(b'NKEPOCH1\n') and b'state=INVALID\n' in epoch and ('run_id='+RUN+'\n').encode() in epoch and b'cutoff_utc=2026-10-06T06:28:43.734078Z\n' in epoch and b'permit_sha256=-\n' in epoch)
def request_ok(request):
 return isinstance(request,bytes) and request.startswith(('NKBACKUP1\nrun='+RUN+'\nstarted=').encode()) and request.endswith(b'\n') and len(request.splitlines())==3
def pending_rows(values):
 return (isinstance(values,list) and len(values)==2 and {r.get('step') for r in values}=={'BACKUP_DB','BACKUP_CONFIG'} and all(r.get('run_id')==RUN and r.get('status')=='RUNNING' and r.get('ended_at') is None and all(r.get(k)==0 for k in ['target_count','success_count','failure_count','byte_count']) and r.get('error_code') is None and r.get('error_summary') is None for r in values))
def marker_namespace_ok(names,phase):
 if phase not in ['OBSERVING','BEFORE_RETIRE','RETIRING','RETIRED','REISOLATING','QUARANTINED']:return False
 if names not in [{'backup-request'},{'backup-request','backup-start.intent'}]:return False
 marked='backup-start.intent' in names
 return marked if phase in ['OBSERVING','BEFORE_RETIRE','QUARANTINED'] else not marked if phase=='RETIRED' else True
def snapshot(phase,database_required=True):
 require(owner()==held and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT and not pathlib.Path('/proc/3418691').exists())
 units={};conf={}
 for unit in UNITS:
  v=show(unit,FIELDS);require(v['LoadState']=='loaded' and v['Id']==unit and v['MainPID']==v['ControlPID']=='0' and not v['Job']);kernel(unit);require(v==show(unit,FIELDS));units[unit]=v;conf[unit]=show(unit,CONFIG);approved_configuration(unit,conf[unit])
 require(units==previous['units'])
 parent=units['schubert-nk-morning-controller.service'];worker=units['schubert-nk-backup.service']
 require(parent['InvocationID']==PARENT and parent['Result']=='timeout' and parent['ExecMainCode']=='1' and parent['ExecMainStatus']=='143')
 require(worker['InvocationID']==BACKUP and worker['Result']=='success' and worker['ExecMainCode']=='1' and worker['ExecMainStatus']=='0')
 journal=[json.loads(r) for r in command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'-u','schubert-nk-backup.service','--since','2026-10-06 06:28:40 UTC','--until','2026-10-06 06:29:00 UTC','-o','json','--no-pager'],1048576).splitlines()]
 for kind,job,message in [('start','253068','39f53479d3a045ac8e11786248231fbf'),('stop','253215','9d1aaa27d60140bd96365438aad20286')]:
  matches=[r for r in journal if r.get('_PID')=='1' and r.get('UNIT')=='schubert-nk-backup.service' and r.get('INVOCATION_ID')==BACKUP and r.get('JOB_TYPE')==kind and r.get('JOB_ID')==job and r.get('JOB_RESULT')=='done' and r.get('MESSAGE_ID')==message]
  require(len(matches)==1)
 if database_required:locked_database()
 else:
  require(command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-q','-A','-t','-d','schubert_nk','-c',"select count(*) from pg_stat_activity where datname='schubert_nk' and usename in ('schubert_batch','schubert_api','schubert_web','schubert_inspector'); select count(*) from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and granted;"],4096).splitlines()==[b'0',b'0'])
 db=rows()
 original=tree(pathlib.Path('/var/lib/schubert-nk/maintenance'));backup=tree(pathlib.Path('/srv/schubert-nk/backup'));transfer=tree(pathlib.Path('/srv/schubert-nk/data/transfer'))
 require(original==previous['original'] and backup==previous['backup'] and transfer==previous['transfer'])
 startup=tree(pathlib.Path('/run/schubert-nk/startup'))
 require(len(startup)==66 and not any(p.endswith('.intent') for p in startup))
 epoch=strict(pathlib.Path('/run/schubert-nk/startup/epoch.current'),0o600,1024)
 require(epoch_ok(epoch))
 requestroot=pathlib.Path('/run/schubert-nk/backup-request');names=set(p.name for p in requestroot.iterdir());marked='backup-start.intent' in names
 require(marker_namespace_ok(names,phase))
 request=strict(requestroot/'backup-request',0o600,400)
 require(request_ok(request))
 if marked:require(strict(requestroot/'backup-start.intent',0o600,0)==b'')
 require(command(['/usr/bin/stat','-f','-c','%T',str(requestroot)],1024)==b'tmpfs\n')
 for p in ['/run/schubert-nk/cleanup-request','/run/schubert-nk/expiry-request']:
  require(not list(pathlib.Path(p).iterdir()))
 native=tree(pathlib.Path('/run/schubert-nk/pt-coverage'))
 config=tree(pathlib.Path('/etc/schubert-nk'))
 # No raw bytes or credentials leave this private witness. Approval/link are fixed old release.
 require(pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG477'))
 pending=[r for r in db['schubert.batch_runs'] if r['run_id']==RUN]
 require(pending_rows(pending))
 return {'units':units,'configuration':conf,'rows':db,'original':original,'backup':backup,'transfer':transfer,'startup':startup,'native':native,'config':config,'request':{'sha256':hashlib.sha256(request).hexdigest(),'metadata':metadata(requestroot/'backup-request')}}
def same(actual):require(actual==before)
phase='PREFLIGHT';bus=None;refs=[]
try:
 require(os.geteuid()==0 and len(sys.argv)==3 and sys.argv[1] in ['verify','retire'] and sys.argv[2].isdigit());backend=int(sys.argv[2]);require(backend>1)
 os.umask(0o077);require(not SAVE.exists());SAVE.mkdir(mode=0o700)
 previous=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg479-archive-diagnosis/after-terminal.private.json').read_text());CONFIG=configuration_fields();held=owner()
 bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
 phase='REF_ACQUIRE'
 for unit in UNITS:manager.RefUnit(unit);refs.append(unit)
 before=snapshot('OBSERVING');target=SAVE/'before.private.json'
 with target.open('x') as f:os.fchmod(f.fileno(),0o600);json.dump(before,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
 print('REF_READY',flush=True)
 for line in sys.stdin.buffer:
  name=line.rstrip(b'\n').decode('ascii');require(name in ['OBSERVING','BEFORE_RETIRE','RETIRING','RETIRED','REISOLATING','QUARANTINED','release'])
  phase=name
  if name=='release':
   # Caller has closed DB; dedicated readback above is repeated before that close.
   same(snapshot('RETIRED' if sys.argv[1]=='retire' else 'BEFORE_RETIRE',False))
   for unit in UNITS:require(show(unit,FIELDS)==before['units'][unit]);kernel(unit)
   for unit in reversed(refs):manager.UnrefUnit(unit)
   bus.close();print('REF_RELEASED',flush=True);sys.exit(0)
  same(snapshot(name));print('REF_CHECKED',flush=True)
 raise ValueError('owner channel ended early')
except Exception as failure:
 import traceback
 print('PG480_REFERENCE_FAILURE type='+type(failure).__name__,file=sys.stderr,flush=True)
 for frame in traceback.extract_tb(failure.__traceback__):
  if frame.filename==__file__:print('PG480_REFERENCE_FRAME method='+frame.name+' line='+str(frame.lineno),file=sys.stderr,flush=True)
 print('REF_FAILED',flush=True);print('PG480_REFERENCE_UNKNOWN phase='+phase+' ownerRetained=true',file=sys.stderr,flush=True)
 while True:time.sleep(1)
