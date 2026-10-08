"""SSC225 current-source Bootstrap: separate verify/execute, new-only private outputs.

The normal signed Unit is the only Production entry. Old credentials/source/run
are not restored. CLI compile/oracles and actual verify must succeed before execute.
"""
import datetime
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tarfile
import time

os.umask(0o077)
R = pathlib.Path(__file__).resolve().parent
W = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P = pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
TOOLS = '/var/lib/pgpt-s1-preservation/pg570-bootstrap-tools-v1'
STAGE = '/home/ubuntu/pg570-bootstrap-stage-v1'
CLASSDIR = W / 'pg570-bootstrap-tools-v1'
DEPENDENCIES = ['pg498-pending-tools-v2', 'pg481-pending-tools-v1', 'pg480-backup-tools-v3',
                'pg477-completed-tools-v1', 'pg477-partial-tools-v3', 'pg475-readback-tools-v1',
                'pg474-readback-tools-v1', 'pg473-readback-tools-v1', 'pg471-readback-tools-v3',
                'pg471-completed-tools-v2', 'pg469-current-tools-v3', 'pg468-recovery-tools-v4',
                'pg468-recovery-tools-v2', 'pg466-tool-v3', 'pg465-completed-tool-v2',
                'pg464-completed-readback-v7', 'pg464-code-tools-v2', 'pg461-known30-tool-v3',
                'pg456-applied-tools-v7']


def main():
    assert len(sys.argv) == 2 and sys.argv[1] in ('verify', 'execute')
    mode = sys.argv[1]
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R).decode().strip()
    assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=R) == b''
    for test in ('pg569_parent_join_test.py', 'pg570_directory_identity_test.py',
                 'pg570_bootstrap_contract_test.py'):
        subprocess.run(['python3', '-B', str(R / test)], check=True)
    assert (W / 'pg570-bootstrap-compile-v1.private.log').read_bytes() == b''
    assert (W / 'pg570-bootstrap-argument-oracle-v1.private.log').read_bytes() == (
        b'PG570_ARGUMENT_ORACLE independentAssertions=8 nullNpe0=true ownershipActions0=true\n')
    for name in ('pg570-bootstrap-oracle-v1', 'pg570-reused-credential-oracle-v1',
                 'pg570-reused-history-oracle-v1'):
        raw = (W / (name + '.private.log')).read_bytes()
        assert raw.endswith(b'\nOK\n') and b'FAILED' not in raw
    opts = ['-i', str(P / 'vm-access'), '-oBatchMode=yes', '-oIdentitiesOnly=yes',
            '-oStrictHostKeyChecking=yes', '-oUserKnownHostsFile=' + str(P / 'known_hosts')]
    ssh = ['ssh', *opts, '-p', '22222', 'ubuntu@127.0.0.1']
    files = {n: CLASSDIR / n for n in ('Pg570BootstrapExisting.class', 'Pg570BootstrapExisting$References.class')}
    for name in ('pg570_bootstrap_existing.py', 'pg535_bootstrap_contract.py',
                 'pg536_bootstrap_execution_contract.py', 'pg529_dependency_graph.py',
                 'pg556_parent_receipt.py', 'pg559_terminal_refs.py', 'pg457_stable_actor.py',
                 'pg569_parent_join.py', 'pg570_directory_identity.py'):
        files[name] = R / name
    hashes = {name: hashlib.sha256(p.read_bytes()).hexdigest() for name, p in files.items()}
    log = W / ('pg570-bootstrap-' + mode + '-v1.private.log')
    exit_file = W / ('pg570-bootstrap-' + mode + '-v1.exit')
    result_file = W / ('pg570-bootstrap-' + mode + '-v1.safe.json')
    assert not any(p.exists() for p in (log, exit_file, result_file))
    if mode == 'execute':
        prior = json.loads((W / 'pg570-bootstrap-verify-v1.safe.json').read_bytes())
        assert prior['actualExit'] == 0 and prior['toolHashes'] == hashes
        assert (W / 'pg570-bootstrap-verify-v1.exit').read_bytes() == b'0\n'
    if mode == 'verify':
        bundle = P / 'pg570-bootstrap-tools-v1.private.tar'
        assert not bundle.exists()
        with tarfile.open(bundle, 'x:') as archive:
            for name, path in sorted(files.items()): archive.add(path, arcname=name, recursive=False)
        subprocess.run(ssh + ['test ! -e ' + STAGE + ' && sudo -n test ! -e ' + TOOLS
                            + ' && mkdir -m 700 ' + STAGE], check=True)
        subprocess.run(['scp', *opts, '-P', '22222', str(bundle),
                        'ubuntu@127.0.0.1:' + STAGE + '/'], check=True, stdout=subprocess.DEVNULL)
        payload = r'''import hashlib,os,pathlib,stat,tarfile
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
bundle=pathlib.Path('/home/ubuntu/pg570-bootstrap-stage-v1/pg570-bootstrap-tools-v1.private.tar');assert hashlib.sha256(bundle.read_bytes()).hexdigest()==BUNDLE
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg570-bootstrap-tools-v1');assert not root.exists();root.mkdir(mode=0o700)
with tarfile.open(bundle)as archive:
 members=archive.getmembers();assert len(members)==len(HASHES)and {p.name for p in members}==set(HASHES)and all(p.isfile()and p.name in HASHES for p in members)
 for entry in members:
  raw=archive.extractfile(entry).read();assert hashlib.sha256(raw).hexdigest()==HASHES[entry.name]
  with(root/entry.name).open('xb')as f:os.fchmod(f.fileno(),0o400);f.write(raw);f.flush();os.fsync(f.fileno())
for directory in (root,root.parent):
 fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
'''
        subprocess.run(ssh + ['sudo -n python3 -B -'],
                       input=('HASHES=' + repr(hashes) + '\nBUNDLE='
                              + repr(hashlib.sha256(bundle.read_bytes()).hexdigest()) + '\n' + payload).encode(),
                       check=True, stdout=subprocess.DEVNULL)
    probe = "import hashlib,os,pathlib,stat; root=pathlib.Path(" + repr(TOOLS) + "); assert os.geteuid()==0; assert {p.name for p in root.iterdir()}==set(HASHES)\nfor name,sha in HASHES.items():\n p=root/name;s=p.lstat();assert stat.S_ISREG(s.st_mode)and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o400 and s.st_nlink==1 and hashlib.sha256(p.read_bytes()).hexdigest()==sha\n"
    subprocess.run(ssh + ['sudo -n python3 -B -'], input=('HASHES=' + repr(hashes) + '\n' + probe).encode(),
                   check=True, stdout=subprocess.DEVNULL)
    release = '/opt/schubert-nk/releases/0.1.0-PG548'
    cp = ':'.join([TOOLS, *('/var/lib/pgpt-s1-preservation/' + p for p in DEPENDENCIES),
                   release + '/operations/batch.jar', release + '/operations/lib/*',
                   release + '/api/api.jar', release + '/api/lib/*',
                   '/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'])
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with log.open('xb') as output:
        began = time.monotonic()
        outcome = subprocess.run(ssh + ['sudo -n /opt/jdk-25.0.4/bin/java --enable-native-access=ALL-UNNAMED -cp "'
                                       + cp + '" Pg570BootstrapExisting ' + mode], stdout=output, stderr=output)
        elapsed = time.monotonic() - began; output.flush(); os.fsync(output.fileno())
    with exit_file.open('x') as output:
        output.write(str(outcome.returncode) + '\n'); output.flush(); os.fsync(output.fileno())
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R).decode().strip() == source
    assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=R) == b''
    safe = {'operatorSource': source, 'productionSource': '969d8ded10c0bf5841d9e3a5c531e922caf4a24a',
            'run': 'PG570-bootstrap-' + mode + '-v1', 'actualExit': outcome.returncode,
            'elapsedSeconds': elapsed, 'startedAt': started,
            'endedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'toolHashes': hashes,
            'privateLogSha256': hashlib.sha256(log.read_bytes()).hexdigest(),
            'oldCloseNotInferred': True, 'productionPT0': True, 'formalAccepted': False}
    with result_file.open('x') as output:
        json.dump(safe, output, sort_keys=True); output.flush(); os.fsync(output.fileno())
    print(json.dumps(safe)); sys.exit(outcome.returncode)


if __name__ == '__main__':
    main()
