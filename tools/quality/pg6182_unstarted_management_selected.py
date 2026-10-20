"""New59 ordinary component cases after SSC317; no deployed or refused operations."""
import json
import subprocess
import pg6176_native_assembly_selected as prior
from pg5940_private_lock_compile import ROOT, BASE

CODE='21a905003'


def inventory():
    cases,_=prior.inventory()
    cases['web'].update(('web.bootstrap.WebManagementServerTest','web.bootstrap.WebUnstartedManagementTest'))
    engine=prior.prior.engine
    counts={engine.PACKAGE+c:len(prior.prior.source_test_names(ROOT/('src/schubert-nk-'+m+'/src/test/java')/((engine.PACKAGE+c).replace('.','/')+'.java')))
        for m,names in cases.items() for c in names}
    if (sum(counts.values()),len(counts))!=(59,20):raise ValueError('actual named59/20, no child/input loop inflation')
    return cases,counts


def runner_source():
    raw=prior.prior.base_runner(59,20,target_count=14)
    before="os.pathsep+os.environ['PATH'],MAVEN_OPTS"
    if raw.count(before)!=1:raise ValueError('one pinned Node binding')
    raw=raw.replace(before,'os.pathsep+NODE_PATH,MAVEN_OPTS',1)
    compile(raw,'<own59 source>','exec')
    return raw


def main():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean fixed input first')
    if subprocess.check_output(['git','diff',CODE,'HEAD','--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('strict static Main/Test/gates fixed')
    static=json.loads((BASE/'PG6180-unstarted-management-static-v1/manifest.json').read_bytes())
    anchor=subprocess.check_output(['git','rev-parse',CODE],cwd=ROOT,text=True).strip()
    if not (static['source']==anchor and static['actualExit']==static['mavenActualExit']==0
            and static['sourceFixed'] and static['physicalMain']==1667
            and static['testsExecuted']==static['surefireXmlCount']==static['jacocoExecCount']==0
            and set(static['staticIssues'])==set(prior.prior.engine.MODULES)
            and not any(static['staticIssues'].values())):
        raise ValueError('genuine six static-only0 first')
    cases,counts=inventory()
    targets={'bootstrap':['api/file/ServiceProcessResources'],
        'api':['api/messaging/inbound/'+n for n in ('SyncRequestConsumers','WebLogConsumers','QuestionWorkConsumers','ApiMessagingRuntime')]
            +['api/messaging/config/'+n for n in ('ApiBrokerContexts','ArtemisConnectionFactoryProvider','ArtemisConnectionFactoryProvider$ConsumerProfile')]
            +['api/bootstrap/ApiManagementServer','api/bootstrap/ApiProcessMain','api/storage/ApiApplicationPreparation'],
        'web':['web/messaging/WebBrokerContexts','web/bootstrap/WebNativeRuntime','web/bootstrap/WebManagementServer']}
    engine=prior.prior.engine
    scope={**vars(engine),'SLOT':'pg6182-unstarted-management-selected-v1','NODE_PATH':prior.prior.node_environment(),
        'CASES':cases,'COUNTS':counts,'TARGETS':targets,'test_names':prior.prior.source_test_names}
    exec(compile(runner_source(),'<own new59>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
