"""Same-path63 component cases after actual keeper PG, seven Main/one Test vs red."""
import inspect
import subprocess
import pg5732_enum48_selected as engine
from pg6052_expiry_combined_selected import runner_source
from pg5966_api_sql_selected import source_test_names
from pg5984_web_form_selected_v2 import node_environment
import pg6182_unstarted_management_selected as targets_profile

ROOT=engine.ROOT
OLD='3566d47633180fbebb8576904e85dc31476398ab'
MAIN={'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/'+p+'.java' for p in (
    'api/bootstrap/ApiManagementServer','api/messaging/config/ApiBrokerContexts',
    'api/messaging/config/ArtemisConnectionFactoryProvider','api/messaging/inbound/ApiMessagingRuntime')}
MAIN|={'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/'+p+'.java' for p in (
    'web/bootstrap/WebNativeRuntime','web/messaging/WebBrokerContexts')}
MAIN.add('src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/api/file/ServiceProcessResources.java')
TEST='src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/ServiceResourceRetentionTest.java'


def inventory():
    cases={m:set(v) for m,v in engine.CASES.items()}
    cases['bootstrap'].add('api.file.ServiceResourceRetentionTest')
    cases['api'].update(('api.messaging.inbound.ApiNativeRetentionTest','api.messaging.config.ApiFactoryNativeRetentionTest',
        'api.file.ApiBrokerContextsCredentialTest','api.bootstrap.ApiManagementServerTest','api.bootstrap.ApiManagementStopTest',
        'api.bootstrap.ApiManagementBindTest','api.storage.ApiApplicationPreparationTest','api.storage.ApiPreparationOwnerTest'))
    cases['web'].update(('web.messaging.WebFactoryNativeRetentionTest','api.file.WebBrokerContextsCredentialTest',
        'web.bootstrap.WebManagementServerTest','web.bootstrap.WebUnstartedManagementTest'))
    counts={engine.PACKAGE+c:len(source_test_names(ROOT/('src/schubert-nk-'+m+'/src/test/java')/((engine.PACKAGE+c).replace('.','/')+'.java')))
        for m,names in cases.items() for c in names}
    if (sum(counts.values()),len(counts))!=(63,20):raise ValueError('exact63 actual JUnit/20; child inputs not additional PT')
    return cases,counts


def main():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean fixed PG/Test/operator first')
    if set(subprocess.check_output(['git','diff','--name-only',OLD,'HEAD','--','src'],cwd=ROOT,text=True).splitlines())!=MAIN|{TEST}:
        raise ValueError('exact seven coupled Main and one added fault Test path')
    if subprocess.check_output(['git','diff',OLD,'HEAD','--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('unchanged existing build/static/Current gates')
    cases,counts=inventory();raw=runner_source(63,20,target_count=14)
    before="os.pathsep+os.environ['PATH'],MAVEN_OPTS"
    if raw.count(before)!=1:raise ValueError('one pinned Node binding')
    raw=raw.replace(before,'os.pathsep+NODE_PATH,MAVEN_OPTS',1)
    scope={**vars(engine),'SLOT':'pg6206-keeper-faults-selected-v1','NODE_PATH':node_environment(),
        'CASES':cases,'COUNTS':counts,'test_names':source_test_names}
    target_source=inspect.getsource(targets_profile.main)
    at=target_source.index('    targets=');end=target_source.index('\n    engine=',at)
    exec(compile(target_source[at:end].removeprefix('    ').replace('\n    ','\n'),'<unchanged14 targets>','exec'),scope)
    scope['TARGETS']=scope.pop('targets')
    exec(compile(raw,'<ordinary63 keeper containment>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
