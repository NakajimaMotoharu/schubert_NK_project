"""Known frozen tool diagnostic codes only, never raw private stderr."""
import hashlib
import json
import os
import subprocess
from pg1805_retained_stop_readonly_diagnosis import owner,SSH,W

SLOT='pg1807-retained-stop-structured-trace-v1'
PAYLOAD=r'''
import hashlib,json,pathlib,re
p=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1800-native-stop-v1/refs-prepare.private.log')
raw=p.read_bytes();lines=[]
for line in raw.decode().splitlines():
 if re.fullmatch(r'PG1800_(?:READBACK_UNKNOWN type=[A-Za-z_]+|FRAME method=[A-Za-z0-9_<>]+ line=[0-9]+)',line):lines.append(line)
assert lines
print(json.dumps({'actualExit':0,'structuredTrace':lines,'sha256':hashlib.sha256(raw).hexdigest(),'privateRawExported':False}))
'''


def main():
    os.umask(0o077);before=owner();out=W/SLOT;out.mkdir(mode=0o700)
    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=PAYLOAD.encode(),capture_output=True,timeout=20)
    (out/'stderr.private.log').write_bytes(r.stderr)
    if before!=owner():raise ValueError('fixed owner/failure changed')
    value={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(PAYLOAD.encode()).hexdigest(),'hostRetainedOwner':before}
    if r.returncode==0:value['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
