"""SSC211/BUG820: fixed partial-stop PG515 owner only. Never stops a business Unit."""
import ast,hashlib,importlib.util,json,os,pathlib,signal,time,re
PID=310706;TICKS=1180403;CHILD=310735;CHILD_TICKS=1180516
BOOT='cc9ed874-7f4f-450e-a188-8de1e42c8441'
ARGV='36f0d26dc4cbdf629ae3b837c2e15dc5b66c2341ac1cf019c5b0723ff2ffd456'
CHILD_ARGV='8476771a5992c433aff204c9a4720bdeb612485ea72bf0dc9cee228185a923ac'
TOOLS=pathlib.Path('/var/lib/pgpt-s1-preservation/pg515-issued-api-tools-v3')
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg516-terminal-issued-handoff-v1')
PINS={"Pg515SingleApiRecovery.class":"781da450d5129efc2fcd8dbeb358c549eacfe1eaf5de81f48f8c160bcd96ef51","Pg515SingleApiRecovery$References.class":"2e254fbe4c9baa12a266bae6f1151e0f6200c43e8b7eae609ec1c346f1b70efa","dev/codex/schubert/nk/batch/file/Pg515IssuedApiRecovery.class":"19a0d0082e7453c27f29a5829174e1d72f713a58a125cf18369df58eefcf5b41","dev/codex/schubert/nk/batch/file/Pg513SingleApiIntent.class":"c68eb211f959499950f51e93775834a3c3c76d37a848247f3bfc781ef59c37ae","dev/codex/schubert/nk/batch/file/Pg513SingleApiIntent$Gate.class":"485b5ea07540f6a93036ca203e7e506a2d90e61e790075f536176a129e8b68ab","pg515_single_api_refs.py":"11758e00c409da4b72f84df909697c66a3ad4f845c079ec066578839cae252e3","pg515_confirm_ma.py":"058aa21106aefca184c6b21f7d69d8892e4a2641d7a8f220879f2f3d7bbc3e73"}
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
  and type(peers[0]['pid']) is int and peers[0]['pid']>1 and peers[0]['application']=='PG515-fixed-recovery' and peers[0]['user']=='schubert_batch'
  and locks[0]=={'pid':peers[0]['pid'],'mode':'ExclusiveLock'})
def same_configuration(before,after,old,current,ended):
 if not isinstance(before,dict) or not isinstance(after,dict) or set(before)!=set(after) or 'ExecStart' not in before:return False
 if any(before[k]!=after[k] for k in before if k!='ExecStart'):return False
 if before['ExecStart']==after['ExecStart']:return True
 a=exec_record(before['ExecStart']);b=exec_record(after['ExecStart'])
 return a is not None and b is not None and a[:4]==b[:4] and b[4]==ended and b[4]!='n/a' and a[5]==b[5]==old.get('MainPID') and b[6]=='exited' and current.get('ExecMainCode')=='1' and b[7]==current.get('ExecMainStatus') and h.same_generation(old,current)
def raw():
 h.identity();units={u:h.show(u,h.FIELDS) for u in h.UNITS}
 for u,v in units.items():
  require(h.terminal(v));h.kernel(u)
  if u not in h.ORDER:require(v==baseline['units'][u])
  elif u=='artemis.service':require(h.same_generation(baseline['units'][u],v) and v['ExecMainCode']=='1' and v['ExecMainStatus']=='143' and v['Result']=='success')
  else:require(h.normal_terminal(baseline['units'][u],v))
 require(units['schubert-nk-expiry-cleanup.service']==json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg515-issued-api-recovery-v1/schubert-nk-expiry-cleanup.service.stopped.private').read_text()))
 require(pathlib.Path('/var/lib/pgpt-s1-preservation/pg515-issued-api-recovery-v1/schubert-nk-cleanup.service.stop-reserved.private').read_bytes()==b'oneOwnedStop=true\n')
 release=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG495')
 require(hashlib.sha256(release.joinpath('RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44')
 require('ro' in h.command(['/usr/bin/findmnt','--target',str(release),'--output','OPTIONS','--noheadings']).decode().strip().split(','))
 configuration={u:h.show(u,h.configuration_fields()) for u in h.UNITS}
 for u,old in baseline['configuration'].items():
  if u!='artemis.service':require(configuration[u]==old)
  else:
   ended=h.command(['/usr/bin/systemctl','show',u,'--property=ExecMainExitTimestamp']).decode('ascii').strip().removeprefix('ExecMainExitTimestamp=')
   require(same_configuration(old,configuration[u],baseline['units'][u],units[u],ended))
 require(configuration=={u:h.show(u,h.configuration_fields()) for u in h.UNITS})
 q="begin isolation level repeatable read read only;set local timezone='UTC';";rows={}
 for table in baseline['rows']:
  q+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from (select to_jsonb(t) j from "+table+" t) q;"
 for line in h.command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q+'commit;']).splitlines():
  value=json.loads(line);require(value['table'] not in rows);rows[value['table']]=value['rows']
 require(rows==baseline['rows']);trees={p:h.tree(pathlib.Path(p)) for p in baseline['trees']}
 require(trees==baseline['trees']);require(units=={u:h.show(u,h.FIELDS) for u in h.UNITS})
 current=pathlib.Path('/run/schubert-nk/startup/epoch.current').read_bytes()
 require(hashlib.sha256(current).hexdigest()=='87a7556e280c58a61d1390d69f5ecde78c430fd807f8a025c401af8bd17dd21e')
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
 global h,baseline,lock_baseline,runtime_metadata,runtime_hash,exec_record
 require(os.geteuid()==0 and not SAVE.exists());os.umask(0o077)
 for name,digest in PINS.items():
  p=TOOLS/name;s=p.lstat();require(s.st_uid==s.st_gid==0 and s.st_mode==0o100400 and s.st_nlink==1 and not os.listxattr(p))
  require(hashlib.sha256(p.read_bytes()).hexdigest()==digest)
 spec=importlib.util.spec_from_file_location('fixed_pg513',TOOLS/'pg515_single_api_refs.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h);h.load_definitions()
 parser=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/pg477_unit_references.py').read_bytes()
 require(hashlib.sha256(parser).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
 definitions=[n for n in ast.parse(parser).body if isinstance(n,ast.FunctionDef) and n.name=='exec_record'];require(len(definitions)==1)
 exec(compile(ast.Module(body=definitions,type_ignores=[]),'<pinned primary parser>','exec'),globals())
 base=h.BASE.read_bytes();require(hashlib.sha256(base).hexdigest()==h.BASE_HASH);baseline=json.loads(base);h.baseline=baseline
 before=pathlib.Path('/var/lib/pgpt-s1-preservation/pg515-issued-api-recovery-v1/before.private.json').read_bytes()
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
 SAVE.mkdir(mode=0o700);save('before.private.json',value);save('peer-before.private.json',peers_current())
 h.ROOT=SAVE
 h.broker_stop(baseline['units']['artemis.service'],value['units']['artemis.service'])
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
 save('complete.private.json',{'ownedChildThenJavaTERM':True,'rawUnchangedTwice':True,'currentStillIssued':True,'businessCohortUnchanged':True,'peersLocks0':True,'oldCloseUNKNOWN':True,'businessActions0':True})
 print('PG516_TERMINAL_ISSUED_HANDOFF ownedTERM=true fullRawUnchangedTwice=true businessCohortUnchanged=true currentIssuedPreserved=true peersLocks0=true oldCloseUNKNOWN=true')
if __name__=='__main__':execute()
