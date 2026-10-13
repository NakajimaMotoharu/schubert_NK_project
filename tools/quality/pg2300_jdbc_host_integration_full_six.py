"""One triggered full integration of two independently passed JDBC boundary tests."""
import inspect
import json
import subprocess
import pg1528_filesystem_full_six as transport
from pg2228_root_host_integration_full_six import server_source as previous
from pg2124_metadata_boundary_full_six import production


def server_source(head,digest):
    raw=previous(head,digest).replace('PG2228','PG2300').replace('3633','3635')
    compile(raw,'<current JDBC full3635>','exec')
    return raw


def validate(snapshot):
    receipt=json.loads((transport.prior.W/'pg2296-morning-guard-daily-fixture-v5/manifest.safe.json').read_bytes())
    expected={'actualExit':0,'tests':2,'FESAbortedNotRun':0,'classByteMismatch':0,'javacWarnings':0,'oldNativeImported':False,'source':production()}
    if any(receipt.get(k)!=v for k,v in expected.items()):
        raise ValueError('independently passed current two JDBC tests required')
    if subprocess.check_output(['git','diff',receipt['testSource'],snapshot,'--','src','pom.xml','mvnw','.mvn','program/characterization'],cwd=transport.prior.ROOT):
        raise ValueError('fixed selected test source required')
    paths=subprocess.check_output(['git','diff','--name-only',production(),snapshot,'--','src','pom.xml'],cwd=transport.prior.ROOT,text=True).splitlines()
    if any('/src/main/'in p or p.endswith('pom.xml')for p in paths):
        raise ValueError('Main unchanged current source required')


def main():
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=transport.prior.ROOT,text=True).strip()
    validate(head)
    raw=inspect.getsource(transport.main)
    for old,new in [('PG1528','PG2300'),('pg1528','pg2300'),('3582','3635'),('524','540'),('1637','1643')]:
        raw=raw.replace(old,new)
    raw=raw.replace('3578/523/1635 + LinuxFilesystemClassifier4 tests/one suite/two Main classes, other tests retained','3633/540/1643 qualified full plus two JDBC guard tests in existing suite; Main unchanged')
    raw=raw.replace('SSC269 new production storage/batch dependency and required all-source regression; selected attempts failed before target tests, literal NoTests gates preserved','Two new independently passed JDBC tests; necessary fresh full integration, no management-document repetition or VM mutation')
    namespace={**transport.__dict__,'PRODUCTION':production(),'server_source':server_source}
    exec(compile(raw,'<current JDBC full transport>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
