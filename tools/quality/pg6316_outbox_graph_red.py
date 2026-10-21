"""One ordinary38 independent reproduction; all Main remains original4043 qualified."""
import subprocess
import pg6264_outbox_failure_red as previous
from pg6306_current4043_trace import read_qualified

ROOT=previous.ROOT
OLD='5eb040421ae9ea06ecc70c6eb2e152871c2d0d42'
TESTS={'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/outbound/'+n+'.java'
    for n in ('OutboxDispatcherTest','OwnedOutboxDispatcherTest')}


def inventory():
    cases={module:set(values)for module,values in previous.prior.engine.CASES.items()}
    cases['api'].update(('api.messaging.outbound.OutboxDispatcherTest','api.messaging.outbound.OwnedOutboxDispatcherTest'))
    counts={previous.prior.engine.PACKAGE+name:len(previous.prior.source_test_names(ROOT/('src/schubert-nk-'+module+'/src/test/java')/((previous.prior.engine.PACKAGE+name).replace('.','/')+'.java')))
        for module,names in cases.items()for name in names}
    if(sum(counts.values()),len(counts))!=(38,9):raise ValueError('actual38 declarations/9 suites; no graph input inflation')
    return cases,counts


def runner():
    raw=previous.runner()
    for before,after in (
        ('runner_source(18,8,target_count=16)','runner_source(38,9,target_count=16)'),
        ('pg6264-outbox-failure-red-v1','pg6316-outbox-graph-red-v1'),
        ("scope['targets']['api'].extend(('api/messaging/outbound/OutboxJmsSender','api/messaging/outbound/OutboxDispatcher'))",
         "scope['targets']['api'].extend(('api/messaging/outbound/OwnedOutboxDispatcher','api/messaging/outbound/OutboxDispatcher'))")):
        if raw.count(before)!=1:raise ValueError('one explicit current graph red binding '+before)
        raw=raw.replace(before,after,1)
    return raw


def main():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean committed Test/operator first')
    _,q=read_qualified()
    if q['productionSource']!=OLD:raise ValueError('genuine original4043 qualified before new graph reproduction')
    if set(subprocess.check_output(['git','diff','--name-only',OLD,'HEAD','--','src'],cwd=ROOT,text=True).splitlines())!=TESTS:
        raise ValueError('only two Test edits; all Main unchanged')
    if subprocess.check_output(['git','diff',OLD,'HEAD','--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('gates/Current baseline fixed')
    scope={**vars(previous.prior),'inventory':inventory}
    exec(compile(runner(),'<ordinary38 failure graph reproduction>','exec'),scope)
    return scope['run_red']()


if __name__=='__main__':raise SystemExit(main())
