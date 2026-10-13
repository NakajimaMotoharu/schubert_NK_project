"""Current normal-completed old/new source roles for UNUSED placement, no operator entry."""
import re
from pg1860_warning_actual_graph_sources import sources as previous
from pg2090_current_newrun_owned_stop_sources import receipt_source,projection_source
from pg2124_metadata_boundary_full_six import production

CURRENT='0fd734195b4d5338f6b7e860e087cce561d49562'
OLD_CURRENT='2741c4546afad6c1e8b6efbd53dfb58144edf7bb'
CURRENT_BOM='ee75d0cd61457462eca59e67f5af2d8e677427071514940f3fb594ba93a026d7'
BEFORE='75669b01c69e4ecc2459e73dbd3e0a6abcac7cdfaf6ce4095561314d533b1eb4'
TOOLS='pg2132-current-normal-unused-tools-v1'
SAVE='pg2136-current-normal-unused-placement-v1'
ARCHIVE='pg2134-current-normal-release-v1.tar'
REMOTE='/home/ubuntu/pg2134-current-normal-input-v1'

def bind(raw):
    # Separate old-current and new-candidate roles BEFORE either replacement.
    raw=raw.replace(CURRENT,'__CURRENT_NEW_CANDIDATE__').replace(OLD_CURRENT,CURRENT).replace('__CURRENT_NEW_CANDIDATE__',production())
    raw=raw.replace('PG1846','__NEW_RELEASE__').replace('pg1846','__NEW_RELEASE_LOWER__').replace('PG1638','PG1846').replace('pg1638','pg1846').replace('__NEW_RELEASE__','PG2126').replace('__NEW_RELEASE_LOWER__','pg2126')
    pairs=[('195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1',CURRENT_BOM),('pg1849-warning-completed-current-before-v1','pg2130-current-normal-before-v1'),('4148e3e8-f107-431a-ab27-d6e6d1f1772e','a31dd6da-cf4c-4d0f-ab7c-5c8bb59c0b75'),('9adbf05a-61d0-408b-b51d-ab19c7e5b16a','9026b2ab-bb42-49cd-a2bd-4c661049dce3'),('2026-10-12T18:20:32.598894Z','2026-10-13T03:08:18.452473Z'),('2026-10-12T18:46:52.677350Z','2026-10-13T03:35:44.330028Z'),('b5a12ee25dc44ec49b08f5d084b4052f','2c37fef2a2ff48e7b6a05cfc23f84c19'),('pg1860-warning-unused-tools-v1',TOOLS),('pg1864-warning-unused-placement-v1',SAVE),('pg1862-warning-input-v1',REMOTE.rsplit('/',1)[1]),('pg1862-warning-release-v1.tar',ARCHIVE)]
    for old,new in pairs:raw=raw.replace(old,new)
    for old,new in [('81404764713','113070840714'),('83018953880','114755353173'),('389748','588342')]:raw=re.sub(r'\b'+old+r'\b',new,raw)
    for old,new in [('pg1860','pg2132'),('Pg1860','Pg2132'),('PG1860','PG2132'),('pg1864','pg2136'),('PG1864','PG2136'),('pg1862','pg2134'),('PG1862','PG2134')]:raw=raw.replace(old,new)
    return raw

def sources(bom,before=BEFORE):
    if before!=BEFORE or type(bom)is not str or re.fullmatch('[0-9a-f]{64}',bom)is None:
        raise ValueError('current sealed before and new signed BOM required')
    result={}
    for name,body in previous(bom,before).items():
        name=bind(name);raw=bind(body)
        # Use separately qualified current receipt/projection. Never rewrite old negative UUIDs.
        if name=='pg2132_parent_receipt.py':raw=receipt_source()
        elif name=='pg2132_warning_parent_projection.py':raw=projection_source()
        if name=='Pg2132UnusedStage.java':
            raw=raw.replace('genuineParentWarningOriginal=true\\nmanagerFailureRetained=true\\n','genuineParentNormalWarningOriginal=true\\ncurrentManagerGc=true\\n')
        if name.endswith('.py'):
            from pyflakes.api import check
            # These two exact digest declarations are injected by the immutable compiler from
            # the real bundle. This source-factory check is not that final whole-graph gate.
            context="BUNDLE_HASH='pending-real-bundle'\n" if name in {'pg2132_native_refs.py','pg2132_input_preflight.py'} else ''
            if check(context+raw,'<normal unused factory '+name+'>'):raise ValueError('factory exports except exact pending bundle digest required')
            compile(raw,'<actual normal unused helper>','exec')
        result[name]=raw
    if any('__CURRENT_'in raw or '__NEW_RELEASE'in raw for raw in result.values()):raise ValueError('unbound role marker')
    return result

if __name__=='__main__':raise SystemExit('source factory only; no VM operation')
