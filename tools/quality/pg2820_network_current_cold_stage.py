"""New-only immutable cold helper stage; no prepare/issuer/application start."""
import inspect
import pg1446_current_cold_stage as prior
from pg2816_network_current_cold_sources import TOOLS,BOOT,SOURCE,qualify_before


def source():
    raw=inspect.getsource(prior.main)
    for a,b in [('pg1444-current-cold-frozen-v2.safe.json','pg2818-network-current-cold-frozen-v1.safe.json'),
      ('pg1446','pg2820'),('PG1446','PG2820'),('pg1441-current-cold-tools-v1',TOOLS),
      ('3d69f5af-6bac-46b1-a540-7591c4a79a0d',BOOT),('769ddb15cd735c25fef581b5f9850ef9d0053c0f',SOURCE)]:
        if a not in raw:raise ValueError('whole immutable currentboot stage binding required')
        raw=raw.replace(a,b)
    compile(raw,'<current boot immutable newonly stage>','exec');return raw


def main():
    qualify_before();ns={**prior.__dict__,'OUT':prior.W/'pg2820-network-current-cold-stage-v1','TOOLS':prior.W/TOOLS}
    exec(compile(source(),'<current cold stage no execution permission>','exec'),ns);ns['main']();return 0


if __name__=='__main__':raise SystemExit(main())
