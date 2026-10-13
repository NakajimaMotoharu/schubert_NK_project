"""Fresh role-fixed RO graph; old failed tools/actions never replayed."""
import pg2154_normal_candidate_ro_dispatch as prior
from pg2164_normal_candidate_ro_fixed_sources import sources,TOOLS,CLASS,bind
from pg2165_normal_candidate_ro_fixed_compile import TARGET

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg2166-fixed-stage-v1'
STAGE=bind(prior.STAGE).replace('0.1.0-PG1638','0.1.0-PG1846').replace('pg2154-fixed-stage-v1','pg2166-fixed-stage-v1')


def source():return bind(prior.source()).replace('pg2153-frozen','pg2165-frozen').replace('pg2154-','pg2166-')


def main():
    ns={**prior.prior.__dict__,'__file__':__file__,'TARGET':TARGET,'TOOLS':TOOLS,'CLASS':CLASS,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'sources':sources,'CANDIDATE':prior.production(),'OLD':prior.CURRENT,'BEFORE':prior.BEFORE}
    exec(compile(source(),'<actual fixed normal RO dispatch>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
