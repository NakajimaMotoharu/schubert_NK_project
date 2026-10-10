"""SSC257258 fixed child->Java pidfd TERM, never replay any business stop."""
import ast
import inspect
import json
from pg1141_failed_owner_preflight import payload as previous
from pg1041_cold_policy_diagnostic import W
import pg1026_cold_observation_contract as contract
import pg1120_current_failed_capture as transport


def payload():
    saved=json.loads((W/'pg1141-failed-owner-preflight-v1.safe.json').read_bytes())
    if saved['actualExit']!=0 or saved['privateSnapshotSha256']!='6119d517c5880b95815b03a32c35bc15627489aebb52fa26925195d9bcdcbc64':
        raise ValueError('fixed complete old owner proof refused')
    raw=previous().replace('failed-owner-preflight-v1','fixed-failed-owner-handoff-v1')
    marker='bus=dbus.SystemBus(private=True);manager=dbus.Interface'
    raw=raw[:raw.index(marker)]+BODY
    definitions=[n for n in ast.parse(inspect.getsource(contract)).body if isinstance(n,ast.FunctionDef)and n.name in {'durable_reservation','terminate_once'}]
    if len(definitions)!=2:raise ValueError('fixed independently tested once-contract source refused')
    snippet='import os,re\n'+ast.unparse(ast.Module(body=definitions,type_ignores=[]))
    raw="import signal,select,time,types\ncontract=types.ModuleType('fixed-once-contract')\nexec("+repr(snippet)+",contract.__dict__)\nSIGNALS=0\n"+raw
    ast.parse(raw);return raw


BODY=r'''
PRIOR=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/failed-owner-preflight-v1/observed.private.json')
raw_prior=PRIOR.read_bytes();require(hashlib.sha256(raw_prior).hexdigest()=='6119d517c5880b95815b03a32c35bc15627489aebb52fa26925195d9bcdcbc64')
PROVEN=json.loads(raw_prior)
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus');refs=[]
def current():
 value=capture();require(value==PROVEN['current']);return value
def child_before(pid,ticks):
 require((pid,ticks)==(404614,4248757));value=whole();require(value==PROVEN);return value
def parent_before(pid,ticks):
 require((pid,ticks)==(404585,4248646));require(not pathlib.Path('/proc/404614').exists()and not daemon.NameHasOwner(PROVEN['owner']['childBus']))
 java=actor_proof(404585,4248646,'61d39d9b14028d6861a43af6b68502107d5b30a8c5c7ec8eeedd2e715f6d8207','/opt/jdk-25.0.4/bin/java',set())
 require(java==dict(PROVEN['owner']['java'],children=[]))
 locks=PROVEN['owner']['locks']
 for name,proof in locks.items():
  p=pathlib.Path('/run/schubert-nk')/name;require(md(p)==proof['metadata'])
  for fd,flags in proof['fds'].items():
   proc=pathlib.Path('/proc/404585');require(str((proc/'fd'/fd).readlink())==str(p))
   require((proc/'fdinfo'/fd).read_text().split('flags:')[1].splitlines()[0].strip()==flags)
  matches=[];s=p.stat()
  for row in pathlib.Path('/proc/locks').read_text().splitlines():
   v=row.split()
   if len(v)>=8 and len(v[5].split(':'))==3:
    d=v[5].split(':')
    if(int(d[0],16),int(d[1],16),int(d[2]))==(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino):matches.append(v)
  require(len(matches)==1 and matches[0][1:5]==['FLOCK','ADVISORY','WRITE','404585'])
 return {'current':current(),'java':java,'locks':locks,'childGone':True,'busGone':True}
def reserve(pid,value):
 require(pid in (404614,404585))
 contract.durable_reservation(directory_fd,str(pid)+'.term-reserved.private.json',json.dumps({'pid':pid,'proofSha256':hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest(),'oldNormalClose':False}).encode())
def send(fd):
 global SIGNALS
 SIGNALS+=1;signal.pidfd_send_signal(fd,signal.SIGTERM,None,0)
def wait(fd):
 poll=select.poll();poll.register(fd,select.POLLIN);return bool(poll.poll(15000))
def gone(pid):
 end=time.monotonic()+15
 while pathlib.Path('/proc',str(pid)).exists()and time.monotonic()<end:time.sleep(.02)
 require(not pathlib.Path('/proc',str(pid)).exists())
def post():
 require(not pathlib.Path('/proc/404585').exists()and not pathlib.Path('/proc/404614').exists())
 require(not daemon.NameHasOwner(PROVEN['owner']['childBus']))
 for name,proof in PROVEN['owner']['locks'].items():
  p=pathlib.Path('/run/schubert-nk')/name;require(md(p)==proof['metadata']);s=p.stat()
  for row in pathlib.Path('/proc/locks').read_text().splitlines():
   v=row.split()
   if len(v)>=8 and len(v[5].split(':'))==3:
    d=v[5].split(':');require((int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino))
 resource_zero();return current()
try:
 for u in units:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)
 before=whole();require(before==PROVEN==whole());SAVE.mkdir(mode=0o700)
 with(SAVE/'before.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(before,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 directory_fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(directory_fd)
 contract.terminate_once(404614,4248757,child_before,reserve,lambda pid:os.pidfd_open(pid,0),send,wait,os.close)
 gone(404614);require(not daemon.NameHasOwner(PROVEN['owner']['childBus']));current()
 contract.terminate_once(404585,4248646,parent_before,reserve,lambda pid:os.pidfd_open(pid,0),send,wait,os.close)
 gone(404585);after=post();require(after==post())
 with(SAVE/'after.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(after,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 os.fsync(directory_fd);os.close(directory_fd)
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
print(json.dumps({'privateAfterSha256':hashlib.sha256((SAVE/'after.private.json').read_bytes()).hexdigest(),'signals':SIGNALS,'fixedOldChildAndJavaGone':True,'oldBusGone':True,'allOriginalsDbBackupSourceUnchangedTwice':True,'oldPeersAdvisoryMaintenanceAdmission0':True,'newMetadataScopeNormalClose':True,'oldOperationNormalClose':False,'businessStopsStartsRevoke0':True,'cleanupStillOriginalActiveExited':True,'formalAccepted':False}))
'''


def main():
    raw=inspect.getsource(transport.main).replace('pg1120-current-failed-capture-v1','pg1142-fixed-failed-owner-handoff-v1').replace('PG1120-current-failed-capture-v1','PG1142-fixed-failed-owner-handoff-v1')
    env=dict(transport.__dict__);env['PAYLOAD']=payload();exec(compile(raw,'<once fixed old child Java handoff>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
