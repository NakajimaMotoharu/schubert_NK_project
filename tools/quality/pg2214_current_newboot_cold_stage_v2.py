"""BUG1218/YKT985: whole immutable stage bound to actual current frozen source."""
import inspect
import pg1446_current_cold_stage as prior
from pg2208_current_newboot_cold_sources import TOOLS,BOOT,SOURCE,qualify_before


def source():
    raw=inspect.getsource(prior.main)
    for old,new in [('pg1444-current-cold-frozen-v2.safe.json','pg2209-current-newboot-cold-frozen-v1.safe.json'),
      ('pg1446','pg2214'),('PG1446','PG2214'),('pg1441-current-cold-tools-v1',TOOLS),
      ('3d69f5af-6bac-46b1-a540-7591c4a79a0d',BOOT),
      ('769ddb15cd735c25fef581b5f9850ef9d0053c0f',SOURCE)]:
        if old not in raw:raise ValueError('explicit whole immutable stage role required '+old)
        raw=raw.replace(old,new)
    compile(raw,'<whole corrected newboot stage>','exec');return raw


def main():
    qualify_before()
    ns={**prior.__dict__,'OUT':prior.W/'pg2214-current-newboot-cold-stage-v2','TOOLS':prior.W/TOOLS}
    exec(compile(source(),'<whole corrected current stage>','exec'),ns);ns['main']();return 0


if __name__=='__main__':raise SystemExit(main())
