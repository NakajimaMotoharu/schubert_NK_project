"""Distinct same-file finish action; no replay of failed preparation."""
import pg2318_current_cold_resume_dispatch as previous
from pg2330_current_existing_runtime_finish_sources import bind,sources,TOOLS,CLASS,SOURCE,BOM
from pg2331_current_existing_runtime_finish_compile import TARGET

REMOTE='/home/ubuntu/pg2332-fixed-stage-v1'
GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
STAGE=bind(previous.STAGE).replace('pg2318','pg2332')


def source():
    return bind(previous.source()).replace('pg2318','pg2332').replace('pg2317-frozen','pg2331-frozen')


def main():
    base=previous.previous.template.prior.prior.prior.prior
    ns={**base.__dict__,'sources':sources,'TOOLS':TOOLS,'CLASS':CLASS,'TARGET':TARGET,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'CANDIDATE':SOURCE,'BOM':BOM}
    exec(compile(source(),'<current existing file stage finish>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
