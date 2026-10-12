"""Same direct compiler with immutable new-slot marker sources."""
import inspect
import pg1868_warning_candidate_ro_compile as prior
from pg1872_warning_ro_marker_sources import sources,TOOLS,bind

TARGET=prior.W/TOOLS


def main():
    raw=bind(inspect.getsource(prior.main)).replace('pg1868-','pg1873-')
    ns={**prior.__dict__,'TARGET':TARGET,'TOOLS':TOOLS,'sources':sources}
    # Actual nested writer reads its own new TARGET, not the old module global.
    exec(compile(inspect.getsource(prior.write),'<new-only RO nested writer>','exec'),ns)
    exec(compile(raw,'<new-only direct RO marker compiler>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
