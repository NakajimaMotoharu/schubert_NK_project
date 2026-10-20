"""New finite native-policy component fixtures plus six guards; not native Root execution."""
import subprocess
import pg5732_enum48_selected as engine
from pg6052_expiry_combined_selected import runner_source as base_runner
from pg5966_api_sql_selected import source_test_names
from pg5984_web_form_selected_v2 import node_environment

ROOT=engine.ROOT
SLOT='pg6164-native-retention-selected-v1'
CODE='ecc7b4cd969aebd4bbb91a8635f1a2f66d4a5c3b'


def inventory():
    cases={m:set(v) for m,v in engine.CASES.items()}
    cases['bootstrap'].add('api.file.ServiceResourceRetentionTest')
    cases['api'].update(('api.messaging.inbound.ApiNativeRetentionTest','api.messaging.config.ApiFactoryNativeRetentionTest','api.file.ApiBrokerContextsCredentialTest'))
    cases['web'].update(('web.messaging.WebFactoryNativeRetentionTest','api.file.WebBrokerContextsCredentialTest'))
    counts={engine.PACKAGE+c:len(source_test_names(ROOT/('src/schubert-nk-'+m+'/src/test/java')/((engine.PACKAGE+c).replace('.','/')+'.java'))) for m,names in cases.items() for c in names}
    if(sum(counts.values()),len(counts))!=(25,13):raise ValueError('fixed real25/13; child/input loops not JUnit count inflation')
    return cases,counts


def runner_source():
    raw=base_runner(25,13,target_count=9)
    before="os.pathsep+os.environ['PATH'],MAVEN_OPTS"
    if raw.count(before)!=1:raise ValueError('one pinned Node binding')
    raw=raw.replace(before,'os.pathsep+NODE_PATH,MAVEN_OPTS',1)
    compile(raw,'<finite owned retention component PT>','exec')
    return raw


def main():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean fixed source/operator first')
    if subprocess.check_output(['git','diff',CODE,'HEAD','--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('evidence/operator-only save after exact strict-static source, no Main/Test changes')
    cases,counts=inventory()
    targets={'bootstrap':['api/file/ServiceProcessResources'],
        'api':['api/messaging/inbound/'+n for n in ('SyncRequestConsumers','WebLogConsumers','QuestionWorkConsumers','ApiMessagingRuntime')]
            +['api/messaging/config/'+n for n in ('ApiBrokerContexts','ArtemisConnectionFactoryProvider','ArtemisConnectionFactoryProvider$ConsumerProfile')],
        'web':['web/messaging/WebBrokerContexts']}
    scope={**vars(engine),'SLOT':SLOT,'NODE_PATH':node_environment(),
        'CASES':cases,'COUNTS':counts,'TARGETS':targets,'test_names':source_test_names}
    exec(compile(runner_source(),'<ordinary finite own policy fixtures>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
