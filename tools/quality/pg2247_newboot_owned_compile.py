"""All current-boot fifteen-source ABI phases, only after actual whole fullseal."""
import pg2189_newsource_owned_stop_compile as prior
from pg2246_newboot_owned_sources import sources,context,SOURCE,TOOLS


def main():
    before,_,_,_=context()
    raw=prior.prior.old.prior.prior.compiler_source().replace('Pg1609','Pg2246').replace('pg1610','pg2247').replace('pg1544-release-v1','pg2126-release-v1')
    ns={**prior.prior.old.prior.prior.prior.prior.__dict__,'sources':sources,'SOURCE':SOURCE,'BEFORE':before,'TARGET':prior.prior.old.prior.prior.prior.prior.W/TOOLS}
    exec(compile(raw,'<actual newboot owned fifteen ABI>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
