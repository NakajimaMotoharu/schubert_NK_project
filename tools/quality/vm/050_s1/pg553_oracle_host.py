"""Independent cleanup/wire oracle new-only Root400 closure, no business writes/start."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg553_precondition import successful_preflight

os.umask(0o077)
R=Path(__file__).resolve().parent;W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
files={n:R/n for n in('pg553_inbox_oracle.py','pg478_cleanup_oracle.py','pg478_independent_layouts.json')}
hashes={n:hashlib.sha256(p.read_bytes()).hexdigest()for n,p in files.items()}
opts=['-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts')]
ssh=['ssh',*opts,'-p','22222','ubuntu@127.0.0.1'];scp=['scp',*opts,'-P','22222']
stage='/home/ubuntu/pg553-oracle-stage-v3';dest='/var/lib/pgpt-s1-preservation/pg553-oracle-tools-v3'
log=W/'pg553-oracle-host-v3.private.log';assert not log.exists()
exit_bytes=(W/'pg553-preflight-host-v2.exit').read_bytes()
receipt=json.loads((W/'pg553-preflight-host-v2.success.json').read_bytes())
assert successful_preflight(exit_bytes,receipt)
precheck='import hashlib,json,pathlib; p=pathlib.Path("/var/lib/pgpt-s1-preservation/pg553-newrun-preflight-v2/before.private.json"); raw=p.read_bytes(); assert hashlib.sha256(raw).hexdigest()=='+repr(receipt['beforeSha256'])+'; d=json.loads(raw); assert d["source"]=='+repr(receipt['source'])+' and d["manifestSha256"]=='+repr(receipt['manifestSha256'])
subprocess.run(ssh+['sudo -n python3 -B -'],input=precheck.encode(),check=True,stdout=subprocess.DEVNULL)
subprocess.run(ssh+['test ! -e '+stage+' && sudo -n test ! -e '+dest+' && mkdir -m 700 '+stage],check=True)
subprocess.run(scp+[*map(str,files.values()),'ubuntu@127.0.0.1:'+stage+'/'],check=True,stdout=subprocess.DEVNULL)
payload='HASHES='+repr(hashes)+'\n'+r'''
import os,pathlib,hashlib,subprocess
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
r=pathlib.Path('/var/lib/pgpt-s1-preservation/pg553-oracle-tools-v3');s=pathlib.Path('/home/ubuntu/pg553-oracle-stage-v3');assert not r.exists();r.mkdir(mode=0o700)
assert {p.name for p in s.iterdir()}==set(HASHES)
for name,sha in HASHES.items():
    raw=(s/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==sha
    with(r/name).open('xb')as f:os.fchmod(f.fileno(),0o400);f.write(raw);f.flush();os.fsync(f.fileno())
for p in(r,r.parent):
    fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
subprocess.run(['/usr/bin/python3','-B',str(r/'pg553_inbox_oracle.py'),'capture'],check=True)
'''
with log.open('xb')as f:
    run=subprocess.run(ssh+['sudo -n python3 -B -'],input=payload.encode(),stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
with(W/'pg553-oracle-host-v3.exit').open('x')as f:f.write(str(run.returncode)+'\n');f.flush();os.fsync(f.fileno())
print(json.dumps({'run':'PG553-oracle-host-v3','actualExit':run.returncode,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest(),'toolHashes':hashes,'starts0':True,'productionPT0':True}));raise SystemExit(run.returncode)
