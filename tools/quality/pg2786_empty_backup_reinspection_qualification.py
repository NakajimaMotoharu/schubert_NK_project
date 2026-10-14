"""Read-only exact XML/current counters for three empty reinspection cases."""
import inspect
import pg2752_db_backup_handoff_qualification as previous


def main():
    raw=inspect.getsource(previous.main)
    for a,b in [('pg2750-db-backup-handoff-selected-v1','pg2784-empty-backup-reinspection-selected-v1'),
                ('PG2750-selected-v1','PG2784-selected-v1'),("'PG2750'","'PG2784'"),
                ('mdb2750001BackupObservationRejectsInHandoffBeforeJdbcAndPreservesFailedPair','mdb2784001EmptyBackupReinspectionCannotAuthorizeResumeOrObservation'),
                ('PT-MDB-2750-001','PT-MDB-2784-001'),('pg2752-db-backup-handoff-qualified-v1','pg2786-empty-backup-reinspection-qualified-v1')]:
        if a not in raw:raise ValueError('exact empty inspection qualification target required')
        raw=raw.replace(a,b)
    first=raw.index("assert counters['BRANCH']")
    last=raw.index("assert all(v['classByteMismatch']",first)
    proof="""assert counters['BRANCH']=={'missed':1,'covered':31}
other=next(v for v in c.findall('method')if v.get('name')=='beginResumeBackup')
other_counters={v.get('type'):{'missed':int(v.get('missed')),'covered':int(v.get('covered'))}for v in other.findall('counter')}
assert other_counters['BRANCH']['missed']==2 and other_counters['LINE']['missed']==0
"""
    raw=raw[:first]+proof+raw[last:]
    raw=raw.replace("'LINE':788","'LINE':785").replace("'BRANCH':532","'BRANCH':526").replace("'remainingLines':lines,",'').replace("'newCounterGain':0","'newBranchGain':3,'newLineGain':1,'resumeCounters':other_counters,'fixtureModes':3")
    ns={**previous.__dict__}
    exec(compile(raw,'<independent three empty reinspection qualification>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
