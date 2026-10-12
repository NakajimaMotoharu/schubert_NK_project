"""New-only immutable stage, then single current owned stop (never Root start)."""
import sys
import pg1705_new_source_owned_stop_dispatch as prior
from pg1772_warning_owned_stop_sources import sources,context,SOURCE,TOOLS

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS


def rebind(raw):
    return prior.rebind(raw).replace('1705','1774').replace('1703','1772').replace('1704','1773').replace('1706-new-source-stop-preflight-v1','1775-warning-stop-preflight-v1').replace('pg1772-new-source-owned-stop-tools-v1',TOOLS)


def main():
    if sys.argv[1:]not in (['stage'],['stop']):raise ValueError('only fixed stage/stop required')
    before,_,_,_=context()
    ns={**prior.prior.prior.prior.previous.previous.__dict__,'GUEST':GUEST,'STAGE':rebind(prior.prior.STAGE),'sources':sources,'SOURCE':SOURCE,'BEFORE':before}
    exec(compile(rebind(prior.prior.source()),'<single warning-owned stop transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
