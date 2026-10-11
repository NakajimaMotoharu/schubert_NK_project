"""Exact proved pre-stop Ref then Java ordinary TERM, old close UNKNOWN preserved.

SS343/353/SSC214/265/266 QA047; no service/epoch/intent/DB write or Root replay.
"""
import ast
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import SSH,W
import pg1498_retained_pair_readonly_proof as proof

EXTRA=r'''
HANDOFF=BASE/'pg1499-retained-publication-pair-handoff-v1'
require(not os.path.lexists(HANDOFF))
old_raw=(BASE/'pg1498-retained-publication-pair-proof-v1/proof.private.json').read_bytes()
require(hashlib.sha256(old_raw).hexdigest()=='b76ba20d9c058cbf07f37f47356ba472bc33270d6bfdac9a804a64584923efba')
old_proof=json.loads(old_raw);require(old_proof['stopReservations0']is True and old_proof['oldNormalCloseUnknown']is True)
first=snapshot();require(first==snapshot()==old_proof['current']);validate_current(first)
owned=pair();require(owned==old_proof['pair']and owned==pair())
def same_peer():
 sql="begin read only;select json_build_object('pid',pid,'port',client_port,'address',client_addr::text)from pg_stat_activity where pid="+str(BACKEND)+"and usename='schubert_batch'and application_name='PG266-publication-recover';commit;"
 lines=command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],4096).splitlines();require(len(lines)==1)
 peer=json.loads(lines[0]);require(peer['pid']==BACKEND and peer['address']=='127.0.0.1'and type(peer['port'])is int and 1<=peer['port']<=65535)
 def socket_ids(pid):
  found=[]
  for fd in(pathlib.Path('/proc')/str(pid)/'fd').iterdir():
   target=str(fd.readlink());m=re.fullmatch(r'socket:\[([0-9]+)\]',target)
   if m:found.append(m[1])
  return found
 client=socket_ids(92297);server=socket_ids(BACKEND);port='0100007F:'+format(peer['port'],'04X')
 records=[line.split()for line in pathlib.Path('/proc/net/tcp').read_text().splitlines()[1:]]
 require(sum(len(r)>=10 and r[1]==port and r[2]=='0100007F:1538'and r[3]=='01'and r[9]in client for r in records)==1)
 require(sum(len(r)>=10 and r[1]=='0100007F:1538'and r[2]==port and r[3]=='01'and r[9]in server for r in records)==1)
 return peer
same_peer()
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
for unit in UNITS:manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)
HANDOFF.mkdir(mode=0o700)
def save(name,data):
 with(HANDOFF/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(data);f.flush();os.fsync(f.fileno())
 fd=os.open(HANDOFF,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
def reserve(pid,before):save(str(pid)+'.term-once.private',json.dumps({'fixedOwnedTermOnce':True,'pid':pid,'before':before},sort_keys=True).encode())
def wait(fd):
 import select
 p=select.poll();p.register(fd,select.POLLIN);require(bool(p.poll(30000)));return True
def send(fd):
 import signal
 signal.pidfd_send_signal(fd,signal.SIGTERM,None,0)
def before_child(pid,ticks):
 require(pid==92323 and ticks==CHILD_TICKS)
 current=snapshot();require(current==snapshot()==first);validate_current(current);require(pair()==owned)
 same_peer()
 return owned['child']
def parent_after_child(pid=92297,ticks=1431673):
 require(pid==92297 and ticks==1431673)
 current=snapshot();require(current==snapshot()==first);validate_current(current)
 parent=process(92297,1431673,expected_args);require(parent['children']==[]and not pathlib.Path('/proc/92323').exists())
 fixed=dict(owned['parent']);fixed.pop('locks');fixed['children']=[]
 # Java's Process pipe reaper may normally close only the child's known stdin/stdout pipes.
 old_fds=fixed.pop('fds');actual_fds=parent.pop('fds');require(set(actual_fds)<=set(old_fds))
 require(all(actual_fds[k]==old_fds[k]for k in actual_fds))
 child_pipes={owned['child']['fds'][k]for k in ['0','1']};require(all(old_fds[k]in child_pipes for k in set(old_fds)-set(actual_fds)))
 require(parent==fixed)
 locks.owned_flocks(pathlib.Path('/proc/locks').read_text().splitlines(),owned['parent']['locks'],92297);peer_check()
 same_peer()
 daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus')
 require(not any(daemon.NameHasOwner(n)for n in owned['child']['busNames']))
 return parent
contract.terminate_once(92323,CHILD_TICKS,before_child,reserve,os.pidfd_open,send,wait,os.close)
parent_after_child()
contract.terminate_once(92297,1431673,parent_after_child,reserve,os.pidfd_open,send,wait,os.close)
require(not pathlib.Path('/proc/92297').exists()and not pathlib.Path('/proc/92323').exists())
PEER_CLOSED=True;peer_check()
for path,m in owned['parent']['locks'].items():
 require(metadata(ROOT/path)==m)
 for line in pathlib.Path('/proc/locks').read_text().splitlines():
  fields=line.split()
  if len(fields)==8 and fields[1]=='FLOCK':
   dev=fields[5].split(':');require((int(dev[0],16),int(dev[1],16),int(dev[2]))!=(os.major(m[0]),os.minor(m[0]),m[1]))
after=snapshot();require(after==snapshot()==first);validate_current(after)
save('after.private.json',json.dumps(after,sort_keys=True).encode())
for unit in reversed(refs):manager.UnrefUnit(unit)
refs=[];bus.close()
save('complete.private',b'exactRefThenJavaOwnedTerm=true\nallOriginalDbEpochNativeUnchanged=true\noldCloseUnknown=true\nserviceStops0=true\n')
print(json.dumps({'actualExit':0,'refThenJavaOwnedTerm':True,'parentPeerAdvisoryMAAndChildBusGone':True,'allOriginalDbEpochNativeUnchanged':True,'independentMetadataRefsNormalClosed':True,'oldCloseUnknown':True,'serviceStops0':True,'afterSha256':hashlib.sha256(json.dumps(after,sort_keys=True).encode()).hexdigest(),'formalAccepted':False}))
'''

def payload():
    raw=proof.payload();start=raw.index('first=snapshot();require(first==snapshot());validate_current(first);a=pair();')
    return raw[:start]+EXTRA

def main():
    os.umask(0o077);out=W/'pg1499-retained-publication-pair-handoff-v1';out.mkdir(mode=0o700)
    previous=json.loads((W/'pg1498-retained-publication-pair-proof-v1/manifest.safe.json').read_bytes());assert previous['actualExit']==0 and previous['guest']['proofSha256']=='b76ba20d9c058cbf07f37f47356ba472bc33270d6bfdac9a804a64584923efba'
    # Reuse exactly the proved entry bindings; never reconstruct credentials or invent authority.
    saved=(W/'pg1498-retained-publication-pair-proof-v1/payload.private.py').read_text();t=ast.parse(saved)
    bindings=[n for n in t.body if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id in {'EXPECTED_ARGS','FROZEN_HASHES','CHILD_TICKS'}for x in n.targets)]
    assert len(bindings)==3
    raw=ast.unparse(ast.Module(body=bindings,type_ignores=[]))+'\n'+payload();compile(raw,'<fixed once pair handoff>','exec')
    (out/'payload.private.py').write_text(raw)
    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw.encode(),capture_output=True,timeout=180)
    (out/'stderr.private.log').write_bytes(r.stderr)
    result={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'oldCloseUnknown':True,'serviceStops0':True,'formalAccepted':False}
    if r.returncode==0:result['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(result));return r.returncode

if __name__=='__main__':raise SystemExit(main())
