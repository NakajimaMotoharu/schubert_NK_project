"""Actual isolated PostgreSQL retained-backup pre-completion contract; current frozen Main."""
import inspect
import pg2750_db_backup_handoff_selected as previous

SOURCE=previous.SOURCE
FILES=[previous.FILES[0],'tools/quality/vm/050_s1/Pg2754RetainedBackupLauncher.java',*previous.FILES[2:]]


def server():
    raw=previous.server().replace('PG2750','PG2754').replace('Pg2750BackupHandoffLauncher','Pg2754RetainedBackupLauncher')
    compile(raw,'<isolated retained Backup pre-completion>','exec');return raw


def main():
    raw=inspect.getsource(previous.main).replace('PG2750','PG2754').replace('pg2750','pg2754').replace('pg2754-db-backup-handoff-selected-v1','pg2754-retained-backup-selected-v1')
    ns={**previous.__dict__,'FILES':FILES,'server':server}
    exec(compile(raw,'<current retained Backup selected source>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
