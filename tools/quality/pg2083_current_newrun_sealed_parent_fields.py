"""Public parent18 only from a qualified immutable current fullseal, no historical/live-state substitution."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,SSH
from pg2070_current_newrun_observer import SOURCE

SLOT='pg2083-current-newrun-sealed-parent-fields-v1'


def payload(sha):
    if type(sha)is not str or len(sha)!=64 or any(c not in '0123456789abcdef'for c in sha):raise ValueError('qualified whole seal hash required')
    return 'EXPECTED='+repr(sha)+'\nSOURCE='+repr(SOURCE)+'''\nimport hashlib,json,pathlib
p=pathlib.Path('/var/lib/pgpt-s1-preservation/pg2081-current-newrun-full-live-seal-v1/before.private.json');raw=p.read_bytes()
assert hashlib.sha256(raw).hexdigest()==EXPECTED
before=json.loads(raw);fields=before['units']['schubert-nk-morning-controller.service']
assert len(fields)==18 and before['source']==SOURCE
print(json.dumps({'sealedBeforeSha256':EXPECTED,'parentState18':fields,'source':SOURCE,'startsStopsWrites0':True}))
'''


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed public field reader required')
    actual=json.loads((W/'pg2081-current-newrun-full-live-seal-v1/manifest.safe.json').read_bytes())
    if actual['actualExit']!=0 or actual['productionSource']!=SOURCE or actual['sqlOracleQualified']is not True:raise ValueError('actual whole current seal required')
    raw=payload(actual['privateBeforeSha256']);out=W/(SLOT+'.safe.json')
    if out.exists():raise ValueError('one new public current projection required')
    r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=10)
    if r.returncode:raise ValueError('immutable current parent observation refused')
    value={**json.loads(r.stdout),'actualExit':0,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'formalAccepted':False}
    os.umask(0o077)
    with out.open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(value));return 0


if __name__=='__main__':raise SystemExit(main())
