"""BUG1215 every role-specific candidate path bound before actual RO emission."""
from pg2152_normal_candidate_ro_sources import sources as prior
from pg2132_current_normal_unused_sources import BEFORE

TOOLS='pg2164-normal-candidate-ro-tools-v1'
SAVE='pg2167-normal-candidate-host-ro-v1'
CLASS='Pg2164CandidateRo'


def bind(raw):
    return raw.replace('pg2152','pg2164').replace('Pg2152','Pg2164').replace('PG2152','PG2164').replace('pg2155','pg2167')


def sources(bom,before=BEFORE):
    result={bind(n):bind(raw)for n,raw in prior(bom,before).items()}
    name='pg2164_native_refs.py';raw=result[name]
    old="candidate_root=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1638')"
    if raw.count(old)!=1:raise ValueError('exact obsolete candidate-before role required')
    result[name]=raw.replace(old,"candidate_root=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG2126')")
    for body in result.values():
        if '0.1.0-PG1638'in body:raise ValueError('all actual graph old release roles forbidden')
    return result
