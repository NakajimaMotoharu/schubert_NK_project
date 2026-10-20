"""Grouped49 ordinary ownership/component cases, partial counters reported honestly."""
import pg6164_native_retention_selected as prior

CODE='158bd39f35a5a68bcf3b656ede0355eaba7635c5'


def inventory():
    cases,_=prior.inventory()
    cases['api'].update(('api.bootstrap.ApiManagementServerTest','api.bootstrap.ApiManagementStopTest',
        'api.bootstrap.ApiManagementBindTest','api.storage.ApiApplicationPreparationTest','api.storage.ApiPreparationOwnerTest'))
    counts={prior.engine.PACKAGE+c:len(prior.source_test_names(prior.ROOT/('src/schubert-nk-'+m+'/src/test/java')/((prior.engine.PACKAGE+c).replace('.','/')+'.java')))
        for m,names in cases.items() for c in names}
    if (sum(counts.values()),len(counts))!=(49,18):raise ValueError('explicit current49/18 named JUnit; loops not extra cases')
    return cases,counts


def runner_source():
    raw=prior.base_runner(49,18,target_count=13)
    before="os.pathsep+os.environ['PATH'],MAVEN_OPTS"
    if raw.count(before)!=1:raise ValueError('one pinned Node binding')
    raw=raw.replace(before,'os.pathsep+NODE_PATH,MAVEN_OPTS',1)
    compile(raw,'<own finite49>','exec')
    return raw


def main():
    if prior.subprocess.check_output(['git','status','--porcelain'],cwd=prior.ROOT):raise ValueError('clean fixed source')
    if prior.subprocess.check_output(['git','diff',CODE,'HEAD','--','src','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=prior.ROOT):
        raise ValueError('strict-static Main/Test/gates fixed; metadata/operator only')
    import json
    from pg5940_private_lock_compile import BASE
    static=json.loads((BASE/'PG6174-native-assembly-static-v1/manifest.json').read_bytes())
    if not (static['source']==CODE and static['actualExit']==static['mavenActualExit']==0
            and static['sourceFixed'] and static['physicalMain']==1667
            and static['testsExecuted']==static['surefireXmlCount']==static['jacocoExecCount']==0
            and set(static['staticIssues'])==set(prior.engine.MODULES)
            and not any(static['staticIssues'].values())):
        raise ValueError('actual six strict static-only terminal before ordinary49')
    cases,counts=inventory()
    targets={'bootstrap':['api/file/ServiceProcessResources'],
        'api':['api/messaging/inbound/'+n for n in ('SyncRequestConsumers','WebLogConsumers','QuestionWorkConsumers','ApiMessagingRuntime')]
            +['api/messaging/config/'+n for n in ('ApiBrokerContexts','ArtemisConnectionFactoryProvider','ArtemisConnectionFactoryProvider$ConsumerProfile')]
            +['api/bootstrap/ApiManagementServer','api/bootstrap/ApiProcessMain','api/storage/ApiApplicationPreparation'],
        'web':['web/messaging/WebBrokerContexts','web/bootstrap/WebNativeRuntime']}
    # Fixed Main/Test may have later metadata-only saves; original begin records the actual HEAD.
    scope={**vars(prior.engine),'SLOT':'pg6176-native-assembly-selected-v1','NODE_PATH':prior.node_environment(),
        'CASES':cases,'COUNTS':counts,'TARGETS':targets,'test_names':prior.source_test_names}
    exec(compile(runner_source(),'<own local49>', 'exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
