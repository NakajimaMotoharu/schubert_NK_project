"""Distinct new-only cold one-time preparation; old staged2942 never replayed."""
import inspect
import pg2946_current_resume_dispatch as prior
from pg2950_current_cold_resume_sources import bind,sources,TOOLS,CLASS,SOURCE,BOM
from pg2952_current_cold_resume_compile import TARGET

REMOTE='/home/ubuntu/pg2954-fixed-stage-v1'
GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
STAGE=bind(prior.STAGE).replace('pg2946','pg2954')


def source():return bind(prior.source()).replace('pg2946','pg2954').replace('pg2944-frozen','pg2952-frozen')


def main():
    raw=inspect.getsource(prior.main)
    ns={**prior.__dict__,'bind':bind,'sources':sources,'TOOLS':TOOLS,'CLASS':CLASS,'SOURCE':SOURCE,'BOM':BOM,'TARGET':TARGET,'REMOTE':REMOTE,'GUEST':GUEST,'STAGE':STAGE,'source':source}
    exec(compile(raw,'<current cold exact dispatch namespace>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
