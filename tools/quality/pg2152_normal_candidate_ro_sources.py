"""Normal completed old/current and signed candidate-only RO; no Unit exchange."""
import inspect
from pg1686_completed_candidate_ro_sources import sources as template,method as old_method,preflight as old_preflight
import pg1686_completed_candidate_ro_sources as original
from pg2144_normal_unused_fixed_sources import sources as completed
from pg2132_current_normal_unused_sources import CURRENT,CURRENT_BOM,production,BEFORE

TOOLS='pg2152-normal-candidate-ro-tools-v1'
SAVE='pg2155-normal-candidate-host-ro-v1'
CLASS='Pg2152CandidateRo'


def role_bind(raw,bom):
    pairs=[('2741c4546afad6c1e8b6efbd53dfb58144edf7bb',production()),('4d6bcbddb417b76d27e52d5d9640752c300edccf',CURRENT),('PG1638','__NEW__'),('pg1638','__NEWLOW__'),('PG1544','PG1846'),('pg1544','pg1846'),('__NEW__','PG2126'),('__NEWLOW__','pg2126'),('195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1',bom)]
    for old,new in pairs:raw=raw.replace(old,new)
    return raw


def preflight(bom):
    raw=role_bind(old_preflight(),bom)
    for old,new in [('Pg1686','Pg2152'),('pg1686','pg2152'),('pg2152-completed-candidate-ro-tools-v1',TOOLS),('pg1689-completed-candidate-host-ro-v1',SAVE),('PG1681_INPUT_CLOSURE_READY','PG2152_INPUT_CLOSURE_READY')]:raw=raw.replace(old,new)
    return raw


def sources(bom,before=BEFORE):
    code=inspect.getsource(template)
    for old,new in [('pg1681_input_preflight.py','pg2144_input_preflight.py'),('Pg1640','Pg2144'),('pg1640','pg2144'),('PG1640','PG2144'),('Pg1686','Pg2152'),('pg1686','pg2152'),('PG1686','PG2152'),('Pg1660CurrentIdentityTest','Pg2144CurrentIdentityTest'),('Pg1681InputBoundaryTest','Pg2144InputBoundaryTest'),('pg1681-completed-unused-tools-v4','pg2144-current-normal-unused-tools-v1'),('pg1684-completed-unused-placement-v4','pg2148-current-normal-unused-placement-v1'),("METHOD.replace('PG832','PG1638')","METHOD.replace('PG832','PG2126')"),("ORACLE.replace('PG832','PG1638')","ORACLE.replace('PG832','PG2126')")]:code=code.replace(old,new)
    ns={**original.__dict__,'TOOLS':TOOLS,'SAVE':SAVE,'CLASS':CLASS,'BOM':bom,'SOURCE':production(),'completed':lambda digest:completed(digest,before),'method':lambda:role_bind(old_method(),bom),'preflight':lambda:preflight(bom)}
    exec(compile(code,'<actual normal candidate RO factory>','exec'),ns)
    result=ns['sources']()
    result={name.replace('Pg2144','Pg2152'):body.replace('Pg2144','Pg2152').replace('pg2152-current-normal-unused-tools-v1',TOOLS)for name,body in result.items()}
    if CURRENT_BOM not in '\n'.join(result.values()):raise ValueError('old current tuple must remain separately sealed')
    for body in result.values():
        if "'SuccessExitStatus': ''"in body:raise ValueError('obsolete warning setting forbidden')
    return result
