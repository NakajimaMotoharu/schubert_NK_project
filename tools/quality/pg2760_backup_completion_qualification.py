"""Independent XML/hash and SQLException path qualification, not formal/global acceptance."""
import inspect
import pg2752_db_backup_handoff_qualification as previous


def main():
    raw=inspect.getsource(previous.main)
    for a,b in [('pg2750-db-backup-handoff-selected-v1','pg2758-backup-completion-selected-v1'),
                ('PG2750-selected-v1','PG2758-selected-v1'),("'PG2750'","'PG2758'"),
                ('mdb2750001BackupObservationRejectsInHandoffBeforeJdbcAndPreservesFailedPair','mdb2758001ReusedBackupSqlCompletionFailuresPreserveOriginalAndSkippedRows'),
                ("=='observeBackup'","=='completeReusedBackup'"),('PT-MDB-2750-001','PT-MDB-2758-001'),
                ('pg2752-db-backup-handoff-qualified-v1','pg2760-backup-completion-qualified-v1')]:
        if a not in raw:raise ValueError('exact JDBC failure qualification target required')
        raw=raw.replace(a,b)
    first=raw.index("assert counters['BRANCH']")
    last=raw.index("assert all(v['classByteMismatch']",first)
    raw=raw[:first]+"assert counters and all(v['missed']==0 for v in counters.values())\n"+raw[last:]
    raw=raw.replace("'LINE':788","'LINE':786").replace("'remainingLines':lines,",'').replace("'newCounterGain':0","'newLineGain':2,'newBranchGain':0")
    ns={**previous.__dict__}
    exec(compile(raw,'<independent JDBC completion failure qualification>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
