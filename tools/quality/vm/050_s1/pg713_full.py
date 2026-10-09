"""Fresh whole-six trigger: changed Expiry production and new test group; old success not reused."""
from pathlib import Path
import subprocess
from pg680_owner_full import source as previous

R = Path(__file__).resolve().parent


def source():
    raw = previous(); assert raw.count('pg680-owner-six-host-v1') == 1
    return raw.replace('pg680-owner-six-host-v1', 'pg713-expiry-six-host-v1').replace('PG680_FULL', 'PG713_FULL')


if __name__ == '__main__':
    fixed = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    raise SystemExit(subprocess.run(['/bin/bash', '-s', '--', fixed], input=source().encode()).returncode)
