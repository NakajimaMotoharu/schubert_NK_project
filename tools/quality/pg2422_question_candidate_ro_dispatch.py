"""Fixed candidate-only host RO stage/prepare; no ordinary startup or publication."""
import pg2166_normal_candidate_ro_fixed_dispatch as prior
from pg2420_question_candidate_ro_sources import sources,TOOLS,CLASS,bind
from pg2421_question_candidate_ro_compile import TARGET
from pg2412_question_unused_sources import CURRENT,BEFORE,production

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg2422-fixed-stage-v1'
STAGE=bind(prior.STAGE).replace('pg2166-fixed-stage-v1','pg2422-fixed-stage-v1')


def source():
    raw=bind(prior.source()).replace('pg2165-frozen','pg2421-frozen').replace(
        'pg2166-','pg2422-').replace('pg2150-normal-unused-independent-post-v1','pg2418-question-unused-independent-post-v1')
    compile(raw,'<new current question candidate RO dispatch>','exec')
    return raw


def main():
    namespace={**prior.prior.prior.__dict__,'__file__':__file__,'TARGET':TARGET,'TOOLS':TOOLS,
               'CLASS':CLASS,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'sources':sources,
               'CANDIDATE':production(),'OLD':CURRENT,'BEFORE':BEFORE}
    exec(compile(source(),'<actual question candidate readonly entry>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':
    raise SystemExit(main())
