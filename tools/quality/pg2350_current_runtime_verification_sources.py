"""SSC284 new normal M/A/DB/Ref verification only; no file write/reload/start."""
from pyflakes.api import check
import pg2330_current_existing_runtime_finish_sources as prior

SOURCE=prior.SOURCE
BOM=prior.BOM
BEFORE='312f9fc3291bd6a1b087b7de8ac452a6b665105583501c96bea49c9fa958efbe'
TOOLS='pg2350-current-runtime-verification-tools-v1'
SAVE='pg2354-current-runtime-verification-v1'
CLASS='Pg2350RuntimeVerification'


def bind(raw):
    return raw.replace(prior.TOOLS,TOOLS).replace(prior.SAVE,SAVE).replace(prior.CLASS,CLASS).replace('Pg2330','Pg2350').replace('PG2330','PG2350').replace('pg2330','pg2350').replace('finish-runtime','verify-runtime').replace(prior.BEFORE,BEFORE).replace('pg2328-current-partial-loaded-view-post-v1/after.private.json','pg2348-current-reloaded-recovery-post-v1/after.private.json')


def sources():
    values={bind(n):bind(raw)for n,raw in prior.sources().items()}
    io=values['pg2350_existing_runtime.py']
    start=io.index('    def reload(self):');end=io.index('    def close(self):',start)
    io=io[:start]+"    def confirm(self):\n        require(not self.reloaded);self.verify();self.reloaded=True\n\n"+io[end:]
    values['pg2350_existing_runtime.py']=io.replace('import subprocess\n','')
    refs=values['pg2350_native_refs.py']
    refs=prior.one(refs,'pinned_runtime.reload();placed=True','pinned_runtime.confirm();placed=True')
    refs=refs.replace("if action=='finish':","if action=='verify':")
    values['pg2350_native_refs.py']=refs
    values['pg2350_native_owned_stop.py']=values['pg2350_native_owned_stop.py'].replace("'finish'","'verify'")
    java=values[CLASS+'.java']
    java=prior.one(java,'"finish".equals(name)','"verify".equals(name)')
    java=prior.one(java,'phase="ONLY_EXISTING_RUNTIME_RELOAD";refs.check("finish");','phase="VERIFICATION_ONLY_CURRENT_RUNTIME";refs.check("verify");')
    java=prior.one(java,'freshResumeRuntimePrepared=true\\nnormalSingleRuntimeReload=true\\n','freshResumeRuntimePrepared=false\\nnormalSingleRuntimeReload=false\\nverificationOnlyNormalScope=true\\n')
    values[CLASS+'.java']=java
    for name,raw in values.items():
        if name.endswith('.py'):
            if check(raw,'<current verification only '+name+'>'):raise ValueError('all verification globals required')
            compile(raw,'<current verification only>','exec')
    return values
