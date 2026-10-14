"""Read-only exact XML/counters for actual persisted identity refusal; remaining guards stay open."""
import inspect
import pg2752_db_backup_handoff_qualification as previous


def main():
    raw=inspect.getsource(previous.main)
    for a,b in [('pg2750-db-backup-handoff-selected-v1','pg2762-post-begin-identity-selected-v1'),
                ('PG2750-selected-v1','PG2762-selected-v1'),("'PG2750'","'PG2762'"),
                ('mdb2750001BackupObservationRejectsInHandoffBeforeJdbcAndPreservesFailedPair','mdb2762001PostBeginRejectsForeignRunAndActualLogCutoffDrift'),
                ("=='observeBackup'","=='recheckConsistent'"),('PT-MDB-2750-001','PT-MDB-2762-001'),
                ('pg2752-db-backup-handoff-qualified-v1','pg2764-post-begin-identity-qualified-v1')]:
        if a not in raw:raise ValueError('exact actual identity qualification target required')
        raw=raw.replace(a,b)
    first=raw.index("assert counters['BRANCH']")
    last=raw.index("assert all(v['classByteMismatch']",first)
    raw=raw[:first]+"assert counters['BRANCH']['missed']==1 and counters['LINE']['missed']==0 and counters['METHOD']['missed']==0\n"+raw[last:]
    raw=raw.replace("'BRANCH':532","'BRANCH':530").replace("'remainingLines':lines,",'').replace("'newCounterGain':0","'newBranchGain':2,'methodNotYetAllBranches':True")
    ns={**previous.__dict__}
    exec(compile(raw,'<independent actual persisted identity qualification>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
