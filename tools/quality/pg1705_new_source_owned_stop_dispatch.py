"""New-only immutable stage/one owned stop after actual newSource complete seal."""
import sys
import pg1611_current_ordinary_owned_stop_dispatch as prior
from pg1703_new_source_owned_stop_sources import sources, context, SOURCE, TOOLS

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS


def rebind(raw):
    return (raw.replace('1611','1705').replace('1609','1703').replace('1610','1704')
            .replace('1612-current-ordinary-stop-preflight-v1','1706-new-source-stop-preflight-v1')
            .replace('pg1703-current-ordinary-owned-stop-tools-v1',TOOLS)
            .replace('0.1.0-PG1544','0.1.0-PG1638'))


def main():
    if sys.argv[1:]not in (['stage'],['stop']):raise ValueError('only exact stage/stop allowed')
    before,_,_,_=context()
    ns={**prior.prior.prior.previous.previous.__dict__,'GUEST':GUEST,'STAGE':rebind(prior.STAGE),
        'sources':sources,'SOURCE':SOURCE,'BEFORE':before}
    exec(compile(rebind(prior.source()),'<new Source once owned stop transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
