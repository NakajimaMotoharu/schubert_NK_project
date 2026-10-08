"""SSC220 fixed source stdin deployment, diagnostic preflight or one pinned tool handoff."""
import datetime
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time

os.umask(0o077)
R=pathlib.Path(__file__).resolve().parent
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
assert sys.argv[1:] in (['preflight'],['execute'])
mode=sys.argv[1]
RUN='PG545-runtime-'+mode+'-v1'
prefix=RUN.lower()
for name in ['pg543_retirement_contract_test.py','pg545_runtime_handoff_test.py']:
 subprocess.run(['python3','-B',str(R/name)],check=True)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip()
if mode=='execute':
 assert subprocess.check_output(['git','status','--porcelain'],cwd=R)==b''
 prior=json.loads((W/'pg545-runtime-preflight-v1.source.json').read_bytes())
 assert prior['actualExit']==0
files={n:(R/n).read_bytes()for n in ['pg542_current_contract.py','pg543_retirement_contract.py','pg543_runtime_readback.py','pg545_runtime_owned_handoff_v1.py']}
hashes={n:hashlib.sha256(b).hexdigest()for n,b in files.items()}
if mode=='execute':assert prior['toolHashes']==hashes
payload="import sys,types\nsys.path.insert(0,'/var/lib/pgpt-s1-preservation/pg543-retirement-tools-v3')\n"
for name in ['pg542_current_contract.py','pg543_retirement_contract.py','pg543_runtime_readback.py']:
 module=name.removesuffix('.py')
 payload+='m=types.ModuleType('+repr(module)+');m.__file__='+repr(name)+';sys.modules[m.__name__]=m;exec('+repr(files[name].decode())+',m.__dict__)\n'
payload+='sys.argv='+repr(['pg545_runtime_owned_handoff_v1.py',mode])+"\n__file__='pg545_runtime_owned_handoff_v1.py'\nexec(compile("+repr(files['pg545_runtime_owned_handoff_v1.py'].decode())+", __file__, 'exec'), globals())\n"
log=W/(prefix+'.private.log');assert not log.exists()
start=datetime.datetime.now(datetime.timezone.utc).isoformat();began=time.monotonic()
ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
with log.open('xb')as f:
 result=subprocess.run(ssh,input=payload.encode(),stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
with(W/(prefix+'.exit')).open('x')as f:f.write(str(result.returncode)+'\n')
report={'run':RUN,'sourceCommit':head,'toolHashes':hashes,'actualExit':result.returncode,
        'startedAt':start,'finishedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'elapsedSeconds':time.monotonic()-began,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest(),
        'oldCloseUNKNOWN':True,'productionPT0':True,'businessActions0':True}
with(W/(prefix+'.source.json')).open('x')as f:json.dump(report,f,sort_keys=True)
print(json.dumps(report));raise SystemExit(result.returncode)
