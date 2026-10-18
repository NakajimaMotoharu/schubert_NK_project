"""Future-run PostgreSQL binary observation, never retroactive VM/DB qualification."""
import hashlib
from pathlib import Path
import subprocess


def capture(pg_root, selected_suites, runner=subprocess.run):
    root = Path(pg_root)
    binary = root / 'lib/postgresql/18/bin/postgres'
    if not binary.is_file():
        raise ValueError('configured isolated PostgreSQL binary missing')
    env = {'PATH': '/usr/bin:/bin', 'LANG': 'C', 'LC_ALL': 'C',
           'LD_LIBRARY_PATH': str(root / 'lib/x86_64-linux-gnu') + ':' + str(root / 'lib/postgresql/18/lib')}
    result = runner([str(binary), '--version'], env=env, capture_output=True, text=True,
                    timeout=10, check=False)
    version = result.stdout.strip()
    if result.returncode != 0 or not version.startswith('postgres (PostgreSQL) 18.') or '\n' in version:
        raise ValueError('isolated PostgreSQL version observation failed')
    return {'postgresVersion': version, 'postgresSha256': hashlib.sha256(binary.read_bytes()).hexdigest(),
            'isolatedFixtureDatabaseSelected':
                'dev.codex.schubert.nk.api.file.ServiceProcessResourcesTest' in selected_suites,
            'originalOrVmDatabaseActions': 0, 'historicalRunQualification': False}
