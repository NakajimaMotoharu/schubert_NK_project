"""Independent XML/static/archive/unchanged Main qualification of fresh PG2300."""
import inspect
import subprocess
import pg1533_filesystem_full_qualification as engine
from pg2229_root_host_integration_full_qualification import server as previous
from pg2300_jdbc_host_integration_full_six import validate,production


def server():
    raw=previous().replace('PG2228','PG2300').replace('3633','3635').replace("'batch':(1236,172,568)","'batch':(1238,172,568)")
    compile(raw,'<fresh JDBC full independent qualification>','exec')
    return raw


def main():
    raw=inspect.getsource(engine.main).replace('pg1533-filesystem-full-qualified-v1','pg2301-jdbc-host-integration-qualified-v1').replace('pg1532-server-six-v1','pg2300-server-six-v1').replace('PG1532','PG2300').replace('4d6bcbddb417b76d27e52d5d9640752c300edccf',production())
    marker="subprocess.check_output(['git', 'diff', '"+production()+"', begun['snapshot'], '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization'], cwd=root)"
    if raw.count(marker)!=1:raise ValueError('exact full provenance boundary required')
    raw=raw.replace(marker,"qualified_snapshot(root,begun['snapshot'])")
    def qualified_snapshot(root,snapshot):
        validate(snapshot)
        return False
    namespace={**engine.__dict__,'CODE':server(),'qualified_snapshot':qualified_snapshot}
    exec(compile(raw,'<current JDBC result qualification>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
