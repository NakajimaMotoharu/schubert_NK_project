"""SSC246 fixed metadata7427 retirement only, old live Java/child/DB unchanged."""
import ast
import hashlib
import json
from pg1050_cold_tree_preflight import payload as previous
from pg1051_cold_tree_preflight_v2 import dispatch
from pg1041_cold_policy_diagnostic import W

HANDOFF = r'''
 phase='FIXED_METADATA_BEFORE'
 def metadata_actor():
  v=actor(7427,1860448,'5a5cff3ba9f3379bceb96da8fda3ef4a6ab51547f4b5cd0c1d9305e99b4c2ad0','/usr/bin/python3.14',set())
  assert len(v['fds'])==349
  assert int(daemon.GetConnectionUnixProcessID(METADATA_BUS))==7427 and int(daemon.GetConnectionUnixUser(METADATA_BUS))==0
  return v
 names=[str(n)for n in daemon.ListNames()if str(n).startswith(':')and int(daemon.GetConnectionUnixProcessID(n))==7427]
 assert len(names)==1;METADATA_BUS=names[0]
 def whole():
  return {'base':read(),'metadata':metadata_actor(),'bus':METADATA_BUS,
   'oldScriptSha256':OLD_SCRIPT_SHA,'oldLogSha256':OLD_LOG_SHA,'oldSource':OLD_SOURCE}
 before=whole();assert before==whole()
 private=json.dumps(before,sort_keys=True).encode()
 with(save/'before.private.json').open('xb')as f:f.write(private);f.flush();os.fsync(f.fileno())
 reservation_fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(reservation_fd)
 def verify(pid,ticks):
  assert pid==7427 and ticks==1860448
  current=whole();assert current==before;return current
 def reserve(pid,value):
  global RESERVATION_ATTEMPTED
  assert pid==7427 and value==before;RESERVATION_ATTEMPTED=True
  contract.durable_reservation(reservation_fd,'7427.term-reserved.private.json',json.dumps(
   {'pid':7427,'ticks':1860448,'argvSha256':value['metadata']['argvSha256'],'proofSha256':hashlib.sha256(private).hexdigest()},sort_keys=True).encode())
 def send(fd):
  global SIGNAL_ATTEMPTED
  SIGNAL_ATTEMPTED=True;signal.pidfd_send_signal(fd,signal.SIGTERM,None,0)
 def wait(fd):
  poll=select.poll();poll.register(fd,select.POLLIN);return bool(poll.poll(15000))
 phase='ONCE_METADATA_TERM'
 contract.terminate_once(7427,1860448,verify,reserve,lambda pid:os.pidfd_open(pid,0),send,wait,os.close)
 deadline=time.monotonic()+15
 while pathlib.Path('/proc/7427').exists()and time.monotonic()<deadline:time.sleep(.02)
 phase='AFTER_METADATA_TERM'
 def post():
  assert not pathlib.Path('/proc/7427').exists()and not daemon.NameHasOwner(METADATA_BUS)
  v=read();assert v==before['base'];return v
 after=post();assert after==post()
 with(save/'after.private.json').open('xb')as f:f.write(json.dumps(after,sort_keys=True).encode());f.flush();os.fsync(f.fileno())
 os.fsync(reservation_fd);os.close(reservation_fd);reservation_fd=None
'''


def payload():
    oldroot=W/'pg1055-cold-tree-preflight-v3'
    begin=json.loads((oldroot/'begin.safe.json').read_bytes())
    script=(oldroot/'guest-script.private.py').read_bytes()
    log=(oldroot/'result.private.log').read_bytes()
    if begin['operatorSource']!='da73f7001' and not begin['operatorSource'].startswith('da73f7001'):
        raise ValueError('fixed old metadata source required')
    if hashlib.sha256(script).hexdigest()!=begin['scriptSha256']:
        raise ValueError('old metadata script changed')
    lines=[json.loads(line)for line in log.splitlines()]
    if (lines[0]['phase']!='WHOLE_TWO_READ' or lines[0]['type']!='ValueError'
            or not lines[0]['ownershipRetained'] or lines[0]['signalAttempted']):
        raise ValueError('fixed old failure witness required')
    raw=previous().replace('PG1050-cold-tree-preflight-v1','PG1056-cold-metadata-handoff-v1')
    raw=raw.replace("/tree-preflight-v1'","/tree-preflight-v3/metadata-handoff-v1'")
    raw=raw.replace('import dbus,time,stat,re','import dbus,time,stat,re,signal,select')
    raw=raw.replace("held=[];refs=[];bus=None;manager=None;phase='ENTRY'",
                    "RESERVATION_ATTEMPTED=False;SIGNAL_ATTEMPTED=False;reservation_fd=None\nheld=[];refs=[];bus=None;manager=None;phase='ENTRY'")
    start=" phase='WHOLE_TWO_READ';before=read();assert before==read()"
    end=" phase='OBSERVER_NORMAL_CLOSE'"
    if raw.count(start)!=1 or raw.count(end)!=1:
        raise ValueError('fixed metadata handoff body required')
    raw=raw[:raw.index(start)]+HANDOFF+raw[raw.index(end):]
    tree=ast.parse(raw)
    final="print(json.dumps({'run':'PG1056-cold-metadata-handoff-v1','actualExit':0,'source':env['SOURCE'],'boot':env['BOOT'],'oldMetadataPid':7427,'oldMetadataGone':True,'oldMetadataBusGone':True,'oldJava5463AndChild5489Unchanged':True,'sameReadOnlyServerPeerRetained':True,'allOriginalsUnchangedTwice':True,'observerNormalClose':True,'oldOperationNormalClose':False,'oldTransportExit':None,'signalAttempted':SIGNAL_ATTEMPTED,'reservationDurable':True,'beforePrivateSha256':hashlib.sha256(private).hexdigest(),'formalAccepted':False}))"
    tree.body[-1]=ast.parse(final).body[0]
    prefix='OLD_SOURCE='+repr(begin['operatorSource'])+'\nOLD_SCRIPT_SHA='+repr(begin['scriptSha256'])+'\nOLD_LOG_SHA='+repr(hashlib.sha256(log).hexdigest())+'\n'
    return prefix+ast.unparse(tree)


if __name__=='__main__':
    dispatch('PG1056-cold-metadata-handoff-v1','pg1056-cold-metadata-handoff-v1',payload())
