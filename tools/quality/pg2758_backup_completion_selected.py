"""Actual JDBC completion faults against isolated PostgreSQL, unchanged current Main/native."""
import pg2754_retained_backup_selected as previous

SOURCE=previous.SOURCE
FILES=[previous.FILES[0],'tools/quality/vm/050_s1/Pg2758BackupCompletionFailureLauncher.java',*previous.FILES[2:]]


def server():
    raw=previous.server().replace('PG2754','PG2758').replace('Pg2754RetainedBackupLauncher','Pg2758BackupCompletionFailureLauncher').replace('PG2758-selected-v3','PG2758-selected-v1')
    compile(raw,'<isolated actual JDBC completion faults>','exec');return raw


def transport_body():
    raw=previous.transport_body().replace('PG2754','PG2758').replace('pg2754','pg2758').replace('PG2758-selected-v3','PG2758-selected-v1')
    if raw.count('PG2758-selected-v1')!=5 or 'PG2754' in raw or 'selected-v3' in raw:
        raise ValueError('complete new-only JDBC completion transport required')
    compile(raw,'<current JDBC completion transport>','exec');return raw


def main():
    base=previous.previous
    ns={**base.transport.__dict__,'SOURCE':SOURCE,'FILES':FILES,'SLOT':'pg2758-backup-completion-selected-v1',
        'SERVER':server(),'native_input':base.native_input}
    exec(compile(transport_body(),'<actual JDBC completion source>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
