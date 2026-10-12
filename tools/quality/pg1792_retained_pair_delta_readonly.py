"""Diagnosed current pair delta; field names only, no signal or mutation authority."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import SSH,W
from pg1782_warning_live_peer_proof_direct import payload as proof_payload

SLOT='pg1792-retained-pair-delta-readonly-v1'
BODY=r'''
saved=json.loads((BASE/'pg1782-warning-live-peer-readonly-v1/proof.private.json').read_bytes())
parent=recovery_actor();child=ref_child(parent);peer=same_peer()
def norm(v):return json.loads(json.dumps(v,sort_keys=True))
def changes(a,b):return sorted(k for k in set(a)|set(b)if a.get(k)!=b.get(k))
parent=norm(parent);child=norm(child);peer=norm(peer)
result={'parentTopChanges':changes(saved['parent'],parent),'childTopChanges':changes(saved['child'],child),'peerTopChanges':changes(saved['peer'],peer),'parentFdChanges':[],'childFdChanges':[],'signals0':True,'formalAccepted':False}
for name,actual in [('parent',parent),('child',child)]:
 for fd in sorted(set(saved[name]['fds'])|set(actual['fds']),key=int):
  oldfd=saved[name]['fds'].get(fd);newfd=actual['fds'].get(fd)
  if oldfd==newfd:continue
  result[name+'FdChanges'].append({'fd':fd,'presentBefore':oldfd is not None,'presentNow':newfd is not None,'targetChanged':oldfd is None or newfd is None or oldfd['target']!=newfd['target'],'metadataIndexes':[i for i in range(9)if oldfd and newfd and oldfd['metadata'][i]!=newfd['metadata'][i]]})
out=BASE/'pg1792-retained-pair-delta-readonly-v1';out.mkdir(mode=0o700)
with(out/'current.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(json.dumps({'parent':parent,'child':child,'peer':peer},sort_keys=True).encode());f.flush();os.fsync(f.fileno())
fd=os.open(out,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
result['privateSha256']=hashlib.sha256((out/'current.private.json').read_bytes()).hexdigest()
print(json.dumps(result))
'''


def payload():
    raw=proof_payload();raw=raw[:raw.index('bus=dbus.SystemBus(private=True);manager=')]
    raw=raw.replace("SAVE=BASE/'pg1782-warning-live-peer-readonly-v1'","SAVE=BASE/"+repr(SLOT))
    # ref_child needs a fresh independent readonly bus for child name lookup.
    raw+="bus=dbus.SystemBus(private=True)\ntry:\n"+'\n'.join(' '+l if l else l for l in BODY.splitlines())+"\nfinally:bus.close()\n"
    from pyflakes.api import check
    if check(raw,'<pair field-delta readonly>'):raise ValueError('actual emitted globals required')
    compile(raw,'<diagnostic pair readonly>','exec');return raw


def main():
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode()
    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=30)
    (out/'stderr.private.log').write_bytes(r.stderr)
    result={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'signals0':True}
    if r.returncode==0:result['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(result));return r.returncode


if __name__=='__main__':raise SystemExit(main())
