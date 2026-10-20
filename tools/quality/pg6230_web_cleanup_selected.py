"""One coupled Web compound cleanup/Core readability group, only after genuine prior whole."""
import inspect
import json
import pg6206_keeper_faults_selected as prior
from pg5940_private_lock_compile import BASE,W,sha

ROOT=prior.ROOT
OLD='55109c74737208f906b69c04cd0931b466d2fadd'
MAIN={'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebManagementServer.java',
    'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/api/file/ServiceProcessResources.java'}
TEST='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebManagementServerTest.java'


def inventory():
    raw=inspect.getsource(prior.inventory)
    if raw.count('(63,20)')!=1:raise ValueError('one declared prior inventory dimension')
    raw=raw.replace('(63,20)','(64,20)',1).replace('exact63 actual','exact64 actual')
    scope=vars(prior).copy();exec(compile(raw,'<current64 lexical declarations>','exec'),scope)
    return scope['inventory']()


def baseline():
    qpath=BASE/'PG6212-current4027-cases/qualification.json'
    receipt=W/'pg6214-original4027-artifacts-v1/manifest.safe.json'
    q,r=[json.loads(p.read_bytes()) for p in (qpath,receipt)]
    if not(q['actualExit']==q['FESFlakyNotRun']==q['staticSixModules']==r['actualExit']==0
        and q['productionSource']==r['source']==OLD and (q['tests'],q['suites'],q['mainClasses'])==(4027,605,1667)
        and q['currentOriginalXmlQualified'] and q['returnedOriginalTerminalExact']
        and sha(qpath)==r['publicQualificationSha256'] and r['wholeReplayed'] is False):
        raise ValueError('genuine original prior whole and independent artifact identity first')


def main():
    baseline()
    raw=inspect.getsource(prior.main)
    if raw.count('runner_source(63,20,target_count=14)')!=1 or raw.count('pg6206-keeper-faults-selected-v1')!=1:
        raise ValueError('one reviewed finite component runner/namespace')
    raw=raw.replace('runner_source(63,20,target_count=14)','runner_source(64,20,target_count=14)',1)
    raw=raw.replace('pg6206-keeper-faults-selected-v1','pg6230-web-cleanup-selected-v1',1)
    raw=raw.replace('exact seven coupled Main and one added fault Test path','exact two coupled Main and one compound Test path')
    scope={**vars(prior),'ROOT':ROOT,'OLD':OLD,'MAIN':MAIN,'TEST':TEST,'inventory':inventory}
    exec(compile(raw,'<ordinary64 coupled cleanup group>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
