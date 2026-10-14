"""One fresh integration of four new independent DB tests; current Main unchanged."""
import ast
import hashlib
import inspect
import json
import subprocess
from pathlib import Path
import pg2798_jdbc_null_fixed_full_six as prior

SOURCE=prior.SOURCE
FAILURE='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/BackupFailureSnapshotTest.java'
ARTIFACT='program/characterization/reports/nk/PG2900-native-a01-v1/artifacts/CHR-A01.json'


def validate(snapshot):
    prior.validate(SOURCE)
    root=Path(__file__).resolve().parents[2]
    git=lambda *args:subprocess.check_output(['git',*args],cwd=root)
    changes=set(git('diff','--name-only',SOURCE,snapshot,'--',*prior.SCOPE).decode().splitlines())
    if changes!={prior.TEST,FAILURE,ARTIFACT}:raise ValueError('two Test-only sources and explicit A01 result required')
    for slot,path,count in [('pg2912-jdbc-compound-close-selected-v2',prior.TEST,61),('pg2916-failed-pair-boundary-selected-v1',FAILURE,6)]:
        out=prior.W/slot;result=json.loads((out/'manifest.safe.json').read_bytes())
        if any(result.get(k)!=v for k,v in {'actualExit':0,'tests':count,'FESAbortedNotRun':0,'coverageClaim':False,'nativeImported':False,'vmActions':0}.items()):raise ValueError('actual independent selected whole Test qualification required')
        payload=(out/'selected.private.py').read_bytes()
        if hashlib.sha256(payload).hexdigest()!=result['payloadSha256']:raise ValueError('actual payload hash required')
        value=ast.literal_eval(payload.decode().splitlines()[0].removeprefix('INPUT='))
        current=git('show',snapshot+':'+path)
        if hashlib.sha256(current).hexdigest()!=value['files'][Path(path).name]or current.decode().count('@Test\n')!=count:
            raise ValueError('whole Test bytes equal actual selected compile input required')
    # Artifact is data, not code/oracle. Reuse the already qualified real A01 check.
    import pg2908_network_current_native_qualification as native
    ns={**native.result_guard.__dict__,'ARTIFACT':ARTIFACT,'SOURCE':SOURCE}
    exec(compile(inspect.getsource(native.result_guard.result_changes),'<independent A01 result only>','exec'),ns)
    ns['result_changes']([ARTIFACT],git('show',snapshot+':'+ARTIFACT),Path(native.result_guard.BASELINE).read_bytes(),json.loads((prior.W/'pg2900-chr-a01-native-v1.safe.json').read_bytes()))


def server_source(head,digest):
    raw=prior.server_source(head,digest).replace('PG2798','PG2918').replace('3680','3684')
    compile(raw,'<fresh whole3684 unchanged Main1643>','exec');return raw


def main():
    raw=inspect.getsource(prior.main).replace('PG2798','PG2918').replace('pg2798','pg2918').replace('3680','3684')
    raw=raw.replace('3673 retained plus five independently real-DB Session methods and two owner-admission methods; changed JDBC Main;542suite1643',
        '3680 retained plus one compound Session close and three failed-pair identity/null methods; Main unchanged;542suite1643')
    raw=raw.replace('BUG1251/YKT1017 changed JDBC null-resource Main and seven grouped tests require one fresh all-source/static regression; Source042 native not portable',
        'Four independently real-DB methods require one fresh Test-input integration; same a9 Main must independently match actual PG2802 and its native9; no Root/VM replay')
    ns={**prior.__dict__,'validate':validate,'server_source':server_source}
    exec(compile(raw,'<four grouped DB contracts fresh full>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
