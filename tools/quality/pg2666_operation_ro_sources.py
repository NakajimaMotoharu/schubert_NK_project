"""New resource candidate RO graph; current originals and ordinary source remain a79."""
from pyflakes.api import check
import pg2524_strict_candidate_ro_sources as previous
from pg2658_operation_candidate_sources import bind as roles,sources as current_graph,BEFORE

TOOLS='pg2666-operation-ro-tools-v1';SAVE='pg2670-operation-host-ro-v1';CLASS='Pg2666CandidateRo'


def bind(raw):
    raw=roles(raw)
    for a,b in [(previous.TOOLS,TOOLS),(previous.SAVE,SAVE),('pg2524','pg2666'),('Pg2524','Pg2666'),('PG2524','PG2666'),('pg2528','pg2670'),('PG2528','PG2670')]:raw=raw.replace(a,b)
    return raw


def sources(bom,before=BEFORE):
    if before!=BEFORE:raise ValueError('actual current a79 original proof required')
    normal=current_graph(bom);values={bind(n):bind(s)for n,s in previous.sources(bom).items()}
    for suffix in ['parent_receipt.py','warning_parent_projection.py']:values['pg2666_'+suffix]=normal['pg2658_'+suffix]
    for name,raw in values.items():
        if name.endswith('.py'):
            prelude="BUNDLE_HASH='pending-real-bundle'\n"if name=='pg2666_native_refs.py'else ''
            if check(prelude+raw,'<whole operation readonly graph>'):raise ValueError('complete namespace required')
            compile(raw,'<new candidate readonly graph>','exec')
    return values


if __name__=='__main__':raise SystemExit('source factory only')
