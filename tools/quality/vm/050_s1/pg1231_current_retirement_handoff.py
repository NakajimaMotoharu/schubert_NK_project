"""Fixed child then parent once pidfd TERM; full originals/native/resource post."""
import ast
import inspect
import pg1230_current_retirement_owner_proof as previous
import pg1222_completed_retirement_preflight as transport
import pg1026_cold_observation_contract as once
import pg611_durable as durable

PROOF='a8f2d03d857227eb3199fa0843638874b6e4dd3fe18032dfb1921158c212c0f5'

def payload():
    s=previous.payload();t=ast.parse(s)
    block=next(n for n in t.body if isinstance(n,ast.Try)and isinstance(n.body[0],ast.For))
    prefix=s[:sum(len(x)for x in s.splitlines(keepends=True)[:block.lineno-1])]
    n=next(n for n in block.body if isinstance(n,ast.FunctionDef)and n.name=='snapshot')
    capture=ast.get_source_segment(s,n)
    capture='\n'.join(x[1:]if x.startswith(' ')else x for x in capture.splitlines())
    # get_source_segment starts at 'def', remaining function lines retain the try
    # indent. Keep that function's relative indent, not an outside return.
    capture=capture.replace('def snapshot():','def owned_snapshot():')
    free=capture.replace('def owned_snapshot():','def free_snapshot():').replace("lines[-2:]==[b'1',b'1']","lines[-2:]==[b'0',b'0']")
    free=free.replace("if (int(d[0],16),int(d[1],16),int(d[2]))==(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino):require(f[1:5]==['FLOCK','ADVISORY','WRITE','560237'])","require((int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino))")
    nodes=[n for n in ast.parse(inspect.getsource(once)).body if isinstance(n,ast.FunctionDef)and n.name in {'durable_reservation','terminate_once'}]
    s=prefix+'\n'+capture+'\n'+free+'\nimport signal,select,time,types\n'+ast.unparse(ast.Module(body=nodes,type_ignores=[]))
    s+='\nWRITER_SOURCE='+repr(inspect.getsource(durable))+'\nwriter=types.ModuleType("actual_durable");exec(WRITER_SOURCE,writer.__dict__)\n'+BODY
    compile(s,'<actual fixed current retirement handoff>','exec');return s

BODY=r'''
raw=(base/'pg1230-current-retirement-owner-proof-v1/before.private.json').read_bytes();require(hashlib.sha256(raw).hexdigest()=='a8f2d03d857227eb3199fa0843638874b6e4dd3fe18032dfb1921158c212c0f5');proven=json.loads(raw)
require(proven['current']==after)
SAVE=base/'pg1231-current-retirement-handoff-v1';require(not os.path.lexists(SAVE))
signals=0;reserved=set();reservation_fd=None
def parent_only():
 p=pathlib.Path('/proc/560237');status=dict(x.split(':',1)for x in(p/'status').read_text().splitlines()if ':'in x)
 require(int((p/'stat').read_text().rpartition(')')[2].split()[19])==5931043 and hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()=='a2a6e372a802b53532507516ca880eff09efc0f6bf6f86aa27b70047c110d13f')
 require(str((p/'exe').readlink())=='/opt/jdk-25.0.4/bin/java'and status['Uid'].split()==status['Gid'].split()==['0']*4 and status['Groups'].split()==['0']and status['PPid'].strip()=='560235')
 require(not pathlib.Path('/proc/560266').exists()and all(not(t/'children').read_text().strip()for t in(p/'task').iterdir()))
 links=[]
 for f in(p/'fd').iterdir():
  try:links.append(str(f.readlink()))
  except FileNotFoundError:continue
 require(all('/run/schubert-nk/'+n in links for n in ['maintenance.lock','startup-admission.lock']))
 return{'pid':560237,'ticks':5931043,'argvSha256':'a2a6e372a802b53532507516ca880eff09efc0f6bf6f86aa27b70047c110d13f','childGone':True}
def verify(pid,ticks):
 require(pid in COHORT and ticks==COHORT[pid][0])
 if pid==560266:
  value=fixed_owner();require(value==proven['owner']);return value
 return parent_only()
def reserve(pid,value):
 require(pid not in reserved and pid in COHORT);reserved.add(pid)
 durable_reservation(reservation_fd,str(pid)+'.term-reserved.private.json',json.dumps({'pid':pid,'ticks':COHORT[pid][0],'argvSha256':COHORT[pid][1],'oldNormalClose':False},sort_keys=True).encode())
def send(fd):
 global signals
 require(len(reserved)==signals+1 and signals<2);signals+=1;signal.pidfd_send_signal(fd,signal.SIGTERM)
def wait(fd):
 poll=select.poll();poll.register(fd,select.POLLIN)
 if not poll.poll(30000):return False
 pid=560266 if signals==1 else 560237
 deadline=time.monotonic()+3
 while pathlib.Path('/proc',str(pid)).exists()and time.monotonic()<deadline:time.sleep(.01)
 return not pathlib.Path('/proc',str(pid)).exists()
try:
 for u in UNITS:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)
 require(fixed_owner()==proven['owner']and owned_snapshot()==proven['native']and owned_snapshot()==proven['native']and fixed_owner()==proven['owner'])
 SAVE.mkdir(mode=0o700);reservation_fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);writer.save(SAVE,'before.private.json',raw)
 terminate_once(560266,5931153,verify,reserve,os.pidfd_open,send,wait,os.close)
 daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus');require(not daemon.NameHasOwner(':1.312146')and parent_only()==parent_only())
 terminate_once(560237,5931043,verify,reserve,os.pidfd_open,send,wait,os.close)
 require(signals==2 and not pathlib.Path('/proc/560237').exists()and not pathlib.Path('/proc/560266').exists())
 require(free_snapshot()==proven['native']and free_snapshot()==proven['native'])
 writer.save(SAVE,'after.private.json',json.dumps({'current':after,'native':proven['native'],'source':'d5b00104280028d9ea81b44c1d1c805f3c2861ed','fixedOldOwnerGone':True,'oldNormalClose':False,'allClientsAdvisoryFlocks0':True},sort_keys=True).encode())
 os.close(reservation_fd);reservation_fd=None
except Exception as failure:
 if reserved:
  print('PG1231_RECOVERY_UNKNOWN type='+type(failure).__name__+' signalsAttempted='+str(signals)+' refsMustRemain=true',flush=True)
  while True:time.sleep(1)
 raise
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
print(json.dumps({'run':'PG1231-current-retirement-handoff-v1','privateAfterSha256':hashlib.sha256((SAVE/'after.private.json').read_bytes()).hexdigest(),'signalsAttempted':signals,'oldFixedJavaRefAndBusGone':True,'original24RowsFull32RuntimeNativePreserved':True,'allClientAdvisoryFlocks0':True,'newMetadataReferencesNormalClose':True,'oldNormalClose':False,'formalAccepted':False}))
'''

def main():
    entry=inspect.getsource(transport.main).replace('pg1222-completed-retirement-preflight-v1','pg1231-current-retirement-handoff-v1')
    env=dict(transport.__dict__);env['payload']=payload
    exec(compile(entry,'<fixed current once child-parent transport>','exec'),env);return env['main']()

if __name__=='__main__':raise SystemExit(main())
