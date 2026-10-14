"""Required fresh whole integration after BUG1245 Test-only deterministic repair."""
import inspect
import json
import subprocess
from pathlib import Path
import pg2650_operation_post_full_six as previous
from pg1446_current_cold_stage import W

SOURCE=previous.SOURCE
BASELINE='875182d902002e3f578bf64889cff83752cc31fd'
TEST_PATH='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/mq/ArtemisExpiryPurgeClientTest.java'


def validate(snapshot):
    root=Path(__file__).resolve().parents[2]
    def git(*a):return subprocess.check_output(['git',*a],cwd=root)
    previous.validate(BASELINE)
    if set(git('diff','--name-only',BASELINE,snapshot,'--',*previous.SCOPE).decode().splitlines())!={TEST_PATH}:raise ValueError('one fixed fixture and unchanged full resource/Main input required')
    selected=json.loads((W/'pg2692-expiry-selected-v2/manifest.safe.json').read_bytes())
    if type(selected.get('actualExit'))is not int or selected['actualExit']!=0:raise ValueError('actual selected independent fixed fixture required')
    result=selected['result']
    if result['tests']!=11 or result['suites']!=3 or result['staticIssues']!=0 or result['inputUnchanged']is not True:raise ValueError('whole selected11/RBAC/unknown contract required')
    for k in ['LINE','METHOD','CLASS','BRANCH']:
        if result['expiryClassCounters'][k]['missed']!=0:raise ValueError('unchanged Expiry Main selectedfour100 required')
    if git('diff','--name-only',result['sourceSnapshot'],snapshot,'--',*previous.SCOPE):raise ValueError('whole fixed selected source equality required')


def server_source(head,digest):return previous.server_source(head,digest).replace('PG2650','PG2694')


def main():
    raw=inspect.getsource(previous.main).replace('PG2650','PG2694').replace('pg2650','pg2694')
    ns={**previous.__dict__,'SOURCE':SOURCE,'validate':validate,'server_source':server_source}
    exec(compile(raw,'<necessary fresh samecandidate fixed fixture integration>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
