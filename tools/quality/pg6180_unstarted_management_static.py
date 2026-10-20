"""SSC317 exact two Main/two Test, six existing static gates, no JUnit/runtime operations."""
import pg6162_native_ports_static as parent

OLD='99e7049fbf04fb23aa6c4143a123ca08285a7312'
MAIN={'src/schubert-nk-'+m+'/src/main/java/dev/codex/schubert/nk/'+p+'.java'
      for m,p in (('api','api/bootstrap/ApiManagementServer'),('web','web/bootstrap/WebManagementServer'))}
TESTS={'src/schubert-nk-'+m+'/src/test/java/dev/codex/schubert/nk/'+p+'.java'
       for m,p in (('api','api/bootstrap/ApiManagementBindTest'),('web','web/bootstrap/WebUnstartedManagementTest'))}


def runner_source():
    raw=parent.runner_source()
    for before,after in {
        'pg6162-native-ports-static-v1':'pg6180-unstarted-management-static-v1',
        'PG6162-native-ports-static-v1':'PG6180-unstarted-management-static-v1',
        'pg6160-api-monitor-static-v1/source':'pg6176-native-assembly-selected-v1/source',
        'changedMainCount=8':'changedMainCount=2'}.items():
        if raw.count(before)!=1:raise ValueError('one pure-static binding '+before)
        raw=raw.replace(before,after,1)
    compile(raw,'<unstarted six-static only>','exec')
    return raw


def main():
    profile=parent.profile
    if profile.subprocess.check_output(['git','diff',OLD,'HEAD','--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=profile.ROOT):
        raise ValueError('build/static/Current unchanged')
    scope={**vars(profile),'OLD':OLD,'MAIN':MAIN,'EXPECTED':MAIN|TESTS,
        'ET':parent.ET,'MODULES':parent.MODULES,'NODE_PATH':parent.node_environment()}
    exec(compile(runner_source(),'<unstarted strict static>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
