"""BUG671: new-only two-file observer namespace. No release/start/stop/permit change."""
import hashlib,pathlib,subprocess
ROOT=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
PRIVATE=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
FILES={n:ROOT/'tools/quality/vm/050_s1'/n for n in ('pg458_watch_parent.py','pg457_stable_actor.py')}
EXPECTED={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in FILES.items()}
OPTIONS=['-i',str(PRIVATE/'vm-access'),'-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(PRIVATE/'known_hosts')]
SSH=['ssh',*OPTIONS,'-p','22222','ubuntu@127.0.0.1'];SCP=['scp',*OPTIONS,'-P','22222']
subprocess.run(SSH+['umask 077; test ! -e /home/ubuntu/pg458-watch-stage-v2 && mkdir /home/ubuntu/pg458-watch-stage-v2'],check=True)
for name,path in FILES.items():subprocess.run(SCP+[str(path),'ubuntu@127.0.0.1:/home/ubuntu/pg458-watch-stage-v2/'+name],check=True)
PAYLOAD='''import hashlib,os,pathlib,stat
assert os.geteuid()==0 and pathlib.Path('/var/lib/cloud/data/instance-id').read_text().strip()=='pgpt-r2-20260927-01'
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
incoming=pathlib.Path('/home/ubuntu/pg458-watch-stage-v2');target=pathlib.Path('/var/lib/pgpt-s1-preservation/pg458-watch-v2')
assert not target.exists() and not target.is_symlink() and set(p.name for p in incoming.iterdir())==set(EXPECTED)
for name,digest in EXPECTED.items():
 p=incoming/name;s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and hashlib.sha256(p.read_bytes()).hexdigest()==digest
target.mkdir(mode=0o700)
for name,digest in EXPECTED.items():
 fd=os.open(target/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o400)
 with os.fdopen(fd,'wb') as stream:stream.write((incoming/name).read_bytes());stream.flush();os.fsync(stream.fileno())
 assert hashlib.sha256((target/name).read_bytes()).hexdigest()==digest
os.chmod(target,0o500)
for p in (target,target.parent):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print('PG458_WATCH_STAGE_V2 exactTwoHashes=true newOnlyRootPrivate=true oldWatchPreserved=true starts0=true stops0=true')
'''
r=subprocess.run(SSH+['sudo -n /usr/bin/python3 -'],input=('EXPECTED='+repr(EXPECTED)+'\n'+PAYLOAD).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
print(r.stdout.decode(),end='')
if r.returncode:print('PG458_WATCH_STAGE_V2_REFUSED actual='+str(r.returncode)+' diagnosticsRedacted=true')
raise SystemExit(r.returncode)
