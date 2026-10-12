"""Freeze actual new Source owned-stop ABI and independent Java vectors."""
import pg1610_current_ordinary_stop_compile as prior
from pg1703_new_source_owned_stop_sources import sources,context,SOURCE,TOOLS


def main():
    before,_,_,_=context()
    raw=prior.compiler_source().replace('Pg1609','Pg1703').replace('pg1610','pg1704')
    raw=raw.replace('pg1544-release-v1','pg1638-release-v1')
    ns={**prior.prior.prior.__dict__,'sources':sources,'SOURCE':SOURCE,'BEFORE':before,
        'TARGET':prior.prior.prior.W/TOOLS}
    exec(compile(raw,'<new Source stop qualification>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
