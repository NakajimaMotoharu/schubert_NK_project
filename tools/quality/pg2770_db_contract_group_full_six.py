"""One necessary fresh all-source integration of four independently qualified actual DB methods."""
import hashlib
import inspect
import json
import subprocess
from pathlib import Path
import pg2744_backup_admission_group_full_six as previous
import pg2600_retention_group_full_six as transport_base
from pg1446_current_cold_stage import W
from pg2510_strict_reference_full_six import SCOPE

SOURCE=previous.SOURCE
FULL='94cb6139af40e2f076dd41c4169cc1f5bc903496'
TEST='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/MorningDatabaseSessionTest.java'
CASES=[
 ('pg2752-db-backup-handoff-qualified-v1','PT-MDB-2750-001','mdb2750001BackupObservationRejectsInHandoffBeforeJdbcAndPreservesFailedPair'),
 ('pg2756-retained-backup-qualified-v1','PT-MDB-2754-001','mdb2754001RetainedBackupRequiresCurrentCompletionAndPreservesOriginalRows'),
 ('pg2760-backup-completion-qualified-v1','PT-MDB-2758-001','mdb2758001ReusedBackupSqlCompletionFailuresPreserveOriginalAndSkippedRows'),
 ('pg2764-post-begin-identity-qualified-v1','PT-MDB-2762-001','mdb2762001PostBeginRejectsForeignRunAndActualLogCutoffDrift'),
]


def method_block(text,name):
    start=text.index('  void '+name+'(')
    end=text.index('\n  }\n',start)+len('\n  }\n')
    return text[start:end]


def validate(snapshot):
    root=Path(__file__).resolve().parents[2]
    git=lambda *args:subprocess.check_output(['git',*args],cwd=root)
    previous.validate(FULL)
    changed=set(git('diff','--name-only',FULL,snapshot,'--',*SCOPE).decode().splitlines())
    if changed!={TEST}:raise ValueError('exact one new DB Test source required; Main/resources unchanged')
    current=git('show',snapshot+':'+TEST)
    for slot,case,name in CASES:
        q=json.loads((W/slot/'manifest.safe.json').read_bytes())
        if type(q.get('actualExit'))is not int or q['actualExit']!=0 or q.get('productionSource')!=SOURCE or q.get('selectedTests')!=1 or q.get('case')!=case or q.get('exactXmlCaseVerified')is not True:
            raise ValueError('four actual independent XML-case/source/hash authorities required')
        old=git('show',q['testSource']+':'+TEST)
        if hashlib.sha256(old).hexdigest()!=q['inputFiles']['MorningDatabaseSessionTest.java']:
            raise ValueError('actual selected whole input hash required')
        if method_block(old.decode(),name)!=method_block(current.decode(),name):
            raise ValueError('exact selected method input unchanged in final group required')
    last=json.loads((W/CASES[-1][0]/'manifest.safe.json').read_bytes())
    if hashlib.sha256(current).hexdigest()!=last['inputFiles']['MorningDatabaseSessionTest.java']:
        raise ValueError('final whole Test must equal latest actual selected compile input')


def server_source(head,digest):
    raw=previous.server_source(head,digest).replace('PG2744','PG2770').replace('3669','3673')
    compile(raw,'<four independent DB methods full3673>','exec');return raw


def main():
    raw=inspect.getsource(transport_base.main).replace('PG2600','PG2770').replace('pg2600','pg2770').replace('3657','3673').replace('540','541')
    raw=raw.replace('3653 retained plus four independently accepted JDBC boundary methods; unchanged Main541suite1643',
        '3669 retained plus four independently qualified actual DB methods2750-2754-2758-2762; unchanged Main/resources541suite1643')
    raw=raw.replace('One required integration for2588/2590/2592/2594; no management-only repetition',
        'One required grouped DB integration for2750/2754/2758/2762; actual isolated SQL and current retained native; no VM replay')
    if '2588/2590/2592/2594' in raw or '3653 retained' in raw:raise ValueError('exact current count basis/trigger required')
    ns={**transport_base.__dict__,'SOURCE':SOURCE,'validate':validate,'server_source':server_source}
    exec(compile(raw,'<necessary DB grouped full transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
