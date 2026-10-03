"""Fixed new-only cold Root tools; preserve original sealed PG432 tool classes."""
import hashlib
import json
import pathlib
import subprocess
import sys

root = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
work = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
private = pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
options = ['-i', str(private / 'vm-access'), '-o', 'BatchMode=yes', '-o', 'IdentitiesOnly=yes',
           '-o', 'StrictHostKeyChecking=yes', '-o', 'UserKnownHostsFile=' + str(private / 'known_hosts')]
ssh = ['ssh', '-p', '22222'] + options + ['ubuntu@127.0.0.1']
scp = ['scp', '-P', '22222'] + options
assert sys.argv[1:] in ([], ['--resume-staged'])
resume = bool(sys.argv[1:])
log = work / ('pg444-root-placement-v2.log' if resume else 'pg444-root-placement.log')
assert not log.exists()
subprocess.run(['git', 'diff', '--exit-code', 'HEAD', '--', 'tools'], cwd=root, check=True)
assert not subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '--', 'tools'], cwd=root).strip()
old = {}
for line in (work / 'pg432-root-prior-and-agent-sha.log').read_text().splitlines()[:21]:
    digest, path = line.split()
    assert pathlib.PurePosixPath(path).parent == pathlib.PurePosixPath('/var/lib/pgpt-s1-preservation/pg431-deploy-tools')
    old[pathlib.PurePosixPath(path).name] = digest
assert len(old) == 21
for path in (work / 'pg432-frozen-tools-W26ZJ4').glob('*.class'):
    assert path.name in old
    old[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
compiled = work / 'pg444-tools-v6'
new = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in compiled.glob('*.class')}
assert len(new) == 7 and 'Pg431KnownPairRecovery.class' not in new
manifest = json.loads((root / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG444-cold-tools-v6/manifest.json').read_text())
assert new == {v['name']: v['sha256'] for v in manifest['classes']}
for entry in manifest['sourceFiles']:
    assert hashlib.sha256((root / entry['path']).read_bytes()).hexdigest() == entry['sha256']
if not resume:
    subprocess.run(ssh + ['umask 077; test ! -e /home/ubuntu/pg444-cold-stage && mkdir /home/ubuntu/pg444-cold-stage'], check=True)
    for name in sorted(new):
        subprocess.run(scp + [str(compiled / name), 'ubuntu@127.0.0.1:/home/ubuntu/pg444-cold-stage/' + name], check=True)
payload = r'''import hashlib,os,pathlib,stat
assert os.geteuid()==0
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
assert pathlib.Path('/var/lib/cloud/data/instance-id').read_text().strip()=='pgpt-r2-20260927-01'
base=pathlib.Path('/var/lib/pgpt-s1-preservation');prior=base/'pg432-deploy-tools';target=base/'pg444-deploy-tools'
incoming=pathlib.Path('/home/ubuntu/pg444-cold-stage')
def info(p,mode):
    s=p.lstat();assert s.st_uid==0 and s.st_gid==0 and s.st_mode==mode and (not stat.S_ISREG(mode) or s.st_nlink==1)
def content(p,digest):
    before=p.lstat();b=p.read_bytes();after=p.lstat()
    # BUG596: atime is allowed to change on read; it is not an integrity field.
    def identity(s):return (s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_nlink,s.st_size,s.st_ctime_ns,s.st_mtime_ns)
    assert identity(before)==identity(after) and hashlib.sha256(b).hexdigest()==digest
    return b
for p in [pathlib.Path('/'),pathlib.Path('/var'),pathlib.Path('/var/lib'),base]:
    s=p.lstat();assert stat.S_ISDIR(s.st_mode) and s.st_uid==0 and s.st_gid==0 and not(s.st_mode&0o022)
info(prior,0o40500)
assert {p.name for p in prior.iterdir()}==set(OLD) and {p.name for p in incoming.iterdir()}==set(NEW)
values={}
for n,d in OLD.items():info(prior/n,0o100400);values[n]=content(prior/n,d)
for n,d in NEW.items():
    p=incoming/n;s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and not(s.st_mode&0o077)
    values[n]=content(p,d)
assert len(values)==26 and not target.exists() and not target.is_symlink()
target.mkdir(mode=0o700)
for n,b in values.items():
    p=target/n;fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o400)
    with os.fdopen(fd,'wb') as f:f.write(b);f.flush();os.fsync(f.fileno())
    info(p,0o100400);assert p.read_bytes()==b
os.chmod(target,0o500)
for p in [target,base]:
    fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
for n,d in OLD.items():info(prior/n,0o100400);content(prior/n,d)
print('PG444_ROOT_PLACEMENT classes=26 shaMatches=true rootClosed=true priorUnchanged=true coldOnly=true serviceActions=0 authorityIssued=false')
'''
result = subprocess.run(ssh + ['sudo -n /usr/bin/python3 -'],
                        input=('OLD=' + repr(old) + '\nNEW=' + repr(new) + '\n' + payload).encode(),
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if result.returncode:
    secret = work / ('pg444-root-placement-v2-failure-private.log' if resume else 'pg444-root-placement-failure-private.log')
    secret.touch(mode=0o600)
    secret.write_bytes(result.stderr)
    log.write_text('PG444_ROOT_PLACEMENT_FAILED diagnosticsRedacted=true exit=' + str(result.returncode) + '\n')
else:
    assert result.stdout == b'PG444_ROOT_PLACEMENT classes=26 shaMatches=true rootClosed=true priorUnchanged=true coldOnly=true serviceActions=0 authorityIssued=false\n'
    log.write_bytes(result.stdout)
print(log.read_text(), end='')
raise SystemExit(result.returncode)
