"""All current fifteen-source ABI phases, after independent same-source fullseal."""
import pg2031_fresh_normal_warning_stop_compile as prior
from pg2188_newsource_owned_stop_sources import sources,context,SOURCE,TOOLS


def main():
    before,_,_,_=context()
    raw=prior.old.prior.prior.compiler_source().replace('Pg1609','Pg2188').replace('pg1610','pg2189').replace('pg1544-release-v1','pg2126-release-v1')
    ns={**prior.old.prior.prior.prior.prior.__dict__,'sources':sources,'SOURCE':SOURCE,'BEFORE':before,'TARGET':prior.old.prior.prior.prior.prior.W/TOOLS}
    exec(compile(raw,'<actual newsource owned fifteen ABI>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
