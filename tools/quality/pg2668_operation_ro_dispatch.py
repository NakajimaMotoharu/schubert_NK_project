"""New-only candidate RO stage/prepare; no publication/business operation."""
import pg2526_strict_candidate_ro_dispatch as previous
from pg2666_operation_ro_sources import sources,TOOLS,CLASS,bind
from pg2667_operation_ro_compile import TARGET
from pg2658_operation_candidate_sources import CURRENT,BEFORE,production

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS;REMOTE='/home/ubuntu/pg2668-fixed-stage-v1'
STAGE=bind(previous.STAGE).replace('pg2526-fixed-stage-v1','pg2668-fixed-stage-v1')


def source():
    raw=bind(previous.source()).replace('pg2525-frozen','pg2667-frozen').replace('pg2526-','pg2668-').replace('pg2522-current-strict-candidate-post-v1','pg2664-operation-unused-post-v1')
    old="['git','diff','--name-only',CANDIDATE,'--','src','pom.xml']"
    if raw.count(old)!=1:raise ValueError('one complete selected source guard required')
    raw=raw.replace(old,"['git','diff','--name-only','411abb597f15a221acd4c0da4a407a035fcbdd20','HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization']")
    compile(raw,'<new readonly direct body>','exec');return raw


def main():
    engine=previous.previous.prior.prior.prior
    ns={**engine.__dict__,'__file__':__file__,'TARGET':TARGET,'TOOLS':TOOLS,'CLASS':CLASS,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'sources':sources,'CANDIDATE':production(),'OLD':CURRENT,'BEFORE':BEFORE}
    exec(compile(source(),'<new operation readonly dispatch>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
