"""Required candidate-source fullsix for SSC278 Unit normalWARNING contract.

Not a repeat of PG1755: deployed old Unit and new SuccessExitStatus10 differ.
"""
import inspect
import json
import subprocess
import pg1528_filesystem_full_six as transport
from pg1754_host_boundary_full_six import server_source as previous_server

CANDIDATE='0fd734195b4d5338f6b7e860e087cce561d49562'
OLD='2741c4546afad6c1e8b6efbd53dfb58144edf7bb'


def server_source(head,digest):
    raw=previous_server(head,digest).replace('PG1754','PG1844').replace(OLD,CANDIDATE)
    compile(raw,'<candidate Unit10 fresh complete fullsix>','exec');return raw


def main():
    if subprocess.check_output(['git','diff','--name-only',CANDIDATE,'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization']):raise ValueError('fixed whole candidate source required')
    selected=json.loads((transport.prior.W/'pg1790-morning-unit-green-v1/manifest.safe.json').read_bytes())
    # Validate the real limited green outcome without borrowing the old full run.
    if selected.get('actualExit')!=0 or selected.get('tests')!=4 or any(selected.get(k)!=0 for k in ['failures','errors','skipped','javacWarnings']):raise ValueError('real independent Unit green test required')
    raw=inspect.getsource(transport.main).replace('PG1528','PG1844').replace('pg1528','pg1844').replace('3582','3618').replace('524','536').replace('1637','1643')
    raw=raw.replace('3578/523/1635 + LinuxFilesystemClassifier4 tests/one suite/two Main classes, other tests retained','PG1755 3618/536/1643 retained; independent MUNIT4 now exact SuccessExitStatus10, all Java Main unchanged')
    raw=raw.replace('SSC269 new production storage/batch dependency and required all-source regression; selected attempts failed before target tests, literal NoTests gates preserved','SSC278 Production Unit SuccessExitStatus10 and independent MUNIT contract changed; necessary candidate-source fullsix before signed deployment, not old-source reuse')
    ns={**transport.__dict__,'PRODUCTION':CANDIDATE,'server_source':server_source}
    exec(compile(raw,'<candidate-source required whole transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
