"""One ordinary28 reproduction: two Test-only edits on original4040 qualified Main."""
import subprocess
import pg6264_outbox_failure_red as previous
from pg6276_current4040_trace import read_qualified

ROOT=previous.ROOT
OLD='b4230118efcc429ee29d6e6f5761c55175f1e85e'
TESTS={'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/'+p+'.java'
    for p in ('messaging/ArtemisRequestSenderTest','logging/WebLogMessageSenderTest')}


def inventory():
    cases={module:set(values)for module,values in previous.prior.engine.CASES.items()}
    cases['web'].update(('web.messaging.ArtemisRequestSenderTest','web.logging.WebLogMessageSenderTest'))
    counts={previous.prior.engine.PACKAGE+name:len(previous.prior.source_test_names(ROOT/('src/schubert-nk-'+module+'/src/test/java')/((previous.prior.engine.PACKAGE+name).replace('.','/')+'.java')))
        for module,names in cases.items()for name in names}
    if(sum(counts.values()),len(counts))!=(28,9):raise ValueError('actual28 declared methods/9 suites, no matrix inflation')
    return cases,counts


def runner():
    raw=previous.runner()
    for before,after in (
        ('runner_source(18,8,target_count=16)','runner_source(28,9,target_count=16)'),
        ('pg6264-outbox-failure-red-v1','pg6294-web-send-red-v1'),
        ("scope['targets']['api'].extend(('api/messaging/outbound/OutboxJmsSender','api/messaging/outbound/OutboxDispatcher'))",
         "scope['targets']['web'].extend(('web/messaging/ArtemisRequestSender','web/logging/WebLogMessageSender'))")):
        if raw.count(before)!=1:raise ValueError('one explicit new red binding '+before)
        raw=raw.replace(before,after,1)
    return raw


def main():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean committed Test/operator first')
    _,q=read_qualified()
    if q['productionSource']!=OLD:raise ValueError('actual whole4040 and original artifacts before new red')
    if set(subprocess.check_output(['git','diff','--name-only',OLD,'HEAD','--','src'],cwd=ROOT,text=True).splitlines())!=TESTS:
        raise ValueError('only two Test changes; all Main unchanged')
    if subprocess.check_output(['git','diff',OLD,'HEAD','--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('actual gates/Current fixed')
    scope={**vars(previous.prior),'inventory':inventory}
    exec(compile(runner(),'<new only28 ordinary Web send reproduction>','exec'),scope)
    return scope['run_red']()


if __name__=='__main__':raise SystemExit(main())
