"""Independent literal pending identity test against frozen current Main; no VM action."""
import inspect
import pg2220_root_uid_host_selected as previous
from pg2674_operation_pending_sources import production

SOURCE = production()
FILES = [
    'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/BackupArtifactVerifierTest.java',
    'tools/quality/vm/050_s1/Pg2740BackupPendingLauncher.java',
    *previous.FILES[2:],
]


def server():
    raw = previous.SERVER.replace('PG2220', 'PG2740').replace('Pg2220RootUidLauncher',
        'Pg2740BackupPendingLauncher').replace('source-full-PG2124', 'source-full-PG2694')
    compile(raw, '<frozen new-source independent pending test>', 'exec')
    return raw


def main():
    raw = inspect.getsource(previous.main).replace('PG2220', 'PG2740').replace('pg2220',
        'pg2740').replace('pg2125-metadata-boundary-full-qualified-v1',
                        'pg2695-expiry-fixed-full-qualified-v1')
    ns = {**previous.__dict__, 'SOURCE': SOURCE, 'FILES': FILES,
          'SLOT': 'pg2740-backup-pending-selected-v1', 'SERVER': server()}
    exec(compile(raw, '<new-only limited host transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
