"""Newsource staged once owned stop, current full proof and normal parent tuple."""
import types
import pg2092_current_newrun_owned_stop_dispatch as prior
from pg2188_newsource_owned_stop_sources import sources,context,SOURCE,TOOLS,BOM
from pg2186_newsource_full_live_seal import payload as full_payload,SLOT as POST_SLOT

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg2190-fixed-stage-v1'
ARCHIVE='pg2190-'+TOOLS+'.tar'
STAGE=prior.STAGE.replace(prior.ARCHIVE,ARCHIVE).replace('pg2092','pg2190').replace('PG2092','PG2190').replace(prior.TOOLS,TOOLS).replace('pg2090','pg2188').replace('Pg2090','Pg2188').replace('PG1846','PG2126').replace('ee75d0cd61457462eca59e67f5af2d8e677427071514940f3fb594ba93a026d7',BOM).replace('0fd734195b4d5338f6b7e860e087cce561d49562',SOURCE)
PARENT_PREQUAL=prior.PARENT_PREQUAL.replace('pg2090','pg2188')


def post_payload():
    v=prior.runner.json.loads((prior.W/'pg2180-newsource-live-binding-v1/manifest.safe.json').read_bytes())
    return full_payload({**v['binding'],'rootPid':v['rootPid']})


def run_source():
    raw=prior.run_source()
    for old,new in [('pg2091','pg2189'),('pg2092','pg2190'),('pg2093','pg2191'),('pg2094-current-newrun-pre-stop-full-v1','pg2192-newsource-pre-stop-full-v1'),('Pg2090','Pg2188'),('PG1846','PG2126')]:raw=raw.replace(old,new)
    return raw


def run_action(action):
    ns={**prior.runner.__dict__,'GUEST':GUEST,'REMOTE':REMOTE,'ARCHIVE':ARCHIVE,'STAGE':STAGE,'PARENT_PREQUAL':PARENT_PREQUAL,'sources':sources,'context':context,'SOURCE':SOURCE,'TOOLS':TOOLS,'W':prior.W,'POST_SLOT':POST_SLOT,'post_payload':post_payload}
    exec(compile(run_source(),'<actual newsource once owned stop entry>','exec'),ns);return ns['run_action'](action)


def main():
    fn=types.FunctionType(prior.main.__code__,{**prior.__dict__,'run_action':run_action})
    return fn()


if __name__=='__main__':raise SystemExit(main())
