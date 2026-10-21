"""One grouped84 green after the two-Web-Main PG; preserve all original red oracles."""
import json
import subprocess
import pg6294_web_send_red as red
from pg5940_private_lock_compile import W

ROOT=red.ROOT
OLD='1e98c9daffb1a6db6c9fae290841e89f0ff10cbe'
MAIN={'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/'+p+'.java'
    for p in ('messaging/ArtemisRequestSender','logging/WebLogMessageSender')}


def inventory():
    cases,_=red.inventory()
    cases['api'].update(('api.messaging.outbound.OutboxFailureOwnershipTest','api.messaging.outbound.OutboxDispatcherTest',
        'api.messaging.outbound.OwnedOutboxDispatcherTest'))
    cases['web'].update(('web.logging.WebLogDispatcherTest','web.logging.WebLogReplayWorkerTest','web.messaging.JmsRequestReplyClientTest'))
    counts={red.previous.prior.engine.PACKAGE+name:len(red.previous.prior.source_test_names(ROOT/('src/schubert-nk-'+module+'/src/test/java')/((red.previous.prior.engine.PACKAGE+name).replace('.','/')+'.java')))
        for module,names in cases.items()for name in names}
    if(sum(counts.values()),len(counts))!=(84,15):raise ValueError('actual84 method declarations/15; matrix and previous PASS not arithmetic')
    return cases,counts


def main():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean fixed Main/Test/operator first')
    failed=json.loads((W/'pg6294-web-send-red-v1/manifest.safe.json').read_bytes())
    expected={('dev.codex.schubert.nk.web.messaging.ArtemisRequestSenderTest','cleanup321001FatalCleanupAndOriginalFailureIdentity'),
        ('dev.codex.schubert.nk.web.logging.WebLogMessageSenderTest','cleanup321002FatalCleanupPriorityAndPlaintextWipe'),
        ('dev.codex.schubert.nk.web.logging.WebLogMessageSenderTest','cleanup321003SameThrowableNeverMasksOriginalFailure')}
    if not(failed['source']==OLD and failed['actualExit']==failed['mavenActualExit']==1 and failed['sourceFixed']
        and(failed['tests'],failed['suites'])==(26,7)and {tuple(r)for r in failed['failedOrSkipped']}==expected):
        raise ValueError('original exact three reproduced failures; red is never PASS')
    if set(subprocess.check_output(['git','diff','--name-only',OLD,'HEAD','--','src'],cwd=ROOT,text=True).splitlines())!=MAIN:
        raise ValueError('exact two Main only; all independent Test/oracles unchanged')
    if subprocess.check_output(['git','diff',OLD,'HEAD','--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('gates/Current fixed')
    raw=red.runner()
    for before,after in (('runner_source(28,9,target_count=16)','runner_source(84,15,target_count=16)'),
        ('pg6294-web-send-red-v1','pg6296-web-send-selected-v1'),('def run_red():','def run_green():')):
        if raw.count(before)!=1:raise ValueError('one explicit green binding '+before)
        raw=raw.replace(before,after,1)
    scope={**vars(red.previous.prior),'inventory':inventory}
    exec(compile(raw,'<ordinary84 Web send and existing callers>','exec'),scope)
    return scope['run_green']()


if __name__=='__main__':raise SystemExit(main())
