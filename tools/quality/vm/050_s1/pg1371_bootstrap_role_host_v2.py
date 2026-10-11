"""New-only complete independent fixture runtime, preserving old partial1370 output."""
import inspect
import pg1370_bootstrap_role_host as previous

LIBRARIES=(
    'org/junit/jupiter/junit-jupiter-api/5.13.4/junit-jupiter-api-5.13.4.jar',
    'org/junit/platform/junit-platform-commons/1.13.4/junit-platform-commons-1.13.4.jar',
    'org/opentest4j/opentest4j/1.3.0/opentest4j-1.3.0.jar',
    'org/apiguardian/apiguardian-api/1.1.2/apiguardian-api-1.1.2.jar',
)

def source():
    raw=inspect.getsource(previous.main).replace('pg1370-bootstrap-role-host-v1','pg1371-bootstrap-role-host-v2').replace('PG1370-bootstrap-role-host-v1','PG1371-bootstrap-role-host-v2')
    marker='    phases={};start=datetime.datetime.now(datetime.timezone.utc)'
    if raw.count(marker)!=1:raise ValueError('one actual fixed runtime boundary required')
    raw=raw.replace(marker,"    libraries={name:sha(repo/name)for name in LIBRARIES}\n    cp+=':'+':'.join(str(repo/name)for name in LIBRARIES)\n"+marker)
    marker="'fixtureHashes':fixtures,'phases':phases"
    if raw.count(marker)!=1:raise ValueError('one complete fixture manifest required')
    raw=raw.replace(marker,"'fixtureHashes':fixtures,'runtimeLibraryHashes':libraries,'phases':phases")
    compile(raw,'<actual complete fixture runtime>','exec');return raw

if __name__=='__main__':
    env=dict(previous.__dict__,LIBRARIES=LIBRARIES)
    exec(compile(source(),'<new fixed Bootstrap-role host build>','exec'),env)
    raise SystemExit(env['main']())
