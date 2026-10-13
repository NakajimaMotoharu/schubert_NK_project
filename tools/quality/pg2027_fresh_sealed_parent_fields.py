"""Extract only public parent state18 from the actual immutable full seal, no live state assumption."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,SSH

RAW=r'''
import hashlib,json,pathlib
p=pathlib.Path('/var/lib/pgpt-s1-preservation/pg2025-fresh-resume-full-live-seal-v1/before.private.json');raw=p.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='8a7d42b110a047d60a3b10d948cf51731dab4b37b59d85052332acaa42942788'
before=json.loads(raw);fields=before['units']['schubert-nk-morning-controller.service']
assert len(fields)==18 and before['source']=='0fd734195b4d5338f6b7e860e087cce561d49562'
print(json.dumps({'sealedBeforeSha256':hashlib.sha256(raw).hexdigest(),'parentState18':fields,'source':before['source'],'startsStopsWrites0':True}))
'''


def main():
    os.umask(0o077);out=W/'pg2027-fresh-sealed-parent-fields-v1.safe.json'
    if out.exists():raise ValueError('new-only sealed observation required')
    actual=json.loads((W/'pg2025-fresh-resume-full-live-seal-v1/manifest.safe.json').read_bytes())
    if actual['actualExit']!=0 or actual['privateBeforeSha256']!='8a7d42b110a047d60a3b10d948cf51731dab4b37b59d85052332acaa42942788':raise ValueError('actual full immutable seal required')
    r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=RAW.encode(),capture_output=True,timeout=10)
    if r.returncode:raise ValueError('actual sealed public state extract refused')
    value={**json.loads(r.stdout),'actualExit':0,'payloadSha256':hashlib.sha256(RAW.encode()).hexdigest(),'formalAccepted':False}
    with out.open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(value));return 0


if __name__=='__main__':raise SystemExit(main())
