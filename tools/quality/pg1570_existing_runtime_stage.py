"""New-only immutable verify-only tools; no runtime preparation/reload."""
import inspect
import pg1446_current_cold_stage as prior
from pg1567_existing_runtime_sources import TOOLS
from pg1568_existing_runtime_compile import valid_frozen
from pg1559_pending_runtime_sources import SOURCE

def main():
    if not valid_frozen(prior.json.loads((prior.W/'pg1568-existing-runtime-frozen-v1.safe.json').read_bytes())):raise ValueError('actual exact verify-only source/run/phases required')
    raw=inspect.getsource(prior.main)
    for a,b in [('pg1446-cold-stage-v1','pg1570-existing-runtime-stage-v1'),('PG1446-current-cold-stage-v1','PG1570-existing-runtime-stage-v1'),('pg1444-current-cold-frozen-v2.safe.json','pg1568-existing-runtime-frozen-v1.safe.json'),('pg1441-current-cold-tools-v1',TOOLS),('769ddb15cd735c25fef581b5f9850ef9d0053c0f',SOURCE)]:
        if a not in raw:raise ValueError('fixed verify-only tool stage boundary refused')
        raw=raw.replace(a,b)
    ns={**prior.__dict__,'OUT':prior.W/'pg1570-existing-runtime-stage-v1','TOOLS':prior.W/TOOLS};exec(compile(raw,'<new immutable verify-only tools stage>','exec'),ns);return ns['main']()

if __name__=='__main__':raise SystemExit(main())
