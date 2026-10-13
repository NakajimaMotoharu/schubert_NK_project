"""New-only recovered cold-profile preparation stage/action; old slot never replayed."""
import pg2306_current_completed_resume_dispatch as previous
from pg2316_current_cold_resume_sources import bind,sources,TOOLS,CLASS,SOURCE,BOM
from pg2317_current_cold_resume_compile import TARGET

REMOTE='/home/ubuntu/pg2318-fixed-stage-v1'
GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
STAGE=bind(previous.STAGE).replace('pg2306','pg2318')


def source():return bind(previous.source()).replace('pg2306','pg2318').replace('pg2305-frozen','pg2317-frozen')


def main():
    base=previous.template.prior.prior.prior.prior
    namespace={**base.__dict__,'sources':sources,'TOOLS':TOOLS,'CLASS':CLASS,'TARGET':TARGET,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'CANDIDATE':SOURCE,'BOM':BOM}
    exec(compile(source(),'<actual current cold stage/prepare>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
