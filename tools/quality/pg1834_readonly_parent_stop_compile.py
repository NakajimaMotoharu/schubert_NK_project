"""Freeze dedicated readonly parent_state without expanding stop scope."""
import pg1773_warning_stop_compile as old
from pg1833_readonly_parent_state_sources import sources,context,SOURCE,TOOLS


def main():
    before,_,_,_=context()
    raw=old.prior.prior.compiler_source().replace('Pg1609','Pg1833').replace('pg1610','pg1834').replace('pg1544-release-v1','pg1638-release-v1')
    ns={**old.prior.prior.prior.prior.__dict__,'sources':sources,'SOURCE':SOURCE,'BEFORE':before,'TARGET':old.prior.prior.prior.prior.W/TOOLS}
    exec(compile(raw,'<readonly parent-state current stop ABI>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
