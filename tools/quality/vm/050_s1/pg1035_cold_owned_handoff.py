"""SSC244 fixed Java3091 noDB handoff, one pidfd TERM. No Unit/business mutation.

The old operation is UNKNOWN even after this new scope returns normally. A
reservation/send/post/close uncertainty retains this observer's References/FDs.
"""
import ast
from pg1002_cold_readonly import capture
from pg1033_cold_handoff_preflight_v6 import payload as previous


HANDOFF = r'''
 # New handoff directory is nested beneath the qualified preflight, so the
 # preservation ancestor's identity/metadata is not changed by our own receipt.
 CORE_COUNT=len(held)
 prior=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1033-cold-handoff-preflight-v6/before.private.json')
 prior_hash='1ca2ee1dda978bbe9fc12b7a7ead8f2a86689629f89e8320ac72295b0652e321'
 prior_size=prior.stat().st_size;require(0<prior_size<=33554432)
 proof=contract.HeldInventory(str(prior.parent),[{'path':prior.name,'size':prior_size,'sha256':prior_hash}],0).open_file();held.append(proof)
 prior_bytes=prior.read_bytes();require(hashlib.sha256(prior_bytes).hexdigest()==prior_hash);prior_value=json.loads(prior_bytes)
 require(metadata(save)[2:6]==[0,0,stat.S_IFDIR|0o700,2]and not os.listxattr(save))
 reservation_fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 def verify_owned(pid,ticks):
  require(pid==3091 and ticks==835207);proof.capture();value=read();require(value==prior_value);return value
 def reserve_owned(pid,value):
  global RESERVATION_ATTEMPTED
  require(pid==3091 and value==prior_value);RESERVATION_ATTEMPTED=True
  contract.durable_reservation(reservation_fd,'3091.term-reserved.private.json',json.dumps(value['actor'],sort_keys=True).encode())
 def send_owned(fd):
  global SIGNAL_ATTEMPTED
  SIGNAL_ATTEMPTED=True;signal.pidfd_send_signal(fd,signal.SIGTERM,None,0)
 def wait_owned(fd):
  poll=select.poll();poll.register(fd,select.POLLIN);return bool(poll.poll(15000))
 phase='BEFORE_FIXED_TERM';before=verify_owned(3091,835207);require(before==verify_owned(3091,835207))
 phase='ONCE_FIXED_TERM'
 contract.terminate_once(3091,835207,verify_owned,reserve_owned,lambda pid:os.pidfd_open(pid,0),send_owned,wait_owned,os.close)
 deadline=time.monotonic()+15
 while pathlib.Path('/proc/3091').exists()and time.monotonic()<deadline:time.sleep(.02)
 require(not pathlib.Path('/proc/3091').exists());OWNER_PID=0
 phase='AFTER_FIXED_TERM'
 def post():
  require(not pathlib.Path('/proc/3091').exists());proof.capture();c=controls();v=snapshot()
  require(v==before['snapshot']and c==before['controls'])
  for h in held:h.capture()
  s=pathlib.Path('/opt/schubert-nk/current').lstat()
  value=safe_json({'snapshot':v,'controls':c,'heldWholeMetadata':[h.capture()for h in held[:CORE_COUNT]],
   'selectorMetadata':metadata(pathlib.Path('/opt/schubert-nk')),
   'selectorLinkMetadata':[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]})
  expected={k:v for k,v in before.items()if k!='actor'};require(value==expected)
  return value
 after=post();require(after==post())
'''


def payload():
    raw = previous()
    old = 'owned_flocks=locks_module.owned_flocks'
    new = "def owned_flocks(lines,m,pid):\n if pid==0:return contract.free_flocks(lines,m)\n return locks_module.owned_flocks(lines,m,pid)"
    if raw.count(old) != 1:
        raise ValueError('fixed kernel dispatch refused')
    raw = raw.replace(old, new)
    raw = raw.replace('import types,sys,time,dbus', 'import types,sys,time,dbus,signal,select')
    raw = raw.replace("save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1033-cold-handoff-preflight-v6')",
                      "save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1033-cold-handoff-preflight-v6/handoff-v1')")
    raw = raw.replace('held=[];refs=[];bus=None;manager=None;phase=',
                      'RESERVATION_ATTEMPTED=False;SIGNAL_ATTEMPTED=False;reservation_fd=None;CORE_COUNT=0\nheld=[];refs=[];bus=None;manager=None;phase=')
    raw = raw.replace('[h.capture()for h in held]', '[h.capture()for h in held[:CORE_COUNT]]')
    old = " phase='INDEPENDENT_TWO_READ';before=read();after=read();require(before==after)"
    if raw.count(old) != 1:
        raise ValueError('fixed once handoff insertion refused')
    raw = raw.replace(old, HANDOFF.rstrip())
    raw = raw.replace('failed=failure;failed_phase=phase',
                      'failed=failure;failed_phase=phase\n if RESERVATION_ATTEMPTED:retain(failure)')
    raw = raw.replace(' for h in reversed(held):h.close()',
                      ' if reservation_fd is not None:os.close(reservation_fd)\n for h in reversed(held):h.close()')
    raw = raw.replace('PG1033_REFUSED', 'PG1035_REFUSED').replace('PG1028_CLOSE_UNKNOWN', 'PG1035_HANDOFF_UNKNOWN')
    marker = "private=json.dumps(before,sort_keys=True).encode()"
    if raw.count(marker) != 1:
        raise ValueError('fixed receipt material refused')
    raw = raw.replace(marker, marker + "\nafter_private=json.dumps(after,sort_keys=True).encode()\nwith(save/'after.private.json').open('xb')as f:f.write(after_private);f.flush();os.fsync(f.fileno())")
    # Do not copy the preflight result booleans after actually signalling.
    tree = ast.parse(raw)
    final = tree.body[-1]
    if not isinstance(final, ast.Expr) or not isinstance(final.value, ast.Call):
        raise ValueError('fixed final receipt refused')
    receipt = "print(json.dumps({'run':'PG1035-cold-owned-handoff-v1','actualExit':0,'boot':BOOT,'source':SOURCE,'oldActorPID':3091,'oldActorTicks':835207,'oldActorGone':True,'oldFlocks0':True,'allOriginalsUnchangedTwice':True,'allApplicationDBClients0':True,'allTenColdFull32':True,'signalAttempted':SIGNAL_ATTEMPTED,'reservationDurable':True,'observerScopesReturnedNormally':True,'oldOperationNormalClose':False,'oldTransportExit':None,'handoffOnly':True,'fullColdPreparationAccepted':False,'formalAccepted':False,'beforePrivateSha256':hashlib.sha256(private).hexdigest(),'afterPrivateSha256':hashlib.sha256(after_private).hexdigest()}))"
    tree.body[-1] = ast.parse(receipt).body[0]
    raw = ast.unparse(tree)
    ast.parse(raw)
    return raw


if __name__ == '__main__':
    capture('pg1035-cold-owned-handoff-v1', payload())
