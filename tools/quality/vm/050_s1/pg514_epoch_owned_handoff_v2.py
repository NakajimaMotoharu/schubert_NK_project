"""SSC210/BUG817: fixed pre-stop PG513 owner only. Never stops a business Unit."""
import ast,hashlib,importlib.util,json,os,pathlib,signal,time
PID=309605;TICKS=995739;CHILD=309634;CHILD_TICKS=995850
BOOT='cc9ed874-7f4f-450e-a188-8de1e42c8441'
ARGV='cee2b64efddd54fbbd7c72c48306d6a505c0a7f7d76bfd2e99ae39fbb11782c3'
CHILD_ARGV='ebc1706cca5d81f5d45c802e3ca368ce28ac549d1549cd431d0c2c57d42d5357'
TOOLS=pathlib.Path('/var/lib/pgpt-s1-preservation/pg513-single-api-tools-v7')
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg514-issued-owned-handoff-v2')
PINS={'Pg513SingleApiRecovery.class':'f403c18ce569817d53dbcf32f6be60675555bec7b74c58d53d9ba8b853f7a1a7',
 'Pg513SingleApiRecovery$References.class':'db665007a7aa47d31a50682c19bde64a7ae0527e9c262d7e14008d02c93d6c5a',
 'dev/codex/schubert/nk/batch/file/Pg513SingleApiIntent.class':'c68eb211f959499950f51e93775834a3c3c76d37a848247f3bfc781ef59c37ae',
 'dev/codex/schubert/nk/batch/file/Pg513SingleApiIntent$Gate.class':'485b5ea07540f6a93036ca203e7e506a2d90e61e790075f536176a129e8b68ab',
 'pg513_single_api_refs.py':'e4cb72980da0fdc1a1cb55c8f046534e666b191b3e04bb457bfd5610d0260c62',
 'pg513_confirm_ma.py':'6d22c2ce87fd334d0a27eb69b207d9d2ddcae212efc12bc653d1d8da8dad19db'}
def require(value):
 if not value:raise ValueError('fixed issued pre-stop handoff refused')
def identity(value,pid,ticks,argv,parent=None):
 return (isinstance(value,dict) and set(value)=={'pid','ticks','argv','uid','parent','children'}
  and type(value['pid']) is int and value['pid']==pid and type(value['ticks']) is int and value['ticks']==ticks
  and value['argv']==argv and value['uid']==['0']*4 and type(value['parent']) is int
  and (parent is None or value['parent']==parent) and isinstance(value['children'],set)
  and all(type(c) is int and c>1 for c in value['children']))
def process(pid):
 p=pathlib.Path('/proc')/str(pid);s=(p/'stat').read_text().rpartition(')')[2].split()
 value={'pid':pid,'ticks':int(s[19]),'parent':int(s[1]),'argv':hashlib.sha256((p/'cmdline').read_bytes()).hexdigest(),
  'uid':(p/'status').read_text().split('Uid:')[1].splitlines()[0].split(),
  'children':{int(c) for t in (p/'task').iterdir() for c in (t/'children').read_text().split()}}
 require(value['ticks']==int((p/'stat').read_text().rpartition(')')[2].split()[19]));return value
def owner(child_alive):
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
 v=process(PID);require(identity(v,PID,TICKS,ARGV) and v['children']==({CHILD} if child_alive else set()))
 if child_alive:
  child=process(CHILD);require(identity(child,CHILD,CHILD_TICKS,CHILD_ARGV,PID) and not child['children'])
 locks=pathlib.Path('/proc/locks').read_text().splitlines();links=set()
 for fd in (pathlib.Path('/proc')/str(PID)/'fd').iterdir():
  try:links.add(str(fd.readlink()))
  except FileNotFoundError:pass
 for name,expected in lock_baseline.items():
  p=pathlib.Path('/run/schubert-nk')/name;m=h.metadata(p);require(m==expected and str(p) in links)
  hits=[]
  for line in locks:
   f=line.split()
   if len(f)>=8 and f[1:5]==['FLOCK','ADVISORY','WRITE',str(PID)]:
    d=f[5].split(':')
    if len(d)==3 and (int(d[0],16),int(d[1],16),int(d[2]))==(os.major(m[0]),os.minor(m[0]),m[1]):hits.append(line)
  require(len(hits)==1)
def raw():
 h.identity();units={u:h.show(u,h.FIELDS) for u in h.UNITS};require(units==baseline['units'])
 release=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG495')
 require(hashlib.sha256(release.joinpath('RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44')
 require('ro' in h.command(['/usr/bin/findmnt','--target',str(release),'--output','OPTIONS','--noheadings']).decode().strip().split(','))
 for u in units:
  if u=='artemis.service':h.actor(u,units[u])
  else:h.kernel(u)
 require({u:h.show(u,h.configuration_fields()) for u in h.UNITS}==baseline['configuration'])
 q="begin isolation level repeatable read read only;set local timezone='UTC';";rows={}
 for table in baseline['rows']:
  q+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from (select to_jsonb(t) j from "+table+" t) q;"
 for line in h.command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q+'commit;']).splitlines():
  value=json.loads(line);require(value['table'] not in rows);rows[value['table']]=value['rows']
 require(rows==baseline['rows']);trees={p:h.tree(pathlib.Path(p)) for p in baseline['trees']}
 require(trees==baseline['trees']);require(units=={u:h.show(u,h.FIELDS) for u in h.UNITS})
 current=pathlib.Path('/run/schubert-nk/startup/epoch.current').read_bytes()
 require(hashlib.sha256(current).hexdigest()=='87a7556e280c58a61d1390d69f5ecde78c430fd807f8a025c401af8bd17dd21e')
 peers="select count(*) from pg_stat_activity where datname='schubert_nk' and usename in ('schubert_batch','schubert_app','schubert_web_session','schubert_backup','schubert_inbox_inspector');select count(*) from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and granted;"
 require(h.command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-d','schubert_nk','-c',peers]).splitlines()==[b'0',b'0'])
 runtime=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf')
 require(h.metadata(runtime)==runtime_metadata and hashlib.sha256(runtime.read_bytes()).hexdigest()==runtime_hash)
 return {'units':units,'rows':rows,'trees':trees}
def save(name,data):
 with (SAVE/name).open('x') as f:os.fchmod(f.fileno(),0o600);json.dump(data,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
def wait_gone(pid,seconds):
 end=time.monotonic()+seconds
 while pathlib.Path('/proc',str(pid)).exists() and time.monotonic()<end:time.sleep(.05)
 require(not pathlib.Path('/proc',str(pid)).exists())
"""BUG818/YKT587: exact PG502 cold-after lock reference, NOT PG504 runtime schema."""
import stat
def cold_lock_reference(value):
 if not isinstance(value,dict) or set(value)!={'units','rows','trees','owner','prepared'} or value['prepared'] is not True:return False
 owner=value['owner']
 if not isinstance(owner,list) or len(owner)!=3 or type(owner[0]) is not int or owner[0]<2 or type(owner[1]) is not int or owner[1]<1:return False
 locks=owner[2]
 if not isinstance(locks,dict) or set(locks)!={'maintenance.lock','startup-admission.lock'}:return False
 for v in locks.values():
  if not isinstance(v,list) or len(v)!=9 or any(type(x) is not int or x<0 for x in v):return False
  if v[1]<1 or v[2:7]!=[0,0,stat.S_IFREG|0o600,1,0]:return False
 return isinstance(value['units'],dict) and len(value['units'])==10 and isinstance(value['rows'],dict) and len(value['rows'])==24 and isinstance(value['trees'],dict)
def execute():
 global h,baseline,lock_baseline,runtime_metadata,runtime_hash
 require(os.geteuid()==0 and not SAVE.exists());os.umask(0o077)
 for name,digest in PINS.items():
  p=TOOLS/name;s=p.lstat();require(s.st_uid==s.st_gid==0 and s.st_mode==0o100400 and s.st_nlink==1 and not os.listxattr(p))
  require(hashlib.sha256(p.read_bytes()).hexdigest()==digest)
 spec=importlib.util.spec_from_file_location('fixed_pg513',TOOLS/'pg513_single_api_refs.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h);h.load_definitions()
 base=h.BASE.read_bytes();require(hashlib.sha256(base).hexdigest()==h.BASE_HASH);baseline=json.loads(base);h.baseline=baseline
 before=pathlib.Path('/var/lib/pgpt-s1-preservation/pg513-single-api-recovery-v1/before.private.json').read_bytes()
 require(hashlib.sha256(before).hexdigest()=='506c9066342d2ef613d653cd54cd4f5873e7d3b90bdfb20b1baa08feb5cce298')
 require(json.loads(before)=={'rows':baseline['rows'],'trees':baseline['trees']})
 prior=pathlib.Path('/var/lib/pgpt-s1-preservation/pg502-cold-preparation-v1/refs-after.private.json').read_bytes()
 require(hashlib.sha256(prior).hexdigest()=='07d74f8b4a5dbf99b801ff2f272e57d1e693dfba61d323800dc180fc6b6d2f49')
 prior=json.loads(prior);require(cold_lock_reference(prior));lock_baseline=prior['owner'][2]
 recipe=pathlib.Path('/var/lib/pgpt-s1-preservation/pg504-resume-tools-v1/pg504_resume_refs.py').read_bytes()
 require(hashlib.sha256(recipe).hexdigest()=='7b877339cea6f058bab34982a620a2d0195db726fe28616db86603ee24a9c105')
 definitions=[n for n in ast.parse(recipe).body if isinstance(n,ast.FunctionDef) and n.name=='fixed_dropin'];require(len(definitions)==1)
 oracle={'require':require,'RUN_ID':'91a748b4-1abe-484c-9682-44f46429b324'}
 exec(compile(ast.Module(body=definitions,type_ignores=[]),'<fixed signed runtime recipe>','exec'),oracle)
 expected_runtime=oracle['fixed_dropin'](pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG495/systemd/schubert-nk-morning-controller.service').read_bytes(),
  pathlib.Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/pg477-native-coverage.conf').read_bytes())
 runtime=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf')
 require(runtime.read_bytes()==expected_runtime and not os.listxattr(runtime))
 runtime_metadata=h.metadata(runtime);runtime_hash=hashlib.sha256(runtime.read_bytes()).hexdigest()
 require(runtime_metadata[2:6]==[0,0,0o100644,1])
 owner(True);value=raw();owner(True);require(value==raw());owner(True)
 parent_fd=os.pidfd_open(PID);child_fd=os.pidfd_open(CHILD);owner(True)
 SAVE.mkdir(mode=0o700);save('before.private.json',value)
 save('term-reservation.private.json',{'pid':PID,'ticks':TICKS,'argv':ARGV,'child':CHILD,'childTicks':CHILD_TICKS,'childArgv':CHILD_ARGV,'boot':BOOT,'oldCloseUNKNOWN':True,'repeatForbidden':True})
 owner(True);signal.pidfd_send_signal(child_fd,signal.SIGTERM);os.close(child_fd);wait_gone(CHILD,5)
 owner(False);signal.pidfd_send_signal(parent_fd,signal.SIGTERM);os.close(parent_fd);wait_gone(PID,15)
 require(value==raw() and value==raw())
 for name in lock_baseline:
  m=h.metadata(pathlib.Path('/run/schubert-nk')/name)
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)>=8 and f[1]=='FLOCK':
    d=f[5].split(':');require((int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(m[0]),os.minor(m[0]),m[1]))
 save('complete.private.json',{'ownedChildThenJavaTERM':True,'rawUnchangedTwice':True,'currentStillIssued':True,'businessCohortUnchanged':True,'peersLocks0':True,'oldCloseUNKNOWN':True,'businessActions0':True})
 print('PG514_ISSUED_HANDOFF ownedTERM=true fullRawUnchangedTwice=true businessCohortUnchanged=true currentIssuedPreserved=true peersLocks0=true oldCloseUNKNOWN=true')
if __name__=='__main__':execute()
