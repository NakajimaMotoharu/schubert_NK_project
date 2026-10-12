"""New immutable verify-only source. Preserve previous actual prepared/failed source."""
import inspect
import pg1560_pending_runtime_compile as prior
from pg1567_existing_runtime_sources import CLASS,TOOLS,java,refs

def compiler_source():
    raw=prior.compiler_source()
    for a,b in [('pg1560-pending-runtime-build-v2','pg1568-existing-runtime-build-v1'),('pg1560-pending-runtime-frozen-v2','pg1568-existing-runtime-frozen-v1'),('PG1560-pending-runtime-frozen-v2','PG1568-existing-runtime-frozen-v1'),('pg1558-pending-publication-independent-closing-v1/manifest.safe.json','pg1566-retained-runtime-pair-closing-v1/manifest.safe.json'),('pg1559_pending_runtime_refs.py','pg1567_existing_runtime_refs.py'),('Pg1560RuntimeArgumentTest','Pg1568RuntimeArgumentTest'),('pg1559_pending_runtime_test.py','pg1567_existing_runtime_test.py')]:
        if a not in raw:raise ValueError('fixed verify-only compiler boundary refused')
        raw=raw.replace(a,b)
    return raw.replace(".replace('\"prepare-ro\"','\"prepare\"')", ".replace('\"prepare-ro\"','\"verify-existing\"')")

def valid_frozen(v):
    return type(v)is dict and v.get('run')=='PG1568-existing-runtime-frozen-v1'and v.get('actualExit')==0 and v.get('productionSource')==prior.SOURCE and v.get('helperSource')=='769ddb15cd735c25fef581b5f9850ef9d0053c0f'and type(v.get('phases'))is list and len(v['phases'])==8 and all(p.get('exit')==0 for p in v['phases'])

def main():
    raw=inspect.getsource(prior.main)
    ns={**prior.__dict__,'compiler_source':compiler_source,'CLASS':CLASS,'TOOLS':TOOLS,'java':java,'refs':refs}
    exec(compile(raw,'<fresh normal runtime verification compiler>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
