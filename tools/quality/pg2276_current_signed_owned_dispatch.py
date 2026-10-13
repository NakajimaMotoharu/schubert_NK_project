"""New-only post-recovery current stop; no Root/Backup/start/reload replay."""
import types
import pg2266_newboot_owned_dispatch_v2 as prior
from pg2274_current_signed_owned_sources import sources,context,SOURCE,TOOLS,BOM

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg2276-fixed-stage-v1'
ARCHIVE='pg2276-'+TOOLS+'.tar'
STAGE=prior.STAGE.replace(prior.ARCHIVE,ARCHIVE).replace(prior.REMOTE,REMOTE).replace(prior.prior.TOOLS,TOOLS).replace('pg2246','pg2274').replace('Pg2246','Pg2274').replace('pg2266','pg2276').replace('PG2266','PG2276')
PARENT_PREQUAL=prior.prior.PARENT_PREQUAL.replace('pg2246','pg2274')


def run_source():
    return prior.run_source().replace('pg2266','pg2276').replace('pg2247','pg2275').replace('pg2249','pg2277').replace('pg2250','pg2278').replace('Pg2246','Pg2274')


def run_action(action):
    ns={**prior.prior.prior.prior.runner.__dict__,'GUEST':GUEST,'REMOTE':REMOTE,'ARCHIVE':ARCHIVE,'STAGE':STAGE,'PARENT_PREQUAL':PARENT_PREQUAL,'sources':sources,'context':context,'SOURCE':SOURCE,'TOOLS':TOOLS,'BOM':BOM,'POST_SLOT':prior.prior.POST_SLOT,'post_payload':prior.prior.post_payload}
    exec(compile(run_source(),'<corrected actual current once owned dispatch>','exec'),ns);return ns['run_action'](action)


def main():
    fn=types.FunctionType(prior.prior.prior.prior.main.__code__,{**prior.prior.prior.prior.__dict__,'run_action':run_action})
    return fn()


if __name__=='__main__':raise SystemExit(main())
