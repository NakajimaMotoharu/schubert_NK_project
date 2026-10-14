"""Current a9 graph with proven SSC259260 cold writer/coarse clock, not ancestor fine clock."""
from pyflakes.api import check
import pg2316_current_cold_resume_sources as prior
import pg2942_current_completed_resume_sources as current

SOURCE=current.SOURCE;BOM=current.BOM;BOOT=current.BOOT;BEFORE=current.BEFORE;RUN=current.RUN
TOOLS='pg2950-current-cold-resume-tools-v1'
SAVE='pg2954-current-cold-resume-preparation-v1'
CLASS='Pg2950FreshResumePreparation'


def bind(raw):
    return current.bind(raw).replace(prior.TOOLS,TOOLS).replace(prior.SAVE,SAVE).replace('pg2316','pg2950').replace('Pg2316','Pg2950').replace('PG2316','PG2950').replace(current.TOOLS,TOOLS).replace(current.SAVE,SAVE).replace('pg2942','pg2950').replace('Pg2942','Pg2950').replace('PG2942','PG2950')


def sources():
    values={bind(n):bind(raw)for n,raw in prior.sources().items()}
    proved=current.sources()
    for suffix in ['parent_receipt.py','warning_parent_projection.py','configuration.py','configuration_capture.py','row_bound.py','stable_journal.py']:
        values['pg2950_'+suffix]=bind(proved['pg2942_'+suffix])
    refs=values['pg2950_native_refs.py']
    marker='            mutation_begin_ns=metadata_lower_ns()'
    if refs.count(marker)!=1:raise ValueError('one actual coarse metadata reservation required')
    refs=refs.replace(marker,marker+"\n            durable_save(SAVE,'metadata-clock-lower.private.json',json.dumps({'clockId':5,'lowerNs':mutation_begin_ns,'fallback':False},sort_keys=True).encode())")
    values['pg2950_native_refs.py']=refs
    for name,raw in values.items():
        if name.endswith('.py'):
            if check(raw,'<current coarse clock cold complete '+name+'>'):raise ValueError('complete namespace required')
            compile(raw,'<current cold owner no historic authority>','exec')
        if any(x in raw for x in [prior.SOURCE,prior.BOM,prior.RUN,'b2d6f605','PG2126','pg2316','pg2304']):
            raise ValueError('historical positive authority in final graph: '+name)
    return values
