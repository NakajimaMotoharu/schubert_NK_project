"""New-only host evidence for SSC244 pure contracts; never contacts the VM."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
OUT = Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg1027-host-contract-v2')


def main():
    os.umask(0o077)
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('committed source required')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    names = ['pg1026_cold_observation_contract.py', 'pg1026_cold_observation_contract_test.py',
             'pg1027_cold_contract_capture.py']
    hashes = {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in names}
    OUT.mkdir(mode=0o700)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    command = ['python3', '-B', str(HERE / 'pg1026_cold_observation_contract_test.py'), '-v']
    with (OUT / 'test.log').open('xb') as f:
        result = subprocess.run(command, cwd=ROOT, stdout=f, stderr=f)
        f.flush()
        os.fsync(f.fileno())
    unchanged = (subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == source
                 and not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT)
                 and hashes == {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in names})
    value = {'run': 'PG1027-host-contract-v2', 'actualExit': result.returncode,
             'operatorSource': source, 'sourceUnchanged': unchanged, 'sourceHashes': hashes,
             'startedUTC': started, 'completedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'command': command, 'logSha256': hashlib.sha256((OUT / 'test.log').read_bytes()).hexdigest(),
             'hostTests': 10, 'vmActions': 0, 'formalAccepted': False,
             'fullColdPreparationAccepted': False, 'relatedBUG': ['BUG-1009', 'BUG-1010'],
             'relatedSSC': ['SSC-244'], 'relatedYKT': ['YKT-778', 'YKT-779']}
    with (OUT / 'manifest.safe.json').open('x') as f:
        json.dump(value, f, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
    directory = os.open(OUT, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    print(json.dumps(value, sort_keys=True))
    raise SystemExit(result.returncode if unchanged else 1)


if __name__ == '__main__':
    main()
