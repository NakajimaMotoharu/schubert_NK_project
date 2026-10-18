"""One new RO stage or prepare-ro, no publication/start/old authority transfer."""
import sys
import pg5004_ssc304_ro_dispatch as previous
import pg5446_ownership_ro_sources as role
from pg5448_ownership_ro_compile import TARGET,generated
from pg4996_resume_connection import authenticate_host

GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
REMOTE='/home/ubuntu/pg5450-fixed-stage-v1'
STAGE=(previous.STAGE.replace(previous.GUEST,GUEST).replace(previous.REMOTE,REMOTE)
    .replace('0.1.0-PG4860','0.1.0-PG4980')
    .replace('pg5000-ssc304-ro-tools-v1.retry2.tar','pg5446-ownership-ro-tools-v1.tar'))


def entry_source():
    raw=previous.entry_source()
    for old,new in(('pg5004','pg5450'),('pg5002','pg5448'),('Pg5000','Pg5446'),('PG4860','PG4980')):
        raw=raw.replace(old,new)
    raw=raw.replace("archive=P/(role.TOOLS+'.retry2.tar')","archive=P/(role.TOOLS+'.tar')")
    return raw.replace("('pg5450-'+action+'-v2')","('pg5450-'+action+'-v1')").replace('pg5450-stage-v2.exit','pg5450-stage-v1.exit')


def main():
    if sys.argv[1:]not in(['stage'],['prepare-ro']):raise ValueError('explicit RO stage/prepare only')
    authenticate_host()
    ns={**vars(previous.previous.previous.previous),'__file__':__file__,'role':role,'TARGET':TARGET,
        'generated':generated,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE}
    exec(compile(entry_source(),'<currentA2 candidate296 RO>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
