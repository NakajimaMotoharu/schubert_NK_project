"""Direct readonly entrypoint; no nested entrypoint text replacement.

BUG1166/1167 YKT934/935 SSC279. Existing1774 retains its host ownership.
This is diagnosed observation only, not a parallel management action.
"""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import SSH,W
from pg1780_warning_live_peer_proof import payload as prior_payload

SLOT='pg1782-warning-live-peer-readonly-v1'


def payload():
    raw=prior_payload().replace('pg1780-warning-live-peer-readonly-v1',SLOT)
    compile(raw,'<fixed current live peer proof>','exec');return raw


def main():
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    raw=payload().encode()
    (out/'payload.private.py').write_bytes(raw)
    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=90)
    (out/'stderr.private.log').write_bytes(r.stderr)
    result={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'signals0':True,'wholeAccepted':False}
    if r.returncode==0:result['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(result));return r.returncode


if __name__=='__main__':raise SystemExit(main())
