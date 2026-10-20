"""SSC316 prepared failure ports, strict six-module compile/SpotBugs only, no JUnit."""
import inspect
import xml.etree.ElementTree as ET
import pg6153_api_test_compile_preflight as profile
from pg5984_web_form_selected_v2 import node_environment

OLD='292c06cc226522028aeb9978e545c1f12d7c84c9'
MAIN={'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/'+p+'.java' for p in (
    'inbound/SyncRequestConsumers','inbound/WebLogConsumers','inbound/QuestionWorkConsumers',
    'inbound/ApiMessagingRuntime','config/ApiBrokerContexts','config/ArtemisConnectionFactoryProvider')}
MAIN|={'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/api/file/ServiceProcessResources.java',
    'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/WebBrokerContexts.java'}
TESTS={'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/'+p+'.java' for p in (
    'api/messaging/inbound/ApiNativeRetentionTest','api/messaging/config/ApiFactoryNativeRetentionTest',
    'api/messaging/config/ApiFactoryOwnershipTest','api/file/ApiBrokerContextsCredentialTest')}
TESTS|={'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/'+p+'.java' for p in ('OwnedRetentionProcess','ServiceResourceRetentionTest')}
TESTS|={'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/'+p+'.java' for p in (
    'web/messaging/WebFactoryNativeRetentionTest','web/messaging/WebBrokerFactoryOwnershipTest','api/file/WebBrokerContextsCredentialTest')}
MODULES=('protocol','storage','bootstrap','api','web','batch')


def runner_source():
    raw=inspect.getsource(profile.main)
    replacements={
        ' != {TEST}:':' != EXPECTED:',
        "'pg6153-api-test-compile-preflight-v1'":"'pg6162-native-ports-static-v1'",
        "'PG6153-api-test-compile-preflight-v1'":"'PG6162-native-ports-static-v1'",
        "W/'pg6150-api-factory-close-selected-v1/source'":"W/'pg6160-api-monitor-static-v1/source'",
        'if len(main_paths) != 851 or any(sha(p) != sha(previous/p.relative_to(snapshot)) for p in main_paths):':
            'if len(main_paths) != 851 or {p.relative_to(snapshot).as_posix() for p in main_paths if sha(p) != sha(previous/p.relative_to(snapshot))} != MAIN:',
        "os.pathsep+os.environ['PATH'], MAVEN_OPTS":'os.pathsep+NODE_PATH, MAVEN_OPTS',
        "'-pl', 'src/schubert-nk-api', '-am', 'test-compile']":
            "'-pl', ','.join('src/schubert-nk-'+m for m in MODULES), 'test-compile', 'com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check']",
        'code = actual if actual else 0 if fixed and not reports and not jacoco else 1':
            "static_issues={m:len(ET.parse(snapshot/('src/schubert-nk-'+m+'/target/spotbugsXml.xml')).getroot().findall('BugInstance')) if (snapshot/('src/schubert-nk-'+m+'/target/spotbugsXml.xml')).exists() else None for m in MODULES}\n    physical=sum(len(list((snapshot/('src/schubert-nk-'+m+'/target/classes')).rglob('*.class'))) for m in MODULES)\n    code=actual if actual else 0 if fixed and not reports and not jacoco and all(v==0 for v in static_issues.values()) and physical==1667 else 1",
        "compiledModules=['protocol','storage','bootstrap','api'] if actual==0 else []":'compiledModules=list(MODULES) if actual==0 else []',
        'all851MainUnchanged=True, testsExecuted=0':'all851MainUnchanged=False, changedMainCount=8, physicalMain=physical, staticIssues=static_issues, testsExecuted=0',
        "compileConfiguration='existing unchanged module -Xlint:all/-Werror and inherited Main type/null compiler; lifecycle ends at test-compile'":
            "compileConfiguration='six unchanged format/type/null/Test-Xlint-Werror/SpotBugs gates; no JUnit or native execution'"}
    for before,after in replacements.items():
        if raw.count(before)!=1:raise ValueError('one explicit pure-static six-module binding: '+before)
        raw=raw.replace(before,after,1)
    compile(raw,'<native ports static only>','exec')
    return raw


def main():
    if profile.subprocess.check_output(['git','diff',OLD,'HEAD','--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=profile.ROOT):
        raise ValueError('unchanged build/static/Current, no exclusions')
    scope={**vars(profile),'OLD':OLD,'MAIN':MAIN,'EXPECTED':MAIN|TESTS,'ET':ET,'MODULES':MODULES,'NODE_PATH':node_environment()}
    exec(compile(runner_source(),'<strict native ports compile/static>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
