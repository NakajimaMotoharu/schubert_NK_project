"""New-only fixed-source readonly observer staging; no business start."""
import hashlib,json,os,pathlib,subprocess
from pg553_precondition import successful_preflight,SOURCE,DIGEST
os.umask(0o077)
R=pathlib.Path(__file__).resolve().parent;W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
assert successful_preflight((W/'pg553-preflight-host-v2.exit').read_bytes(),json.loads((W/'pg553-preflight-host-v2.success.json').read_bytes()))
assert (W/'pg553-oracle-host-v3.exit').read_bytes()==b'0\n'
files={n:R/n for n in ['pg554_watch_parent.py','pg554_stable_actor.py','pg462_observer_identity.py']}
hashes={n:hashlib.sha256(p.read_bytes()).hexdigest()for n,p in files.items()}
opts=['-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts')]
ssh=['ssh',*opts,'-p','22222','ubuntu@127.0.0.1'];scp=['scp',*opts,'-P','22222']
stage='/home/ubuntu/pg554-observer-stage-v1';dest='/var/lib/pgpt-s1-preservation/pg554-observer-v1'
log=W/'pg554-observer-stage-v1.private.log';assert not log.exists()
subprocess.run(ssh+['test ! -e '+stage+' && sudo -n test ! -e '+dest+' && mkdir -m 700 '+stage],check=True)
subprocess.run(scp+[*map(str,files.values()),'ubuntu@127.0.0.1:'+stage+'/'],check=True,stdout=subprocess.DEVNULL)
payload=r'''
import hashlib,json,os,pathlib,subprocess
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
current=pathlib.Path('/opt/schubert-nk/current');raw=(current/'RELEASE-MANIFEST.json').read_bytes()
assert current.readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG548') and hashlib.sha256(raw).hexdigest()==DIGEST and json.loads(raw)['source']['commit']==SOURCE
before=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg553-newrun-preflight-v2/before.private.json').read_bytes())
for unit,expected in before['units'].items():
 raw=subprocess.check_output(['/usr/bin/systemctl','show',unit,'--property='+','.join(expected)],timeout=5)
 assert dict(x.split('=',1)for x in raw.decode().splitlines())==expected
 for p in pathlib.Path('/sys/fs/cgroup/system.slice',unit).glob('**/cgroup.procs'):assert not p.read_text().strip()
r=pathlib.Path('/var/lib/pgpt-s1-preservation/pg554-observer-v1');s=pathlib.Path('/home/ubuntu/pg554-observer-stage-v1');assert not r.exists() and {p.name for p in s.iterdir()}==set(HASHES)
for n,h in HASHES.items():assert hashlib.sha256((s/n).read_bytes()).hexdigest()==h
r.mkdir(mode=0o700)
for n,h in HASHES.items():
 with(r/n).open('xb')as f:os.fchmod(f.fileno(),0o400);f.write((s/n).read_bytes());f.flush();os.fsync(f.fileno())
for p in(r,r.parent):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print('observerStaged=true starts0=true currentSourceVerified=true')
'''
with log.open('xb')as f:
 run=subprocess.run(ssh+['sudo -n python3 -B -'],input=('HASHES='+repr(hashes)+'\nSOURCE='+repr(SOURCE)+'\nDIGEST='+repr(DIGEST)+'\n'+payload).encode(),stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
with(W/'pg554-observer-stage-v1.exit').open('x')as f:f.write(str(run.returncode)+'\n')
print(json.dumps({'actualExit':run.returncode,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest(),'hashes':hashes,'starts0':True}));raise SystemExit(run.returncode)
