"""Freeze state18/config2 whole helper closure against actual unchanged Main."""
import pg1773_warning_stop_compile as old
from pg1821_warning_parent_configuration_sources import sources,context,SOURCE,TOOLS


def main():
    before,_,_,_=context()
    raw=old.prior.prior.compiler_source().replace('Pg1609','Pg1821').replace('pg1610','pg1825').replace('pg1544-release-v1','pg1638-release-v1')
    ns={**old.prior.prior.prior.prior.__dict__,'sources':sources,'SOURCE':SOURCE,'BEFORE':before,'TARGET':old.prior.prior.prior.prior.W/TOOLS}
    exec(compile(raw,'<state18/config2 current stop ABI>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
