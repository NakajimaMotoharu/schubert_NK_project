"""Current new-day actual live Root/original tuple, read-only fixed generation."""
import hashlib
import json
import os
import subprocess
from pg1454_current_day_observer import R
from pg1450_current_cold_retry import W
from pg1446_current_cold_stage import SSH
from pg1321_live_root_binding import BODY

SOURCE='769ddb15cd735c25fef581b5f9850ef9d0053c0f'
BOM='ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99'


def compose(expected):
    if not isinstance(expected,dict)or not all(isinstance(expected.get(k),str)and expected[k]for k in['MainPID','InvocationID','ExecMainStartTimestampMonotonic','Job']):raise ValueError('actual start tuple required')
    raw=BODY.replace('cbca8738-3b24-4090-b77c-bf029677cdd6','3d69f5af-6bac-46b1-a540-7591c4a79a0d').replace('cbca87383b244090b77cbf029677cdd6','3d69f5af6bac46b1a5407591c4a79a0d')
    raw='SOURCE='+repr(SOURCE)+'\nDIGEST='+repr(BOM)+'\nEXPECTED='+repr(expected)+'\n'+raw
    compile(raw,'<actual new-day live binding>','exec');return raw


def main():
    start=json.loads((W/'pg1456-current-day-once-v1/manifest.safe.json').read_bytes())
    assert start['actualExit']==0 and start['guest']['externalStartIssuedOnce']and start['guest']['source']==SOURCE
    os.umask(0o077);out=W/'pg1457-current-day-live-binding-v1';out.mkdir(mode=0o700)
    raw=compose(start['guest']['parent']).encode()
    with(out/'payload.private.py').open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=30)
    with(out/'observer.private.log').open('xb')as f:f.write(r.stderr);f.flush();os.fsync(f.fileno())
    result={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'formalAccepted':False}
    if r.returncode==0:result.update(json.loads(r.stdout))
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(result,sort_keys=True));return r.returncode


if __name__=='__main__':raise SystemExit(main())
