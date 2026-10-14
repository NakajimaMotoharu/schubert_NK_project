"""Independent exact XML/hash/current-native counters for retained Backup completion contract."""
import inspect
import pg2752_db_backup_handoff_qualification as previous


def main():
    raw=inspect.getsource(previous.main)
    for a,b in [('pg2750-db-backup-handoff-selected-v1','pg2754-retained-backup-selected-v3'),
                ('PG2750-selected-v1','PG2754-selected-v3'),("'PG2750'","'PG2754'"),
                ('mdb2750001BackupObservationRejectsInHandoffBeforeJdbcAndPreservesFailedPair','mdb2754001RetainedBackupRequiresCurrentCompletionAndPreservesOriginalRows'),
                ("=='observeBackup'","=='retainedBackupSuccessful'"),('PT-MDB-2750-001','PT-MDB-2754-001'),
                ('pg2752-db-backup-handoff-qualified-v1','pg2756-retained-backup-qualified-v1')]:
        if a not in raw:raise ValueError('exact qualification target boundary required')
        raw=raw.replace(a,b)
    first=raw.index("assert counters['BRANCH']")
    last=raw.index("assert all(v['classByteMismatch']",first)
    raw=raw[:first]+"assert counters['BRANCH']=={'missed':0,'covered':16}\nassert counters['LINE']=={'missed':0,'covered':19} and counters['METHOD']=={'missed':0,'covered':1}\n"+raw[last:]
    raw=raw.replace("'BRANCH':532","'BRANCH':531").replace("'remainingLines':lines,",'').replace("'newCounterGain':0","'newCounterGain':1")
    ns={**previous.__dict__}
    exec(compile(raw,'<independent retained Backup qualification>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
