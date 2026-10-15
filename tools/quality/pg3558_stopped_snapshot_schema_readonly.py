"""Bounded frozen schema/runtime filename diagnosis; no business/Unit operation."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate

SLOT='pg3558-stopped-snapshot-schema-v1'
BODY=r'''
from pathlib import Path
import json,hashlib
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28'
assert hashlib.sha256(Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='dc535a48a8d8d46ae5c33a442143e376c59b882a1e098ea7579e3f070fe92d72'
raw=Path('/var/lib/pgpt-s1-preservation/pg3520-native-stop-v1/after.private.json').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='9ffdbbc3e605bd9b1b66f543ae35322b5e5481623f40cec054d35f6be280841b'
value=json.loads(raw)
def shape(v,depth):
 if isinstance(v,dict):return {'type':'dict','count':len(v),'keys':list(v)[:8],'examples':{k:shape(x,depth-1)for k,x in list(v.items())[:3]}if depth else {}}
 if isinstance(v,list):return {'type':'list','count':len(v),'elementTypes':sorted({type(x).__name__ for x in v})}
 return {'type':type(v).__name__}
print(json.dumps({'actualExit':0,'schema':{k:shape(value[k],2)for k in ['originals','backup','extraDurable']},'runtimeFilenames':list(value['runtime']),'startupFilenames':list(value['startup']),'rawRowOrSecretValuesExported':False,'actions0':True}))
'''


def main():
    compile(BODY,'<frozen shape readonly>','exec');os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=BODY.encode(),capture_output=True,timeout=30)
    (out/'stdout.private.json').write_bytes(r.stdout);(out/'stderr.private.log').write_bytes(r.stderr)
    v={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(BODY.encode()).hexdigest(),'actions0':True}
    if r.returncode==0:v['guest']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(v,sort_keys=True));print(json.dumps(v));return r.returncode


if __name__=='__main__':raise SystemExit(main())
