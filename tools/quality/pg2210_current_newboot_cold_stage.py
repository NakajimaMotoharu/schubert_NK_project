"""New immutable root-private tools stage after actual current ABI; no permission."""
import inspect
import pg1446_current_cold_stage as prior
from pg2208_current_newboot_cold_sources import TOOLS,BOOT,qualify_before


def main():
    qualify_before();raw=inspect.getsource(prior.main)
    for old,new in [('pg1444-current-cold-frozen-v2.safe.json','pg2209-current-newboot-cold-frozen-v1.safe.json'),
      ('pg1446','pg2210'),('PG1446','PG2210'),('pg1441-current-cold-tools-v1',TOOLS),
      ('3d69f5af-6bac-46b1-a540-7591c4a79a0d',BOOT)]:
        if old not in raw:raise ValueError('explicit current immutable stage required '+old)
        raw=raw.replace(old,new)
    ns={**prior.__dict__,'OUT':prior.W/'pg2210-current-newboot-cold-stage-v1','TOOLS':prior.W/TOOLS}
    exec(compile(raw,'<newboot immutable cold stage>','exec'),ns);ns['main']();return 0


if __name__=='__main__':raise SystemExit(main())
