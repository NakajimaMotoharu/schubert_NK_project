"""Separate fresh readonly full post after completed once signals; never signal/replay.

Old1502 failed post/metadata close and old1495 Java143 remain UNKNOWN/failed.
"""
import ast
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import SSH,W
import pg1498_retained_pair_readonly_proof as proof

BODY=r'''
SAVE_POST=BASE/'pg1503-retained-publication-pair-closing-v1';require(not os.path.lexists(SAVE_POST))
old_raw=(BASE/'pg1498-retained-publication-pair-proof-v1/proof.private.json').read_bytes();require(hashlib.sha256(old_raw).hexdigest()=='b76ba20d9c058cbf07f37f47356ba472bc33270d6bfdac9a804a64584923efba')
old_proof=json.loads(old_raw);old_pair=old_proof['pair'];require(old_proof['stopReservations0']is True)
handoff=BASE/'pg1502-retained-publication-pair-handoff-v4'
require(set(p.name for p in handoff.iterdir())=={'92297.term-once.private','92323.term-once.private'})
for pid in [92323,92297]:
 record=json.loads((handoff/(str(pid)+'.term-once.private')).read_bytes());require(record['fixedOwnedTermOnce']is True and record['pid']==pid and record['before']['pid']==pid)
 # No signal: terminal/reap observation is a separate bounded postcondition.
 deadline=time.monotonic()+30
 while pathlib.Path('/proc',str(pid)).exists()and time.monotonic()<deadline:time.sleep(.05)
 require(not pathlib.Path('/proc',str(pid)).exists())
PEER_CLOSED=True;peer_check()
require(contract.free_flocks(pathlib.Path('/proc/locks').read_text().splitlines(),old_pair['parent']['locks']))
for name,value in old_pair['parent']['locks'].items():require(metadata(ROOT/name)==value)
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus')
 require(not any(daemon.NameHasOwner(n)for n in old_pair['child']['busNames']))
 for unit in UNITS:manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)
 first=snapshot();second=snapshot();require(first==second==old_proof['current']);validate_current(first)
 require(not any(SAVE.glob('*.stop-reserved.private'))and not any(SAVE.glob('*.stopped.private'))and not(SAVE/'complete.private').exists())
 SAVE_POST.mkdir(mode=0o700);encoded=json.dumps(first,sort_keys=True).encode()
 with(SAVE_POST/'after.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
 for unit in reversed(refs):manager.UnrefUnit(unit)
 refs=[];bus.close();bus=None
 with(SAVE_POST/'complete.private').open('xb')as f:f.write(b'independentFullReadonlyClosing=true\nmanagementPairPeerAdvisoryMABusGone=true\noldNormalCloseUnknown=true\n');f.flush();os.fsync(f.fileno())
 fd=os.open(SAVE_POST,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
finally:
 if refs:raise ValueError('new readonly metadata references not normally returned')
 if bus is not None:bus.close()
print(json.dumps({'actualExit':0,'full24DbTenFull32Signed187OriginalBackupCredentialNativeUnchanged':True,'managementPairPeerAdvisoryMABusGone':True,'newMetadataRefsNormalClosed':True,'oldNormalCloseUnknown':True,'root1456StillFailed':True,'brokerStillActive':True,'afterSha256':hashlib.sha256(encoded).hexdigest(),'signals0':True,'serviceStops0':True,'formalAccepted':False}))
'''

def payload():
    raw=proof.payload();start=raw.index('first=snapshot();require(first==snapshot());validate_current(first);a=pair();')
    prefix=raw[:start];prefix=prefix[prefix.index('import sys,subprocess\n')+len('import sys,subprocess\n'):]
    begin=prefix.index('q=subprocess.run(');end=prefix.index('sys.argv=',begin)
    prefix=prefix[:begin]+prefix[end:]
    end=prefix.index('\n',prefix.index('sys.argv='))
    prefix="import sys,subprocess\nsys.argv=['fixed-readonly-closing','verify','2']"+prefix[end:]
    marker='require(not os.path.lexists(PAIR_SAVE))';assert prefix.count(marker)==1
    prefix=prefix.replace(marker,'require(os.path.isdir(PAIR_SAVE))')
    return prefix+'\n'+BODY

def main():
    os.umask(0o077);out=W/'pg1503-retained-publication-pair-closing-v1';out.mkdir(mode=0o700)
    saved=(W/'pg1498-retained-publication-pair-proof-v1/payload.private.py').read_text();tree=ast.parse(saved)
    nodes=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in {'EXPECTED_ARGS','FROZEN_HASHES','CHILD_TICKS'}for t in n.targets)];assert len(nodes)==3
    raw=ast.unparse(ast.Module(body=nodes,type_ignores=[]))+'\n'+payload();compile(raw,'<fresh readonly pair fullclosing>','exec')
    (out/'payload.private.py').write_text(raw)
    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw.encode(),capture_output=True,timeout=90)
    (out/'stderr.private.log').write_bytes(r.stderr)
    result={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'signals0':True,'formalAccepted':False,'oldNormalCloseUnknown':True}
    if r.returncode==0:result['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(result));return r.returncode

if __name__=='__main__':raise SystemExit(main())
