"""Independent exact XML and both skipped rejection branches, no inferred global union."""
import inspect
import pg2752_db_backup_handoff_qualification as previous


def main():
    raw=inspect.getsource(previous.main)
    for a,b in [('pg2750-db-backup-handoff-selected-v1','pg2780-resume-skip-history-selected-v1'),
                ('PG2750-selected-v1','PG2780-selected-v1'),("'PG2750'","'PG2780'"),
                ('mdb2750001BackupObservationRejectsInHandoffBeforeJdbcAndPreservesFailedPair','mdb2780001ResumeRejectsEitherNonSkippedAttemptBeforeCommit'),
                ("=='observeBackup'","=='beginResumeBackup'"),('PT-MDB-2750-001','PT-MDB-2780-001'),
                ('pg2752-db-backup-handoff-qualified-v1','pg2782-resume-skip-history-qualified-v1')]:
        if a not in raw:raise ValueError('exact resume skip qualification target required')
        raw=raw.replace(a,b)
    first=raw.index("assert counters['BRANCH']")
    last=raw.index("assert all(v['classByteMismatch']",first)
    raw=raw[:first]+"assert counters['BRANCH']['missed']==1 and counters['LINE']['missed']==1 and counters['METHOD']['missed']==0\n"+raw[last:]
    raw=raw.replace("'LINE':788","'LINE':786").replace("'BRANCH':532","'BRANCH':527").replace("'remainingLines':lines,",'').replace("'newCounterGain':0","'newBranchGain':2,'methodNotYetAllBranches':True")
    ns={**previous.__dict__}
    exec(compile(raw,'<independent both resumed skips qualification>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
