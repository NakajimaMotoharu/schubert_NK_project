"""One finite stage/activate; no ordinary start or old authority transfer."""
import inspect
import sys
import pg5458_ownership_publication_dispatch as previous
import pg5624_current_publication_sources as role
from pg5626_current_publication_compile import TARGET,generated
from pg4996_resume_connection import authenticate_host

GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
REMOTE='/home/ubuntu/pg5628-current-publication-stage-v1'
STAGE=(previous.STAGE.replace(previous.GUEST,GUEST).replace(previous.REMOTE,REMOTE)
    .replace('pg5454-ownership-publication-tools-v1.tar',role.TOOLS+'.tar').replace('0.1.0-PG4980','0.1.0-PG5430'))


def qualify_fixed(fixed):
    if type(fixed.get('actualExit'))is not int:raise ValueError('actual integer fixed qualification required')
    template=previous.previous.previous.previous.previous
    scope={**vars(template),'role':role}
    raw=inspect.getsource(template.qualify_fixed)
    for old,new in(('Pg3788','Pg5624'),('pg3788','pg5624'),('Pg3780','Pg5616'),('pg3780','pg5616')):raw=raw.replace(old,new)
    exec(compile(raw,'<exact0ea finite graph/target binding>','exec'),scope)
    return scope['qualify_fixed'](fixed)


def source():
    raw=previous.source()
    for old,new in(('pg5458','pg5628'),('pg5456','pg5626'),('Pg5454','Pg5624'),('PG4980','PG5430')):raw=raw.replace(old,new)
    return raw


def namespace():
    return{**vars(previous.previous.previous.previous.previous.previous),'__file__':__file__,'role':role,'TARGET':TARGET,
      'generated':generated,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'qualify_fixed':qualify_fixed}


def main():
    if sys.argv[1:]not in(['stage'],['activate']):raise ValueError('one finite explicit stage/activate only')
    from pg5630_current_publication_post import payload
    payload()  # Actual frozen24 hashes must compose the independent post BEFORE mutation.
    authenticate_host();scope=namespace()
    exec(compile(source(),'<finite code-only0ea publication>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
