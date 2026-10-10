"""SSC191 fixed pre-Ref Java once pidfd TERM; unknown is never normal close."""
import ast
import inspect
import json
from pg1203_failed_stop_owner_proof import prefix
from pg1041_cold_policy_diagnostic import W
import pg1026_cold_observation_contract as contract
import pg1204_jvm_gc_append_oracle as oracle
import pg1120_current_failed_capture as transport


def payload():
    proof=json.loads((W/'pg1205-failed-stop-owner-proof-v2.safe.json').read_bytes())
    sha='bc6aadd65dd12610d0d413579c18b280a03b28fdff4cddfe3c2bbca058165c55'
    if proof['actualExit']!=0 or proof['beforePrivateSha256']!=sha or not proof['newMetadataReferencesNormalClose']:
        raise ValueError('qualified full fixed failed owner proof required')
    nodes=[n for n in ast.parse(inspect.getsource(contract)).body if isinstance(n,ast.FunctionDef)and n.name in {'durable_reservation','terminate_once'}]
    if len(nodes)!=2:raise ValueError('fixed tested one-signal contract required')
    s=prefix().replace("failed-stop-owner-proof-v1'","failed-stop-owner-handoff-v1'")
    s+='\nimport signal, select, time\n'+ast.unparse(ast.Module(body=nodes,type_ignores=[]))
    s+='\nGC_SOURCE='+repr(inspect.getsource(oracle))+'\ngc_oracle=types.ModuleType("independent_gc_append");exec(GC_SOURCE,gc_oracle.__dict__)\n'+BODY
    ast.parse(s);return s


BODY=r'''
prior=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/failed-stop-owner-proof-v2/before.private.json').read_bytes()
require(hashlib.sha256(prior).hexdigest()=='bc6aadd65dd12610d0d413579c18b280a03b28fdff4cddfe3c2bbca058165c55');proven=json.loads(prior)
reservation_attempted=False;signals=0;reservation_fd=None
def current():
 v=capture();require(all(v[k]==proven['current'][k]for k in v if k!='journals'));gc_oracle.qualify(proven['current']['journals'],v['journals']);return v
def verify(pid,ticks):
 require((pid,ticks)==(PID,TICKS));v=fixed_owner();require(v==proven['owner']);return v
def reserve(pid,owner):
 global reservation_attempted
 require(pid==PID and owner==proven['owner']and not reservation_attempted);reservation_attempted=True
 durable_reservation(reservation_fd,str(PID)+'.term-reserved.private.json',json.dumps({'pid':PID,'ticks':TICKS,'argvSha256':ARGV,'oldNormalClose':False},sort_keys=True).encode())
def send(fd):
 global signals
 require(reservation_attempted and signals==0);signals=1;signal.pidfd_send_signal(fd,signal.SIGTERM)
def wait(fd):
 poll=select.poll();poll.register(fd,select.POLLIN);return bool(poll.poll(30000))
def free_locks():
 for name in ['maintenance.lock','startup-admission.lock']:
  p=pathlib.Path('/run/schubert-nk')/name;s=p.stat()
  for row in pathlib.Path('/proc/locks').read_text().splitlines():
   f=row.split()
   if len(f)>=8 and f[1]=='FLOCK':
    d=f[5].split(':');require((int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino))
try:
 for u in CAPTURE_UNITS:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)
 owner=fixed_owner();require(owner==proven['owner']);before_handoff=current();require(before_handoff==current()and owner==fixed_owner())
 SAVE.mkdir(mode=0o700);reservation_fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 terminate_once(PID,TICKS,verify,reserve,os.pidfd_open,send,wait,os.close)
 require(signals==1 and not pathlib.Path('/proc',str(PID)).exists());free_locks()
 after=current();require(after==current())
 with(SAVE/'after.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);json.dump(after,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 for i,raw_journal in enumerate(JOURNAL_READS):
  with(SAVE/('journal-read-'+str(i)+'.private.json')).open('xb')as f:os.fchmod(f.fileno(),0o600);json.dump(raw_journal,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 os.fsync(reservation_fd);os.close(reservation_fd);reservation_fd=None
except Exception as failure:
 if reservation_attempted:
  print('PG1206_RECOVERY_UNKNOWN type='+type(failure).__name__+' signalsAttempted='+str(signals)+' refsMustRemain=true',flush=True)
  while True:time.sleep(1)
 raise
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'privateAfterSha256':hashlib.sha256((SAVE/'after.private.json').read_bytes()).hexdigest(),'signalsAttempted':signals,'oldJavaGone':True,'oldHadNoChildNoBus':True,'currentFourOrdinaryAndAllOriginalsUnchanged':True,'allOldMaintenanceAdmissionPeersAdvisory0':True,'newMetadataReferencesNormalClose':True,'oldNormalClose':False,'formalAccepted':False}))
'''


def main():
    s=inspect.getsource(transport.main).replace('pg1120-current-failed-capture-v1','pg1206-failed-stop-owner-handoff-v1').replace('PG1120-current-failed-capture-v1','PG1206-failed-stop-owner-handoff-v1')
    env=dict(transport.__dict__);env['PAYLOAD']=payload();exec(compile(s,'<one fixed preRef owner retirement>','exec'),env);return env['main']()


if __name__=='__main__':raise SystemExit(main())
