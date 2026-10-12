"""Fresh candidate XML/static/all Main bytes; old full not candidate acceptance."""
import inspect
import pg1533_filesystem_full_qualification as engine
from pg1756_boundary_full_qualification import server as old_server
from pg1844_warning_unit_full_six import CANDIDATE,OLD


def server():
    raw=old_server().replace('PG1755','PG1844').replace(OLD,CANDIDATE)
    compile(raw,'<independent candidate Unit allsource qualifier>','exec');return raw


def main():
    raw=inspect.getsource(engine.main).replace('pg1533-filesystem-full-qualified-v1','pg1845-warning-unit-full-qualified-v1').replace('pg1532-server-six-v1','pg1844-server-six-v1').replace('PG1532','PG1844').replace('4d6bcbddb417b76d27e52d5d9640752c300edccf',CANDIDATE)
    ns={**engine.__dict__,'CODE':server()}
    exec(compile(raw,'<candidate allsource provenance transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
