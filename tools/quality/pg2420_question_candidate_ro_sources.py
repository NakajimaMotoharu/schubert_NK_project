"""New question candidate-only RO whole graph, retaining retired current normal proof."""
from pyflakes.api import check
import pg2164_normal_candidate_ro_fixed_sources as prior
from pg2412_question_unused_sources import bind as roles, sources as current_graph, BEFORE, CURRENT_BOM

TOOLS = 'pg2420-question-candidate-ro-tools-v1'
SAVE = 'pg2424-question-candidate-host-ro-v1'
CLASS = 'Pg2420CandidateRo'


def bind(raw):
    raw=roles(raw)
    for a,b in [(prior.TOOLS,TOOLS),(prior.SAVE,SAVE),
                ('pg2164','pg2420'),('Pg2164','Pg2420'),('PG2164','PG2420'),
                ('pg2167','pg2424'),('PG2167','PG2424')]:
        raw=raw.replace(a,b)
    return raw


def sources(bom,before=BEFORE):
    if before != BEFORE:
        raise ValueError('one current retired-before authority required')
    normal=current_graph(bom)
    values={bind(n):bind(s) for n,s in prior.sources(bom).items()}
    # The old normal-cohort classifier/projection is not an oracle for this
    # current Root. Keep the independent current receipt/properties intact.
    for suffix in ['parent_receipt.py','warning_parent_projection.py']:
        values['pg2420_'+suffix]=normal['pg2412_'+suffix]
    if CURRENT_BOM not in '\n'.join(values.values()):
        raise ValueError('old current BOM role must remain separate')
    for name,raw in values.items():
        if name.endswith('.py'):
            prelude="BUNDLE_HASH='pending-real-bundle'\n" if name=='pg2420_native_refs.py' else ''
            if check(prelude+raw,'<whole new candidate RO '+name+'>'):
                raise ValueError('all complete readonly namespace exports required')
            compile(raw,'<new question readonly graph>','exec')
        if '0.1.0-PG1638' in raw or '0.1.0-PG1846' in raw:
            raise ValueError('old role release forbidden in new graph')
    return values


if __name__=='__main__':
    raise SystemExit('source factory only; no VM operation')
