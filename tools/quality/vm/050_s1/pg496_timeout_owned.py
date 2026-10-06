"""SSC204 / REC204: ONLY PG493 timeout143, no intents, fresh enclosing M/A/DB.
No start, deployment, fabricated Pair, DONE or old ownership normalization.
Full evidence is Root-private. This module has no import-time VM operations.
"""
import ast,hashlib,json,os,pathlib,shutil,stat,subprocess,sys

ROOT=pathlib.Path('/var/lib/pgpt-s1-preservation/pg496-timeout-no-intents-v1')
BOOT='e07aa706-1acd-4e65-b309-d7f330f79d54'
PARENT='52accf6d68f44487b6e0b3635c20396f'
ORDER=['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service']
EXTRA=['schubert-nk-morning-controller.service','schubert-nk-bootstrap-admin.service']
FIELDS=set('Id,LoadState,ActiveState,SubState,MainPID,ControlPID,Job,InvocationID,ExecMainCode,ExecMainStatus,Result,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,KillMode,SendSIGKILL,Restart,Type,RemainAfterExit'.split(','))
EXPECTED={'caddy.service':('4113865','b656fdfe067a4cb8a542708750af019c',25667027),
 'schubert-nk-web.service':('4108080','1dedba9e9ee648fb94eca6232385e018',25663790),
 'schubert-nk-api.service':('4105598','730085ab1173444b83c9bf2c8127c94e',25662174),
 'artemis.service':('3939714','12360e619aa7445684692c59badc7c51',25552139)}
PINS={'pg481_native_owned_stop.py':'99b24d0b0169fd8e7c6075f01096b6efeedaa953ee759e63eaa0e33f64fcb865',
 'pg480_backup_refs.py':'0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7',
 'pg466_term_witness.py':'e257ac5b9dea23ba91f68231717ee787b839f5d08d95fd67d62ac3c20b568a78',
 'pg471_native_term_witness.py':'f6b800cb5597ebfd7348e172f09b708d3813b991f7452ae1c938e9d2fa3866d1'}
def require(value):
 if not value:raise ValueError('fixed timeout recovery refused')
def parent_value(v):
 return isinstance(v,dict) and set(v)==FIELDS and all(isinstance(x,str) for x in v.values()) and v['Id']=='schubert-nk-morning-controller.service' and v['LoadState']=='loaded' and v['InvocationID']==PARENT and v['Result']=='timeout' and v['ExecMainCode']=='1' and v['ExecMainStatus']=='143' and v['ActiveState']==v['SubState']=='failed' and v['MainPID']==v['ControlPID']=='0' and v['Job']=='' and v['ExecMainStartTimestampMonotonic']=='255346663838'
def epoch_value(raw,invalid):
 if not isinstance(raw,bytes) or not raw.endswith(b'\n'):return False
 fields={}
 try:
  lines=raw.decode('ascii').splitlines()
  if not lines or lines[0]!='NKEPOCH1':return False
  for line in lines[1:]:
   k,v=line.split('=',1)
   if k in fields:return False
   fields[k]=v
 except (ValueError,UnicodeError):return False
 digest=fields.get('permit_sha256','')
 return set(fields)=={'state','boot_id','epoch_id','run_id','cutoff_utc','activation_id','permit_sha256'} and fields['state']==('INVALID' if invalid else 'ISSUED') and fields['boot_id']==BOOT and fields['epoch_id']=='4d35762d-54b4-4187-ab03-cc9b7e9e3baf' and fields['run_id']=='91a748b4-1abe-484c-9682-44f46429b324' and fields['activation_id']=='179758d2-5b77-443a-a743-bf0065e732ea' and fields['cutoff_utc']=='2026-10-06T12:06:14.564793Z' and (digest=='-' if invalid else len(digest)==64 and all(c in '0123456789abcdef' for c in digest))
def command(args):
 r=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=30)
 require(r.returncode==0 and len(r.stdout)<=33554432);return r.stdout
def show(unit):
 require(unit in ORDER+EXTRA);v={}
 for line in command(['/usr/bin/systemctl','show',unit,'--property='+','.join(sorted(FIELDS))]).decode('ascii').splitlines():
  k,value=line.split('=',1);require(k not in v);v[k]=value
 require(set(v)==FIELDS and v['Id']==unit and v['LoadState']=='loaded');return v
def tick(pid):return int((pathlib.Path('/proc')/str(pid)/'stat').read_text().rpartition(')')[2].split()[19])
def holder():
 pid=os.getppid();p=pathlib.Path('/proc')/str(pid);argv=(p/'cmdline').read_bytes().split(b'\0')
 require(argv[0]==b'/opt/jdk-25.0.4/bin/java' and argv[-3]==b'Pg496TimeoutRecovery' and argv[-2] in (b'verify',b'recover') and argv[-1]==b'')
 for name in ('maintenance.lock','startup-admission.lock'):
  target=pathlib.Path('/run/schubert-nk')/name;s=target.lstat()
  require(stat.S_ISREG(s.st_mode) and stat.S_IMODE(s.st_mode)==0o600 and s.st_uid==s.st_gid==0 and s.st_nlink==1 and 'system.posix_acl_access' not in os.listxattr(target))
  links=[]
  for fd in (p/'fd').iterdir():
   try:links.append(str(fd.readlink()))
   except FileNotFoundError:continue
  require(str(target) in links);matches=[]
  for row in pathlib.Path('/proc/locks').read_text().splitlines():
   f=row.split()
   if len(f)>=8 and f[1:5]==['FLOCK','ADVISORY','WRITE',str(pid)]:
    d=f[5].split(':')
    if len(d)==3 and (int(d[0],16),int(d[1],16),int(d[2]))==(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino):matches.append(row)
  require(len(matches)==1)
 sql="select count(*) from pg_catalog.pg_stat_activity a where a.usename='schubert_batch' and a.datname='schubert_nk' and a.application_name='PG496-fixed-recovery' and exists(select 1 from pg_catalog.pg_locks l where l.pid=a.pid and l.locktype='advisory' and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.granted)"
 require(command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql]).strip()==b'1')
 return pid,tick(pid)
def kernel_empty(unit):
 c=pathlib.Path('/sys/fs/cgroup/system.slice')/unit
 if c.exists():
  for p in [c,*[x for x in c.rglob('*') if x.is_dir()]]:require(not (p/'cgroup.procs').read_text().strip() and 'populated 0\n' in (p/'cgroup.events').read_text())
def save(name,data):
 require('/' not in name)
 with (ROOT/name).open('xb') as f:os.fchmod(f.fileno(),0o600);f.write(data);f.flush();os.fsync(f.fileno())
 fd=os.open(ROOT,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
def load_definitions():
 here=pathlib.Path(__file__).parent
 for name,digest in PINS.items():require(hashlib.sha256((here/name).read_bytes()).hexdigest()==digest)
 # Copy only pure read-only metadata functions, never old recovery main/authorization.
 wanted={'metadata','tree','configuration_fields'};source=ast.parse((here/'pg480_backup_refs.py').read_text())
 definitions=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in wanted];require(len(definitions)==3)
 exec(compile(ast.Module(body=definitions,type_ignores=[]),'<pinned readonly metadata>','exec'),globals())
def baseline():return json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg493-parent-failure-v1/observed.private.json').read_text())
def rows():
 sql="begin isolation level repeatable read read only;set local timezone='UTC';";result={}
 tables=list(baseline()['rows']);require(len(tables)==24)
 for table in tables:
  require(all(c.isalnum() or c in '_.' for c in table))
  sql+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from (select to_jsonb(t) j from "+table+" t) q;"
 for line in command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql+'commit;']).splitlines():
  v=json.loads(line);require(v['table'] not in result);result[v['table']]=v['rows']
 require(set(result)==set(tables) and len(result['schubert.batch_runs'])==442);return result
def snapshot():
 previous=baseline();roots=[x for x in previous['trees'] if x!='/run/schubert-nk/pt-coverage']
 return {'rows':rows(),'trees':{x:tree(pathlib.Path(x)) for x in roots},'configuration':{u:configuration(u) for u in ORDER+EXTRA}}
def configuration(unit):
 fields=configuration_fields();value={}
 for line in command(['/usr/bin/systemctl','show',unit,'--property='+','.join(sorted(fields))]).decode().splitlines():
  k,v=line.split('=',1);require(k not in value);value[k]=v
 require(set(value)==fields);return value
def actor(unit,value):
 p=pathlib.Path('/proc')/value['MainPID'];status={k:v.strip() for k,v in (r.split(':',1) for r in (p/'status').read_text().splitlines() if ':' in r)}
 a={'pid':value['MainPID'],'invocation':value['InvocationID'],'ticks':tick(value['MainPID']),
  'authority':{k:status[k] for k in ['Uid','Gid','Groups','CapInh','CapPrm','CapEff','CapBnd','CapAmb','NoNewPrivs']},
  'cgroup':(p/'cgroup').read_text(),'argvSha256':hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()}
 require(a==baseline()['actors'][unit] and (a['pid'],a['invocation'],a['ticks'])==EXPECTED[unit] and a['cgroup']=='0::/system.slice/'+unit+'\n');return a
def parent():
 require(parent_value(show(EXTRA[0])) and not pathlib.Path('/proc/3905484').exists());kernel_empty(EXTRA[0])
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT and pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG489'))
def verify_live():
 owner=holder();parent();units={u:show(u) for u in ORDER+EXTRA}
 require({u:configuration(u) for u in units}==baseline()['configuration'])
 for u,v in units.items():
  if u in EXPECTED:require(v['ActiveState']=='active' and v['SubState']=='running' and v['Result']=='success' and v['Job']=='' and v['ControlPID']=='0');actor(u,v)
  else:require(v==baseline()['units'][u] and v['MainPID']==v['ControlPID']=='0' and v['Job']=='');kernel_empty(u)
  require(v==show(u))
 require(owner==holder());return units
def stop_one(unit):
 from pg481_native_owned_stop import same_generation,normal_terminal,broker_witness
 from pg471_native_term_witness import witness
 require(unit in ORDER);index=ORDER.index(unit)
 require(all((ROOT/(p+'.stopped.private')).is_file() for p in ORDER[:index]))
 owner=holder();parent();before=json.loads((ROOT/'units-before.private.json').read_text())[unit];current=show(unit);issued=False
 if unit in EXPECTED:
  require(current==before);actor(unit,current);require(holder()==owner)
  save(unit+'.stop-reserved.private',b'oneOwnedStop=true\n')
  result=subprocess.run(['/usr/bin/systemctl','stop',unit],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=120)
  require(result.returncode==0);issued=True;current=show(unit)
 elif current['ActiveState']=='active' and current['SubState']=='exited':
  require(current==before);save(unit+'.stop-reserved.private',b'oneOwnedStop=true\n')
  result=subprocess.run(['/usr/bin/systemctl','stop',unit],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=120)
  require(result.returncode==0);issued=True;current=show(unit)
 require(same_generation(before,current) and current['MainPID']==current['ControlPID']=='0' and current['Job']=='');kernel_empty(unit)
 if unit in EXPECTED:require(not (pathlib.Path('/proc')/before['MainPID']).exists())
 if unit in ('schubert-nk-api.service','schubert-nk-web.service','artemis.service'):
  raw=command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_SYSTEMD_INVOCATION_ID='+before['InvocationID'],'-o','json','--no-pager']);save(unit+'.full-journal.private.jsonl',raw)
  data=broker_witness(before,current,raw) if unit=='artemis.service' else witness('API' if 'api' in unit else 'WEB',before,current,raw,before['MainPID'],'999' if 'api' in unit else '997')
  save(unit+'.witness.private.json',json.dumps(data,sort_keys=True).encode())
 else:require(normal_terminal(before,current))
 require(current==show(unit) and owner==holder());save(unit+'.stopped.private',json.dumps(current,sort_keys=True).encode())
 print('PG496_OWNED_STOP unit='+unit+' issued='+str(issued).lower()+' sameGeneration=true kernelEmpty=true oldCloseNotInferred=true')
def main():
 require(os.geteuid()==0 and len(sys.argv)==2);load_definitions();action=sys.argv[1]
 require(action in ['verify','capture','terminal','revoked']+['stop:'+u for u in ORDER]);parent();holder()
 for target in ['timers.target','paths.target']:require(command(['/usr/bin/systemctl','show',target,'--property=LoadState']).strip()==b'LoadState=masked')
 if action=='verify':verify_live();return
 require(ROOT.is_dir() and not ROOT.is_symlink() and ROOT.stat().st_uid==ROOT.stat().st_gid==0 and stat.S_IMODE(ROOT.stat().st_mode)==0o700)
 if action=='capture':
  units=verify_live();data=snapshot();require(data==snapshot());save('units-before.private.json',json.dumps(units,sort_keys=True).encode());save('snapshot-before.private.json',json.dumps(data,sort_keys=True).encode())
  for source,target in [('/run/schubert-nk/pt-coverage','native-before'),('/run/schubert-nk/startup','startup-before')]:
   shutil.copytree(source,ROOT/target,symlinks=True)
   for p in [ROOT/target,*(ROOT/target).rglob('*')]:
    require(not p.is_symlink());os.chmod(p,0o700 if p.is_dir() else 0o600)
    if p.is_file():
     with p.open('rb') as f:os.fsync(f.fileno())
   if target=='startup-before':
    require({p.name for p in (ROOT/target).iterdir()}=={p.name for p in pathlib.Path(source).iterdir()})
    for p in (ROOT/target).iterdir():require(p.is_file() and p.read_bytes()==(pathlib.Path(source)/p.name).read_bytes())
  require(data==snapshot() and units==verify_live())
  fd=os.open(ROOT,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
  try:os.fsync(fd)
  finally:os.close(fd)
  return
 if action.startswith('stop:'):stop_one(action[5:]);return
 require(all((ROOT/(u+'.stopped.private')).is_file() for u in ORDER))
 for u in ORDER+EXTRA:
  v=show(u);require(v['MainPID']==v['ControlPID']=='0' and v['Job']=='');kernel_empty(u)
 before=json.loads((ROOT/'snapshot-before.private.json').read_text());actual=snapshot()
 if action=='revoked':
  require(epoch_value(pathlib.Path('/run/schubert-nk/startup/epoch.current').read_bytes(),True))
  # Only canonical epoch.current contents/inode may change; every other raw tree entry remains exact.
  startup='/run/schubert-nk/startup';leaf=startup+'/epoch.current'
  require(set(actual['trees'][startup])==set(before['trees'][startup]))
  for tree_name in (startup,leaf):actual['trees'][startup][tree_name]=before['trees'][startup][tree_name]
 require(before==actual)
 save(action+'.private.json',json.dumps({'allTenKernelEmpty':True,'all24TablesPreserved':True,'intentsRetired':0,'oldCloseNotInferred':True},sort_keys=True).encode())
if __name__=='__main__':main()
