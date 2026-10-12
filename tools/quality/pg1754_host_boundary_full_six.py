"""One batched fresh full regression after independent host matrices, Main unchanged."""
import inspect
import json
import subprocess
import pg1528_filesystem_full_six as transport
from pg1633_api_boundary_full_six import server_source as existing_server
from pg1719_current_bootstrap_sources import SOURCE

def server_source(head,digest):
    raw=existing_server(head,digest).replace('PG1633','PG1754')
    for old,new in [('tests==3596','tests==3618'),("'expectedTests':3596","'expectedTests':3618"),('suites==532','suites==536')]:
        if raw.count(old)!=1:raise ValueError('one actual full-count field required')
        raw=raw.replace(old,new)
    from pyflakes.api import check
    if check(raw,'<batched current test/Main fullsix>'):raise ValueError('actual static closure required')
    return raw

def main():
    for name,number,count in [('pg1717-formatted-api-selected-qualified-v1','1716',5),('pg1740-successful-projection-qualified-v1','1739',7),('pg1745-root-exact-qualified-v1','1743',8),('pg1747-caddy-exact-qualified-v1','1746',2),('pg1751-expiry-exact-qualified-v1','1750',4)]:
        v=json.loads((transport.prior.W/name/'manifest.safe.json').read_bytes())
        if v['actualExit']!=0 or v['testsByRun']!={number:count}:raise ValueError('all changed tests independently qualified')
    paths=subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','mvnw','.mvn','program/characterization'],cwd=transport.prior.ROOT,text=True).splitlines()
    if len(paths)!=6 or any('/src/test/'not in p for p in paths):raise ValueError('same Production and exactly six Test files required')
    raw=inspect.getsource(transport.main).replace('PG1528','PG1754').replace('pg1528','pg1754').replace('3582','3618').replace('524','536').replace('1637','1643')
    raw=raw.replace('3578/523/1635 + LinuxFilesystemClassifier4 tests/one suite/two Main classes, other tests retained','3596/532/1643 + API1/Backup7/Root8/Caddy2/Expiry4; four new suites, Main byte unchanged')
    raw=raw.replace('SSC269 new production storage/batch dependency and required all-source regression; selected attempts failed before target tests, literal NoTests gates preserved','Batched independently qualified host boundary integration: five Test groups/six changed Test files, one fresh full six; not management-doc repeat')
    ns={**transport.__dict__,'server_source':server_source,'PRODUCTION':SOURCE}
    exec(compile(raw,'<one fixed batched fullsix dispatch>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
