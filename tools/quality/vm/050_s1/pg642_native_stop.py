"""Publish immutable new-cohort tools then owned ordered stop under enclosing M/A/DB.

Only after genuine PG640 and current A01; no deployment/start/repair/epoch change.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
import time
from pg642_stop_binding import generate

R = Path(__file__).resolve().parent
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P = Path('/home/mini/codex/project1/work/pgpt-vm/private')
DEST = '/var/lib/pgpt-s1-preservation/pg642-native-tools-v1'
STAGE = '/home/ubuntu/pg642-native-stage-v1'


def main():
    os.umask(0o077)
    assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=R.parents[3]) == b''
    assert (W/'pg640-completed-readonly-v1.exit').read_bytes() == b'0\n'
    assert (W/'pg641-chr-a01-native-v1.exit').read_bytes() == b'0\n'
    assert (W/'pg642-native-compile-v1.private.log').read_bytes() == b''
    assert (W/'pg642-argument-oracle-v1.private.log').read_bytes() == b'PG642_ARGUMENT_ORACLE independentAssertions=6 nullNpe0=true ownershipActions0=true\n'
    proof = json.loads((W/'pg640-completed-readonly-v1.safe.json').read_bytes())
    generated = generate(proof)
    target = W/'pg642-native-tools-v1'
    build = json.loads((W/'pg642-native-build-v1.safe.json').read_bytes())
    assert build['actualCompileExit'] == build['argumentExit'] == 0 and build['genuineParentBeforeSha256'] == proof['beforeSha256']
    for name, raw in generated.items(): assert (target/name).read_text() == raw
    for name, sha in build['files'].items(): assert hashlib.sha256((target/name).read_bytes()).hexdigest() == sha
    names = ('Pg642NativeStop.class', 'Pg642NativeStop$References.class', 'pg642_native_refs.py',
             'pg642_native_owned_stop.py', 'pg642_parent_receipt.py', 'pg642_durable.py',
             'pg526_term_witness.py', 'pg526_native_term_witness.py')
    hashes = {name: build['files'][name] for name in names}
    bundle = P/'pg642-native-tools-v1.tar'
    with tarfile.open(bundle, 'x:') as tar:
        for name in names: tar.add(target/name, arcname=name, recursive=False)
    opts = ['-i', str(P/'vm-access'), '-oBatchMode=yes', '-oIdentitiesOnly=yes',
            '-oStrictHostKeyChecking=yes', '-oUserKnownHostsFile='+str(P/'known_hosts')]
    ssh = ['ssh', *opts, '-p', '22222', 'ubuntu@127.0.0.1']
    subprocess.run(ssh+['test ! -e '+STAGE+' && sudo -n test ! -e '+DEST+
                        ' && sudo -n test ! -e /var/lib/pgpt-s1-preservation/pg642-native-stop-v1 && mkdir -m700 '+STAGE], check=True)
    subprocess.run(['scp', *opts, '-P', '22222', str(bundle), 'ubuntu@127.0.0.1:'+STAGE+'/'], check=True, stdout=subprocess.DEVNULL)
    payload = r'''
import pathlib,os,tarfile,hashlib,stat
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
p=pathlib.Path('/home/ubuntu/pg642-native-stage-v1/pg642-native-tools-v1.tar');assert hashlib.sha256(p.read_bytes()).hexdigest()==BUNDLE
r=pathlib.Path('/var/lib/pgpt-s1-preservation/pg642-native-tools-v1');assert not os.path.lexists(r);r.mkdir(mode=0o700)
with tarfile.open(p)as t:
 members=t.getmembers();assert len(members)==len(HASHES)and {m.name for m in members}==set(HASHES)
 for m in members:assert m.isfile()and pathlib.PurePosixPath(m.name).name==m.name
 t.extractall(r,filter='data')
for p in r.iterdir():
 s=p.lstat();assert stat.S_ISREG(s.st_mode)and s.st_nlink==1 and not p.is_symlink();os.chown(p,0,0);os.chmod(p,0o400)
 assert hashlib.sha256(p.read_bytes()).hexdigest()==HASHES[p.name]
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
for p in(r,r.parent):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print('PG642_STAGED immutable400=true starts0=true')
'''
    log = W/'pg642-native-stop-v1.private.log'
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with log.open('xb') as f:
        staged = subprocess.run(ssh+['sudo -n python3 -B -'], input=('HASHES='+repr(hashes)+'\nBUNDLE='+repr(hashlib.sha256(bundle.read_bytes()).hexdigest())+'\n'+payload).encode(), stdout=f, stderr=f)
        assert staged.returncode == 0
        prefixes = ['pg642-native-tools-v1', 'pg498-pending-tools-v2', 'pg481-pending-tools-v1',
                    'pg480-backup-tools-v3', 'pg477-completed-tools-v1', 'pg477-partial-tools-v3',
                    'pg475-readback-tools-v1', 'pg474-readback-tools-v1', 'pg473-readback-tools-v1',
                    'pg471-readback-tools-v3', 'pg471-completed-tools-v2', 'pg469-current-tools-v3',
                    'pg468-recovery-tools-v4', 'pg468-recovery-tools-v2', 'pg466-tool-v3',
                    'pg465-completed-tool-v2', 'pg464-completed-readback-v7', 'pg464-code-tools-v2',
                    'pg461-known30-tool-v3', 'pg456-applied-tools-v7']
        cp = ':'.join('/var/lib/pgpt-s1-preservation/'+p for p in prefixes)
        cp += ':/opt/schubert-nk/releases/0.1.0-PG631/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG631/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG631/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG631/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
        began = time.monotonic()
        result = subprocess.run(ssh+['sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'+cp+'" Pg642NativeStop stop'], stdout=f, stderr=f)
        elapsed = time.monotonic()-began; f.flush(); os.fsync(f.fileno())
    with (W/'pg642-native-stop-v1.exit').open('x') as f: f.write(str(result.returncode)+'\n')
    safe = {'actualExit': result.returncode, 'run': 'PG642-native-stop-v1', 'productionSource': proof['productionSource'],
            'operatorSource': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
            'elapsedSeconds': elapsed, 'startedUTC': started, 'endedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'privateLogSha256': hashlib.sha256(log.read_bytes()).hexdigest(), 'oldCloseNotInferred': True,
            'productionPT0': True, 'formalAccepted': False}
    with (W/'pg642-native-stop-v1.safe.json').open('x') as f: json.dump(safe, f, sort_keys=True)
    print(json.dumps(safe)); raise SystemExit(result.returncode)


if __name__ == '__main__': main()
