"""One required fresh full integration of three independent Backup admission methods."""
import hashlib
import inspect
import json
import subprocess
from pathlib import Path
import pg2694_expiry_fixed_full_six as previous
from pg1446_current_cold_stage import W
from pg2722_operation_native_qualification import result_changes, ARTIFACT
from pg2474_question_native_qualified_results import BASELINE

SOURCE=previous.SOURCE
FULL='e6ddab302fb00051fa4395d1da668c9fbcc76ac1'
CASES=[
 ('BackupBundlePublisherTest.java','pg2734-backup-published-qualified-v1','PT-BAT-2732-001'),
 ('BackupRetentionBoundaryTest.java','pg2738-backup-retention-qualified-v1','PT-BAK-2736-001'),
 ('BackupArtifactVerifierTest.java','pg2742-backup-pending-qualified-v1','PT-BAK-2740-001'),
]


def validate(snapshot):
    root=Path(__file__).resolve().parents[2]
    git=lambda *args:subprocess.check_output(['git',*args],cwd=root)
    previous.validate(FULL)
    prefix='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/'
    changed=set(git('diff','--name-only',FULL,snapshot,'--',*previous.previous.SCOPE).decode().splitlines())
    if changed!={prefix+n for n,_,_ in CASES}|{ARTIFACT}:
        raise ValueError('exact three independent Test files and one qualified A01 result required')
    result_changes([ARTIFACT],git('show',snapshot+':'+ARTIFACT),git('show',snapshot+':'+BASELINE),
                   json.loads((W/'pg2720-chr-a01-native-v1.safe.json').read_bytes()))
    for name,slot,case in CASES:
        selected=json.loads((W/slot/'manifest.safe.json').read_bytes())
        if type(selected.get('actualExit'))is not int or selected['actualExit']!=0 or selected.get('productionSource')!=SOURCE or selected.get('selectedTests')!=1 or selected.get('case')!=case or selected.get('exactXmlCaseVerified')is not True:
            raise ValueError('all three independent actual XML cases required')
        if hashlib.sha256(git('show',snapshot+':'+prefix+name)).hexdigest()!=selected['inputFiles'][name]:
            raise ValueError('exact accepted selected whole Test input required')


def server_source(head,digest):
    raw=previous.server_source(head,digest).replace('PG2694','PG2744').replace('3666','3669')
    compile(raw,'<three Backup methods full3669>','exec');return raw


def main():
    raw=inspect.getsource(previous.previous.main).replace('PG2650','PG2744').replace('pg2650','pg2744').replace('3666','3669')
    ns={**previous.previous.__dict__,'SOURCE':SOURCE,'validate':validate,'server_source':server_source}
    exec(compile(raw,'<necessary one grouped Backup whole regression>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
