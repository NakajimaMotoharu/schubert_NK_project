"""Fresh immutable sources and old-current ABI/Werror/CLI freeze; no guest action."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg717_sources as p

R = Path(__file__).resolve().parent
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def main():
    os.umask(0o077)
    assert subprocess.check_output(['git', 'status', '--porcelain']) == b''
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    source_names = ('pg717_sources.py', 'pg717_compile.py', 'pg717_contract_graph_test.py',
                    'pg717_owner_receipt_test.py', 'pg604_unit_sources.py')
    source_hashes = {name: hashlib.sha256((R / name).read_bytes()).hexdigest() for name in source_names}
    assert (W / 'pg716-completed-baseline-v1.exit').read_bytes() == b'0\n'
    subprocess.run(['python3', '-B', str(R / 'pg717_contract_graph_test.py')], check=True)
    target = W / 'pg717-completed-tools-v1'; target.mkdir(mode=0o700)
    values = {'Pg717CompletedDeployment.java': p.java(), 'Pg717CompletedDeploymentTest.java': p.java_test(),
              'pg717_completed_contract.py': p.contract(), 'pg717_completed_refs.py': p.refs(),
              'pg717_parent_receipt.py': p.receipt()}
    for name, raw in values.items():
        with (target / name).open('x') as output:
            os.fchmod(output.fileno(), 0o400); output.write(raw); output.flush(); os.fsync(output.fileno())
    script = p.compile_script(); subprocess.run(['/bin/bash', '-n'], input=script.encode(), check=True)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    outcome = subprocess.run(['/bin/bash', '-s'], input=script.encode(), check=True)
    assert outcome.returncode == 0 and (W / 'pg717-compile-v1.private.log').read_bytes() == b''
    raw = (W / 'pg717-oracle-v1.private.log').read_text(); assert 'conditions20=true' in raw and '\nOK\n' in raw
    assert subprocess.check_output(['git', 'status', '--porcelain']) == b''
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip() == head
    assert source_hashes == {name: hashlib.sha256((R / name).read_bytes()).hexdigest() for name in source_names}
    safe = {'actualExit': 0, 'startedUTC': started, 'completedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'classHashes': {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in target.glob('*.class')},
            'toolHashes': {n: hashlib.sha256((target / n).read_bytes()).hexdigest() for n in values},
            'operatorSource': head, 'source': head, 'toolSourceHashes': source_hashes,
            'graphCases': 3, 'cliConditions': 20, 'guestActions0': True, 'formalAccepted': False}
    with (W / 'pg717-frozen-v1.safe.json').open('x') as output: json.dump(safe, output, sort_keys=True)
    print(json.dumps({'actualExit': 0, 'Werror0': True, 'graph3': True, 'cli20': True, 'guestActions0': True}))


if __name__ == '__main__': main()
