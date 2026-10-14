"""Exact XML/hash and independent oracle strengthening, coverage gain explicitly zero."""
import inspect
import pg2752_db_backup_handoff_qualification as previous


def main():
    raw=inspect.getsource(previous.main)
    for a,b in [('pg2750-db-backup-handoff-selected-v1','pg2788-success-pair-timestamp-selected-v1'),
                ('PG2750-selected-v1','PG2788-selected-v1'),("'PG2750'","'PG2788'"),
                ('mdb2750001BackupObservationRejectsInHandoffBeforeJdbcAndPreservesFailedPair','mdb2788001SuccessfulPairRejectsDifferentStartAndEndWithinValidBounds'),
                ("=='observeBackup'","=='successfulBackup'"),('PT-MDB-2750-001','PT-MDB-2788-001'),
                ('pg2752-db-backup-handoff-qualified-v1','pg2790-success-pair-timestamp-qualified-v1')]:
        if a not in raw:raise ValueError('exact pair timestamp qualification target required')
        raw=raw.replace(a,b)
    first=raw.index("assert counters['BRANCH']")
    last=raw.index("assert all(v['classByteMismatch']",first)
    raw=raw[:first]+"assert counters['BRANCH']=={'missed':2,'covered':22}\nassert counters['LINE']=={'missed':0,'covered':36} and counters['METHOD']=={'missed':0,'covered':1}\n"+raw[last:]
    raw=raw.replace("'LINE':788","'LINE':786").replace("'BRANCH':532","'BRANCH':529").replace("'remainingLines':lines,",'')
    ns={**previous.__dict__}
    exec(compile(raw,'<independent existing pair timestamp oracle strengthening>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
