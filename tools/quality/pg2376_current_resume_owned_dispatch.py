"""Distinct current-generation immutable stage and once owned stop, never Root replay."""
import json
import types
import pg2276_current_signed_owned_dispatch as previous
from pg2374_current_resume_owned_sources import sources,context,SOURCE,TOOLS,BOM
from pg2368_current_resume_full_seal import payload
from pg1446_current_cold_stage import W

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg2376-fixed-stage-v1'
ARCHIVE='pg2376-'+TOOLS+'.tar'
STAGE=previous.STAGE.replace(previous.ARCHIVE,ARCHIVE).replace(previous.REMOTE,REMOTE).replace(previous.TOOLS,TOOLS).replace('pg2274','pg2374').replace('Pg2274','Pg2374').replace('pg2276','pg2376').replace('PG2276','PG2376')
PARENT_PREQUAL=previous.PARENT_PREQUAL.replace('pg2274','pg2374')
POST_SLOT='pg2368-current-resume-full-seal-v1'


def post_payload():
    live=json.loads((W/'pg2362-current-resume-live-binding-v1/manifest.safe.json').read_bytes())
    if live['actualExit']!=0 or live['productionSource']!=SOURCE:raise ValueError('current actual live tuple required')
    return payload({**live['binding'],'rootPid':live['rootPid']})


def run_source():
    return previous.run_source().replace('pg2276','pg2376').replace('pg2275','pg2375').replace('pg2277','pg2377').replace('pg2278','pg2378').replace('Pg2274','Pg2374')


def run_action(action):
    base=previous.prior.prior.prior.prior.runner
    ns={**base.__dict__,'GUEST':GUEST,'REMOTE':REMOTE,'ARCHIVE':ARCHIVE,'STAGE':STAGE,'PARENT_PREQUAL':PARENT_PREQUAL,'sources':sources,'context':context,'SOURCE':SOURCE,'TOOLS':TOOLS,'BOM':BOM,'POST_SLOT':POST_SLOT,'post_payload':post_payload}
    exec(compile(run_source(),'<current once owned dispatch>','exec'),ns);return ns['run_action'](action)


def main():
    base=previous.prior.prior.prior.prior
    fn=types.FunctionType(base.main.__code__,{**base.__dict__,'run_action':run_action});return fn()


if __name__=='__main__':raise SystemExit(main())
