"""Full fifteen-source Java ABI after actual current full seal; no rebuild of Production."""
import pg2375_current_resume_owned_compile as prior
from pg2458_question_current_owned_sources import sources,context,SOURCE,TOOLS


def main():
    before,_,_,_=context()
    engine=prior.previous.prior.prior.prior.old.prior.prior
    raw=engine.compiler_source().replace('Pg1609','Pg2458').replace('pg1610','pg2459').replace('pg1544-release-v1','pg2428-release-v1')
    ns={**engine.prior.prior.__dict__,'sources':sources,'SOURCE':SOURCE,'BEFORE':before,'TARGET':engine.prior.prior.W/TOOLS}
    exec(compile(raw,'<current whole owned ABI>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
