"""Read-only current GC/sealed20 join, real tenRefs; scope acceptance and business actions0."""
import datetime
import hashlib
import json
import os
import pathlib
import subprocess
import time

os.umask(0o077)
R=pathlib.Path(__file__).resolve().parent
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
RUN='PG537-bootstrap-gc-probe-v2'
files={n:(R/n).read_bytes()for n in ['pg537_bootstrap_gc_contract.py','pg537_bootstrap_gc_readback.py','pg536_bootstrap_execution_contract.py','pg537_bootstrap_retire.py']}
hashes={n:hashlib.sha256(b).hexdigest()for n,b in files.items()}
payload="import sys,types\nsys.path.insert(0,'/var/lib/pgpt-s1-preservation/pg535-bootstrap-tools-v1')\n"
for name in ['pg536_bootstrap_execution_contract.py','pg537_bootstrap_gc_contract.py','pg537_bootstrap_gc_readback.py']:
 module=name.removesuffix('.py')
 payload+='m=types.ModuleType('+repr(module)+');m.__file__='+repr(name)+';sys.modules[m.__name__]=m;exec('+repr(files[name].decode())+',m.__dict__)\n'
payload+=r'''
import pathlib,json,hashlib,dbus
from pg537_bootstrap_gc_readback import load,require
from pg537_bootstrap_gc_contract import unchanged_after_gc
env,snapshot=load(lambda:('READONLY_NO_SCOPE_AUTHORITY',))
bus=dbus.SystemBus(private=True)
manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
refs=[]
for u in env['UNITS']:manager.RefUnit(u);refs.append(u)
first=snapshot();require(first==snapshot())
raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg536-bootstrap-owned-handoff-v1/after.private.json').read_bytes()
require(hashlib.sha256(raw).hexdigest()=='aa8f92166b01b23a7ffd0fa56474fae0048ce20a544f90a3ec06b211732e37ad')
actor=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg535-bootstrap-existing-v1/actor.private.json').read_bytes())
require(unchanged_after_gc(json.loads(raw),first,actor))
for u in reversed(refs):manager.UnrefUnit(u)
bus.close()
print('PG537_GC_READONLY preservedReal20=true currentGcIsIdleOnly=true allOtherValuesUnchanged=true fullSnapshotTwice=true businessActions0=true scopeAcceptance0=true')
'''
log=W/(RUN.lower()+'.private.log');assert not log.exists()
start=datetime.datetime.now(datetime.timezone.utc).isoformat();began=time.monotonic()
ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
with log.open('xb')as f:r=subprocess.run(ssh,input=payload.encode(),stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
with(W/(RUN.lower()+'.exit')).open('x')as f:f.write(str(r.returncode)+'\n')
result={'run':RUN,'actualExit':r.returncode,'toolHashes':hashes,'startedAt':start,
        'finishedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsedSeconds':time.monotonic()-began,
        'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest(),'scopeAcceptance0':True,'businessActions0':True}
with(W/(RUN.lower()+'.source.json')).open('x')as f:json.dump(result,f,sort_keys=True)
print(json.dumps(result));raise SystemExit(r.returncode)

