"""SSC233 immutable completed-current tool stage/verify/activate; no startup."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import time
import pg685_sources as profile

R = Path(__file__).resolve().parent
T = R.parents[3]
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P = Path('/home/mini/codex/project1/work/pgpt-vm/private')
DEST = '/var/lib/pgpt-s1-preservation/pg685-completed-tools-v1'
STAGE = '/home/ubuntu/pg685-completed-stage-v1'
PREFIXES = ['pg685-completed-tools-v1', 'pg498-pending-tools-v2', 'pg481-pending-tools-v1',
            'pg480-backup-tools-v3', 'pg477-completed-tools-v1', 'pg477-partial-tools-v3',
            'pg475-readback-tools-v1', 'pg474-readback-tools-v1', 'pg473-readback-tools-v1',
            'pg471-readback-tools-v3', 'pg471-completed-tools-v2', 'pg469-current-tools-v3',
            'pg468-recovery-tools-v4', 'pg468-recovery-tools-v2', 'pg466-tool-v3',
            'pg465-completed-tool-v2', 'pg464-completed-readback-v7', 'pg464-code-tools-v2',
            'pg461-known30-tool-v3', 'pg456-applied-tools-v7']
HOST_PREFIXES = ['pg498-pending-tools-v3', 'pg464-code-tools-v2', 'pg490-migration-tools-v4',
                 'pg481-pending-tools-v2', 'pg456-tools-v7']

CHECK = r'''
import pathlib,os,stat,hashlib
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG631')
assert hashlib.sha256(pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG631/RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe'
root=pathlib.Path('/var/lib/pgpt-s1-preservation')
for name,sha in DEPENDENCIES.items():
 p=next(root/d/name for d in PREFIXES[1:]if(root/d/name).is_file());s=p.lstat()
 assert stat.S_ISREG(s.st_mode)and s.st_uid==s.st_gid==0 and s.st_nlink==1 and s.st_mode&0o222==0 and hashlib.sha256(p.read_bytes()).hexdigest()==sha
'''


def main():
    os.umask(0o077)
    assert len(sys.argv) == 2 and sys.argv[1] in ('stage', 'verify', 'activate')
    mode = sys.argv[1]
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=T)
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=T, text=True).strip()
    frozen = json.loads((W/'pg685-frozen-v4.safe.json').read_text())
    assert frozen['actualExit'] == 0 and frozen['graphCases'] == 4 and frozen['cliConditions'] == 20
    for name, sha in frozen['toolSourceHashes'].items():
        assert hashlib.sha256((R/name).read_bytes()).hexdigest() == sha
    subprocess.run(['python3', '-B', str(R/'pg685_owner_receipt_test.py')], check=True)
    files = {n: W/'pg685-completed-tools-v4'/n for n in
             ('Pg685CompletedDeployment.class', 'Pg685CompletedDeployment$References.class')}
    for name, path in files.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == frozen['classHashes'][name]
    for name in ('pg685_completed_contract.py', 'pg685_completed_refs.py',
                 'pg604_unit_sources.py', 'pg685_parent_receipt.py'):
        files[name] = R/name
    assert (R/'pg685_completed_refs.py').read_text() == profile.refs()
    hashes = {n: hashlib.sha256(p.read_bytes()).hexdigest() for n, p in files.items()}
    dependencies = {}
    for name in ('Pg464CodeOnlyDeployment.class', 'Pg387TrustedDeployment.class',
                 'Pg387TrustedDeployment$Checked.class', 'Pg407FailedRootRecovery.class',
                 'Pg428ColdBootPreparation.class', 'Pg481PendingDeployment.class'):
        p = next(W/d/name for d in HOST_PREFIXES if (W/d/name).is_file())
        dependencies[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    payload = 'DEPENDENCIES='+repr(dependencies)+'\nPREFIXES='+repr(PREFIXES)+'\nHASHES='+repr(hashes)+'\nDEST='+repr(DEST)+'\n'+CHECK
    opts = ['-i', str(P/'vm-access'), '-oBatchMode=yes', '-oIdentitiesOnly=yes',
            '-oStrictHostKeyChecking=yes', '-oUserKnownHostsFile='+str(P/'known_hosts')]
    ssh = ['ssh', *opts, '-p', '22222', 'ubuntu@127.0.0.1']
    log = W/('pg685-'+mode+'-v1.private.log')
    safe_path = W/('pg685-'+mode+'-v1.safe.json')
    assert not log.exists() and not safe_path.exists()
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with log.open('xb') as stream:
        if mode == 'stage':
            bundle = P/'pg685-completed-tools-v1.tar'; assert not bundle.exists()
            with tarfile.open(bundle, 'x:') as tar:
                for name, p in sorted(files.items()): tar.add(p, arcname=name, recursive=False)
            subprocess.run(ssh+['test ! -e '+STAGE+' && sudo -n test ! -e '+DEST+' && mkdir -m 700 '+STAGE], check=True, stdout=stream, stderr=stream)
            subprocess.run(['scp', *opts, '-P', '22222', str(bundle), 'ubuntu@127.0.0.1:'+STAGE+'/'], check=True, stdout=stream, stderr=stream)
            payload += '\nBUNDLE='+repr(hashlib.sha256(bundle.read_bytes()).hexdigest())+r'''
import tarfile
p=pathlib.Path('/home/ubuntu/pg685-completed-stage-v1/pg685-completed-tools-v1.tar');assert hashlib.sha256(p.read_bytes()).hexdigest()==BUNDLE
r=pathlib.Path(DEST);assert not os.path.lexists(r);r.mkdir(mode=0o700)
with tarfile.open(p)as tar:
 names=[]
 for member in tar.getmembers():
  assert member.isfile()and member.name in HASHES and member.name not in names;names.append(member.name)
 assert set(names)==set(HASHES);tar.extractall(r,filter='data')
for p in(r,*r.iterdir()):
 s=p.lstat();assert not p.is_symlink()and(stat.S_ISDIR(s.st_mode)or(stat.S_ISREG(s.st_mode)and s.st_nlink==1))
 os.chown(p,0,0);os.chmod(p,0o700 if p.is_dir()else 0o400)
 if p.is_file():assert hashlib.sha256(p.read_bytes()).hexdigest()==HASHES[p.name]
for p in(r,r.parent):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print('PG685_STAGED toolBytesPinned=true businessActions0=true')
'''
        else:
            payload += r'''
r=pathlib.Path(DEST);assert {p.name for p in r.iterdir()}==set(HASHES)
for p in r.iterdir():
 s=p.lstat();assert stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and hashlib.sha256(p.read_bytes()).hexdigest()==HASHES[p.name]
'''
        began = time.monotonic()
        result = subprocess.run(ssh+['sudo -n python3 -B -'], input=payload.encode(), stdout=stream, stderr=stream, timeout=90)
        if result.returncode == 0 and mode != 'stage':
            cp = ':'.join('/var/lib/pgpt-s1-preservation/'+p for p in PREFIXES)
            cp += ':/opt/schubert-nk/releases/0.1.0-PG631/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG631/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG631/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG631/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
            result = subprocess.run(ssh+['sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" Pg685CompletedDeployment '+mode], stdout=stream, stderr=stream)
        elapsed = time.monotonic()-began; stream.flush(); os.fsync(stream.fileno())
    with (W/('pg685-'+mode+'-v1.exit')).open('x') as stream: stream.write(str(result.returncode)+'\n')
    safe = {'run': 'PG685-'+mode+'-v1', 'operatorSource': source, 'candidateSource': profile.SOURCE,
            'actualExit': result.returncode, 'elapsedSeconds': elapsed, 'startedUTC': started,
            'completedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'privateLogSha256': hashlib.sha256(log.read_bytes()).hexdigest(), 'toolHashes': hashes,
            'externalDependencyHashes': dependencies, 'frozenToolSource': frozen['source'],
            'rawExported': False, 'formalAccepted': False, 'oldUnknownNormalized': False}
    with safe_path.open('x') as stream:
        json.dump(safe, stream, indent=2); stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    print(json.dumps({'run': safe['run'], 'actualExit': result.returncode, 'elapsedSeconds': elapsed,
                      'oldUnknownNormalized': False, 'formalAccepted': False}))
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
