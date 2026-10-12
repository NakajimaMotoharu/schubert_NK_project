"""New-only immutable tool stage; no service/permission/epoch changes."""
import inspect
import pg1446_current_cold_stage as prior
from pg1512_original_component_profile_sources import TOOLS

def main():
 raw=inspect.getsource(prior.main)
 for a,b in [('pg1446-cold-stage-v1','pg1513-original-component-stage-v1'),('pg1444-current-cold-frozen-v2.safe.json','pg1512-original-component-frozen-v1.safe.json'),('pg1441-current-cold-tools-v1',TOOLS),('PG1446-current-cold-stage-v1','PG1513-original-component-stage-v1')]:
  assert a in raw;raw=raw.replace(a,b)
 ns={**prior.__dict__,'OUT':prior.W/'pg1513-original-component-stage-v1','TOOLS':prior.W/TOOLS}
 exec(compile(raw,'<new readonly stage>','exec'),ns);return ns['main']()
if __name__=='__main__':raise SystemExit(main())
