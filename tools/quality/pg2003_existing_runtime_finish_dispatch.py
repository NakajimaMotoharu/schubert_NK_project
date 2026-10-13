"""Separate action/archive/root for existing-file finish, same actual preownership marker."""
import pg1983_fresh_completed_resume_dispatch as prior
from pg2001_existing_runtime_finish_sources import sources,TOOLS,CLASS
from pg2002_existing_runtime_finish_compile import TARGET

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg2003-fixed-stage-v1'
STAGE=prior.STAGE.replace('pg1983-fixed-stage-v1','pg2003-fixed-stage-v1').replace('pg1983-qualified-tools-v1.tar','pg2003-qualified-tools-v1.tar').replace('pg1980-fresh-resume-tools-v1',TOOLS)


def source():
    return prior.source().replace('pg1983-','pg2003-').replace('pg1980_native','pg2001_native').replace('pg1980_input','pg2001_input').replace('Pg1980','Pg2001').replace('PG1980','PG2001').replace('pg1982-frozen','pg2002-frozen').replace('prepare-resume','finish-runtime')


def main():
    base=prior.prior.prior.prior
    ns={**base.prior.__dict__,'sources':sources,'TOOLS':TOOLS,'CLASS':CLASS,'TARGET':TARGET,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE}
    exec(compile(source(),'<actual remaining runtime entry>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
