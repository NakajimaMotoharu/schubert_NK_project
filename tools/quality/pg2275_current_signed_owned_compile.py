"""New-only full immutable fifteen-source compile after BUG1224 correction."""
import pg2247_newboot_owned_compile as prior
from pg2274_current_signed_owned_sources import sources,context,SOURCE,TOOLS


def main():
    before,_,_,_=context()
    raw=prior.prior.prior.old.prior.prior.compiler_source().replace('Pg1609','Pg2274').replace('pg1610','pg2275').replace('pg1544-release-v1','pg2126-release-v1')
    ns={**prior.prior.prior.old.prior.prior.prior.prior.__dict__,'sources':sources,'SOURCE':SOURCE,'BEFORE':before,'TARGET':prior.prior.prior.old.prior.prior.prior.prior.W/TOOLS}
    exec(compile(raw,'<corrected signed-current owned full ABI>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
