"""Fixed new-only 16-class operator namespace, no release/DB/start/permit side effect."""
import hashlib
import pathlib
import subprocess

RUN = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
PRIVATE = pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
SSH = ['ssh', '-i', str(PRIVATE / 'vm-access'), '-p', '22222', '-o', 'BatchMode=yes',
       '-o', 'IdentitiesOnly=yes', '-o', 'StrictHostKeyChecking=yes',
       '-o', 'UserKnownHostsFile=' + str(PRIVATE / 'known_hosts'), 'ubuntu@127.0.0.1']
SCP = ['scp', '-i', str(PRIVATE / 'vm-access'), '-P', '22222', '-o', 'BatchMode=yes',
       '-o', 'IdentitiesOnly=yes', '-o', 'StrictHostKeyChecking=yes',
       '-o', 'UserKnownHostsFile=' + str(PRIVATE / 'known_hosts')]
NAMES = ['Pg387TrustedDeployment', 'Pg387TrustedDeployment$Checked', 'Pg407FailedRootRecovery',
         'Pg410KnownAuthRecovery', 'Pg410KnownAuthRecovery$Receipt', 'Pg422KnownIncompleteRecovery',
         'Pg422SignedMigration', 'Pg422SignedMigration$Data', 'Pg423AssetFixtureRecovery',
         'Pg424KnownApiRecovery', 'Pg425KnownApiRecovery', 'Pg428ColdBootPreparation',
         'Pg428ColdBootPreparation$1Node', 'Pg456SignedMigration', 'Pg456SignedMigration$Data',
         'Pg456AppliedCompletion']
FILES = {name + '.class': RUN / 'pg456-tools-v7' / (name + '.class') for name in NAMES}
EXPECTED = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in FILES.items()}
subprocess.run(SSH + ['umask 077; test ! -e /home/ubuntu/pg456-applied-stage-v7 && mkdir /home/ubuntu/pg456-applied-stage-v7'], check=True)
for name, path in FILES.items():
    subprocess.run(SCP + [str(path), 'ubuntu@127.0.0.1:/home/ubuntu/pg456-applied-stage-v7/' + name], check=True)
PAYLOAD = '''import hashlib,os,pathlib,stat
assert os.geteuid()==0
assert pathlib.Path('/var/lib/cloud/data/instance-id').read_text().strip()=='pgpt-r2-20260927-01'
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
incoming=pathlib.Path('/home/ubuntu/pg456-applied-stage-v7')
target=pathlib.Path('/var/lib/pgpt-s1-preservation/pg456-applied-tools-v7')
assert not target.exists() and not target.is_symlink()
assert set(p.name for p in incoming.iterdir())==set(EXPECTED)
for name,digest in EXPECTED.items():
    p=incoming/name;s=p.lstat()
    assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and hashlib.sha256(p.read_bytes()).hexdigest()==digest
target.mkdir(mode=0o700)
for name,digest in sorted(EXPECTED.items()):
    fd=os.open(target/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o400)
    with os.fdopen(fd,'wb') as stream:
        stream.write((incoming/name).read_bytes());stream.flush();os.fsync(stream.fileno())
    assert hashlib.sha256((target/name).read_bytes()).hexdigest()==digest
os.chmod(target,0o500)
for p in [target,target.parent]:
    fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print('PG456_APPLIED_STAGE classes16=true hashes=true root0500Files0400=true productionChanged=false')
'''
result = subprocess.run(SSH + ['sudo -n /usr/bin/python3 -'], input=('EXPECTED=' + repr(EXPECTED) + '\n' + PAYLOAD).encode(),
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(result.stdout.decode(), end='')
if result.returncode:
    print('PG456_APPLIED_STAGE_REFUSED actual=' + str(result.returncode) + ' diagnosticsRedacted=true')
raise SystemExit(result.returncode)
