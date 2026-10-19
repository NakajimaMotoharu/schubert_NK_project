"""One RO stage/prepare only; no finite publication or business start."""
import sys
import pg5450_ownership_ro_dispatch as previous
import pg5616_current_ro_sources as role
from pg5618_current_ro_compile import TARGET,generated
from pg4996_resume_connection import authenticate_host
import pg5622_current_ro_post as post

GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
REMOTE='/home/ubuntu/pg5620-fixed-stage-v1'
STAGE=(previous.STAGE.replace(previous.GUEST,GUEST).replace(previous.REMOTE,REMOTE)
    .replace('0.1.0-PG4980','0.1.0-PG5430').replace('pg5446-ownership-ro-tools-v1.tar','pg5616-current-ro-tools-v1.tar'))


def entry_source():
    raw=previous.entry_source()
    for old,new in(('pg5450','pg5620'),('pg5448','pg5618'),('Pg5446','Pg5616'),('PG4980','PG5430')):raw=raw.replace(old,new)
    return raw


def namespace():
    return{**vars(previous.previous.previous.previous.previous),'__file__':__file__,'role':role,'TARGET':TARGET,
      'generated':generated,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE}


def main():
    if sys.argv[1:]not in(['stage'],['prepare-ro']):raise ValueError('explicit RO stage/prepare only')
    post.payload();authenticate_host();scope=namespace()
    exec(compile(entry_source(),'<current296 candidate0ea RO only>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
