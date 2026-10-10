"""SSC252 fixed20312 read-only retained observer retirement, no business start."""
import ast
import hashlib
import json
from pathlib import Path
from pg1103_linked_preservation_post import payload as previous
from pg1050_cold_tree_preflight import BODY as old_body
from pg1051_cold_tree_preflight_v2 import dispatch
from pg1041_cold_policy_diagnostic import W


def payload():
    root=W/'pg1108-cold-ordinary-once-v1';begin=json.loads((root/'begin.safe.json').read_bytes())
    if begin['operatorSource']!='296ad46bc9b0adbcca07688b729b6ddc26e50322' or begin['scriptSha256']!='5f4c9fc66b9ab0ce8960846208c9ea80f561cc332d79b5884ba4ef5606a0c19f':raise ValueError('fixed old source required')
    if hashlib.sha256((root/'guest-script.private.py').read_bytes()).hexdigest()!=begin['scriptSha256'] or hashlib.sha256((root/'result.private.log').read_bytes()).hexdigest()!='09e5fedd9400be084fb71a7d316243c1a4cfc63afe9f4cf6e01318ac142f438f':raise ValueError('fixed old witness required')
    raw=previous().replace('PG1103-linked-preservation-post-v1','PG1110-readonly-once-retirement-v1').replace('/var/lib/pgpt-s1-preservation/pg1103-newcurrent-post-v1','/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/readonly-retirement-v1')
    actor=next(n for n in ast.parse(old_body).body if isinstance(n,ast.FunctionDef)and n.name=='actor')
    marker='def post():\n'
    if raw.count(marker)!=1:raise ValueError('fixed retirement helper insertion refused')
    raw=raw.replace(marker,ast.unparse(actor)+'\n'+HELPERS+'\n'+marker)
    start=" phase='WHOLE_POST';after=post();assert after==post()"
    end=" phase='NORMAL_CLOSE'"
    if raw.count(start)!=1 or raw.count(end)!=1:raise ValueError('fixed retirement phase refused')
    raw=raw[:raw.index(start)]+HANDOFF+raw[raw.index(end):]
    raw=raw.replace("'current1068FullSigned':True", "'current1068FullSigned':True,'oldReadonlyActorGone':True,'oldBusGone':True,'signalCount':SIGNALS,'oldNormalClose':False")
    return 'import signal,select\nSIGNALS=0\n'+raw


HELPERS=r'''
def metadata_actor():
 value=actor(20312,3250518,'5a5cff3ba9f3379bceb96da8fda3ef4a6ab51547f4b5cd0c1d9305e99b4c2ad0','/usr/bin/python3.14',set(),20310)
 assert len(value['fds'])==452
 assert not os.path.lexists('/var/lib/pgpt-s1-preservation/pg1108-ordinary-cold-once-v1/external-start-guard.private.json')
 failed=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1108-ordinary-cold-once-v1')
 assert env['metadata'](failed)[2:6]==[0,0,stat.S_IFDIR|0o700,2]and not list(failed.iterdir())and not os.listxattr(failed)
 assert int(daemon.GetConnectionUnixProcessID(OLD_BUS))==20312 and int(daemon.GetConnectionUnixUser(OLD_BUS))==0
 return value
def whole():return {'post':post(),'actor':metadata_actor(),'bus':OLD_BUS}
'''


HANDOFF=r'''
 phase='FIXED_READONLY_ACTOR'
 daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus')
 names=[str(n)for n in daemon.ListNames()if str(n).startswith(':')and int(daemon.GetConnectionUnixProcessID(n))==20312]
 assert len(names)==1;OLD_BUS=names[0]
 before=whole();assert before==whole();private=json.dumps(before,sort_keys=True).encode()
 with(save/'before.private.json').open('xb')as f:f.write(private);f.flush();os.fsync(f.fileno())
 reservation_fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(reservation_fd)
 def verify(pid,ticks):
  assert(pid,ticks)==(20312,3250518);value=whole();assert value==before;return value
 def reserve(pid,value):
  assert pid==20312 and value==before
  contract.durable_reservation(reservation_fd,'20312.term-reserved.private.json',json.dumps({'pid':pid,'ticks':3250518,'proofSha256':hashlib.sha256(private).hexdigest()},sort_keys=True).encode())
 def send(fd):
  global SIGNALS
  SIGNALS+=1;assert SIGNALS==1;signal.pidfd_send_signal(fd,signal.SIGTERM,None,0)
 def wait(fd):
  p=select.poll();p.register(fd,select.POLLIN);return bool(p.poll(15000))
 phase='ONCE_READONLY_TERM';contract.terminate_once(20312,3250518,verify,reserve,lambda pid:os.pidfd_open(pid,0),send,wait,os.close)
 until=time.monotonic()+15
 while pathlib.Path('/proc/20312').exists()and time.monotonic()<until:time.sleep(.02)
 phase='WHOLE_AFTER';assert not pathlib.Path('/proc/20312').exists()and not daemon.NameHasOwner(OLD_BUS)
 after=post();assert after==before['post']==post()
 private=json.dumps(after,sort_keys=True).encode()
 with(save/'after.private.json').open('xb')as f:f.write(private);f.flush();os.fsync(f.fileno())
 os.fsync(reservation_fd);os.close(reservation_fd)
'''


if __name__=='__main__':dispatch('PG1110-readonly-once-retirement-v1','pg1110-readonly-once-retirement-v1',payload())
