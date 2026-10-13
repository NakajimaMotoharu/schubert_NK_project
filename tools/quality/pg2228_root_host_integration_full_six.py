"""One required current test/native integration full after two independent Root boundaries."""
import inspect
import json
import subprocess
import pg1528_filesystem_full_six as transport
from pg2124_metadata_boundary_full_six import server_source as previous,production


def server_source(head,digest):
    raw=previous(head,digest).replace('PG2124','PG2228').replace('3631','3633')
    compile(raw,'<one current test/native full3633>','exec');return raw


def main():
    source=production()
    changed=subprocess.check_output(['git','diff','--name-only',source,'HEAD','--','src','pom.xml'],text=True).splitlines()
    if any('/src/main/' in p or p.endswith('pom.xml') for p in changed):raise ValueError('current unchanged Main required')
    value=json.loads((transport.prior.W/'pg2222-root-host-selected-v1/manifest.safe.json').read_bytes())
    if value['actualExit']!=0 or value['tests']!=2 or value['FESAbortedNotRun']!=0 or value['classByteMismatch']!=0:
        raise ValueError('actual latest two independent selected tests required')
    raw=inspect.getsource(transport.main)
    for old,new in [('PG1528','PG2228'),('pg1528','pg2228'),('3582','3633'),('524','540'),('1637','1643')]:raw=raw.replace(old,new)
    raw=raw.replace('3578/523/1635 + LinuxFilesystemClassifier4 tests/one suite/two Main classes, other tests retained','3631/540/1643 qualified Main plus ROOTCTX010/011 two tests in existing suite; Main unchanged')
    raw=raw.replace('SSC269 new production storage/batch dependency and required all-source regression; selected attempts failed before target tests, literal NoTests gates preserved','Current newboot test/native integration after two mandatory host tests; fresh full3633 once, no management-only repetition or VM operation')
    ns={**transport.__dict__,'PRODUCTION':source,'server_source':server_source}
    exec(compile(raw,'<one current integration full transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
