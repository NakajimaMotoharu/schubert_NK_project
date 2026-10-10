"""Once child then parent retirement of fixed DB/Ref cohort; full32 post retained."""
import ast
import inspect
import json
from pg1214_current_full32_owner_proof import prefix
from pg1041_cold_policy_diagnostic import W
import pg1026_cold_observation_contract as contract
import pg1120_current_failed_capture as transport


def payload():
    proof=json.loads((W/'pg1214-full32-stop-owner-proof-v1.safe.json').read_bytes())
    if proof['actualExit']!=0 or proof['privateBeforeSha256']!='85f0dca57985978756d31eb34e593317db568c4d95636f081f4944de661d9865':raise ValueError('actual full32 owner proof required')
    s=prefix().replace("full32-stop-owner-proof-v1'","full32-stop-owner-handoff-v1'")
    node=next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef)and n.name=='capture')
    after=ast.get_source_segment(s,node).replace('def capture():','def capture_after():').replace(".splitlines()==[b'1',b'1']",".splitlines()==[b'0',b'0']")
    s+='\n'+after+'\nimport signal,select,time\n'
    nodes=[n for n in ast.parse(inspect.getsource(contract)).body if isinstance(n,ast.FunctionDef)and n.name in {'durable_reservation','terminate_once'}]
    s+=ast.unparse(ast.Module(body=nodes,type_ignores=[]))+'\n'+BODY
    ast.parse(s);return s


BODY=r'''
base=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1')
old_raw=(base/'full32-stop-owner-proof-v1/before.private.json').read_bytes();require(hashlib.sha256(old_raw).hexdigest()=='85f0dca57985978756d31eb34e593317db568c4d95636f081f4944de661d9865');PROVEN=json.loads(old_raw)
old20=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/completed-current-before-v1/before.private.json').read_bytes();require(hashlib.sha256(old20).hexdigest()=='398324fdea98d2469067a1e93858cd292b4e0328da5712b709c7bb99cffeadfa');completed_current=json.loads(old20)
signals=0;reserved=set();reservation_fd=None
def parent_only():
 p=pathlib.Path('/proc/555802');status=dict(x.split(':',1)for x in(p/'status').read_text().splitlines()if ':'in x)
 require(int((p/'stat').read_text().rpartition(')')[2].split()[19])==5659239 and hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()=='22cb32f47743110124a6b3358f13aa19732fb2b9db201840044fa897ae9e9abe')
 require(str((p/'exe').readlink())=='/opt/jdk-25.0.4/bin/java'and status['Uid'].split()==status['Gid'].split()==['0']*4 and status['Groups'].split()==['0']and status['PPid'].strip()=='555800')
 require(not pathlib.Path('/proc/555831').exists()and all(not(t/'children').read_text().strip()for t in(p/'task').iterdir()))
 fd_names=[]
 for f in(p/'fd').iterdir():
  try:fd_names.append(str(f.readlink()))
  except FileNotFoundError:continue
 for name in ['maintenance.lock','startup-admission.lock']:require('/run/schubert-nk/'+name in fd_names)
 return{'pid':555802,'ticks':5659239,'argvSha256':'22cb32f47743110124a6b3358f13aa19732fb2b9db201840044fa897ae9e9abe','childGone':True}
def verify(pid,ticks):
 if pid==555831:
  require(ticks==5659344);v=fixed_owner();require(v==PROVEN['owner']);return v
 require((pid,ticks)==(555802,5659239));return parent_only()
def reserve(pid,value):
 require(pid in {555831,555802}and pid not in reserved);reserved.add(pid)
 durable_reservation(reservation_fd,str(pid)+'.term-reserved.private.json',json.dumps({'pid':pid,'ticks':COHORT[pid][0],'argvSha256':COHORT[pid][1],'oldNormalClose':False},sort_keys=True).encode())
def send(fd):
 global signals
 require(len(reserved)==signals+1 and signals<2);signals+=1;signal.pidfd_send_signal(fd,signal.SIGTERM)
def wait(fd):
 poll=select.poll();poll.register(fd,select.POLLIN);return bool(poll.poll(30000))
def free_locks():
 for name in ['maintenance.lock','startup-admission.lock']:
  s=(pathlib.Path('/run/schubert-nk')/name).stat()
  for row in pathlib.Path('/proc/locks').read_text().splitlines():
   f=row.split()
   if len(f)>=8 and f[1]=='FLOCK':
    d=f[5].split(':');require((int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino))
def after_whole():
 v=capture_after();require(all(v[k]==completed_current[k]for k in v if k!='journals'));gc_oracle.qualify(PROVEN['current']['journals'],v['journals'])
 configs={};scope={}
 for u in CAPTURE_UNITS:
  value=config.complete_configuration(command(['/usr/bin/systemctl','show',u,'--property='+','.join(sorted(bridge.FULL))]).decode(),u)
  configs[u],scope[u]=bridge.extend(v['configuration'][u],value,v['units'][u]);require(configs[u]==PROVEN['current']['configuration'][u])
 v['historicalConfiguration']=v['configuration'];v['configuration']=configs;v['configurationScope']=scope;free_locks();return v
try:
 for u in CAPTURE_UNITS:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)
 observed=whole();require(observed==PROVEN==whole());SAVE.mkdir(mode=0o700);reservation_fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 writer.save(SAVE,'before.private.json',json.dumps(observed,sort_keys=True).encode())
 terminate_once(555831,5659344,verify,reserve,os.pidfd_open,send,wait,os.close)
 daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus');require(not daemon.NameHasOwner(':1.311674'));require(parent_only()==parent_only())
 terminate_once(555802,5659239,verify,reserve,os.pidfd_open,send,wait,os.close)
 require(signals==2 and not pathlib.Path('/proc/555802').exists()and not pathlib.Path('/proc/555831').exists())
 after=after_whole();require(after==after_whole());writer.save(SAVE,'after.private.json',json.dumps(after,sort_keys=True).encode())
 for i,raw_journal in enumerate(JOURNAL_READS):writer.save(SAVE,'journal-read-'+str(i)+'.private.json',json.dumps(raw_journal,sort_keys=True).encode())
 os.fsync(reservation_fd);os.close(reservation_fd);reservation_fd=None
except Exception as failure:
 if reserved:
  print('PG1215_RECOVERY_UNKNOWN type='+type(failure).__name__+' signalsAttempted='+str(signals)+' refsMustRemain=true',flush=True)
  while True:time.sleep(1)
 raise
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
print(json.dumps({'privateAfterSha256':hashlib.sha256((SAVE/'after.private.json').read_bytes()).hexdigest(),'signalsAttempted':signals,'oldJavaRefSenderBusGone':True,'allOriginalsAndCurrentFourOwnedPreserved':True,'allFull32ConfigurationRetained':True,'oldPeersAdvisoryMaintenanceAdmission0':True,'newMetadataReferencesNormalClose':True,'oldNormalClose':False,'formalAccepted':False}))
'''


def main():
    s=inspect.getsource(transport.main).replace('pg1120-current-failed-capture-v1','pg1215-full32-owner-handoff-v1').replace('PG1120-current-failed-capture-v1','PG1215-full32-owner-handoff-v1')
    env=dict(transport.__dict__);env['PAYLOAD']=payload();exec(compile(s,'<current fixed full32 child parent handoff>','exec'),env);return env['main']()


if __name__=='__main__':raise SystemExit(main())
