"""Fresh XML/static/archive/Main provenance qualification; old native cannot qualify changed Main."""
import inspect
import pg1533_filesystem_full_qualification as engine
from pg1845_warning_unit_full_qualification import server as previous_server
from pg2124_metadata_boundary_full_six import production

def server():
    raw=previous_server().replace('PG1844','PG2124').replace('0fd734195b4d5338f6b7e860e087cce561d49562',production())
    raw=raw.replace("'batch':(1221,168,568)","'batch':(1234,172,568)").replace('==3618','==3631').replace('==536','==540').replace("'tests':3618","'tests':3631").replace("'suites':536","'suites':540")
    old="old=json.loads((B/'runs/PG1633-six-v1/manifest.safe.json').read_bytes())"
    if raw.count(old)!=1:raise ValueError('one qualified previous-source byte comparison required')
    raw=raw.replace(old,"old=json.loads((B/'runs/PG1844-six-v1/manifest.safe.json').read_bytes())")
    raw=raw.replace('require(changed==[])',"require(set(changed)=={'batch:dev/codex/schubert/nk/batch/file/CaddyPublicConfiguration.class','batch:dev/codex/schubert/nk/batch/platform/RootStartupContext.class','batch:dev/codex/schubert/nk/batch/file/MorningBackupArtifacts.class'})")
    compile(raw,'<fresh whole metadata source independent qualifier>','exec');return raw

def main():
    raw=inspect.getsource(engine.main).replace('pg1533-filesystem-full-qualified-v1','pg2125-metadata-boundary-full-qualified-v1').replace('pg1532-server-six-v1','pg2124-server-six-v1').replace('PG1532','PG2124').replace('4d6bcbddb417b76d27e52d5d9640752c300edccf',production())
    ns={**engine.__dict__,'CODE':server()}
    exec(compile(raw,'<source-fixed whole metadata qualifier entry>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())
