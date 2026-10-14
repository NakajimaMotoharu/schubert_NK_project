"""Current one finite normal resume preparation; no Root start/permit/business SQL."""
import inspect
import pg2306_current_completed_resume_dispatch as prior
from pg2942_current_completed_resume_sources import bind,sources,TOOLS,CLASS,SOURCE,BOM
from pg2944_current_resume_compile import TARGET

REMOTE='/home/ubuntu/pg2946-fixed-stage-v1'
GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
STAGE=bind(prior.STAGE).replace('pg2306','pg2946')


def source():
    raw=bind(prior.source()).replace('pg2306','pg2946').replace('pg2305-frozen','pg2944-frozen')
    raw='CLASS='+repr(CLASS)+'\nTOOLS='+repr(TOOLS)+'\n'+raw
    compile(raw,'<all final current producer stage and prepare>','exec');return raw


def main():
    raw=inspect.getsource(prior.main)
    ns={**prior.__dict__,'bind':bind,'sources':sources,'TOOLS':TOOLS,'CLASS':CLASS,'SOURCE':SOURCE,'BOM':BOM,'TARGET':TARGET,'REMOTE':REMOTE,'GUEST':GUEST,'STAGE':STAGE,'source':source}
    exec(compile(raw,'<same closed current dispatch>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
