"""New-only SSC168 tool closed set; never runs recovery or starts a service."""
import hashlib
import pathlib
import subprocess
import sys

version='v2'

private=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
source=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg460-nss-tool-'+version)
names=['Pg460CaddyNssPreparation.class','Pg460CaddyNssPreparationTest.class']
sources=[source/name for name in names]
expected={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
options=['-i',str(private/'vm-access'),'-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(private/'known_hosts')]
ssh=['ssh',*options,'-p','22222','ubuntu@127.0.0.1']
subprocess.run(ssh+['set -eu; umask 077; test ! -e /home/ubuntu/pg460-nss-stage-'+version+'; mkdir /home/ubuntu/pg460-nss-stage-'+version],check=True)
subprocess.run(['scp',*options,'-P','22222',*[str(p) for p in sources],'ubuntu@127.0.0.1:/home/ubuntu/pg460-nss-stage-'+version+'/'],check=True)
payload='''import hashlib,os,pathlib,stat
assert os.geteuid()==0
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
source=pathlib.Path('/home/ubuntu/pg460-nss-stage-'+VERSION)
assert {p.name for p in source.iterdir()}==set(EXPECTED)
raws={}
for name,digest in EXPECTED.items():
 p=source/name;s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1
 raws[name]=p.read_bytes();assert hashlib.sha256(raws[name]).hexdigest()==digest
target=pathlib.Path('/var/lib/pgpt-s1-preservation/pg460-nss-tool-'+VERSION)
assert not target.exists() and not target.is_symlink();target.mkdir(mode=0o700)
for name,raw in raws.items():
 fd=os.open(target/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o400)
 with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
 assert hashlib.sha256((target/name).read_bytes()).hexdigest()==EXPECTED[name]
os.chmod(target,0o500)
for p in [target,target.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print('PG460_NSS_STAGE closedClasses2=true byteHash=true root0500File0400=true nativeMutation=false')
'''
r=subprocess.run(ssh+['sudo -n python3 -'],input=('EXPECTED='+repr(expected)+'\nVERSION='+repr(version)+'\n'+payload).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
print(r.stdout.decode(),end='')
if r.returncode:print('PG460_NSS_STAGE_REFUSED diagnosticsRedacted=true actual='+str(r.returncode))
raise SystemExit(r.returncode)
