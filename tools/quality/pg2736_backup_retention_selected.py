"""Actual missed retention admission conditions; pure fixture and real held FD only."""
import inspect
import pg2220_root_uid_host_selected as previous
from pg2674_operation_publication_sources import production

SOURCE=production()
FILES=[
    'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/BackupRetentionBoundaryTest.java',
    'tools/quality/vm/050_s1/Pg2736BackupRetentionLauncher.java',
    *previous.FILES[2:],
]


def server():
    raw=previous.SERVER.replace('PG2220','PG2736').replace('Pg2220RootUidLauncher',
        'Pg2736BackupRetentionLauncher').replace('source-full-PG2124','source-full-PG2694')
    raw=raw.replace('PG2736-selected-v1','PG2736-selected-v2')
    compile(raw,'<frozen Main retention admission selected>','exec');return raw


def main():
    raw=inspect.getsource(previous.main).replace('PG2220','PG2736').replace('pg2220','pg2736').replace('PG2736-selected-v1','PG2736-selected-v2').replace(
        'pg2125-metadata-boundary-full-qualified-v1','pg2695-expiry-fixed-full-qualified-v1')
    ns={**previous.__dict__,'SOURCE':SOURCE,'FILES':FILES,'SLOT':'pg2736-backup-retention-selected-v2',
        'SERVER':server()}
    exec(compile(raw,'<new-only retention source transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
