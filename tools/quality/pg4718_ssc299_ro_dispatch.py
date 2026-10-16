"""Explicit normal RO action, direct actual entry selectors and one gate."""
import inspect
import sys
import pg3998_literal_invariant_ro_dispatch as old
import pg4714_ssc299_ro_sources as role
from pg4716_ssc299_ro_compile import TARGET,generated
from pg4434_current_candidate_admission_read import authenticate_host

GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
REMOTE='/home/ubuntu/pg4718-fixed-stage-v1'
STAGE=role.bind(old.previous.template.STAGE)


def entry_source():
    raw=inspect.getsource(old.previous.main)
    for before,after in [('pg3784','pg4718'),('pg3782','pg4716'),('Pg3780','Pg4714'),('PG3420','PG4432')]:
        raw=raw.replace(before,after)
    return raw


def main():
    if sys.argv[1:] not in [['stage'],['prepare-ro']]:raise ValueError('exact RO stage/prepare action only')
    authenticate_host()
    ns={**vars(old.previous),'__file__':__file__,'role':role,'TARGET':TARGET,'generated':generated,
        'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE}
    exec(compile(entry_source(),'<direct normal RO action selector>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
