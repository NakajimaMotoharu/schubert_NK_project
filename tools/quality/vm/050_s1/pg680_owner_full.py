"""Fresh whole-six after Inspector + shared parent guard; no source reuse."""
from pathlib import Path
import subprocess
from pg672_full_v2 import source as previous

R = Path(__file__).resolve().parent


def source():
    raw = previous()
    assert raw.count('pg672-entry-six-host-v2') == 1
    raw = raw.replace('pg672-entry-six-host-v2', 'pg680-owner-six-host-v1')
    return raw.replace('PG672_FULL', 'PG680_FULL')


if __name__ == '__main__':
    fixed = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    raise SystemExit(subprocess.run(['/bin/bash', '-s', '--', fixed], input=source().encode()).returncode)
