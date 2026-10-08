"""New-only Root400 preflight tool; fixed SSH, safe output, private runtime evidence."""
import hashlib,json,os,pathlib,subprocess
os.umask(0o077)
r=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation');w=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');p=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
f=r/'tools/quality/vm/050_s1/pg553_newrun_preflight.py';sha=hashlib.sha256(f.read_bytes()).hexdigest()
opts=['-i',str(p/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(p/'known_hosts')]
ssh=['ssh',*opts,'-p','22222','ubuntu@127.0.0.1'];scp=['scp',*opts,'-P','22222']
assert not (w/'pg553-preflight-host-v2.private.log').exists()
subprocess.run(ssh+['test ! -e /home/ubuntu/pg553-preflight-v2 && mkdir -m 700 /home/ubuntu/pg553-preflight-v2 && sudo -n test ! -e /var/lib/pgpt-s1-preservation/pg553-preflight-tools-v2'],check=True)
subprocess.run(scp+[str(f),'ubuntu@127.0.0.1:/home/ubuntu/pg553-preflight-v2/'],check=True,stdout=subprocess.DEVNULL)
subprocess.run(ssh+['sudo -n install -d -m 700 /var/lib/pgpt-s1-preservation/pg553-preflight-tools-v2 && sudo -n install -m 400 /home/ubuntu/pg553-preflight-v2/pg553_newrun_preflight.py /var/lib/pgpt-s1-preservation/pg553-preflight-tools-v2/'],check=True)
actual=subprocess.check_output(ssh+['sudo -n sha256sum /var/lib/pgpt-s1-preservation/pg553-preflight-tools-v2/pg553_newrun_preflight.py']).decode().split()[0];assert actual==sha
run=subprocess.run(ssh+['sudo -n python3 -B /var/lib/pgpt-s1-preservation/pg553-preflight-tools-v2/pg553_newrun_preflight.py prepare'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with (w/'pg553-preflight-host-v2.private.log').open('xb') as log:log.write(run.stdout);log.write(run.stderr);log.flush();os.fsync(log.fileno())
with (w/'pg553-preflight-host-v2.exit').open('x') as out:out.write(str(run.returncode)+'\n');out.flush();os.fsync(out.fileno())
if run.returncode==0:
 receipt=json.loads(run.stdout);assert receipt['run']=='PG553-newrun-preflight-v2'
 with (w/'pg553-preflight-host-v2.success.json').open('x') as out:json.dump(receipt,out,sort_keys=True);out.flush();os.fsync(out.fileno())
print(run.stdout.decode(),end='');print('PG553_PREFLIGHT_HOST actualExit='+str(run.returncode));raise SystemExit(run.returncode)
