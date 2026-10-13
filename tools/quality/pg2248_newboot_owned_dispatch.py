"""Once current-boot owned stop, after same-run fullseal, immutable ABI and fresh full proof."""
import types
import pg2190_newsource_owned_stop_dispatch as prior
from pg2246_newboot_owned_sources import sources,context,SOURCE,TOOLS,BOM
from pg2242_newboot_fresh_day_full_seal import payload as full_payload,SLOT as POST_SLOT
from pg2208_current_newboot_cold_sources import BOOT

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg2248-fixed-stage-v1'
ARCHIVE='pg2248-'+TOOLS+'.tar'
STAGE=prior.STAGE.replace(prior.ARCHIVE,ARCHIVE).replace(prior.TOOLS,TOOLS).replace('pg2190','pg2248').replace('PG2190','PG2248').replace('pg2188','pg2246').replace('Pg2188','Pg2246')
STAGE=STAGE.replace('3d69f5af-6bac-46b1-a540-7591c4a79a0d',BOOT)
PARENT_PREQUAL=prior.PARENT_PREQUAL.replace('pg2188','pg2246')


def post_payload():
    from pg1446_current_cold_stage import W
    import json
    live=json.loads((W/'pg2230-newboot-current-live-binding-v1/manifest.safe.json').read_bytes())
    before=json.loads((W/'pg2226-newboot-fresh-day-before-v1/manifest.safe.json').read_bytes())
    oracle=json.loads((W/'pg2238-newboot-before-selectors-v1/manifest.safe.json').read_bytes())
    if any(v['actualExit']!=0 for v in [live,before,oracle]):raise ValueError('actual current fresh tuple required')
    return full_payload({**live['binding'],'rootPid':live['rootPid']},before['guest']['privateBeforeSha256'],oracle['guest']['privateOracleSha256'])


def run_source():
    raw=prior.run_source()
    for old,new in [('pg2189','pg2247'),('pg2190','pg2248'),('pg2191','pg2249'),('pg2192-newsource-pre-stop-full-v1','pg2250-newboot-pre-stop-full-v1'),('Pg2188','Pg2246')]:raw=raw.replace(old,new)
    raw=raw.replace('before, _, _, _ = context()','before, _, done, _ = context()').replace("'currentManagerGc': True","'currentManagerGc': done['currentManagerGc']")
    return raw


def run_action(action):
    ns={**prior.prior.runner.__dict__,'GUEST':GUEST,'REMOTE':REMOTE,'ARCHIVE':ARCHIVE,'STAGE':STAGE,'PARENT_PREQUAL':PARENT_PREQUAL,'sources':sources,'context':context,'SOURCE':SOURCE,'TOOLS':TOOLS,'BOM':BOM,'POST_SLOT':POST_SLOT,'post_payload':post_payload}
    exec(compile(run_source(),'<actual current-boot once owned stop entry>','exec'),ns);return ns['run_action'](action)


def main():
    fn=types.FunctionType(prior.prior.main.__code__,{**prior.prior.__dict__,'run_action':run_action})
    return fn()


if __name__=='__main__':raise SystemExit(main())
