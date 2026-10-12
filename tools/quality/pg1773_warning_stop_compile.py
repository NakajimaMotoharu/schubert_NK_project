"""Freeze WARNING-original/failure-manager current stop ABI before guest action."""
import pg1704_new_source_stop_compile as prior
from pg1772_warning_owned_stop_sources import sources,context,SOURCE,TOOLS


def main():
    before,_,_,_=context()
    raw=prior.prior.compiler_source().replace('Pg1609','Pg1772').replace('pg1610','pg1773')
    raw=raw.replace('pg1544-release-v1','pg1638-release-v1')
    ns={**prior.prior.prior.prior.__dict__,'sources':sources,'SOURCE':SOURCE,'BEFORE':before,'TARGET':prior.prior.prior.prior.W/TOOLS}
    exec(compile(raw,'<current warning stop ABI compiler>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
