"""Separate full post after fixed current initial-before pair recovery."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg1814_current_pair_independent_post import payload as previous_payload,SLOT as OLD_SLOT

SLOT='pg1824-initial-before-pair-independent-full-post-v1'


def payload():
    raw=previous_payload().replace(OLD_SLOT,SLOT).replace('/proc/479190','/proc/481511').replace('/proc/479219','/proc/481540')
    if '4148e3e8-f107-431a-ab27-d6e6d1f1772e'not in raw:raise ValueError('actual unchanged Root required')
    compile(raw,'<current initial-before recovered whole post>','exec');return raw


def main():
    receipt=json.loads((W/'pg1823-identity-stop-pair-once-handoff-v1/manifest.safe.json').read_bytes())
    if receipt['actualExit']!=0 or receipt['queuedSameHostGateAcquired']is not True:raise ValueError('actual current once recovery and same gate required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode()
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=120)
    (out/'stderr.private.log').write_bytes(r.stderr)
    value={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'oldNormalCloseUnknown':True,'formalAccepted':False}
    if r.returncode==0:value['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
