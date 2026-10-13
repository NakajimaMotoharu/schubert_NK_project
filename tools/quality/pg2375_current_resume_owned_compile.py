"""Fresh actual fifteen-source ABI after current resume full seal, no Production rebuild."""
import pg2275_current_signed_owned_compile as previous
from pg2374_current_resume_owned_sources import sources,context,SOURCE,TOOLS


def main():
    before,_,_,_=context()
    engine=previous.prior.prior.prior.old.prior.prior
    raw=engine.compiler_source().replace('Pg1609','Pg2374').replace('pg1610','pg2375').replace('pg1544-release-v1','pg2126-release-v1')
    ns={**engine.prior.prior.__dict__,'sources':sources,'SOURCE':SOURCE,'BEFORE':before,'TARGET':engine.prior.prior.W/TOOLS}
    exec(compile(raw,'<current fifteen-source full ABI>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
