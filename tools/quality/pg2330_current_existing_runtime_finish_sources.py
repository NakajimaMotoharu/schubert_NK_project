"""Existing exact fragment, only reserved normal reload remains; no rewrite/mkdir."""
import inspect
from pyflakes.api import check
import pg2000_existing_runtime_file as existing
import pg2316_current_cold_resume_sources as prior

SOURCE=prior.SOURCE
BOM=prior.BOM
BEFORE='dd7b0c65e624834c708d120c9d7756b54807d6b572fcb36a51a2d712ce001be7'
BASE='/var/lib/pgpt-s1-preservation/pg2328-current-partial-loaded-view-post-v1/after.private.json'
TOOLS='pg2330-current-existing-runtime-finish-tools-v1'
SAVE='pg2334-current-existing-runtime-finish-v1'
CLASS='Pg2330ExistingRuntimeFinish'


def bind(raw):
    return raw.replace(prior.TOOLS,TOOLS).replace(prior.SAVE,SAVE).replace('Pg2316FreshResumePreparation',CLASS).replace('pg2316_native','pg2330_native').replace('pg2316_input','pg2330_input').replace('pg2316_configuration','pg2330_configuration').replace('pg2316_durable','pg2330_durable').replace('pg2316_warning','pg2330_warning').replace('pg2316_parent','pg2330_parent').replace('pg2316_row','pg2330_row').replace('pg2316_stable','pg2330_stable').replace('pg2316_resume_contract','pg2330_resume_contract').replace('Pg2316','Pg2330').replace('PG2316','PG2330').replace('prepare-resume','finish-runtime').replace(prior.BEFORE,BEFORE).replace('pg2274-native-stop-v1/after.private.json','pg2328-current-partial-loaded-view-post-v1/after.private.json')


def existing_source():
    raw=inspect.getsource(existing)
    raw=raw.replace('zz-pg1980-once-resume.conf','zz-pg2316-once-resume.conf')
    raw=raw.replace('28,15250','28,4224').replace('28,5514','28,4223').replace('1791850609774873609','1791913648316105696').replace('1791850609774000000','1791913648316105696')
    return raw.replace('78f1488383951e0fc2716bcf63ab41f75c64e975440e7f5e079fd6129f8612ec','888ee8561e9c25da302470c2561cdbf65cbf10cdebf668f7196f27b485bc5035')


def one(raw,old,new):
    if raw.count(old)!=1:raise ValueError('one exact current existing-runtime boundary required')
    return raw.replace(old,new)


def sources():
    result={bind(name):bind(raw)for name,raw in prior.sources().items()}
    raw=result['pg2330_native_refs.py']
    raw=one(raw,'import pg2316_runtime_writer as runtime','import pg2330_existing_runtime as existing_runtime')
    raw=one(raw,'import pg2330_resume_contract as resume_contract\n','')
    start=raw.index('    runtime_root=');end=raw.index('    def capture_data(',start)
    raw=raw[:start]+'    pinned_runtime=existing_runtime.ExistingRuntime(SAVE)\n\n'+raw[end:]
    for key in ['rows','configuration','extraDurable','unitFilesActual']:
        raw=raw.replace("json.loads(original)['"+key+"']","json.loads(original)['before']['"+key+"']")
    # Both before and after views already expose the exact file declaration due to GC/LoadUnit.
    # A normal explicit reload is still mandatory; no duplicate --resume delta is expected.
    start=raw.index('        if placed:\n',raw.index('    def capture_data('))
    end=raw.index('        durable =',start)
    raw=raw[:start]+"        for u,v in cfg.items():require(config_same(signed_cfg[u],v,exec_record))\n"+raw[end:]
    start=raw.index('    def check_data(now):');end=raw.index('    def save(',start)
    raw=raw[:start]+CHECK+raw[end:]
    raw=one(raw,'prior = json.loads(baseline)',"prior = json.loads(baseline)['before']")
    start=raw.index("        if action == 'prepare':");end=raw.index("        if action in ['terminal', 'release']:",start)
    raw=raw[:start]+"        if action=='finish':\n            require(not placed);pinned_runtime.reload();placed=True\n            check_data(capture_data(True))\n"+raw[end:]
    raw=one(raw,'            bus.close()','            pinned_runtime.close();bus.close()')
    result['pg2330_native_refs.py']=raw
    result['pg2330_native_owned_stop.py']=result['pg2330_native_owned_stop.py'].replace("'prepare'","'finish'")
    java=result[CLASS+'.java']
    java=one(java,'"prepare".equals(name)','"finish".equals(name)')
    java=one(java,'phase="FINITE_FRESH_RESUME_PREPARATION";refs.check("prepare");','phase="ONLY_EXISTING_RUNTIME_RELOAD";refs.check("finish");')
    result[CLASS+'.java']=java
    del result['pg2316_runtime_writer.py']
    result['pg2330_existing_runtime.py']=existing_source()
    for name,body in result.items():
        if name.endswith('.py'):
            if check(body,'<current existing runtime '+name+'>'):raise ValueError('all finish-source globals required')
            compile(body,'<current existing runtime>','exec')
    return result


CHECK=r'''
    def check_data(now):
        require(first is not None and set(now)==set(first)and same_value(now,first))
        pinned_runtime.verify()
        for u in UNITS:
            require(h.terminal(show(u,FIELDS)));h.kernel_empty(u)

'''
