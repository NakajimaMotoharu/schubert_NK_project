"""Fixed failed Ref then Java once-TERM; full current unchanged, oldclose false."""
import ast
import inspect
import pg1222_completed_retirement_preflight as transport
import pg1251_fresh_stop_failed_owner_proof as previous
import pg1026_cold_observation_contract as once
import pg611_durable as durable

PROOF='bfbe425a2cd582b527a1519a2ecdc7e453770e396934fc53c0ca6c6eff88c19f'

def payload():
    s=previous.payload();s=s[:s.index('raw=pathlib.Path(BASELINE).read_bytes()')]
    s=s.replace('fresh-stop-failed-owner-v1','fresh-stop-fixed-handoff-v1')
    nodes=[n for n in ast.parse(inspect.getsource(once)).body if isinstance(n,ast.FunctionDef)and n.name in {'durable_reservation','terminate_once'}]
    s+='\nimport signal,select,time\n'+ast.unparse(ast.Module(body=nodes,type_ignores=[]))+'\nWRITER='+repr(inspect.getsource(durable))+'\nwriter=types.ModuleType("actual_durable");exec(WRITER,writer.__dict__)\n'+BODY
    compile(s,'<actual fixed child then Java current handoff>','exec');return s

BODY=r'''
proof_path=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/fresh-stop-failed-owner-v1/before.private.json');proof_raw=proof_path.read_bytes();require(hashlib.sha256(proof_raw).hexdigest()=='bfbe425a2cd582b527a1519a2ecdc7e453770e396934fc53c0ca6c6eff88c19f');proven=json.loads(proof_raw)
baseline_raw=pathlib.Path(BASELINE).read_bytes();require(hashlib.sha256(baseline_raw).hexdigest()==BASELINE_SHA and json.loads(baseline_raw)==proven['current'])
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
signals=0;reserved=set();reservation_fd=None
def parent_only():
 p=pathlib.Path('/proc/691075');fields=(p/'stat').read_text().rpartition(')')[2].split();status=dict(x.split(':',1)for x in(p/'status').read_text().splitlines()if ':'in x)
 require(int(fields[19])==6303152 and int(fields[1])==691073 and hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()=='672b75588b7097cbd4edca1798498b5ab6e91664b5c7ea71b206284795198700'and str((p/'exe').readlink())=='/opt/jdk-25.0.4/bin/java')
 require(status['Uid'].split()==status['Gid'].split()==['0']*4 and status['Groups'].split()==['0']and not pathlib.Path('/proc/691104').exists()and all(not(t/'children').read_text().strip()for t in(p/'task').iterdir()))
 links=[]
 for f in(p/'fd').iterdir():
  try:links.append(str(f.readlink()))
  except FileNotFoundError:continue
 require(all('/run/schubert-nk/'+name in links for name in ['maintenance.lock','startup-admission.lock','startup']))
 return{'pid':691075,'ticks':6303152,'childGone':True}
def verify(pid,ticks):
 require(pid in COHORT and ticks==COHORT[pid][0])
 if pid==691104:
  v=fixed_owner();require(v==proven['owner']);return v
 return parent_only()
def reserve(pid,value):
 require(pid in COHORT and pid not in reserved);reserved.add(pid)
 durable_reservation(reservation_fd,str(pid)+'.term-reserved.private.json',json.dumps({'pid':pid,'ticks':COHORT[pid][0],'argvSha256':COHORT[pid][1],'oldNormalClose':False},sort_keys=True).encode())
def send(fd):
 global signals
 require(len(reserved)==signals+1 and signals<2);signals+=1;signal.pidfd_send_signal(fd,signal.SIGTERM)
def wait(fd):
 poll=select.poll();poll.register(fd,select.POLLIN)
 if not poll.poll(30000):return False
 pid=691104 if signals==1 else 691075;deadline=time.monotonic()+3
 while pathlib.Path('/proc',str(pid)).exists()and time.monotonic()<deadline:time.sleep(.01)
 return not pathlib.Path('/proc',str(pid)).exists()
def free_resources():
 require(not pathlib.Path('/proc/691075').exists()and not pathlib.Path('/proc/691104').exists())
 daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus');require(not daemon.NameHasOwner(':1.463495'))
 q="select count(*)from pg_stat_activity where pid=691102 or(datname='schubert_nk'and usename in('schubert_batch','schubert_backup','schubert_inbox_inspector'));select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;"
 require(command(['sudo','-n','-u','postgres','psql','-X','-qAt','-d','schubert_nk','-c',q]).splitlines()==[b'0',b'0'])
 for name in ['maintenance.lock','startup-admission.lock']:
  st=pathlib.Path('/run/schubert-nk',name).lstat()
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   fields=line.split()
   if len(fields)>=8 and fields[1]=='FLOCK':
    dev=fields[5].split(':');require((int(dev[0],16),int(dev[1],16),int(dev[2]))!=(os.major(st.st_dev),os.minor(st.st_dev),st.st_ino))
 return True
try:
 for u in units:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)
 require(fixed_owner()==proven['owner']and capture()==proven['current']and capture()==proven['current']and fixed_owner()==proven['owner'])
 SAVE.mkdir(mode=0o700);reservation_fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);writer.save(SAVE,'before.private.json',proof_raw)
 terminate_once(691104,6303259,verify,reserve,os.pidfd_open,send,wait,os.close)
 daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus');require(not daemon.NameHasOwner(':1.463495')and parent_only()==parent_only())
 terminate_once(691075,6303152,verify,reserve,os.pidfd_open,send,wait,os.close)
 require(signals==2 and free_resources()and capture()==proven['current']and free_resources()and capture()==proven['current'])
 value={'current':proven['current'],'source':'d5b00104280028d9ea81b44c1d1c805f3c2861ed','oldMgmtPeerAdvisoryFlocks0':True,'oldNormalClose':False,'ordinaryFourStillOwnedLive':True}
 writer.save(SAVE,'after.private.json',json.dumps(value,sort_keys=True).encode());os.close(reservation_fd);reservation_fd=None
except Exception as failure:
 if reserved:
  print('PG1252_RECOVERY_UNKNOWN type='+type(failure).__name__+' signalsAttempted='+str(signals)+' refsMustRemain=true',flush=True)
  while True:time.sleep(1)
 raise
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
print(json.dumps({'privateAfterSha256':hashlib.sha256((SAVE/'after.private.json').read_bytes()).hexdigest(),'signalsAttempted':signals,'oldFixedJavaRefBusDatabaseGone':True,'full24Full32Signed187StartupOriginalBackupNativeUnchanged':True,'oldMgmtPeerAdvisoryFlocks0':True,'ordinaryFourStillOwnedLive':True,'newMetadataReferencesNormalClose':True,'oldNormalClose':False,'formalAccepted':False}))
'''

def main():
    entry=inspect.getsource(transport.main).replace('pg1222-completed-retirement-preflight-v1','pg1252-fresh-stop-fixed-handoff-v1')
    env=dict(transport.__dict__);env['payload']=payload
    exec(compile(entry,'<new-only fixed once handoff transport>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
