"""New-only exact used runtime file retire/reload under fresh full normal scopes."""
import inspect
import pg3038_current_runtime_retirement_dispatch as engine
import pg3880_current_resume_owned_dispatch as owned
from pg3902_current_runtime_retirement_sources import sources,SOURCE,SHA,TOOLS
from pg3882_current_resume_owned_post import payload as stopped_payload

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg3906-current-runtime-retirement-stage-v1'
ARCHIVE='pg3906-'+TOOLS+'.tar'
POST_SLOT='pg3882-current-resume-owned-post-v1'


def bind(raw):
    for old,new in [('pg3034','pg3902'),('Pg3034','Pg3902'),('pg3006','pg3876'),('pg3012','pg3882'),
                    ('pg3008','pg3878'),('pg3036','pg3904'),('pg3038','pg3906'),('pg3039','pg3907'),('pg3041','pg3909')]:raw=raw.replace(old,new)
    return raw


STAGE=owned.namespace()['stage']().replace(owned.ARCHIVE,ARCHIVE).replace(owned.REMOTE,REMOTE).replace(owned.role.TOOLS,TOOLS).replace('pg3876','pg3902').replace('Pg3876','Pg3902')
PARENT_PREQUAL=bind(engine.PARENT_PREQUAL)


def namespace():
    values={**engine.__dict__,'previous':owned,'sources':sources,'SOURCE':SOURCE,'SHA':SHA,'TOOLS':TOOLS,
        'GUEST':GUEST,'REMOTE':REMOTE,'ARCHIVE':ARCHIVE,'POST_SLOT':POST_SLOT,'STAGE':STAGE,
        'PARENT_PREQUAL':PARENT_PREQUAL,'stopped_payload':stopped_payload}
    for fn in [engine.context,engine.post_payload,engine.run_source,engine.run_action,engine.main]:
        raw=bind(inspect.getsource(fn)).replace('pg3882-current-resume-owned-post-v1',POST_SLOT)
        if fn is engine.run_source:
            raw=raw.replace('raw = previous.run_source()',"raw = previous.namespace()['run_source']().replace('pg3878','pg3904').replace('pg3880','pg3906').replace('pg3881','pg3907').replace('pg3883','pg3909').replace('Pg3876','Pg3902')")
        exec(compile(raw,'<closed current exact runtime retirement dispatcher>','exec'),values)
    return values


def context():return namespace()['context']()


def run_source():return namespace()['run_source']()


def post_payload():return namespace()['post_payload']()


def main():return namespace()['main']()


if __name__=='__main__':raise SystemExit(main())
