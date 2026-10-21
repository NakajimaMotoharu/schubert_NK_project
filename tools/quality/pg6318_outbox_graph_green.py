"""One grouped86 green on two corrected API Main; independent red oracles remain fixed."""
import json
import subprocess
import pg6316_outbox_graph_red as red
from pg5940_private_lock_compile import W

ROOT=red.ROOT
OLD='3bb2339f702c91b51476e17e22723da193638174'
MAIN={'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/'+n+'.java'
    for n in ('OutboxDispatcher','OwnedOutboxDispatcher')}


def inventory():
    cases,_=red.inventory()
    cases['api'].add('api.messaging.outbound.OutboxFailureOwnershipTest')
    cases['web'].update(('web.messaging.ArtemisRequestSenderTest','web.logging.WebLogMessageSenderTest',
        'web.logging.WebLogDispatcherTest','web.logging.WebLogReplayWorkerTest','web.messaging.JmsRequestReplyClientTest'))
    counts={red.previous.prior.engine.PACKAGE+name:len(red.previous.prior.source_test_names(ROOT/('src/schubert-nk-'+module+'/src/test/java')/((red.previous.prior.engine.PACKAGE+name).replace('.','/')+'.java')))
        for module,names in cases.items()for name in names}
    if(sum(counts.values()),len(counts))!=(86,15):raise ValueError('actual86 declarations/15 suites, not arithmetic prior PASS')
    return cases,counts


def main():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean fixed Main/Test/operator first')
    original=subprocess.check_output(['git','rev-parse',OLD],cwd=ROOT,text=True).strip()
    failed=json.loads((W/'pg6316-outbox-graph-red-v1/manifest.safe.json').read_bytes())
    expected={('dev.codex.schubert.nk.api.messaging.outbound.OwnedOutboxDispatcherTest','graph322001NestedFatalStopsOwnedWorkerBeforeAnotherDispatch'),
        ('dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatcherTest','graph322002NestedFatalNeverMarksOrdinaryFailureAndNonfatalCycleStillRetries')}
    if not(failed['source']==original and failed['actualExit']==failed['mavenActualExit']==1 and failed['sourceFixed']
        and(failed['tests'],failed['suites'])==(32,6)and {tuple(r)for r in failed['failedOrSkipped']}==expected):
        raise ValueError('original exact two reproduced graph failures, never red PASS')
    if set(subprocess.check_output(['git','diff','--name-only',original,'HEAD','--','src'],cwd=ROOT,text=True).splitlines())!=MAIN:
        raise ValueError('two Main only; all independent red Test/oracles fixed')
    if subprocess.check_output(['git','diff',original,'HEAD','--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('gates/Current fixed')
    raw=red.runner()
    for before,after in (('runner_source(38,9,target_count=16)','runner_source(86,15,target_count=16)'),
        ('pg6316-outbox-graph-red-v1','pg6318-outbox-graph-selected-v1'),('def run_red():','def run_green():')):
        if raw.count(before)!=1:raise ValueError('one explicit new green binding '+before)
        raw=raw.replace(before,after,1)
    scope={**vars(red.previous.prior),'inventory':inventory}
    exec(compile(raw,'<ordinary86 graph classification and existing senders>','exec'),scope)
    return scope['run_green']()


if __name__=='__main__':raise SystemExit(main())
