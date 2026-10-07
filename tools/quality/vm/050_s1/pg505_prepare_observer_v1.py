"""New-only immutable current cold-source observer; no service mutation."""
import hashlib,os,pathlib,subprocess
os.umask(0o077)
R=pathlib.Path(__file__).resolve().parent
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
files={name:R/name for name in ['pg505_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py']}
expected={name:hashlib.sha256(p.read_bytes()).hexdigest() for name,p in files.items()}
options=['-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts')]
ssh=['ssh',*options,'-p','22222','ubuntu@127.0.0.1'];scp=['scp',*options,'-P','22222']
log=W/'pg505-observer-stage-v1.private.log';assert not log.exists()
assert (W/'pg504-resume-native-v1.exit').read_text().strip()=='0'
stage='/home/ubuntu/pg505-observer-stage-v1'
subprocess.run(ssh+['test ! -e '+stage+' && sudo -n test ! -e /var/lib/pgpt-s1-preservation/pg505-observer-v1 && mkdir -m 700 '+stage],check=True)
subprocess.run(scp+[*map(str,files.values()),'ubuntu@127.0.0.1:'+stage+'/'],check=True,stdout=subprocess.DEVNULL)
payload=r'''
import hashlib,json,os,pathlib,stat,subprocess
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
prep=pathlib.Path('/var/lib/pgpt-s1-preservation/pg504-resume-preparation-v1')
assert hashlib.sha256((prep/'complete.private').read_bytes()).hexdigest()=='ac7a0eb9af359638ed84bab5951afe69cfc2636e2b460233f82029560aa762ad'
raw=(prep/'refs-after.private.json').read_bytes();assert hashlib.sha256(raw).hexdigest()=='67fa28ad6f289589994af0be7022a20fe12b673685d0c151ffb791dd91fec52e'
before=json.loads(raw)
assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path(before['current'])==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG495')
assert hashlib.sha256(pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44'
for name,expected in before['units'].items():
 raw=subprocess.check_output(['/usr/bin/systemctl','show',name,'--property='+','.join(sorted(expected))],timeout=5)
 assert dict(line.split('=',1) for line in raw.decode('ascii').splitlines())==expected
 for p in pathlib.Path('/sys/fs/cgroup/system.slice',name).glob('**/cgroup.procs'):assert not p.read_text().strip()
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg505-observer-v1');stage=pathlib.Path('/home/ubuntu/pg505-observer-stage-v1')
assert not root.exists() and set(p.name for p in stage.iterdir())==set(EXPECTED)
for name,sha in EXPECTED.items():assert hashlib.sha256((stage/name).read_bytes()).hexdigest()==sha
root.mkdir(mode=0o700)
for name,sha in EXPECTED.items():
 with (root/name).open('xb') as f:os.fchmod(f.fileno(),0o400);f.write((stage/name).read_bytes());f.flush();os.fsync(f.fileno())
 assert hashlib.sha256((root/name).read_bytes()).hexdigest()==sha
for p in [root,root.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print('PG505_OBSERVER_STAGED currentBoot=true exact3Root400=true normalPreparationVerified=true starts0=true')
'''
with log.open('xb') as f:
 result=subprocess.run(ssh+['sudo -n python3 -B -'],input=('EXPECTED='+repr(expected)+'\n'+payload).encode(),stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
print('PG505_OBSERVER_STAGE exit='+str(result.returncode)+' privateLogSha256='+hashlib.sha256(log.read_bytes()).hexdigest())
raise SystemExit(result.returncode)
