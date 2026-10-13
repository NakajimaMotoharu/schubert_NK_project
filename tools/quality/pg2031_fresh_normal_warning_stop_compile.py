"""Freeze all ABI phases of the exact current normal-warning stop profile before owner admission."""
import pg1773_warning_stop_compile as old
from pg2030_fresh_normal_warning_owned_stop_sources import sources,context,SOURCE,TOOLS


def main():
    before,_,_,_=context()
    raw=old.prior.prior.compiler_source().replace('Pg1609','Pg2030').replace('pg1610','pg2031').replace('pg1544-release-v1','pg1846-release-v1')
    ns={**old.prior.prior.prior.prior.__dict__,'sources':sources,'SOURCE':SOURCE,'BEFORE':before,'TARGET':old.prior.prior.prior.prior.W/TOOLS}
    exec(compile(raw,'<exact fresh normal-warning ABI>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
