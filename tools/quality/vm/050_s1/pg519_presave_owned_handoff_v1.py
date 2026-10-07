"""SSC212/BUG821: fixed pre-SAVE PG519 owner only. Never stops a business Unit."""
import ast,hashlib,importlib.util,json,os,pathlib,signal,time
PID=317317;TICKS=1323648;CHILD=317346;CHILD_TICKS=1323764
BOOT='cc9ed874-7f4f-450e-a188-8de1e42c8441'
ARGV='b7596427a9f33333fa4d4f12c02a0223434dac7f7df748e1a982d40ee8bb9269'
CHILD_ARGV='e653326b14f0e0a7349f497d06465a0a2c57930cb8400d056735f0e9deaf3d3f'
TOOLS=pathlib.Path('/var/lib/pgpt-s1-preservation/pg519-retirement-tools-v1')
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg519-presave-owned-handoff-v1')
PINS={"Pg519RuntimeRetirement.class":"cd3f77cba6a1a9c0d38b3bb16e99cc2d1541a4bc1b7d19875777ba3df1a73292","Pg519RuntimeRetirement$References.class":"cef2269302dba4aa9485828a2a60527187055825dea744a63b91ab38c7f42e67","pg519_runtime_retirement_refs.py":"b678ceb2b535d5c2951391f6fea18eb69ace65a3f7f0c8b3cd9c98b4e9781c9b","pg519_runtime_retirement_test.py":"4bc4267da462cb12b4ad2d1cc73056332967906b6b42c66bf35315425df9e1da","pg477_unit_references.py":"b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4"}
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
def peers_current():
 q="select coalesce(jsonb_agg(jsonb_build_object('pid',pid,'application',application_name,'user',usename)),'[]'::jsonb) from pg_stat_activity where datname='schubert_nk' and usename in ('schubert_batch','schubert_app','schubert_web_session','schubert_backup','schubert_inbox_inspector');select coalesce(jsonb_agg(jsonb_build_object('pid',pid,'mode',mode)),'[]'::jsonb) from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and objsubid=1 and granted;"
 lines=h.command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-d','schubert_nk','-c',q]).splitlines()
 require(len(lines)==2);peers,locks=[json.loads(x) for x in lines]
 require(peer_contract(peers,locks));return {'peers':peers,'locks':locks}
def peer_contract(peers,locks):
 if peers==[] and locks==[]:return True
 return (isinstance(peers,list) and len(peers)==1 and isinstance(locks,list) and len(locks)==1
  and isinstance(peers[0],dict) and set(peers[0])=={'pid','application','user'}
  and type(peers[0]['pid']) is int and peers[0]['pid']>1 and peers[0]['application']=='PG519-runtime-retirement' and peers[0]['user']=='schubert_batch'
  and locks[0]=={'pid':peers[0]['pid'],'mode':'ExclusiveLock'})
def raw():
 h.identity();units={u:h.show(u,h.FIELDS) for u in h.UNITS}
 require(units==baseline['units'])
 for u,v in units.items():require(h.terminal(v));h.kernel(u)
 release=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG495')
 require(hashlib.sha256(release.joinpath('RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44')
 require('ro' in h.command(['/usr/bin/findmnt','--target',str(release),'--output','OPTIONS','--noheadings']).decode().strip().split(','))
 configuration={u:h.show(u,h.configuration_fields()) for u in h.UNITS}
 require(configuration==baseline['configuration'])
 require(configuration=={u:h.show(u,h.configuration_fields()) for u in h.UNITS})
 q="begin isolation level repeatable read read only;set local timezone='UTC';";rows={}
 for table in baseline['rows']:
  q+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from (select to_jsonb(t) j from "+table+" t) q;"
 for line in h.command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q+'commit;']).splitlines():
  value=json.loads(line);require(value['table'] not in rows);rows[value['table']]=value['rows']
 require(rows==baseline['rows']);trees={p:h.tree(pathlib.Path(p)) for p in baseline['trees']}
 require(trees==baseline['trees']);require(units=={u:h.show(u,h.FIELDS) for u in h.UNITS})
 current=pathlib.Path('/run/schubert-nk/startup/epoch.current').read_bytes()
 require(hashlib.sha256(current).hexdigest()=='85776ad116f8f506a97a51a092afee8d2da2378bbe682c5cbf183ab3672f4da3')
 peers_current()
 runtime=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf')
 require(h.metadata(runtime)==runtime_metadata and hashlib.sha256(runtime.read_bytes()).hexdigest()==runtime_hash)
 return {'units':units,'rows':rows,'trees':trees,'configuration':configuration}
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
 helper=pathlib.Path('/var/lib/pgpt-s1-preservation/pg518-native-role-tools-v3/pg518_native_role_refs.py')
 require(hashlib.sha256(helper.read_bytes()).hexdigest()=='767ea6247ab0e4e000ce94cca8b9937896d5a2e8b16ccaf72952032b477d7166')
 spec=importlib.util.spec_from_file_location('fixed_pg518',helper);h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h);h.load_definitions()
 base=pathlib.Path('/var/lib/pgpt-s1-preservation/pg518-native-role-recovery-v1/after.private.json').read_bytes()
 require(hashlib.sha256(base).hexdigest()=='420b5cfe66b3d47b5d44473d1e663d681c6ac13c629b9c9de119b6dd304a35ff')
 baseline=json.loads(base);require(set(baseline)=={'rows','trees'})
 terminal=pathlib.Path('/var/lib/pgpt-s1-preservation/pg516-terminal-issued-handoff-v1/before.private.json').read_bytes()
 require(hashlib.sha256(terminal).hexdigest()=='36362db410eb99db610dc896adf95bb2c9f485c9c81518da0c99cdd353758a80')
 terminal=json.loads(terminal);require(terminal['rows']==baseline['rows'])
 baseline.update(units=terminal['units'],configuration=terminal['configuration']);h.baseline=baseline
 completed=pathlib.Path('/var/lib/pgpt-s1-preservation/pg518-native-role-recovery-v1/complete.private').read_bytes()
 require(hashlib.sha256(completed).hexdigest()=='2641e40f8f6fc25c724eb387beb145cade5b9d7852a45100dc4e525e33f2e49f')
 failed=pathlib.Path('/var/lib/pgpt-s1-preservation/pg519-runtime-retirement-v1')
 require(set(p.name for p in failed.iterdir())=={'refs-prepare.private.log'})
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
 SAVE.mkdir(mode=0o700);save('before.private.json',value);save('peer-before.private.json',peers_current())
 save('old-ref-error.private.json',{'sha256':hashlib.sha256((failed/'refs-prepare.private.log').read_bytes()).hexdigest(),'noOldBeforeImage':True})
 require(value==raw());owner(True)
 save('term-reservation.private.json',{'pid':PID,'ticks':TICKS,'argv':ARGV,'child':CHILD,'childTicks':CHILD_TICKS,'childArgv':CHILD_ARGV,'boot':BOOT,'oldCloseUNKNOWN':True,'repeatForbidden':True})
 owner(True);signal.pidfd_send_signal(child_fd,signal.SIGTERM);os.close(child_fd);wait_gone(CHILD,5)
 owner(False);signal.pidfd_send_signal(parent_fd,signal.SIGTERM);os.close(parent_fd);wait_gone(PID,15)
 require(value==raw() and value==raw());require(peers_current()=={'peers':[],'locks':[]})
 for name in lock_baseline:
  m=h.metadata(pathlib.Path('/run/schubert-nk')/name)
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)>=8 and f[1]=='FLOCK':
    d=f[5].split(':');require((int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(m[0]),os.minor(m[0]),m[1]))
 save('complete.private.json',{'ownedChildThenJavaTERM':True,'rawUnchangedTwice':True,'currentStillInvalid':True,'businessCohortUnchanged':True,'peersLocks0':True,'oldCloseUNKNOWN':True,'businessActions0':True})
 print('PG519_PRESAVE_OWNED_HANDOFF ownedTERM=true fullRawUnchangedTwice=true businessCohortUnchanged=true currentInvalidPreserved=true peersLocks0=true oldCloseUNKNOWN=true')
if __name__=='__main__':execute()
