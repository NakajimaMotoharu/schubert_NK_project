"""113 coupled ordinary cases including every affected listener/consumer contract and shared resources."""
import inspect
import subprocess
import pg6206_keeper_faults_selected as prior
from pg6230_web_cleanup_selected import inventory as prior_inventory

ROOT=prior.ROOT
OLD='b3f25ddbf6fe2e55e7143d8e198cf646499fd186'
NAMES=('InboundTransactions','QuestionWorkConsumers','QuestionWorkListener','SyncRequestConsumers',
    'SyncRequestListener','TransactedEventListener','WebLogConsumers','WebLogListener')
MAIN={'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/'+n+'.java'for n in NAMES}
TEST='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/inbound/ConfirmedRollbackCallbackTest.java'


def inventory():
    cases,_=prior_inventory()
    cases['bootstrap'].add('api.file.ServiceProcessResourcesTest')
    cases['api'].update('api.messaging.inbound.'+n for n in ('SyncRequestConsumersTest','QuestionWorkConsumersTest',
        'WebLogConsumersTest','SyncRequestListenerTest','InternalEventListenerTest','InboundTransactionsPrimaryContractTest','ConfirmedRollbackCallbackTest'))
    counts={prior.engine.PACKAGE+c:len(prior.source_test_names(ROOT/('src/schubert-nk-'+m+'/src/test/java')/((prior.engine.PACKAGE+c).replace('.','/')+'.java')))
        for m,names in cases.items()for c in names}
    if(sum(counts.values()),len(counts))!=(113,28):raise ValueError('actual113 source declarations/28; matrix inputs not extra PT')
    return cases,counts


def main():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean fixed source/operator first')
    changed=set(subprocess.check_output(['git','diff','--name-only',OLD,'HEAD','--','src'],cwd=ROOT,text=True).splitlines())
    if changed!=MAIN|{TEST}:raise ValueError('eight coupled Main and one expanded independent Test')
    if subprocess.check_output(['git','diff',OLD,'HEAD','--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('unchanged actual gates/Current')
    raw=inspect.getsource(prior.main);start=raw.index('    cases,counts=inventory()')
    raw='def run_green():\n'+raw[start:]
    raw=raw.replace('runner_source(63,20,target_count=14)','runner_source(113,28,target_count=19)',1)
    raw=raw.replace('pg6206-keeper-faults-selected-v1','pg6238-confirmed-rollback-selected-v1',1)
    # Retain the existing14 target inventory and add only the five newly changed listener/helper owners.
    before="    scope['TARGETS']=scope.pop('targets')"
    after="    scope['targets']['api'].extend('api/messaging/inbound/'+name for name in ('SyncRequestListener','TransactedEventListener','QuestionWorkListener','WebLogListener','InboundTransactions'))\n"+before
    if raw.count(before)!=1:raise ValueError('one actual target inventory binding')
    raw=raw.replace(before,after,1)
    scope={**vars(prior),'inventory':inventory}
    exec(compile(raw,'<ordinary113 callback group>','exec'),scope)
    return scope['run_green']()


if __name__=='__main__':raise SystemExit(main())
