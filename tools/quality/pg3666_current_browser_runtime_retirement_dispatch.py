"""One exact existing runtime file retire/reload, no starts/stops/business writes."""
import inspect
import pg3038_current_runtime_retirement_dispatch as engine
import pg3604_current_browser_owned_dispatch as owned
from pg3662_current_browser_runtime_retirement_sources import sources,SOURCE,SHA,TOOLS
from pg3606_current_browser_owned_post import payload as stopped_payload

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg3666-current-runtime-retirement-stage-v1'
ARCHIVE='pg3666-'+TOOLS+'.tar'
POST_SLOT='pg3606-current-browser-owned-post-v1'


def bind(raw):
    for old,new in [('pg3034','pg3662'),('Pg3034','Pg3662'),('pg3006','pg3600'),('pg3012','pg3606'),
                    ('pg3008','pg3602'),('pg3036','pg3664'),('pg3038','pg3666'),('pg3039','pg3667'),('pg3041','pg3669')]:raw=raw.replace(old,new)
    return raw


STAGE=owned.stage().replace(owned.ARCHIVE,ARCHIVE).replace(owned.REMOTE,REMOTE).replace(owned.TOOLS,TOOLS).replace('pg3600','pg3662').replace('Pg3600','Pg3662')
PARENT_PREQUAL=bind(engine.PARENT_PREQUAL)


def namespace():
    ns={**engine.__dict__,'previous':owned,'sources':sources,'SOURCE':SOURCE,'SHA':SHA,'TOOLS':TOOLS,
        'GUEST':GUEST,'REMOTE':REMOTE,'ARCHIVE':ARCHIVE,'POST_SLOT':POST_SLOT,'STAGE':STAGE,
        'PARENT_PREQUAL':PARENT_PREQUAL,'stopped_payload':stopped_payload}
    for fn in [engine.context,engine.post_payload,engine.run_source,engine.run_action,engine.main]:
        raw=bind(inspect.getsource(fn))
        raw=raw.replace('pg3606-current-resume-owned-post-v1',POST_SLOT)
        if fn is engine.run_source:
            raw=raw.replace('raw = previous.run_source()',"raw = previous.run_source().replace('pg3602','pg3664').replace('pg3604','pg3666').replace('pg3605','pg3667').replace('pg3607','pg3669').replace('Pg3600','Pg3662')")
        exec(compile(raw,'<closed current exact runtime retirement dispatcher>','exec'),ns)
    return ns


def context():return namespace()['context']()


def run_source():return namespace()['run_source']()


def post_payload():return namespace()['post_payload']()


def main():return namespace()['main']()


if __name__=='__main__':raise SystemExit(main())
