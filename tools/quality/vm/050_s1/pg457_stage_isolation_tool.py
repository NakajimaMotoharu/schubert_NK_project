"""New-only isolated singleton operator, hash verified. No actual isolation/start/stop."""
import hashlib
import pathlib
import subprocess
private=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
source=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg457-isolation-tool-v2/Pg457OwnedIsolation.class')
expected=hashlib.sha256(source.read_bytes()).hexdigest()
options=['-i',str(private/'vm-access'),'-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(private/'known_hosts')]
ssh=['ssh',*options,'-p','22222','ubuntu@127.0.0.1']
subprocess.run(ssh+['umask 077; test ! -e /home/ubuntu/pg457-isolation-stage && mkdir /home/ubuntu/pg457-isolation-stage'],check=True)
subprocess.run(['scp',*options,'-P','22222',str(source),'ubuntu@127.0.0.1:/home/ubuntu/pg457-isolation-stage/Pg457OwnedIsolation.class'],check=True)
payload='''import hashlib,os,pathlib,stat
assert os.geteuid()==0
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
source=pathlib.Path('/home/ubuntu/pg457-isolation-stage/Pg457OwnedIsolation.class');s=source.lstat()
assert stat.S_ISREG(s.st_mode) and s.st_nlink==1
raw=source.read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED
target=pathlib.Path('/var/lib/pgpt-s1-preservation/pg457-isolation-tool-v2')
assert not target.exists() and not target.is_symlink();target.mkdir(mode=0o700)
fd=os.open(target/'Pg457OwnedIsolation.class',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o400)
with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
assert hashlib.sha256((target/'Pg457OwnedIsolation.class').read_bytes()).hexdigest()==EXPECTED
os.chmod(target,0o500)
for p in [target,target.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print('PG457_ISOLATION_STAGE singleton=true byteHash=true root0500File0400=true stopIssued=false')
'''
r=subprocess.run(ssh+['sudo -n python3 -'],input=('EXPECTED='+repr(expected)+'\n'+payload).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
print(r.stdout.decode(),end='')
if r.returncode:print('PG457_ISOLATION_STAGE_REFUSED diagnosticsRedacted=true actual='+str(r.returncode))
raise SystemExit(r.returncode)
