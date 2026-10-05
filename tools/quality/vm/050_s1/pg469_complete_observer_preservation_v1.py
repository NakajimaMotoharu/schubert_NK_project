"""BUG749 new-only completion of exact immutable observer + empty private exec archive."""
import hashlib,pathlib,subprocess,os,inspect
from pg469_native_file_identity import identity
os.umask(0o077)
R=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation');W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
expected={n:hashlib.sha256((R/'tools/quality/vm/050_s1'/n).read_bytes()).hexdigest() for n in ['pg469_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py']}
payload='EXPECTED='+repr(expected)+'\n'+inspect.getsource(identity)+'\n'+r'''import pathlib,hashlib,os,stat,subprocess,json
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG469')
units=['schubert-nk-morning-controller.service','schubert-nk-api.service','schubert-nk-web.service','schubert-nk-backup.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','artemis.service','caddy.service']
for unit in units:
 raw=subprocess.check_output(['systemctl','show',unit,'-pMainPID','-pControlPID','-pJob'],text=True,timeout=5);v=dict(line.split('=',1) for line in raw.splitlines());assert v['MainPID']==v['ControlPID']=='0' and not v['Job']
 for p in pathlib.Path('/sys/fs/cgroup/system.slice',unit).glob('**/cgroup.procs'):assert not p.read_text().strip()
root=pathlib.Path('/var/lib/pgpt-s1-preservation');tools=root/'pg469-observer-v1';archive=root/'pg469-before-native-v1'
assert stat.S_IMODE(archive.stat().st_mode)==0o700 and archive.stat().st_uid==0 and not list(archive.iterdir())
assert set(p.name for p in tools.iterdir())==set(EXPECTED)
for n,sha in EXPECTED.items():
 p=tools/n;s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o400 and s.st_nlink==1 and hashlib.sha256(p.read_bytes()).hexdigest()==sha
base=pathlib.Path('/run/schubert-nk/pt-coverage');paths=['parent/parent.exec','root-api/root-api.exec','backup/backup.exec','cleanup/cleanup.exec','expiry/expiry.exec'];saved=[]
assert set(p.relative_to(base).as_posix() for p in base.rglob('*.exec'))==set(paths)
for name in paths:
 p=base/name;before=identity(p.lstat());assert p.is_file() and not p.is_symlink() and before[3]==1
 raw=p.read_bytes();assert before==identity(p.lstat());target=archive/name.replace('/','-')
 with target.open('xb') as f:os.fchmod(f.fileno(),0o600);f.write(raw);f.flush();os.fsync(f.fileno())
 assert target.read_bytes()==raw and before==identity(p.lstat());saved.append({'originalPath':str(p),'savedPath':str(target),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'identity':before,'originalUntouched':True})
with (archive/'manifest.private.json').open('x') as f:os.fchmod(f.fileno(),0o600);json.dump(saved,f,indent=2);f.flush();os.fsync(f.fileno())
for p in [tools,archive,root]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print('PG469_OBSERVER_PRESERVATION_CLOSED exact3Root400=true old5NativeExecPreserved=true originalExecContentUntouched=true starts0=true permits0=true')
'''
run=subprocess.run(['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1','sudo -n python3 -B -'],input=payload.encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with (W/'pg469-observer-preservation-v1.private.log').open('xb') as f:f.write(run.stdout);f.write(run.stderr)
print(run.stdout.decode(),end='');raise SystemExit(run.returncode)
