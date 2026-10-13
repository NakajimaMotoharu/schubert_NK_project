"""One explicit owned finite current cold preparation, not Root/Backup/ADMIN."""
import inspect
import pg1450_current_cold_retry as prior
from pg2208_current_newboot_cold_sources import TOOLS,BOOT,qualify_before


def source():
    raw=inspect.getsource(prior.prepare)
    raw=raw.replace('qualified_handoff()','qualify_before()')
    raw=raw.replace('PG1452-current-cold-owned-prepare-v1','PG2212-current-newboot-cold-owned-prepare-v1')
    for old,new in [('pg1451-current-cold-stage-v1','pg2214-current-newboot-cold-stage-v2'),
      ('pg1452-current-cold-owned-prepare-v1','pg2212-current-newboot-cold-owned-prepare-v1'),
      ('pg1450-current-cold-tools-v1',TOOLS),('pg1452-current-cold-prepared-v1','pg2212-current-newboot-cold-prepared-v1'),
      ('3d69f5af-6bac-46b1-a540-7591c4a79a0d',BOOT),('Pg1450CurrentColdPreparation','Pg2208CurrentColdPreparation'),
      ('0.1.0-PG1292','0.1.0-PG2126')]:
        if old not in raw:raise ValueError('explicit current preparation tuple required '+old)
        raw=raw.replace(old,new)
    # No assertion about an old PID: the new complete cold/kernel/DB proof owns
    # admission. Never treat a recycled old boot PID as a current owner.
    old="require(not pathlib.Path('/proc/3323').exists())\n"
    if raw.count(old)!=1:raise ValueError('one obsolete oldboot PID guard required')
    raw=raw.replace(old,'')
    compile(raw,'<newboot current cold prepare dispatch>','exec');return raw


def main():
    ns={**prior.__dict__,'qualify_before':qualify_before,'FROZEN':prior.W/'pg2209-current-newboot-cold-frozen-v1.safe.json'}
    exec(compile(source(),'<one owned finite preparation>','exec'),ns);return ns['prepare']()


if __name__=='__main__':raise SystemExit(main())
