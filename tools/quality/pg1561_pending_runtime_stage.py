"""Immutable SSC270 tool stage, no reload/start/permit."""
import inspect
import pg1446_current_cold_stage as prior
from pg1559_pending_runtime_sources import TOOLS,SOURCE
from pg1560_pending_runtime_compile import valid_frozen

def main():
    if not valid_frozen(prior.json.loads((prior.W/'pg1560-pending-runtime-frozen-v2.safe.json').read_bytes())):raise ValueError('exact actual runtime frozen run/source/phases required')
    raw=inspect.getsource(prior.main)
    for a,b in [('pg1446-cold-stage-v1','pg1561-pending-runtime-stage-v1'),('PG1446-current-cold-stage-v1','PG1561-pending-runtime-stage-v1'),('pg1444-current-cold-frozen-v2.safe.json','pg1560-pending-runtime-frozen-v2.safe.json'),('pg1441-current-cold-tools-v1',TOOLS),('769ddb15cd735c25fef581b5f9850ef9d0053c0f',SOURCE)]:
        if a not in raw:raise ValueError('fixed current source stage boundary refused')
        raw=raw.replace(a,b)
    ns={**prior.__dict__,'OUT':prior.W/'pg1561-pending-runtime-stage-v1','TOOLS':prior.W/TOOLS};exec(compile(raw,'<new current runtime tool stage>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())
