"""Read-only new-current observer; no business start/stop authority."""
import pg2446_question_current_observer as previous
from pg2532_strict_normal_publication_sources import candidate_bom
from pg2516_current_strict_candidate_sources import SOURCE


def source(bom=None):
    if bom is None:
        bom = candidate_bom()
    if type(bom) is not str or len(bom) != 64 or set(bom) - set('0123456789abcdef'):
        raise ValueError('actual typed new current BOM required')
    raw = previous.source()
    for before, after in [('pg2446', 'pg2538'), ('PG2446', 'PG2538'),
        ('pg2444-question-normal-publication-post-v1', 'pg2536-strict-normal-publication-post-v1'),
        (previous.SOURCE, SOURCE), (previous.BOM, bom), ('PG2428', 'PG2512')]:
        raw = raw.replace(before, after)
    compile(raw, '<new strict current whole observer>', 'exec')
    return raw


def namespace():
    ns = {'__file__':str(previous.R / 'pg2538_strict_current_observer.py'), '__name__':'strict_current_observer'}
    exec(compile(source(), '<new current immutable observer namespace>', 'exec'), ns)
    return ns


if __name__ == '__main__':
    namespace()['main']()
