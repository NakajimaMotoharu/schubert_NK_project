"""New owner, same already published file; only missing normal runtime reload remains."""
import inspect
import pg1980_fresh_completed_resume_sources as prior
import pg2000_existing_runtime_file as existing
from pg1877_warning_publication_sources import once

TOOLS='pg2001-existing-runtime-tools-v1'
SAVE='pg2005-existing-runtime-finish-v1'
CLASS='Pg2001ExistingRuntimeFinish'
BOM=prior.BOM
BEFORE='b3bb209b57ca297b43d5b1fc78e191fcef2dbbf1c9e1645c445b212291a202fe'


def bind(raw):
    return raw.replace(prior.TOOLS,TOOLS).replace(prior.SAVE,SAVE).replace(prior.CLASS,CLASS).replace('pg1980_native','pg2001_native').replace('pg1980_input','pg2001_input').replace('pg1980_configuration','pg2001_configuration').replace('pg1980_durable','pg2001_durable').replace('pg1980_warning','pg2001_warning').replace('pg1980_parent','pg2001_parent').replace('pg1980_row','pg2001_row').replace('pg1980_stable','pg2001_stable').replace('pg1980_resume_contract','pg2001_resume_contract').replace('Pg1980','Pg2001').replace('PG1980','PG2001').replace('prepare-resume','finish-runtime').replace(prior.BEFORE,BEFORE).replace('pg1963-reload-ref-scoped-full-post-v1','pg1995-partial-runtime-recovery-full-post-v1')


def sources():
    result={bind(n):bind(r)for n,r in prior.sources().items()}
    raw=result['pg2001_native_refs.py']
    raw=once(raw,'import pg1980_runtime_writer as runtime','import pg2001_existing_runtime as existing_runtime')
    start=raw.index('    runtime_root=');end=raw.index('    def capture_data(',start)
    raw=raw[:start]+'    pinned_runtime=existing_runtime.ExistingRuntime(SAVE)\n\n'+raw[end:]
    start=raw.index('    def check_data(now):');end=raw.index('    def save(',start)
    raw=raw[:start]+CHECK+raw[end:]
    start=raw.index("        if action == 'prepare':");end=raw.index("        if action in ['terminal', 'release']:",start)
    raw=raw[:start]+"        if action == 'finish':\n            require(not placed);pinned_runtime.reload();placed=True\n            check_data(capture_data(True))\n"+raw[end:]
    raw=once(raw,'            bus.close()','            pinned_runtime.close();bus.close()')
    result['pg2001_native_refs.py']=raw
    result['pg2001_native_owned_stop.py']=result['pg2001_native_owned_stop.py'].replace("'prepare'","'finish'")
    j=result[CLASS+'.java'];j=once(j,'"prepare".equals(name)','"finish".equals(name)')
    j=once(j,'phase="FINITE_FRESH_RESUME_PREPARATION";refs.check("prepare");','phase="ONLY_EXISTING_RUNTIME_RELOAD";refs.check("finish");')
    result[CLASS+'.java']=j
    del result['pg1980_runtime_writer.py']
    result['pg2001_existing_runtime.py']=inspect.getsource(existing)
    return result


CHECK=r'''
    def check_data(now):
        require(first is not None and set(now)==set(first))
        if not placed:require(same_value(now,first))
        else:
            require(all(same_value(now[k],first[k])for k in first if k!='configuration'))
            require(resume_contract.configuration(first['configuration'],now['configuration'],exec_record,config_same))
        pinned_runtime.verify()

'''
