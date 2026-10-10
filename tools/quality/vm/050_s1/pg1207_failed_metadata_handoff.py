"""Recover only fixed metadata sender after actual once Java TERM; never repeat it."""
import ast
import inspect
from pg1203_failed_stop_owner_proof import prefix
import pg1026_cold_observation_contract as contract
import pg1204_jvm_gc_append_oracle as oracle
import pg611_durable as writer
import pg1120_current_failed_capture as transport


def payload():
    s=prefix().replace("failed-stop-owner-proof-v1'","failed-stop-metadata-handoff-v1'")
    s=s.replace('PID=553547','PID=554465').replace('TICKS=5550827','TICKS=5603091').replace('8006b09714090a3298e90430da333e0a823d5e1ad504473fb0fdc6c2f8a63916','5a5cff3ba9f3379bceb96da8fda3ef4a6ab51547f4b5cd0c1d9305e99b4c2ad0')
    node=next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef)and n.name=='fixed_owner')
    s=s.replace(ast.get_source_segment(s,node),OWNER)
    nodes=[n for n in ast.parse(inspect.getsource(contract)).body if isinstance(n,ast.FunctionDef)and n.name in {'durable_reservation','terminate_once'}]
    s+='\nimport signal, select, time\n'+ast.unparse(ast.Module(body=nodes,type_ignores=[]))
    s+='\nGC_SOURCE='+repr(inspect.getsource(oracle))+'\ngc_oracle=types.ModuleType("gc_append");exec(GC_SOURCE,gc_oracle.__dict__)\n'
    s+='WRITER_SOURCE='+repr(inspect.getsource(writer))+'\nwriter=types.ModuleType("durable_bytes_writer");exec(WRITER_SOURCE,writer.__dict__)\n'+BODY
    ast.parse(s);return s


OWNER=r'''
def fixed_owner():
 p=pathlib.Path('/proc')/str(PID);cmd=(p/'cmdline').read_bytes();status=dict(line.split(':',1)for line in(p/'status').read_text().splitlines()if ':'in line)
 require(int((p/'stat').read_text().rpartition(')')[2].split()[19])==TICKS and hashlib.sha256(cmd).hexdigest()==ARGV)
 require(str((p/'exe').readlink())=='/usr/bin/python3.14'and cmd==b'python3\x00-B\x00-\x00')
 require(status['Uid'].split()==status['Gid'].split()==['0']*4 and status['Groups'].split()==['0']and status['PPid'].strip()=='554463')
 require(not(p/'task'/str(PID)/'children').read_text().strip()and len(list((p/'task').iterdir()))==1)
 daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus')
 names=[str(n)for n in daemon.ListNames()if str(n).startswith(':')and int(daemon.GetConnectionUnixProcessID(n))==PID];require(names==[':1.311669'])
 require(not pathlib.Path('/proc/553547').exists())
 old=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/failed-stop-owner-handoff-v1')
 require({p.name for p in old.iterdir()}=={'553547.term-reserved.private.json','after.private.json'})
 require(entry(old/'after.private.json')['metadata'][2:7]==[0,0,stat.S_IFREG|0o600,1,0])
 require(entry(old/'553547.term-reserved.private.json')['sha256']=='ee438951018ac56396a652d82d82a9e9c4fcde809d9aadc56fc99c7f4c75593b')
 return{'pid':PID,'ticks':TICKS,'argvSha256':ARGV,'bus':names[0],'oldFiles':tree(old)}
'''


BODY=r'''
sealed=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/completed-current-before-v1/before.private.json').read_bytes()
require(hashlib.sha256(sealed).hexdigest()=='398324fdea98d2469067a1e93858cd292b4e0328da5712b709c7bb99cffeadfa');completed_current=json.loads(sealed)
reservation_attempted=False;signals=0;reservation_fd=None;proven_owner=None
def current():
 v=capture();require(all(v[k]==completed_current[k]for k in v if k!='journals'));gc_oracle.qualify(completed_current['journals'],v['journals']);return v
def free_locks():
 for name in ['maintenance.lock','startup-admission.lock']:
  p=pathlib.Path('/run/schubert-nk')/name;s=p.stat()
  for row in pathlib.Path('/proc/locks').read_text().splitlines():
   f=row.split()
   if len(f)>=8 and f[1]=='FLOCK':
    d=f[5].split(':');require((int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino))
def verify(pid,ticks):
 require((pid,ticks)==(PID,TICKS));v=fixed_owner();require(v==proven_owner);return v
def reserve(pid,owner):
 global reservation_attempted
 require(pid==PID and owner==proven_owner and not reservation_attempted);reservation_attempted=True
 durable_reservation(reservation_fd,str(PID)+'.term-reserved.private.json',json.dumps({'pid':PID,'ticks':TICKS,'argvSha256':ARGV,'oldNormalClose':False},sort_keys=True).encode())
def send(fd):
 global signals
 require(reservation_attempted and signals==0);signals=1;signal.pidfd_send_signal(fd,signal.SIGTERM)
def wait(fd):
 poll=select.poll();poll.register(fd,select.POLLIN);return bool(poll.poll(30000))
try:
 for u in CAPTURE_UNITS:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)
 free_locks();proven_owner=fixed_owner();before_handoff=current();require(before_handoff==current()and proven_owner==fixed_owner())
 SAVE.mkdir(mode=0o700);reservation_fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 writer.save(SAVE,'before.private.json',json.dumps({'current':before_handoff,'owner':proven_owner},sort_keys=True).encode())
 terminate_once(PID,TICKS,verify,reserve,os.pidfd_open,send,wait,os.close)
 require(signals==1 and not pathlib.Path('/proc',str(PID)).exists());free_locks()
 daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus');require(not daemon.NameHasOwner(':1.311669'))
 after=current();require(after==current())
 writer.save(SAVE,'after.private.json',json.dumps(after,sort_keys=True).encode())
 for i,raw_journal in enumerate(JOURNAL_READS):writer.save(SAVE,'journal-read-'+str(i)+'.private.json',json.dumps(raw_journal,sort_keys=True).encode())
 os.fsync(reservation_fd);os.close(reservation_fd);reservation_fd=None
except Exception as failure:
 if reservation_attempted:
  print('PG1207_RECOVERY_UNKNOWN type='+type(failure).__name__+' signalsAttempted='+str(signals)+' refsMustRemain=true',flush=True)
  while True:time.sleep(1)
 raise
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'privateAfterSha256':hashlib.sha256((SAVE/'after.private.json').read_bytes()).hexdigest(),'signalsAttempted':signals,'oldMetadataPidBusGone':True,'oldJavaGoneWithoutRepeatedSignal':True,'currentFourOrdinaryAndAllOriginalsUnchanged':True,'allOldMaintenanceAdmissionPeersAdvisory0':True,'newMetadataReferencesNormalClose':True,'oldNormalClose':False,'formalAccepted':False}))
'''


def main():
    s=inspect.getsource(transport.main).replace('pg1120-current-failed-capture-v1','pg1207-failed-stop-metadata-handoff-v1').replace('PG1120-current-failed-capture-v1','PG1207-failed-stop-metadata-handoff-v1')
    env=dict(transport.__dict__);env['PAYLOAD']=payload();exec(compile(s,'<fixed metadata sender only retirement>','exec'),env);return env['main']()


if __name__=='__main__':raise SystemExit(main())
