"""Purposeful source-only Main-unchanged preflight/unknown-rollback red; never accepted as PT PASS."""
import inspect
import subprocess
import pg6206_keeper_faults_selected as prior

ROOT=prior.ROOT
OLD='1ba03ac2d9fedbc0d3dc7204ffa4822d66768461'
TEST='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/inbound/ConfirmedRollbackCallbackTest.java'


def inventory():
    cases={m:set(v)for m,v in prior.engine.CASES.items()}
    cases['api'].add('api.messaging.inbound.ConfirmedRollbackCallbackTest')
    counts={prior.engine.PACKAGE+c:len(prior.source_test_names(ROOT/('src/schubert-nk-'+m+'/src/test/java')/((prior.engine.PACKAGE+c).replace('.','/')+'.java')))
        for m,names in cases.items()for c in names}
    if(sum(counts.values()),len(counts))!=(15,8):raise ValueError('independent original12 plus three new red cases, not PASS arithmetic')
    return cases,counts


def main():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean committed red source first')
    if subprocess.check_output(['git','diff','--name-only',OLD,'HEAD','--','src'],cwd=ROOT,text=True).splitlines()!=[TEST]:
        raise ValueError('one new Test only; all Production remains qualified64 source bytes')
    if subprocess.check_output(['git','diff',OLD,'HEAD','--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('existing build/static/Current unchanged')
    raw=inspect.getsource(prior.main)
    start=raw.index('    cases,counts=inventory()')
    raw='def run_red():\n'+raw[start:]
    raw=raw.replace('runner_source(63,20,target_count=14)','runner_source(15,8,target_count=14)',1)
    raw=raw.replace('pg6206-keeper-faults-selected-v1','pg6236-confirmed-rollback-red-v1',1)
    scope={**vars(prior),'inventory':inventory}
    exec(compile(raw,'<purposeful three new API red cases>','exec'),scope)
    return scope['run_red']()


if __name__=='__main__':raise SystemExit(main())
