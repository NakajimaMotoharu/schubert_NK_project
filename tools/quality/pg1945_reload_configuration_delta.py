"""Independent current reload deltas: saved preimage vs fresh manager reads; no writes."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,SSH
from pg1943_reload_retained_diagnosis import owner

SLOT='pg1945-reload-configuration-delta-v1'
PAYLOAD=r'''
import ast,hashlib,json,pathlib,re,subprocess
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1929-partial-reload-v1')
raw=(root/'before.private.json').read_bytes();old=json.loads(raw)
parser=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/pg477_unit_references.py').read_bytes()
assert hashlib.sha256(parser).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4'
node=next(n for n in ast.parse(parser).body if isinstance(n,ast.FunctionDef)and n.name=='exec_record')
ns={'re':re};exec(compile(ast.Module(body=[node],type_ignores=[]),'<independent declaration parser>','exec'),ns)
def read(unit,keys):
 p=subprocess.run(['/usr/bin/systemctl','show',unit,'--property='+','.join(sorted(keys))],capture_output=True,check=True,timeout=15)
 rows=dict(x.split('=',1)for x in p.stdout.decode().splitlines());assert set(rows)==set(keys);return rows
changed={};states={}
for unit,prior in old['configuration'].items():
 a=read(unit,prior);assert a==read(unit,prior)
 fields=[k for k in prior if a[k]!=prior[k]]
 changed[unit]={k:{'beforeSha256':hashlib.sha256(prior[k].encode()).hexdigest(),'afterSha256':hashlib.sha256(a[k].encode()).hexdigest()}for k in fields}
 if 'ExecStart'in fields:
  before=ns['exec_record'](prior['ExecStart']);after=ns['exec_record'](a['ExecStart']);assert before is not None and after is not None
  changed[unit]['ExecStart']['declarationSame']=before[:3]==after[:3]
  changed[unit]['ExecStart']['auxiliaryBefore']=before[3:]
  changed[unit]['ExecStart']['auxiliaryAfter']=after[3:]
 priorstate=old['units'][unit];now=read(unit,priorstate);assert now==read(unit,priorstate)
 states[unit]=[k for k in priorstate if now[k]!=priorstate[k]]
config=read('schubert-nk-morning-controller.service',{'Type','SuccessExitStatus'})
assert config=={'Type':'oneshot','SuccessExitStatus':'10'}
print(json.dumps({'actualExit':0,'configurationDelta':changed,'stateDelta':states,'parentConfiguration':config,'beforeSha256':hashlib.sha256(raw).hexdigest(),'reloadReserved':(root/'daemon-reload-reserved.private').read_bytes()==b'one normal daemon-reload; no retry\n','completeAbsent':not(root/'complete.private').exists(),'signalsStartsStopsReloadsSqlWrites0':True}))
'''


def main():
    os.umask(0o077);before=owner();out=W/SLOT;out.mkdir(mode=0o700)
    r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=PAYLOAD.encode(),capture_output=True,timeout=90)
    (out/'stderr.private.log').write_bytes(r.stderr)
    if before!=owner():raise ValueError('actual same retained host owner required')
    value={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(PAYLOAD.encode()).hexdigest(),'formalAccepted':False}
    if not r.returncode:value['guest']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
