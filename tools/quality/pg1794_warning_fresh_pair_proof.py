"""SSC280 fresh all-FD image; history preserves immutables, not stale pool ids."""
import ast
import hashlib
import inspect
import json
import os
import subprocess
from pg1446_current_cold_stage import SSH,W
from pg1782_warning_live_peer_proof_direct import payload as previous_payload
from pg1793_warning_fresh_history_contract import same,match_parent_history,match_peer_history

SLOT='pg1794-warning-fresh-pair-readonly-v1'


def payload():
    raw=previous_payload()
    nodes=[n for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='SAVE'for t in n.targets)]
    old=ast.get_source_segment(raw,nodes[-1])
    if ast.unparse(nodes[-1])!="SAVE = BASE / 'pg1782-warning-live-peer-readonly-v1'":raise ValueError('one fixed actual writable SAVE required')
    raw=raw.replace(old,'SAVE=BASE/'+repr(SLOT),1)
    marker='bus=dbus.SystemBus(private=True);manager='
    at=raw.index(marker)
    funcs='\n'.join(inspect.getsource(f)for f in [same,match_parent_history,match_peer_history])
    raw=raw[:at]+funcs+'\n'+raw[at:]
    raw=raw.replace('require(parent==recovery_actor())','match_parent_history(parent,recovery_actor())')
    raw=raw.replace('require(peer==same_peer())','match_peer_history(peer,same_peer())')
    raw=raw.replace('require(parent==recovery_actor()and child==ref_child(parent))','match_parent_history(parent,recovery_actor());require(child==ref_child(parent))')
    marker=' SAVE.mkdir(mode=0o700)'
    if raw.count(marker)!=1:raise ValueError('one before-publication history join point required')
    extra="""
 history_raw=(BASE/'pg1782-warning-live-peer-readonly-v1/proof.private.json').read_bytes()
 require(hashlib.sha256(history_raw).hexdigest()=='4c226a4e958291f100b1b20e05ff854dda3e511e1cdc58d16cb11bfb85834a6d')
 history=json.loads(history_raw)
 match_parent_history(history['parent'],parent);match_peer_history(history['peer'],peer)
 require(same(history['child'],child)and same(history['locks'],locks)and current==history['fullCurrent'])
 parent=recovery_actor();peer=same_peer()
 match_parent_history(history['parent'],parent);match_peer_history(history['peer'],peer)
"""
    raw=raw.replace(marker,extra+marker)
    from pyflakes.api import check
    if check(raw,'<actual fresh invariant pair proof>'):raise ValueError('all emitted globals required')
    compile(raw,'<fresh complete retained pair proof>','exec');return raw


def main():
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode()
    (out/'payload.private.py').write_bytes(raw)
    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=90)
    (out/'stderr.private.log').write_bytes(r.stderr)
    result={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'signals0':True,'formalAccepted':False}
    if r.returncode==0:result['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(result));return r.returncode


if __name__=='__main__':raise SystemExit(main())
