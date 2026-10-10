"""SSC245 fixed Java5463/Refs5489 retirement only; old failure stays non-success."""
import ast
import hashlib
import json
from pathlib import Path
from pg1050_cold_tree_preflight import payload as previous
from pg1051_cold_tree_preflight_v2 import dispatch
from pg1041_cold_policy_diagnostic import W

HANDOFF = r'''
 phase='FIXED_TREE_BEFORE';CORE_COUNT=len(held)
 prior=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1037-cold-prepared-v1/tree-preflight-v4/before.private.json')
 proof=pin_file(prior,PRIOR_SHA);prior_bytes=prior.read_bytes();assert hashlib.sha256(prior_bytes).hexdigest()==PRIOR_SHA
 qualified=json.loads(prior_bytes);CHILD_BUS=qualified.pop('childBusUniqueName')
 assert int(daemon.GetConnectionUnixProcessID(CHILD_BUS))==5489 and int(daemon.GetConnectionUnixUser(CHILD_BUS))==0
 def tree_before():
  proof.capture();v=read();assert v==qualified
  assert int(daemon.GetConnectionUnixProcessID(CHILD_BUS))==5489 and int(daemon.GetConnectionUnixUser(CHILD_BUS))==0
  return v
 before=tree_before();assert before==tree_before();private=json.dumps(before,sort_keys=True).encode()
 with(save/'before.private.json').open('xb')as f:f.write(private);f.flush();os.fsync(f.fileno())
 reservation_fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(reservation_fd)
 actual_locks=env['owned_flocks']
 def post_locks(lines,m,pid):
  if pid==0:return contract.free_flocks(lines,m)
  return actual_locks(lines,m,pid)
 expected={k:before[k]for k in ('snapshot','controls','heldWholeMetadata')}
 def data_post():
  assert not pathlib.Path('/proc/5463').exists();proof.capture()
  v={'snapshot':env['snapshot'](),'controls':env['controls'](),'heldWholeMetadata':safe([h.capture()for h in held[:CORE_COUNT]])}
  assert v==expected;return v
 CHILD_ALREADY_GONE=False
 def orphan():
  global CHILD_ALREADY_GONE
  env['OWNER_PID']=0;env['OWNER_BACKEND']=0;env['owned_flocks']=post_locks
  deadline=time.monotonic()+15
  while pathlib.Path('/proc/5463').exists()and time.monotonic()<deadline:time.sleep(.02)
  v=data_post()
  if not pathlib.Path('/proc/5489').exists():
   assert not daemon.NameHasOwner(CHILD_BUS);CHILD_ALREADY_GONE=True
   return {'parentGone':True,'childGone':True,'allPeersAndLocks0':True,'post':v}
  child=actor(5489,1373951,'8067bb56195ab7f05b1427a9d5cf78f5d71e404000acc5f5f3391c5079e5a1d9','/usr/bin/python3.14',set(),1)
  assert child==before['tree']['child']
  assert int(daemon.GetConnectionUnixProcessID(CHILD_BUS))==5489 and int(daemon.GetConnectionUnixUser(CHILD_BUS))==0
  return {'parentGone':True,'childGone':False,'post':v,'child':child}
 def reserve(actor_id,value):
  global RESERVATION_ATTEMPTED
  assert actor_id in ((5463,1373880),(5489,1373951));RESERVATION_ATTEMPTED=True
  contract.durable_reservation(reservation_fd,str(actor_id[0])+'.term-reserved.private.json',json.dumps(
   {'pid':actor_id[0],'ticks':actor_id[1],'proofSha256':hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()},sort_keys=True).encode())
 def send(fd):
  global SIGNAL_ATTEMPTED,SIGNAL_COUNT
  SIGNAL_ATTEMPTED=True;SIGNAL_COUNT+=1;signal.pidfd_send_signal(fd,signal.SIGTERM,None,0)
 def wait(fd):
  poll=select.poll();poll.register(fd,select.POLLIN);return bool(poll.poll(15000))
 phase='ONCE_FIXED_TREE_TERM'
 tree_contract.once_tree((5463,1373880),(5489,1373951),tree_before,orphan,reserve,lambda pid:os.pidfd_open(pid,0),send,wait,os.close)
 deadline=time.monotonic()+15
 while pathlib.Path('/proc/5489').exists()and time.monotonic()<deadline:time.sleep(.02)
 phase='AFTER_FIXED_TREE_TERM'
 assert not pathlib.Path('/proc/5489').exists()and not daemon.NameHasOwner(CHILD_BUS)
 after=data_post();assert after==data_post()
 with(save/'after.private.json').open('xb')as f:f.write(json.dumps(after,sort_keys=True).encode());f.flush();os.fsync(f.fileno())
 os.fsync(reservation_fd);os.close(reservation_fd);reservation_fd=None
'''


def payload():
    manifest=json.loads((W/'pg1059-cold-tree-preflight-v4/manifest.safe.json').read_bytes())
    if manifest['actualExit']!=0 or not manifest['observed']['observerNormalClose']:
        raise ValueError('qualified actual whole preflight required')
    prior=manifest['observed']['beforePrivateSha256']
    if prior!='ce521c73dc0f91d303065ddcb3f8f9c0350b0a142c6a17eb88a9798f1bb6e544':
        raise ValueError('fixed whole preflight reference refused')
    raw=previous().replace('PG1050-cold-tree-preflight-v1','PG1060-cold-owned-tree-handoff-v1')
    raw=raw.replace("/tree-preflight-v1'","/tree-preflight-v4/owned-tree-handoff-v1'")
    raw=raw.replace('import dbus,time,stat,re','import dbus,time,stat,re,signal,select')
    raw=raw.replace('socket_module=types.ModuleType',"tree_contract=types.ModuleType('tree_contract');exec(TREE_CONTRACT_SOURCE,tree_contract.__dict__)\nsocket_module=types.ModuleType")
    raw=raw.replace("held=[];refs=[];bus=None;manager=None;phase='ENTRY'",
                    "RESERVATION_ATTEMPTED=False;SIGNAL_ATTEMPTED=False;SIGNAL_COUNT=0;reservation_fd=None;CORE_COUNT=6\nheld=[];refs=[];bus=None;manager=None;phase='ENTRY'")
    raw=raw.replace('allheld=[h.capture()for h in held]','allheld=[h.capture()for h in held[:CORE_COUNT]]')
    start=" phase='WHOLE_TWO_READ';before=read();assert before==read()";end=" phase='OBSERVER_NORMAL_CLOSE'"
    if raw.count(start)!=1 or raw.count(end)!=1:
        raise ValueError('fixed tree body refused')
    raw=raw[:raw.index(start)]+HANDOFF+raw[raw.index(end):]
    tree=ast.parse(raw)
    final="print(json.dumps({'run':'PG1060-cold-owned-tree-handoff-v1','actualExit':0,'source':env['SOURCE'],'boot':env['BOOT'],'oldParentGone':True,'oldChildGone':True,'allOldClientsAdvisoryAndFlocks0':True,'allOriginalsUnchangedTwice':True,'allTenColdFull32':True,'observerNormalClose':True,'oldOperationNormalClose':False,'oldTransportExit':None,'childExitUnknown':True,'childAlreadyGone':CHILD_ALREADY_GONE,'signalsAttempted':SIGNAL_COUNT,'reservationDurable':True,'beforePrivateSha256':hashlib.sha256(private).hexdigest(),'afterPrivateSha256':hashlib.sha256(json.dumps(after,sort_keys=True).encode()).hexdigest(),'formalAccepted':False}))"
    tree.body[-1]=ast.parse(final).body[0]
    prefix='PRIOR_SHA='+repr(prior)+'\nTREE_CONTRACT_SOURCE='+repr(Path(__file__).with_name('pg1049_cold_tree_contract.py').read_text())+'\n'
    return prefix+ast.unparse(tree)


if __name__=='__main__':
    dispatch('PG1060-cold-owned-tree-handoff-v1','pg1060-cold-owned-tree-handoff-v1',payload())
