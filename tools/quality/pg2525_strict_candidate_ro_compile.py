"""Host ABI for new candidate read-only assembly after qualified unused placement."""
import inspect
import pg2421_question_candidate_ro_compile as previous
from pg2524_strict_candidate_ro_sources import sources, TOOLS, bind
from pg2516_current_strict_candidate_sources import CURRENT, BEFORE, production

TARGET = previous.prior.prior.prior.W / TOOLS


def compiler():
    raw = bind(previous.compiler()).replace('pg2421-', 'pg2525-').replace(
        'pg2438-current-boot-question-post-v1', 'pg2522-current-strict-candidate-post-v1').replace(
        'pg2433-frozen', 'pg2517-frozen')
    compile(raw, '<new candidate host RO ABI>', 'exec')
    return raw


def main():
    ns = {**previous.prior.prior.prior.__dict__, 'TARGET': TARGET, 'TOOLS': TOOLS,
          'sources': sources, 'CANDIDATE': production(), 'OLD': CURRENT, 'BEFORE': BEFORE}
    exec(compile(inspect.getsource(previous.prior.prior.prior.write), '<canonical new RO writer>', 'exec'), ns)
    exec(compile(compiler(), '<new RO full graph entry>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
