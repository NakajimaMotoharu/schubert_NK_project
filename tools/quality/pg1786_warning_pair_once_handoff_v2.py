"""New-only recovery namespace fix; original1784 signal0 failure immutable."""
import ast
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import SSH,W,P
from pg1674_critical_management_gate import management_gate
from pg1784_warning_pair_once_handoff import payload as previous_payload

SLOT='pg1786-warning-pair-once-handoff-v2'


def payload():
    raw=previous_payload()
    nodes=[n for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='SAVE'for t in n.targets)]
    if len(nodes)!=2:raise ValueError('two explicit source SAVE declarations required')
    last=nodes[-1];old=ast.get_source_segment(raw,last)
    if ast.unparse(last)!="SAVE = BASE / 'pg1782-warning-live-peer-readonly-v1'":raise ValueError('actual immutable proof SAVE boundary required')
    raw=raw.replace(old,"SAVE=BASE/"+repr(SLOT),1)
    raw=raw.replace('pg1784-warning-pair-once-handoff-v1',SLOT)
    from pyflakes.api import check
    if check(raw,'<new once handoff namespace>'):raise ValueError('all emitted globals required')
    compile(raw,'<fixed new recovery namespace>','exec');return raw


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
