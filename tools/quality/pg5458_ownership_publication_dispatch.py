"""One finite stage/activate, exact new296 tool kind and fresh original/current ownership."""
import inspect
import sys
import pg5012_ssc304_publication_dispatch as previous
import pg5454_ownership_publication_sources as role
from pg5456_ownership_publication_compile import TARGET,generated
from pg4996_resume_connection import authenticate_host

GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
REMOTE='/home/ubuntu/pg5458-ownership-publication-stage-v1'
STAGE=role.ro.unused.normalized_text(previous.STAGE)
STAGE=(STAGE.replace(previous.GUEST,GUEST).replace(previous.REMOTE,REMOTE)
    .replace('pg5008-ssc304-publication-tools-v1.tar',role.TOOLS+'.tar'))


def qualify_fixed(fixed):
    if type(fixed.get('actualExit'))is not int:raise ValueError('actual int fixed qualification')
    template=previous.previous.previous.previous
    ns={**vars(template),'role':role}
    raw=inspect.getsource(template.qualify_fixed)
    for old,new in(('Pg3788','Pg5454'),('pg3788','pg5454'),('Pg3780','Pg5446'),('pg3780','pg5446')):
        raw=raw.replace(old,new)
    exec(compile(raw,'<exact296 finite target/bound graph>','exec'),ns)
    return ns['qualify_fixed'](fixed)


def source():
    raw=previous.source()
    for old,new in(('pg5012','pg5458'),('pg5010','pg5456'),('Pg5008','Pg5454'),('PG4860','PG4980')):
        raw=raw.replace(old,new)
    return raw


def main():
    if sys.argv[1:]not in(['stage'],['activate']):raise ValueError('one finite explicit stage/activate only')
    authenticate_host()
    ns={**vars(previous.previous.previous.previous.previous),'__file__':__file__,'role':role,'TARGET':TARGET,
        'generated':generated,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'qualify_fixed':qualify_fixed}
    exec(compile(source(),'<actualA2 finite296 publication>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
