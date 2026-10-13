"""Same Main/source and fresh3633 XML/static/archive proof; historical Main byte comparator only."""
import inspect
import hashlib
import json
import subprocess
import pg1533_filesystem_full_qualification as engine
from pg2125_metadata_boundary_full_qualification import server as previous
from pg2124_metadata_boundary_full_six import production

TEST_PATH='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/RootStartupContextTest.java'
TEST_SHA='493ebfb75e95774fe66dd1c47e9a26817c342f08b450077bae6af2286d03865f'


def validate_test_append(old,new):
    if not old.endswith(b'}\n') or not new.startswith(old[:-2]) or hashlib.sha256(new).hexdigest()!=TEST_SHA:
        raise ValueError('fixed two independent tests and all old test bytes required')


def qualified_snapshot(root,snapshot):
    def git(*args):return subprocess.check_output(['git',*args],cwd=root)
    paths=git('diff','--name-only',production(),snapshot,'--','src','pom.xml','mvnw','.mvn','program/characterization').decode().splitlines()
    if paths!=[TEST_PATH]:raise ValueError('only qualified Root test append permitted; Main/config unchanged')
    validate_test_append(git('show',production()+':'+TEST_PATH),git('show',snapshot+':'+TEST_PATH))
    receipt=json.loads((engine.W/'pg2222-root-host-selected-v1/manifest.safe.json').read_bytes())
    if receipt.get('source')!=production() or any(receipt.get(k)!=v for k,v in {'actualExit':0,'tests':2,'FESAbortedNotRun':0,'classByteMismatch':0,'javacWarnings':0,'oldNativeImported':False}.items()):
        raise ValueError('actual independent two-test current Main receipt required')
    if git('diff',receipt['testSource'],snapshot,'--','src','pom.xml','mvnw','.mvn','program/characterization'):
        raise ValueError('full snapshot differs from selected test source')
    return False


def server():
    raw=previous().replace('PG2124','PG2228').replace('3631','3633').replace("'batch':(1234,172,568)","'batch':(1236,172,568)")
    compile(raw,'<fresh Root boundary integration exact qualifier>','exec');return raw


def main():
    raw=inspect.getsource(engine.main).replace('pg1533-filesystem-full-qualified-v1','pg2229-root-host-integration-full-qualified-v1').replace('pg1532-server-six-v1','pg2228-server-six-v1').replace('PG1532','PG2228').replace('4d6bcbddb417b76d27e52d5d9640752c300edccf',production())
    old="subprocess.check_output(['git', 'diff', '"+production()+"', begun['snapshot'], '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization'], cwd=root)"
    if raw.count(old)!=1:raise ValueError('exact host integration guard required')
    raw=raw.replace(old,"qualified_snapshot(root,begun['snapshot'])")
    ns={**engine.__dict__,'CODE':server(),'qualified_snapshot':qualified_snapshot}
    exec(compile(raw,'<fresh Root integration provenance transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
