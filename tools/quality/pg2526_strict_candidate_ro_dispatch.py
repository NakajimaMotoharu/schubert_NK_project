"""New-only read-only stage/prepare; no business startup or publication."""
import pg2422_question_candidate_ro_dispatch as previous
from pg2524_strict_candidate_ro_sources import sources, TOOLS, CLASS, bind
from pg2525_strict_candidate_ro_compile import TARGET
from pg2516_current_strict_candidate_sources import CURRENT, BEFORE, production

GUEST = '/var/lib/pgpt-s1-preservation/' + TOOLS
REMOTE = '/home/ubuntu/pg2526-fixed-stage-v1'
STAGE = bind(previous.STAGE).replace('pg2422-fixed-stage-v1', 'pg2526-fixed-stage-v1')


def source():
    raw = bind(previous.source()).replace('pg2421-frozen', 'pg2525-frozen').replace(
        'pg2422-', 'pg2526-').replace('pg2438-current-boot-question-post-v1', 'pg2522-current-strict-candidate-post-v1')
    compile(raw, '<new candidate readonly direct body>', 'exec')
    return raw


def main():
    ns = {**previous.prior.prior.prior.__dict__, '__file__': __file__, 'TARGET': TARGET,
          'TOOLS': TOOLS, 'CLASS': CLASS, 'GUEST': GUEST, 'REMOTE': REMOTE,
          'STAGE': STAGE, 'sources': sources, 'CANDIDATE': production(), 'OLD': CURRENT, 'BEFORE': BEFORE}
    exec(compile(source(), '<new candidate readonly dispatch>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
