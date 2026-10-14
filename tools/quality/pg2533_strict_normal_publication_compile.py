"""Host complete finite-publication ABI after actual new candidate independent RO."""
import inspect
import pg2441_question_normal_publication_compile as previous
from pg2532_strict_normal_publication_sources import sources, TOOLS, candidate_bom, bind, BEFORE, CURRENT, production

TARGET = previous.prior.prior.W / TOOLS


def compiler(bom):
    raw = bind(previous.compiler(), bom)
    for before, after in [('pg2441-', 'pg2533-'),
        ('pg2426-question-candidate-ro-post-v1', 'pg2530-strict-candidate-ro-post-v1'),
        ('pg2433-frozen', 'pg2517-frozen'), ('pg2432-current-boot-question-tools-v1', 'pg2516-current-strict-candidate-tools-v1'),
        ('Pg2432', 'Pg2516')]:
        raw = raw.replace(before, after)
    compile(raw, '<new finite publication host compiler>', 'exec')
    return raw


def main():
    bom = candidate_bom()
    ns = {**previous.prior.prior.__dict__, 'TARGET': TARGET, 'TOOLS': TOOLS, 'sources': sources,
          'CANDIDATE': production(), 'OLD': CURRENT, 'BOM': bom, 'BEFORE': BEFORE}
    exec(compile(inspect.getsource(previous.prior.prior.write), '<canonical immutable publication writer>', 'exec'), ns)
    exec(compile(compiler(bom), '<new current publication full ABI>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
