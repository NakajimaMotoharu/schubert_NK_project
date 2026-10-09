"""Commit-clean native-tool freeze after all graph/CLI vectors are fixed."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

R = Path(__file__).resolve().parent
T = R.parents[3]
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def recipe(raw):
    before_cp = next(line for line in raw.splitlines() if line.startswith('task_cp='))
    for name in ('completed-tools', 'compile', 'oracle'):
        old = 'pg685-' + name + '-v2'
        assert raw.count(old) == 1
        raw = raw.replace(old, 'pg685-' + name + '-v4')
    assert next(line for line in raw.splitlines() if line.startswith('task_cp=')) == before_cp
    return raw


def main():
    os.umask(0o077)
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=T)
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=T, text=True).strip()
    names = ('Pg685CompletedDeployment.java', 'Pg685CompletedDeploymentTest.java',
             'pg685_compile_v2.sh', 'pg685_sources.py', 'pg685_completed_contract.py',
             'pg685_completed_refs.py', 'pg685_parent_receipt.py', 'pg685_contract_graph_test.py',
             'pg604_unit_sources.py', 'pg685_compile_frozen.py', 'pg685_freeze_test.py')
    hashes = {name: hashlib.sha256((R/name).read_bytes()).hexdigest() for name in names}
    raw = recipe((R/'pg685_compile_v2.sh').read_text())
    assert not (W/'pg685-frozen-v4.safe.json').exists()
    subprocess.run(['python3', '-B', str(R/'pg685_freeze_test.py')], check=True)
    subprocess.run(['/bin/bash', '-n'], input=raw.encode(), check=True)
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result = subprocess.run(['/bin/bash', '-s'], input=raw.encode(), cwd=T)
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=T)
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=T, text=True).strip() == head
    assert hashes == {name: hashlib.sha256((R/name).read_bytes()).hexdigest() for name in names}
    safe = {'actualExit': result.returncode, 'run': 'PG685-frozen-v4', 'source': head,
            'startedUTC': start, 'completedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'toolSourceHashes': hashes, 'productionPTCredit': 0, 'guestActions': 0, 'formalAccepted': False}
    if result.returncode == 0:
        target = W/'pg685-completed-tools-v4'
        assert {p.name for p in target.iterdir()} == {'Pg685CompletedDeployment.class', 'Pg685CompletedDeployment$References.class', 'Pg685CompletedDeploymentTest.class'}
        safe['classHashes'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in target.iterdir()}
        for name, value in safe['classHashes'].items():
            assert hashlib.sha256((W/'pg685-completed-tools-v2'/name).read_bytes()).hexdigest() == value
        safe['oldV2ClassBytesIdentical'] = True
        assert (W/'pg685-compile-v4.private.log').read_bytes() == b''
        log = (W/'pg685-oracle-v4.private.log').read_text()
        assert 'Ran 4 tests' in log and '\nOK\n' in log and 'conditions20=true' in log
        safe['graphCases'] = 4; safe['cliConditions'] = 20
    with (W/'pg685-frozen-v4.safe.json').open('x') as stream:
        json.dump(safe, stream, indent=2); stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    print(json.dumps({'actualExit': result.returncode, 'fixedCommit': head, 'nativeToolsNotYetDeployed': True}))
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
