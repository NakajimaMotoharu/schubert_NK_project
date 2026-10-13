"""Host-only full new-question RO ABI after independent unused placement."""
import inspect
import pg2165_normal_candidate_ro_fixed_compile as prior
from pg2420_question_candidate_ro_sources import sources,TOOLS,bind
from pg2412_question_unused_sources import CURRENT,BEFORE,production

TARGET=prior.prior.prior.W/TOOLS


def compiler():
    raw=bind(prior.compiler())
    for a,b in [('pg2165-','pg2421-'),('pg2150-normal-unused-independent-post-v1','pg2438-current-boot-question-post-v1'),
                ('pg2145-frozen','pg2433-frozen')]:
        raw=raw.replace(a,b)
    compile(raw,'<new question whole RO ABI>','exec')
    return raw


def main():
    namespace={**prior.prior.prior.__dict__,'TARGET':TARGET,'TOOLS':TOOLS,'sources':sources,
               'CANDIDATE':production(),'OLD':CURRENT,'BEFORE':BEFORE}
    exec(compile(inspect.getsource(prior.prior.prior.write),'<canonical new RO writer>','exec'),namespace)
    exec(compile(compiler(),'<host RO full graph>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':
    raise SystemExit(main())
