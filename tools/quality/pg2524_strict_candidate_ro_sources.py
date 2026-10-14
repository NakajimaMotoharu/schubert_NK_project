"""New candidate-only read-only graph retaining actual cdbc original proof."""
from pyflakes.api import check
import pg2420_question_candidate_ro_sources as previous
from pg2516_current_strict_candidate_sources import bind as roles, sources as current_graph, BEFORE

TOOLS = 'pg2524-strict-candidate-ro-tools-v1'
SAVE = 'pg2528-strict-candidate-host-ro-v1'
CLASS = 'Pg2524CandidateRo'


def bind(raw):
    raw = roles(raw)
    for before, after in [(previous.TOOLS, TOOLS), (previous.SAVE, SAVE),
                          ('pg2420', 'pg2524'), ('Pg2420', 'Pg2524'), ('PG2420', 'PG2524'),
                          ('pg2424', 'pg2528'), ('PG2424', 'PG2528')]:
        raw = raw.replace(before, after)
    return raw


def sources(bom, before=BEFORE):
    if before != BEFORE:
        raise ValueError('one actual current cdbc original proof required')
    normal = current_graph(bom)
    values = {bind(n):bind(s) for n,s in previous.sources(bom).items()}
    for suffix in ['parent_receipt.py', 'warning_parent_projection.py']:
        values['pg2524_' + suffix] = normal['pg2516_' + suffix]
    for name, raw in values.items():
        if name.endswith('.py'):
            context = "BUNDLE_HASH='pending-real-bundle'\n" if name == 'pg2524_native_refs.py' else ''
            if check(context + raw, '<new candidate complete read-only graph>'):
                raise ValueError('all actual read-only namespace exports required')
            compile(raw, '<new strict candidate readonly graph>', 'exec')
    return values


if __name__ == '__main__':
    raise SystemExit('source factory only')
