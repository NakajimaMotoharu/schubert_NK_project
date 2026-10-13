"""One owned stop after full current proofs; no Root, deployment or reload replay."""
import json
import types
import pg2376_current_resume_owned_dispatch as prior
from pg2458_question_current_owned_sources import sources,context,SOURCE,TOOLS,BOM
from pg2456_question_current_full_seal import payload
from pg1446_current_cold_stage import W

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg2460-question-owned-stage-v1'
ARCHIVE='pg2460-'+TOOLS+'.tar'
STAGE=prior.STAGE
for a,b in [(prior.ARCHIVE,ARCHIVE),(prior.REMOTE,REMOTE),(prior.TOOLS,TOOLS),
            ('pg2374','pg2458'),('Pg2374','Pg2458'),('pg2376','pg2460'),('PG2376','PG2460'),
            ('PG2126','PG2428'),(prior.SOURCE,SOURCE),(prior.BOM,BOM)]:STAGE=STAGE.replace(a,b)
PARENT_PREQUAL=prior.PARENT_PREQUAL.replace('pg2374','pg2458')
POST_SLOT='pg2456-question-current-full-seal-v1'


def post_payload():
    live=json.loads((W/'pg2450-question-current-live-binding-v1/manifest.safe.json').read_bytes())
    if live['actualExit']!=0 or live['productionSource']!=SOURCE:raise ValueError('actual current source live binding required')
    return payload({**live['binding'],'rootPid':live['rootPid']})


def run_source():
    raw=prior.run_source()
    for a,b in [('pg2376','pg2460'),('pg2375','pg2459'),('pg2377','pg2461'),('pg2378','pg2462'),
                ('Pg2374','Pg2458'),('PG2126','PG2428')]:raw=raw.replace(a,b)
    return raw


def run_action(action):
    base=prior.previous.prior.prior.prior.prior.runner
    ns={**base.__dict__,'GUEST':GUEST,'REMOTE':REMOTE,'ARCHIVE':ARCHIVE,'STAGE':STAGE,
        'PARENT_PREQUAL':PARENT_PREQUAL,'sources':sources,'context':context,'SOURCE':SOURCE,
        'TOOLS':TOOLS,'BOM':BOM,'POST_SLOT':POST_SLOT,'post_payload':post_payload}
    exec(compile(run_source(),'<current new owned stop entry>','exec'),ns);return ns['run_action'](action)


def main():
    base=prior.previous.prior.prior.prior.prior
    return types.FunctionType(base.main.__code__,{**base.__dict__,'run_action':run_action})()


if __name__=='__main__':raise SystemExit(main())
