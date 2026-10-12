"""Candidate-only host read-only mount; old current WARNING unchanged."""
import inspect
import pg1686_completed_candidate_ro_sources as prior
from pg1860_warning_actual_graph_sources import sources as current_sources
from pg1844_warning_unit_full_six import CANDIDATE,OLD

TOOLS='pg1867-warning-candidate-ro-tools-v1'
SAVE='pg1869-warning-candidate-host-ro-v1'
CLASS='Pg1867CandidateRo'


def role_bind(raw,bom):
    raw=raw.replace(OLD,'__NEW_SOURCE__').replace('4d6bcbddb417b76d27e52d5d9640752c300edccf',OLD).replace('__NEW_SOURCE__',CANDIDATE)
    raw=raw.replace('PG1638','__NEW_RELEASE__').replace('pg1638','__NEW_STEM__').replace('PG1544','PG1638').replace('pg1544','pg1638').replace('__NEW_RELEASE__','PG1846').replace('__NEW_STEM__','pg1846')
    return raw.replace('195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1',bom)


def preflight(bom):
    raw=role_bind(prior.preflight(),bom)
    for old,new in [('Pg1686', 'Pg1867'),('pg1686', 'pg1867'),('pg1867-completed-candidate-ro-tools-v1',TOOLS),('pg1689-completed-candidate-host-ro-v1',SAVE)]:raw=raw.replace(old,new)
    return raw


def sources(bom,before):
    raw=inspect.getsource(prior.sources)
    for old,new in [('pg1681_input_preflight.py','pg1860_input_preflight.py'),('Pg1640','Pg1860'),('pg1640','pg1860'),('PG1640','PG1860'),('Pg1686','Pg1867'),('pg1686','pg1867'),('PG1686','PG1867'),('Pg1660CurrentIdentityTest','Pg1860CurrentIdentityTest'),('Pg1681InputBoundaryTest','Pg1860InputBoundaryTest'),('pg1681-completed-unused-tools-v4','pg1860-warning-unused-tools-v1'),('pg1684-completed-unused-placement-v4','pg1864-warning-unused-placement-v1'),("METHOD.replace('PG832','PG1638')","METHOD.replace('PG832','PG1846')"),("ORACLE.replace('PG832','PG1638')","ORACLE.replace('PG832','PG1846')"),(".replace('PG1292','PG1638')",".replace('PG1292','PG1846')")]:raw=raw.replace(old,new)
    # All existing classes (including CurrentIdentity/InputBoundary) were already
    # in the1860 namespace; move only actual prefixes, not arbitrary digits.
    ns={**prior.__dict__,'TOOLS':TOOLS,'SAVE':SAVE,'CLASS':CLASS,'BOM':bom,'SOURCE':CANDIDATE,'completed':lambda digest:current_sources(digest,before),'method':lambda:role_bind(prior.method(),bom),'preflight':lambda:preflight(bom)}
    exec(compile(raw,'<actual WARNING candidate-only RO composition>','exec'),ns)
    result=ns['sources']()
    # Remap references to already-prefixed independent identity/input tests.
    result={name.replace('Pg1860','Pg1867'):body.replace('Pg1860','Pg1867').replace('pg1867-warning-unused-tools-v1',TOOLS)for name,body in result.items()}
    return result
