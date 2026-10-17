"""One explicit stage or prepare-ro action; no publication or business start."""
import inspect
import sys
import pg3998_literal_invariant_ro_dispatch as previous
import pg4872_ssc301_302_ro_sources as role
from pg4874_ssc301_302_ro_compile import TARGET,generated
from pg4434_current_candidate_admission_read import authenticate_host

GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
REMOTE='/home/ubuntu/pg4876-fixed-stage-v1'
STAGE=role.bind(previous.previous.template.STAGE)


def entry_source():
    raw=inspect.getsource(previous.previous.main)
    for a,b in [('pg3784','pg4876'),('pg3782','pg4874'),('Pg3780','Pg4872'),('PG3420','PG4702')]:raw=raw.replace(a,b)
    return raw


def main():
    if sys.argv[1:] not in (['stage'],['prepare-ro']):raise ValueError('one RO stage/prepare only')
    authenticate_host()
    ns={**vars(previous.previous),'__file__':__file__,'role':role,'TARGET':TARGET,'generated':generated,
        'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE}
    exec(compile(entry_source(),'<actual current825e RO selectors>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
