"""One necessary fresh whole regression after grouped Main/test boundaries, no VM mutation."""
import inspect
import json
import subprocess
import pg1528_filesystem_full_six as transport
from pg1844_warning_unit_full_six import server_source as previous_server

CANDIDATE='3b7f3567b'

def production():
    return subprocess.check_output(['git','rev-parse',CANDIDATE],cwd=transport.prior.ROOT,text=True).strip()

def server_source(head,digest):
    raw=previous_server(head,digest).replace('PG1844','PG2124').replace('3618','3631').replace('536','540')
    raw=raw.replace('0fd734195b4d5338f6b7e860e087cce561d49562',production())
    compile(raw,'<necessary grouped metadata source whole regression>','exec');return raw

def main():
    source=production()
    if subprocess.check_output(['git','diff','--name-only',source,'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization'],cwd=transport.prior.ROOT):
        raise ValueError('fixed grouped Main/Test source required')
    for slot,count in [('pg2118-caddy-metadata-selected-v1',29),('pg2122-caddy-metadata-selected-v1',35)]:
        v=json.loads((transport.prior.W/slot/'manifest.safe.json').read_bytes())
        if v['actualExit']!=0 or sum(x['tests']for x in v['tests'].values())!=count or any(x[k]for x in v['tests'].values()for k in ['failures','errors','skipped'])or v['staticIssues']!={'batch':0}:
            raise ValueError('fresh independently qualified changed-module groups required')
    raw=inspect.getsource(transport.main).replace('PG1528','PG2124').replace('pg1528','pg2124').replace('3582','3631').replace('524','540').replace('1637','1643')
    raw=raw.replace('3578/523/1635 + LinuxFilesystemClassifier4 tests/one suite/two Main classes, other tests retained','3618/536/1643 + CaddyMetadata4 + RootTruth1 + BackupRetention4 + BackupMetadata4; four suites, no new Main classes')
    raw=raw.replace('SSC269 new production storage/batch dependency and required all-source regression; selected attempts failed before target tests, literal NoTests gates preserved','PG-D413/414/415 grouped three Main changes plus13 independent tests/four suites; selected29/35 pass; necessary fresh source fullsix/native, not management-doc repeat')
    ns={**transport.__dict__,'PRODUCTION':source,'server_source':server_source}
    exec(compile(raw,'<one source-fixed whole dispatch>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())
