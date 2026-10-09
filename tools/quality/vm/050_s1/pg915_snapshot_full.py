"""451 new-source six-module regression after PG-D407 and independent snapshot oracle."""
import subprocess
from pg857_completed_reference_full import source as previous


def source():
    raw = previous()
    assert raw.count('pg857-completed-reference-six-host-v1') == 1
    return raw.replace('pg857-completed-reference-six-host-v1', 'pg915-snapshot-six-host-v1').replace('PG857_FULL', 'PG915_FULL')


if __name__ == '__main__':
    fixed = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    raise SystemExit(subprocess.run(['/bin/bash', '-s', '--', fixed], input=source().encode()).returncode)
