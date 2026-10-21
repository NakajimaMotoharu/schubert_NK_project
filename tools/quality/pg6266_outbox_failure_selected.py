"""One grouped51 ordinary Outbox/log component run after two-Main PG; keep independent red Test fixed."""
import json
import subprocess
import pg6264_outbox_failure_red as red
from pg5940_private_lock_compile import W

ROOT=red.ROOT
OLD='760eed0db836e4b7194059f73ea93f5cc10f4cb8'
MAIN={'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/'+name+'.java'
    for name in ('OutboxJmsSender','OutboxDispatcher')}


def inventory():
    cases,_=red.inventory()
    cases['api'].update(('api.messaging.outbound.OutboxDispatcherTest','api.messaging.outbound.OwnedOutboxDispatcherTest'))
    cases['web'].add('web.logging.WebLogDispatcherTest')
    counts={red.prior.engine.PACKAGE+name:len(red.prior.source_test_names(ROOT/('src/schubert-nk-'+module+'/src/test/java')/((red.prior.engine.PACKAGE+name).replace('.','/')+'.java')))
        for module,names in cases.items()for name in names}
    if(sum(counts.values()),len(counts))!=(51,11):raise ValueError('actual51 declarations/11, no matrix or historical PASS arithmetic')
    return cases,counts


def main():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean fixed Main/Test/operator first')
    failed=json.loads((W/'pg6264-outbox-failure-red-v1/manifest.safe.json').read_bytes())
    expected={'fail320001NonfatalJmsPrimaryCannotHideCleanupError','fail320002UnreturnedJdbcSetupErrorClosesExactlyOnce',
        'fail320003JdbcSetupCompoundFailuresPreserveIdentity','fail320004RollbackCompoundFailuresNeverSelfSuppress'}
    if not(failed['source']==OLD and failed['actualExit']==failed['mavenActualExit']==1 and failed['sourceFixed']
        and(failed['tests'],failed['suites'])==(12,5)and {row[1]for row in failed['failedOrSkipped']}==expected):
        raise ValueError('original exact four reproduced failures required; red is never PASS')
    changed=set(subprocess.check_output(['git','diff','--name-only',OLD,'HEAD','--','src'],cwd=ROOT,text=True).splitlines())
    if changed!=MAIN:raise ValueError('exact two Main only; six independent oracles and all other Test bodies fixed')
    if subprocess.check_output(['git','diff',OLD,'HEAD','--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('actual gates/Current unchanged')
    raw=red.runner()
    for before,after in (('runner_source(18,8,target_count=16)','runner_source(51,11,target_count=16)'),
        ('pg6264-outbox-failure-red-v1','pg6266-outbox-failure-selected-v1'),('def run_red():','def run_green():')):
        if raw.count(before)!=1:raise ValueError('one explicit new green binding '+before)
        raw=raw.replace(before,after,1)
    scope={**vars(red.prior),'inventory':inventory}
    exec(compile(raw,'<ordinary51 Outbox/log>','exec'),scope)
    return scope['run_green']()


if __name__=='__main__':raise SystemExit(main())
