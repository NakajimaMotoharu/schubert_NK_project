"""Actual isolated PostgreSQL retained-backup pre-completion contract; current frozen Main."""
import inspect
import pg2750_db_backup_handoff_selected as previous

SOURCE=previous.SOURCE
FILES=[previous.FILES[0],'tools/quality/vm/050_s1/Pg2754RetainedBackupLauncher.java',*previous.FILES[2:]]


def server():
    raw=previous.server().replace('PG2750','PG2754').replace('Pg2750BackupHandoffLauncher','Pg2754RetainedBackupLauncher').replace('PG2754-selected-v1','PG2754-selected-v3')
    compile(raw,'<isolated retained Backup pre-completion>','exec');return raw


def transport_body():
    raw=inspect.getsource(previous.transport.main).replace('PG2220','PG2754').replace('pg2220','pg2754').replace('PG2754-selected-v1','PG2754-selected-v3').replace(
        'pg2125-metadata-boundary-full-qualified-v1','pg2745-backup-admission-full-qualified-v1')
    raw=raw.replace(",'libraries':libs}",",'libraries':libs,'native':native_input()}")
    if 'PG2754-selected-v1' in raw or raw.count('PG2754-selected-v3')!=5:
        raise ValueError('completed selected transport must use one new v3 namespace')
    compile(raw,'<current retained Backup completed transport>','exec');return raw


def main():
    ns={**previous.transport.__dict__,'SOURCE':SOURCE,'FILES':FILES,'SLOT':'pg2754-retained-backup-selected-v3',
        'SERVER':server(),'native_input':previous.native_input}
    exec(compile(transport_body(),'<current retained Backup selected source>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
