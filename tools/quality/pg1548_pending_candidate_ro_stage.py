"""New-only immutable candidate RO tools stage, not mount/current/start authority."""
import inspect
import pg1513_original_component_stage as prior
from pg1546_pending_candidate_ro_sources import TOOLS

def main():
    raw=inspect.getsource(prior.main).replace('pg1513-original-component-stage-v1','pg1548-pending-ro-stage-v1').replace('PG1513-original-component-stage-v1','PG1548-pending-ro-stage-v1').replace('pg1512-original-component-frozen-v1.safe.json','pg1547-pending-candidate-ro-frozen-v1.safe.json')
    ns={**prior.__dict__,'TOOLS':TOOLS};exec(compile(raw,'<new-only partial candidate RO tool stage>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())
