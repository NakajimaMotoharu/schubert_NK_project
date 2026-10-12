"""Direct new-only once recovery; original-profile and retained-proof globals split."""
import ast
import hashlib
import json
import os
import re
import subprocess
from pg1446_current_cold_stage import SSH,W,P
from pg1674_critical_management_gate import management_gate
from pg1786_warning_pair_once_handoff_v2 import payload as previous_payload

SLOT='pg1788-warning-pair-once-handoff-v3'


def payload():
    raw=previous_payload()
    marker='CHILD_REAPED=False'
    if raw.count(marker)!=1:raise ValueError('one retained phase body required')
    at=raw.index(marker)
    body=re.sub(r'\bold\b','retained_proof',raw[at:])
    raw=raw[:at]+body
    raw=raw.replace('pg1786-warning-pair-once-handoff-v2',SLOT)
    assignments=[n for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='old'for t in n.targets)]
    if len(assignments)!=1:raise ValueError('original capture profile global must not be overwritten')
    from pyflakes.api import check
    if check(raw,'<isolated retained-proof globals>'):raise ValueError('actual emitted global closure required')
    compile(raw,'<current once recovery separated globals>','exec');return raw


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
