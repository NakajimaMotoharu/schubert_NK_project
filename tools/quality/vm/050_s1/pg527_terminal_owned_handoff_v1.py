"""SSC214 fixed PG526 operator-only handoff. Business actors already stopped; never reissues any business action."""
import ast,hashlib,importlib.util,json,os,pathlib,re,signal,stat,subprocess,sys,time
import dbus
PID=561260;TICKS=2040839;CHILD=561289;CHILD_TICKS=2040952
ARGV='e538b174fdb55b348b364b49ecca438f03c4cd1aba9f65b28ef9f9c85c8119ba'
CHILD_ARGV='ce648ae9ecb7c8fed4e0dcd1677b35dff79ff1c98c3a3d4fadfab8fcb27bb814'
BOOT='cc9ed874-7f4f-450e-a188-8de1e42c8441'
TOOLS=pathlib.Path('/var/lib/pgpt-s1-preservation/pg526-native-tools-v1')
OLD=pathlib.Path('/var/lib/pgpt-s1-preservation/pg526-native-stop-v1')
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg527-prestop-owned-handoff-v1')
PINS={'Pg526NativeStop.class':'0f230570aab6314cecbe81213bbeb993e185a6f157311ea0ef0ce4b3d68d6567','Pg526NativeStop$References.class':'3df43bbfd2ceffe1cb1e0d5d30fa46e5e93723b97d70f54aae48d36bfae038f0','pg526_native_refs.py':'2c1c66a56bca59bd5c97b215934c7612d86a57e56c819cb4b2844dbec6787b4b','pg526_native_owned_stop.py':'846d35af988509a67fc60b413b398a3c38585f2e3d4310ca6502dd06c30ecc42','pg526_term_witness.py':'12b31d12c82c4c068a577e9ad1ef2bce3d5d23812d9b9242698c90681971c31d','pg526_native_term_witness.py':'a1376d489d596e9b30213c4ae6fa93fc02484c7d39c9538ff7065f0bd6349644'}
FOUR=['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service']
def require(v):
 if not v:raise ValueError('fixed terminal-cohort handoff refused')
def identity(value,pid,ticks,argv,parent=None):
 return(isinstance(value,dict)and set(value)=={'pid','ticks','argv','uid','parent','children'}and type(value['pid'])is int and value['pid']==pid and type(value['ticks'])is int and value['ticks']==ticks and value['argv']==argv and value['uid']==['0']*4 and type(value['parent'])is int and(parent is None or value['parent']==parent)and isinstance(value['children'],set)and all(type(c)is int and c>1 for c in value['children']))
def process(pid):
 p=pathlib.Path('/proc')/str(pid);s=(p/'stat').read_text().rpartition(')')[2].split()
 r={'pid':pid,'ticks':int(s[19]),'parent':int(s[1]),'argv':hashlib.sha256((p/'cmdline').read_bytes()).hexdigest(),'uid':(p/'status').read_text().split('Uid:')[1].splitlines()[0].split(),'children':{int(c)for t in(p/'task').iterdir()for c in(t/'children').read_text().split()}}
 require(r['ticks']==int((p/'stat').read_text().rpartition(')')[2].split()[19]));return r
def owner(child):
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
 r=process(PID);require(identity(r,PID,TICKS,ARGV)and r['children']==({CHILD}if child else set()))
 if child:
  c=process(CHILD);require(identity(c,CHILD,CHILD_TICKS,CHILD_ARGV,PID)and not c['children'])
 links=set()
 for fd in(pathlib.Path('/proc')/str(PID)/'fd').iterdir():
  try:links.add(str(fd.readlink()))
  except FileNotFoundError:pass
 for n,m in lock_baseline.items():
  p=pathlib.Path('/run/schubert-nk')/n;require(metadata(p)==m and str(p)in links);hits=[]
  for l in pathlib.Path('/proc/locks').read_text().splitlines():
   f=l.split()
   if len(f)>=8 and f[1:5]==['FLOCK','ADVISORY','WRITE',str(PID)]:
    d=f[5].split(':')
    if len(d)==3 and tuple(int(x,16)for x in d[:2])+(int(d[2]),)==(os.major(m[0]),os.minor(m[0]),m[1]):hits.append(l)
  require(len(hits)==1)
def peer_contract(peers,locks):
 if peers==[]and locks==[]:return True
 return(isinstance(peers,list)and len(peers)==1 and isinstance(locks,list)and len(locks)==1 and isinstance(peers[0],dict)and set(peers[0])=={'pid','application','user'}and type(peers[0]['pid'])is int and peers[0]['pid']>1 and peers[0]['application']=='PG526-native-stop'and peers[0]['user']=='schubert_batch'and locks[0]=={'pid':peers[0]['pid'],'mode':'ExclusiveLock'})
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
def peers_current():
 q="select coalesce(jsonb_agg(jsonb_build_object('pid',pid,'application',application_name,'user',usename)),'[]'::jsonb) from pg_stat_activity where datname='schubert_nk' and usename in ('schubert_batch','schubert_app','schubert_web_session','schubert_backup','schubert_inbox_inspector');select coalesce(jsonb_agg(jsonb_build_object('pid',pid,'mode',mode)),'[]'::jsonb) from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and objsubid=1 and granted;"
 lines=command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-d','schubert_nk','-c',q]).splitlines();require(len(lines)==2);p,l=[json.loads(x)for x in lines];require(peer_contract(p,l));return {'peers':p,'locks':l}
def same_configuration(before,after,old,current,ended):
 if not isinstance(before,dict) or not isinstance(after,dict) or set(before)!=set(after) or 'ExecStart' not in before:return False
 if any(before[k]!=after[k] for k in before if k!='ExecStart'):return False
 if before['ExecStart']==after['ExecStart']:return True
 a=exec_record(before['ExecStart']);b=exec_record(after['ExecStart'])
 return a is not None and b is not None and a[:4]==b[:4] and b[4]==ended and b[4]!='n/a' and a[5]==b[5]==old.get('MainPID') and b[6]=='exited' and current.get('ExecMainCode')=='1' and b[7]==current.get('ExecMainStatus') and h.same_generation(old,current)
def journal_value_hash(raw):
 require(type(raw)is bytes and raw.endswith(b'\n'))
 entries=[json.loads(line,object_pairs_hook=h.unique)for line in raw.splitlines()]
 return hashlib.sha256(json.dumps(entries,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def terminal_matrix(before,now,receipts):
 require(type(before)is dict and type(now)is dict and set(before)==set(now)==set(h.ORDER)|{'schubert-nk-morning-controller.service','schubert-nk-bootstrap-admin.service'})
 require(type(receipts)is dict and set(receipts)==set(FOUR))
 require(all(type(v)is dict and set(v)==h.FIELDS and all(type(x)is str for x in v.values())for v in before.values()))
 h.validate_live({u:before[u]for u in h.ORDER})
 for u,v in now.items():
  old=before[u];require(type(v)is dict and set(v)==h.FIELDS and all(type(x)is str for x in v.values())and h.terminal(v))
  if u in FOUR:require(v==receipts[u])
  if u in ('schubert-nk-api.service','schubert-nk-web.service'):
   require(h.same_generation(old,v)and v['ActiveState']==v['SubState']=='failed'and v['Result']=='exit-code'and v['ExecMainCode']=='1'and v['ExecMainStatus']=='143')
  elif u=='artemis.service':require(h.same_generation(old,v)and v['ActiveState']=='inactive'and v['SubState']=='dead'and v['Result']=='success'and v['ExecMainCode']=='1'and v['ExecMainStatus']=='143')
  elif u in h.ORDER:require(h.normal_terminal(old,v))
  else:require(v==old)
def raw():
 require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
 units={u:show(u,FIELDS)for u in UNITS};require(set(units)==set(baseline['units'])and len(units)==10)
 receipts={u:json.loads((OLD/(u+'.stopped.private')).read_bytes(),object_pairs_hook=h.unique)for u in FOUR};terminal_matrix(baseline['units'],units,receipts)
 for u,v in units.items():
  require(h.terminal(v));h.kernel_empty(u)
  old=baseline['units'][u]
  if u in FOUR:
   receipt=json.loads((OLD/(u+'.stopped.private')).read_bytes(),object_pairs_hook=h.unique);require(v==receipt)
   require((OLD/(u+'.stop-reserved.private')).read_bytes()==b'oneOwnedStop=true\n')
   if u in ('schubert-nk-api.service','schubert-nk-web.service'):
    raw_journal=(OLD/(u+'.full-journal.private.jsonl')).read_bytes()
    proof=h.witness('API'if'api'in u else'WEB',old,v,raw_journal,old['MainPID'],'999'if'api'in u else'997')
    require(proof==json.loads((OLD/(u+'.stop-witness.private')).read_bytes(),object_pairs_hook=h.unique))
   else:require(h.normal_terminal(old,v))
  elif u=='artemis.service':
   broker=command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_SYSTEMD_INVOCATION_ID='+old['InvocationID'],'-o','json','--no-pager'])
   h.broker_witness(old,v,broker)
  elif u in h.ORDER:require(h.normal_terminal(old,v))
  else:require(v==old)
 configuration={u:show(u,configuration_fields())for u in UNITS}
 for u,old in baseline['configuration'].items():
  ended=command(['/usr/bin/systemctl','show',u,'--property=ExecMainExitTimestamp']).decode('ascii').strip().removeprefix('ExecMainExitTimestamp=')
  require(same_configuration(old,configuration[u],baseline['units'][u],units[u],ended))
 dependencies={u:show(u,{'Requires','Before','After','PartOf','BindsTo'})for u in UNITS}
 require('schubert-nk-cleanup.service'in dependencies['artemis.service']['Requires'].split()and'artemis.service'in dependencies['schubert-nk-expiry-cleanup.service']['Requires'].split())
 require(all(dependencies[u]['PartOf']==dependencies[u]['BindsTo']==''for u in ('artemis.service','schubert-nk-expiry-cleanup.service')))
 pid1={}
 for u,job,mono in [('schubert-nk-expiry-cleanup.service','33502',20418217592),('artemis.service','33499',20418357422),('schubert-nk-cleanup.service','33498',20418359226)]:
  journal=command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_PID=1','UNIT='+u,'-o','json','--no-pager'])
  entries=[json.loads(l,object_pairs_hook=h.unique)for l in journal.splitlines()]
  done=[r for r in entries if r.get('MESSAGE_ID')=='9d1aaa27d60140bd96365438aad20286'and r.get('JOB_ID')==job and r.get('JOB_TYPE')=='stop'and r.get('JOB_RESULT')=='done']
  require(len(done)==1 and done[0].get('__MONOTONIC_TIMESTAMP')==str(mono)and done[0].get('INVOCATION_ID')==baseline['units'][u]['InvocationID']and done[0].get('_BOOT_ID')==BOOT.replace('-','')and done[0].get('_UID')=='0'and done[0].get('_PID')=='1')
  pid1[u]=done
 q="begin isolation level repeatable read read only;set local timezone='UTC';";rows={}
 for t in baseline['rows']:q+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from(select to_jsonb(t)j from "+t+" t)q;"
 for l in command(['/usr/bin/sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q+'commit;']).splitlines():
  v=json.loads(l);require(v['table']not in rows);rows[v['table']]=v['rows']
 require(rows==baseline['rows']);startup=tree(pathlib.Path('/run/schubert-nk/startup'));originals=tree(pathlib.Path('/var/lib/schubert-nk/maintenance'));backup=tree(pathlib.Path('/srv/schubert-nk/backup'))
 require(startup==baseline['startup']and originals==baseline['originals']and backup==baseline['backup'])
 native=tree(pathlib.Path('/run/schubert-nk/pt-coverage'));runtime=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf')
 require(hashlib.sha256(runtime.read_bytes()).hexdigest()=='3992c3bcbe97066de238cb97678bb71537643bb598dd5b63a702b15d9e2e44e3')
 release=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG495');require(str(pathlib.Path('/opt/schubert-nk/current').readlink())==str(release)and hashlib.sha256((release/'RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44')
 require('ro'in command(['/usr/bin/findmnt','--target',str(release),'--output','OPTIONS','--noheadings']).decode().strip().split(','))
 require(units=={u:show(u,FIELDS)for u in UNITS});peers_current()
 return{'units':units,'configuration':configuration,'rows':rows,'startup':startup,'originals':originals,'backup':backup,'native':native,'dependencies':dependencies,'pid1Stop':pid1,'oldProofs':tree(OLD),'brokerJournalValueSha256':journal_value_hash(broker),'runtime':{'metadata':metadata(runtime),'sha256':hashlib.sha256(runtime.read_bytes()).hexdigest()}}
def save(n,v):
 with(SAVE/n).open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(v,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
def wait_gone(pid,seconds):
 end=time.monotonic()+seconds
 while pathlib.Path('/proc',str(pid)).exists()and time.monotonic()<end:time.sleep(.05)
 require(not pathlib.Path('/proc',str(pid)).exists())
def execute(perform=True):
 global baseline,lock_baseline,h,exec_record,handoff_bus
 require(os.geteuid()==0 and not SAVE.exists());os.umask(0o077)
 for n,digest in PINS.items():
  p=TOOLS/n;s=p.lstat();require(s.st_uid==s.st_gid==0 and s.st_mode==0o100400 and s.st_nlink==1 and not os.listxattr(p));require(hashlib.sha256(p.read_bytes()).hexdigest()==digest)
 witness=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes();require(hashlib.sha256(witness).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7');s=ast.parse(witness)
 names={'command','show','metadata','tree','configuration_fields'};definitions=[n for n in s.body if isinstance(n,ast.FunctionDef)and n.name in names];require(len(definitions)==len(names));constants=[n for n in s.body if isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)and t.id in{'UNITS','FIELDS'}for t in n.targets)]
 exec(compile(ast.Module(body=constants+definitions,type_ignores=[]),'<fixed readonly definitions>','exec'),globals())
 sys.path.insert(0,str(TOOLS))
 spec=importlib.util.spec_from_file_location('fixed_pg526_owned_stop',TOOLS/'pg526_native_owned_stop.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
 parser=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/pg477_unit_references.py').read_bytes();require(hashlib.sha256(parser).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
 nodes=[n for n in ast.parse(parser).body if isinstance(n,ast.FunctionDef)and n.name=='exec_record'];require(len(nodes)==1);exec(compile(ast.Module(body=nodes,type_ignores=[]),'<fixed primary parser>','exec'),globals())
 require(len(list(OLD.iterdir()))==18 and all((OLD/(u+'.stopped.private')).is_file()and(OLD/(u+'.stop-reserved.private')).is_file()for u in FOUR))
 b=(OLD/'before.private.json').read_bytes();require(hashlib.sha256(b).hexdigest()=='15fa5248869a1290940d776cf9886213475d4ff8850a5b13ad34e75ede5d32eb');baseline=json.loads(b)
 require(set(baseline)=={'units','configuration','rows','pid1','startup','originals','backup'}and len(baseline['rows'])==24 and len(baseline['rows']['schubert.batch_runs'])==462)
 require(hashlib.sha256((OLD/'refs-prepare.private.log').read_bytes()).hexdigest()=='0587a241db0f8a14170a1d30adc9ad6b1ec2466b7112fdfc45f3e385b055c5c2')
 lock_reference=pathlib.Path('/var/lib/pgpt-s1-preservation/pg502-cold-preparation-v1/refs-after.private.json').read_bytes();require(hashlib.sha256(lock_reference).hexdigest()=='07d74f8b4a5dbf99b801ff2f272e57d1e693dfba61d323800dc180fc6b6d2f49');lock_value=json.loads(lock_reference);require(cold_lock_reference(lock_value));lock_baseline=lock_value['owner'][2]
 bus=dbus.SystemBus(private=True);handoff_bus=bus;manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
 for u in UNITS:manager.RefUnit(u);refs.append(u)
 owner(True);value=raw();owner(True);require(value==raw());owner(True)
 require(type(perform)is bool)
 if not perform:
  for u in reversed(refs):manager.UnrefUnit(u)
  bus.close()
  print('PG527_PREFLIGHT fullRawUnchangedTwice=true currentOwner=true businessActions0=true');return
 parent_fd=os.pidfd_open(PID);child_fd=os.pidfd_open(CHILD);owner(True)
 SAVE.mkdir(mode=0o700);save('before.private.json',value);save('peer-before.private.json',peers_current());save('old-ref-error.private.json',{'sha256':hashlib.sha256((OLD/'refs-prepare.private.log').read_bytes()).hexdigest(),'oldCloseUNKNOWN':True})
 broker=command(['/usr/bin/journalctl','--boot='+BOOT.replace('-',''),'_SYSTEMD_INVOCATION_ID='+baseline['units']['artemis.service']['InvocationID'],'-o','json','--no-pager']);require(journal_value_hash(broker)==value['brokerJournalValueSha256'])
 with(SAVE/'broker-full-journal.private.jsonl').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(broker);f.flush();os.fsync(f.fileno())
 save('broker-raw.private.json',{'sha256':hashlib.sha256(broker).hexdigest(),'valueSha256':journal_value_hash(broker)})
 require(value==raw());owner(True);save('term-reservation.private.json',{'pid':PID,'ticks':TICKS,'argv':ARGV,'child':CHILD,'childTicks':CHILD_TICKS,'childArgv':CHILD_ARGV,'boot':BOOT,'repeatForbidden':True,'businessStop0':True,'oldCloseUNKNOWN':True})
 owner(True);signal.pidfd_send_signal(child_fd,signal.SIGTERM);os.close(child_fd);wait_gone(CHILD,5)
 owner(False);signal.pidfd_send_signal(parent_fd,signal.SIGTERM);os.close(parent_fd);wait_gone(PID,15)
 require(value==raw()and value==raw());require(peers_current()=={'peers':[],'locks':[]})
 for m in lock_baseline.values():
  for l in pathlib.Path('/proc/locks').read_text().splitlines():
   f=l.split()
   if len(f)>=8 and f[1]=='FLOCK':
    d=f[5].split(':');require((int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(m[0]),os.minor(m[0]),m[1]))
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
 save('complete.private.json',{'ownedChildThenJavaTERM':True,'allRawUnchangedTwice':True,'terminalCohortPreserved':True,'ownPeerLocks0':True,'newRefNormallyReleased':True,'oldCloseUNKNOWN':True,'businessActions0':True})
 print('PG527_TERMINAL_OWNED_HANDOFF ownedTERM=true terminalCohortPreserved=true fullRawUnchangedTwice=true ownPeerLocks0=true oldCloseUNKNOWN=true')
if __name__=='__main__':
 try:execute()
 except Exception as failure:
  import traceback
  print('PG527_HANDOFF_UNKNOWN type='+type(failure).__name__,flush=True)
  for frame in traceback.extract_tb(failure.__traceback__):
   if frame.filename==__file__:print('PG527_FRAME method='+frame.name+' line='+str(frame.lineno),flush=True)
  if(SAVE/'term-reservation.private.json').exists():
   while True:time.sleep(1)
  raise
