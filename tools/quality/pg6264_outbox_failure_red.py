"""One purposeful six-case ordinary Outbox reproduction on unchanged whole-qualified Main."""
import inspect
import subprocess
import pg6206_keeper_faults_selected as prior
from pg6258_current4034_trace import read_qualified

ROOT=prior.ROOT
OLD='97dd2ba6185143632439f32dfc1d663061f1e55c'
TEST='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxFailureOwnershipTest.java'


def inventory():
    cases={module:set(values)for module,values in prior.engine.CASES.items()}
    cases['api'].add('api.messaging.outbound.OutboxFailureOwnershipTest')
    counts={prior.engine.PACKAGE+name:len(prior.source_test_names(ROOT/('src/schubert-nk-'+module+'/src/test/java')/((prior.engine.PACKAGE+name).replace('.','/')+'.java')))
        for module,names in cases.items()for name in names}
    if(sum(counts.values()),len(counts))!=(18,8):raise ValueError('actual original12 plus independent6, no input-matrix count inflation')
    return cases,counts


def runner():
    raw=inspect.getsource(prior.main);start=raw.index('    cases,counts=inventory()')
    raw='def run_red():\n'+raw[start:]
    raw=raw.replace('runner_source(63,20,target_count=14)','runner_source(18,8,target_count=16)',1)
    raw=raw.replace('pg6206-keeper-faults-selected-v1','pg6264-outbox-failure-red-v1',1)
    before="    scope['TARGETS']=scope.pop('targets')"
    after="    scope['targets']['api'].extend(('api/messaging/outbound/OutboxJmsSender','api/messaging/outbound/OutboxDispatcher'))\n"+before
    if raw.count(before)!=1:raise ValueError('one explicit target extension')
    return raw.replace(before,after,1)


def main():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean committed red source/operator first')
    _,qualified=read_qualified()
    if qualified['productionSource']!=OLD:raise ValueError('actual whole4034 and original artifact qualification before new reproduction')
    if subprocess.check_output(['git','diff','--name-only',OLD,'HEAD','--','src'],cwd=ROOT,text=True).splitlines()!=[TEST]:
        raise ValueError('one new Test only; every Production Main unchanged')
    if subprocess.check_output(['git','diff',OLD,'HEAD','--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('actual gates/Current unchanged')
    scope={**vars(prior),'inventory':inventory}
    exec(compile(runner(),'<ordinary six independent ownership counterexamples>','exec'),scope)
    return scope['run_red']()


if __name__=='__main__':raise SystemExit(main())
