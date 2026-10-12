"""SSC279 once Ref then Java normal TERM, genuine host exclusion retained.

No service stop/start, SQL mutation, Root replay, hotpatch or UNKNOWN success.
Fresh full101/4FD/samepeer proof precedes each pidfd/one-shot reservation.
"""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import SSH,W,P
from pg1674_critical_management_gate import management_gate
from pg1782_warning_live_peer_proof_direct import payload as proof_payload

SLOT='pg1784-warning-pair-once-handoff-v1'

BODY=r'''
CHILD_REAPED=False
HANDOFF=BASE/'pg1784-warning-pair-once-handoff-v1'
old_raw=(BASE/'pg1782-warning-live-peer-readonly-v1/proof.private.json').read_bytes()
require(hashlib.sha256(old_raw).hexdigest()=='4c226a4e958291f100b1b20e05ff854dda3e511e1cdc58d16cb11bfb85834a6d')
old=json.loads(old_raw);require(old['stopReservations0']is True and old['serviceStops0']is True and old['oldCloseUnknown']is True)
def same(a,b):return json.dumps(a,sort_keys=True,separators=(',',':'))==json.dumps(b,sort_keys=True,separators=(',',':'))
def original():require(capture()==old['fullCurrent'])
def pair():
 parent=recovery_actor();require(same(parent,old['parent']));require(same(ref_child(parent),old['child']));require(same(same_peer(),old['peer']))
 require(same([owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']],old['locks']))
 return parent
def reserve(pid):
 with(HANDOFF/(str(pid)+'.term-once.private')).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(json.dumps({'pid':pid,'normalTermOnce':True,'proofSha256':hashlib.sha256(old_raw).hexdigest()},sort_keys=True).encode());f.flush();os.fsync(f.fileno())
 fd=os.open(HANDOFF,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
def tick(pid):return int((pathlib.Path('/proc')/str(pid)/'stat').read_text().rpartition(')')[2].split()[19])
def terminate(pid,ticks,guard):
 import select,signal
 guard();require(tick(pid)==ticks);fd=os.pidfd_open(pid)
 try:
  guard();require(tick(pid)==ticks);reserve(pid);signal.pidfd_send_signal(fd,signal.SIGTERM,None,0)
  poll=select.poll();poll.register(fd,select.POLLIN);require(bool(poll.poll(15000)))
 finally:os.close(fd)
 deadline=time.monotonic()+30
 while pathlib.Path('/proc',str(pid)).exists():
  try:require(tick(pid)==ticks)
  except OSError as e:
   if e.errno in (2,3)and not pathlib.Path('/proc',str(pid)).exists():break
   raise
  require(time.monotonic()<deadline);time.sleep(.05)
def before_child():original();pair()
def parent_image_after_child():
 require(not pathlib.Path('/proc/476116').exists())
 # All remaining parent FD values stay exact. Only the known child stdin/out
 # pipe FDs may have been normally closed by Java's process pipe reaper.
 p=pathlib.Path('/proc/476087');require(tick(476087)==8492401 and(p/'cmdline').read_bytes()==EXPECTED_ARGV)
 status=dict(l.split(':',1)for l in(p/'status').read_text().splitlines()if ':'in l)
 require({int(c)for t in(p/'task').iterdir()for c in(t/'children').read_text().split()}==set())
 current={'pid':476087,'ticks':8492401,'argvSha256':hashlib.sha256(EXPECTED_ARGV).hexdigest(),'authority':{k:status[k].strip()for k in ['Uid','Gid','Groups','NoNewPrivs','CapInh','CapPrm','CapEff','CapBnd','CapAmb','PPid']},'cgroup':(p/'cgroup').read_text(),'fds':{f.name:{'metadata':metadata9(f.stat()),'target':os.readlink(f)}for f in(p/'fd').iterdir()}}
 expected=dict(old['parent']);fds=expected.pop('fds');actual=current.pop('fds');require(same(current,expected)and set(actual)<=set(fds))
 require(all(same(v,fds[k])for k,v in actual.items()))
 pipes={old['child']['fds'][k]['target']for k in ['0','1']};require(all(fds[k]['target']in pipes for k in set(fds)-set(actual)))
 return {**current,'fds':actual}
def actor_for_locks():
 return parent_image_after_child()if CHILD_REAPED else recovery_actor()
def parent_after_child():
 original();parent_image_after_child()
 daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus')
 require(not any(daemon.NameHasOwner(n)for n in old['child']['busNames']))
 require(same([owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']],old['locks'])and same(same_peer(),old['peer']))
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for unit in UNITS:manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)
 before_child();HANDOFF.mkdir(mode=0o700)
 with(HANDOFF/'fresh-before.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(json.dumps({'parent':pair(),'proof':old},sort_keys=True).encode());f.flush();os.fsync(f.fileno())
 terminate(476116,8492565,before_child)
 CHILD_REAPED=True
 parent_after_child()
 terminate(476087,8492401,parent_after_child)
 require(not pathlib.Path('/proc/476116').exists()and not pathlib.Path('/proc/476087').exists())
 q="begin read only;select count(*)from pg_stat_activity where datname='schubert_nk'and usename in ('schubert_batch','schubert_migration');select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;commit;"
 require(command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],4096).splitlines()==[b'0',b'0'])
 for lock in old['locks']:
  require(metadata9(pathlib.Path('/run/schubert-nk',lock['name']).lstat())==tuple(lock['metadata']))
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   fields=line.split()
   if len(fields)<8:continue
   d=fields[5].split(':');require(len(d)!=3 or (int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(lock['metadata'][0]),os.minor(lock['metadata'][0]),lock['metadata'][1]))
 after=capture();require(after==old['fullCurrent'])
 # Standard daemon DB sockets are still bound to their original service owner.
 q="begin read only;select json_build_object('pid',pid,'port',client_port,'role',usename)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid()order by pid;commit;"
 peers=[json.loads(l)for l in command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q],4096).splitlines()]
 expected=[{k:r[k]for k in ['pid','port','role']}for r in old['peer']['allPeers']if r['role']!='schubert_batch'];require(peers==expected)
 with(HANDOFF/'after.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(json.dumps(after,sort_keys=True).encode());f.flush();os.fsync(f.fileno())
finally:
 for unit in reversed(refs):manager.UnrefUnit(unit)
 bus.close()
with(HANDOFF/'complete.private').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(b'normalRefThenJavaTermOnce=true\nmanagementPeerAdvisoryMA0=true\nliveDaemonAndAllOriginalValuesPreserved=true\nnewObserverReferencesReturnedNormally=true\noldCloseUnknown=true\nserviceStartsStops0=true\n');f.flush();os.fsync(f.fileno())
fd=os.open(HANDOFF,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'normalRefThenJavaTermOnce':True,'managementPeerAdvisoryMA0':True,'liveDaemonPeersPreserved':True,'all24Config32Signed187OriginalBackupNativeUnchanged':True,'newObserverReferencesReturnedNormally':True,'oldCloseUnknown':True,'serviceStartsStops0':True,'afterSha256':hashlib.sha256((HANDOFF/'after.private.json').read_bytes()).hexdigest(),'formalAccepted':False}))
'''


def payload():
    raw=proof_payload();marker='bus=dbus.SystemBus(private=True);manager='
    at=raw.index(marker);raw=raw[:at]+BODY
    marker='actual=recovery_actor();linked='
    if raw.count(marker)!=1:raise ValueError('one allFD lock actor boundary required')
    raw=raw.replace(marker,'actual=actor_for_locks();linked=')
    from pyflakes.api import check
    if check(raw,'<actual once pair handoff>'):raise ValueError('emitted globals required')
    compile(raw,'<actual once pair handoff>','exec');return raw


def main():
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode()
    (out/'payload.private.py').write_bytes(raw)
    with management_gate(P/'current-management-critical.lock')as fd:
        s=os.fstat(fd);gate={'pid':os.getpid(),'device':s.st_dev,'inode':s.st_ino,'held':True}
        r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=240)
    (out/'stderr.private.log').write_bytes(r.stderr)
    result={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'hostGate':gate,'oldNormalCloseUnknown':True,'formalAccepted':False}
    if r.returncode==0:result['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(result));return r.returncode


if __name__=='__main__':raise SystemExit(main())
