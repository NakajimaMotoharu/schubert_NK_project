"""SS316 B2, exact four Main/three Test, strict six-module compile/static without JUnit."""
import pg6162_native_ports_static as parent

OLD='7b6296d5cd378a0d19e94c51bbe4919c0028482c'
MAIN={'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/'+p+'.java' for p in (
    'api/bootstrap/ApiManagementServer','api/bootstrap/ApiProcessMain','api/storage/ApiApplicationPreparation')}
MAIN.add('src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebNativeRuntime.java')
TESTS={'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/'+p+'.java' for p in (
    'api/bootstrap/ApiManagementStopTest','api/bootstrap/ApiManagementBindTest','api/storage/ApiPreparationOwnerTest')}


def runner_source():
    raw=parent.runner_source()
    for before,after in {
        'pg6162-native-ports-static-v1':'pg6174-native-assembly-static-v1',
        'PG6162-native-ports-static-v1':'PG6174-native-assembly-static-v1',
        'pg6160-api-monitor-static-v1/source':'pg6170-native-retention-selected-v3/source',
        'changedMainCount=8':'changedMainCount=4'}.items():
        if raw.count(before)!=1:raise ValueError('one explicit static-only binding '+before)
        raw=raw.replace(before,after,1)
    compile(raw,'<B2 no JUnit>','exec')
    return raw


def main():
    profile=parent.profile
    if profile.subprocess.check_output(['git','diff',OLD,'HEAD','--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=profile.ROOT):
        raise ValueError('unchanged build/static/Current')
    scope={**vars(profile),'OLD':OLD,'MAIN':MAIN,'EXPECTED':MAIN|TESTS,
        'ET':parent.ET,'MODULES':parent.MODULES,'NODE_PATH':parent.node_environment()}
    exec(compile(runner_source(),'<SS316 strict six-static only>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
