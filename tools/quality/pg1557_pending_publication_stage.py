"""New-only immutable tool stage; no publication/runtime authority."""
import inspect
import pg1513_original_component_stage as prior
from pg1553_pending_publication_java import TOOLS

def main():
    raw=inspect.getsource(prior.main).replace('pg1513-original-component-stage-v1','pg1557-pending-publication-stage-v1').replace('PG1513-original-component-stage-v1','PG1557-pending-publication-stage-v1').replace('pg1512-original-component-frozen-v1.safe.json','pg1555-pending-publication-frozen-v1.safe.json')
    ns={**prior.__dict__,'TOOLS':TOOLS};exec(compile(raw,'<new-only partial publication tools stage>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())
