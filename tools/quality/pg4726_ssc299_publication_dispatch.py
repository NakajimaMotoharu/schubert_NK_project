"""Finite stage/activate only, explicit current selectors and fresh ownership."""
import inspect
import sys
import pg4006_literal_invariant_publication_dispatch as old
import pg4722_ssc299_publication_sources as role
from pg4724_ssc299_publication_compile import TARGET,generated
from pg4434_current_candidate_admission_read import authenticate_host

GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
REMOTE='/home/ubuntu/pg4726-ssc299-publication-stage-v1'
STAGE=role.bind(old.previous.template.stage(old.previous.template.role.ro.role.BOM).replace(old.previous.template.REMOTE,REMOTE))


def qualify_fixed(fixed):
    if type(fixed.get('actualExit'))is not int:raise ValueError('actual numeric qualification required')
    ns={**vars(old.previous),'role':role}
    raw=inspect.getsource(old.previous.qualify_fixed)
    for a,b in [('Pg3788','Pg4722'),('pg3788','pg4722'),('Pg3780','Pg4714'),('pg3780','pg4714')]:raw=raw.replace(a,b)
    exec(compile(raw,'<exact finite publication target kind>','exec'),ns)
    return ns['qualify_fixed'](fixed)


def source():
    raw=old.previous.source()
    for a,b in [('pg3792','pg4726'),('pg3790','pg4724'),('Pg3788','Pg4722'),('PG3420','PG4432')]:raw=raw.replace(a,b)
    return raw


def main():
    if sys.argv[1:]not in [['stage'],['activate']]:raise ValueError('one explicit finite stage/activate action')
    authenticate_host()
    ns={**vars(old.previous.previous),'__file__':__file__,'role':role,'TARGET':TARGET,
        'generated':generated,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'qualify_fixed':qualify_fixed}
    exec(compile(source(),'<direct actual finite publication entry>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
