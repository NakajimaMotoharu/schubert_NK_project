"""Separate whole unchanged image after current pair normal limited recovery."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg1798_warning_recovery_independent_post import payload as previous_payload,SLOT as PREVIOUS_SLOT

SLOT='pg1814-current-pair-independent-full-post-v1'


def payload():
    raw=previous_payload().replace(PREVIOUS_SLOT,SLOT).replace('/proc/476087','/proc/479190').replace('/proc/476116','/proc/479219')
    if '4148e3e8-f107-431a-ab27-d6e6d1f1772e'not in raw:raise ValueError('actual Root UUID unchanged required')
    compile(raw,'<current recovered pair whole post>','exec');return raw


def main():
    receipt=json.loads((W/'pg1813-current-warning-pair-once-handoff-v1/manifest.safe.json').read_bytes())
    if receipt['actualExit']!=0 or receipt['queuedSameHostGateAcquired']is not True:raise ValueError('actual normal limited recovery and same host gate required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode()
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=120)
    (out/'stderr.private.log').write_bytes(r.stderr)
    result={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'oldNormalCloseUnknown':True,'formalAccepted':False}
    if r.returncode==0:result['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True)
    print(json.dumps(result));return r.returncode


if __name__=='__main__':raise SystemExit(main())
