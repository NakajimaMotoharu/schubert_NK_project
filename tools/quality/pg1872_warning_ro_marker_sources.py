"""New-only RO input marker fixed; old failed slot and Root identities untouched."""
from pg1867_warning_candidate_ro_sources import sources as previous

TOOLS='pg1872-warning-candidate-ro-tools-v1'
CLASS='Pg1872CandidateRo'


def bind(raw):
    return raw.replace('pg1869','pg1874').replace('pg1867','pg1872').replace('Pg1867','Pg1872').replace('PG1867','PG1872').replace('PG1681_INPUT_CLOSURE_READY','PG1872_INPUT_CLOSURE_READY')


def sources(bom,before):return {bind(n):bind(raw)for n,raw in previous(bom,before).items()}
