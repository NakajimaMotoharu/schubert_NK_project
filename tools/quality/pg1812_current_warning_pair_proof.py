"""Same current pair/full proof with approved ordinary pool bounds only."""
import ast
import hashlib
import inspect
import json
import os
import subprocess
from pg1810_typed_current_warning_pair_proof import payload as previous_payload
from pg1812_warning_pool_contract import validate_current_peers
from pg1805_retained_stop_readonly_diagnosis import owner,SSH,W

SLOT='pg1812-current-warning-pair-proof-v1'


def payload():
    raw=previous_payload();tree=ast.parse(raw)
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='validate_peers')
    raw=raw.replace(ast.get_source_segment(raw,node),inspect.getsource(validate_current_peers)+"\ndef validate_peers(rows,lock_count):return validate_current_peers(rows,lock_count,CURRENT_BACKEND)\n")
    marker="require(len(lines) == 5 and lines[-1] == b'1')"
    if raw.count(marker)!=1:raise ValueError('one fixed current query population gate required')
    raw=raw.replace(marker,"require(5 <= len(lines) <= 12 and lines[-1] == b'1')").replace('pg1810-typed-current-warning-pair-proof-v1',SLOT)
    raw=raw.replace("'allFourCurrentPeersSocketBound': True","'allCurrentPeersSocketBound': True, 'peerCount': len(peer['allPeers'])")
    from pyflakes.api import check
    if check(raw,'<SSC281 current all-peer proof>'):raise ValueError('closed actual emitted globals required')
    compile(raw,'<actual approved pool proof>','exec');return raw


def main():
    os.umask(0o077);before=owner();out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode();(out/'payload.private.py').write_bytes(raw)
    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=120)
    (out/'stderr.private.log').write_bytes(r.stderr)
    if before!=owner():raise ValueError('fixed retained host owner changed')
    value={'actualExit':r.returncode,'hostRetainedOwner':before,'payloadSha256':hashlib.sha256(raw).hexdigest(),'signals0':True,'formalAccepted':False}
    if r.returncode==0:value['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
