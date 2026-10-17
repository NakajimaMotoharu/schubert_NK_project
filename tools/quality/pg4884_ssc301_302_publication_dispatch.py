"""Finite stage/activate only; exact current and new candidate role admission."""
import inspect
import sys
import pg4006_literal_invariant_publication_dispatch as previous
import pg4880_ssc301_302_publication_sources as role
from pg4882_ssc301_302_publication_compile import TARGET,generated
from pg4434_current_candidate_admission_read import authenticate_host

GUEST='/var/lib/pgpt-s1-preservation/'+role.TOOLS
REMOTE='/home/ubuntu/pg4884-ssc301-302-publication-stage-v1'
STAGE=role.bind(previous.previous.template.stage(previous.previous.template.role.ro.role.BOM).replace(previous.previous.template.REMOTE,REMOTE))


def qualify_fixed(fixed):
    if type(fixed.get('actualExit'))is not int:raise ValueError('actual numeric fixed qualification')
    ns={**vars(previous.previous),'role':role}
    raw=inspect.getsource(previous.previous.qualify_fixed)
    for a,b in [('Pg3788','Pg4880'),('pg3788','pg4880'),('Pg3780','Pg4872'),('pg3780','pg4872')]:raw=raw.replace(a,b)
    exec(compile(raw,'<exact finite target and bound graph>','exec'),ns);return ns['qualify_fixed'](fixed)


def source():
    raw=previous.previous.source()
    for a,b in [('pg3792','pg4884'),('pg3790','pg4882'),('Pg3788','Pg4880'),('PG3420','PG4702')]:raw=raw.replace(a,b)
    return raw


def main():
    if sys.argv[1:] not in (['stage'],['activate']):raise ValueError('one finite stage/activate action only')
    authenticate_host()
    ns={**vars(previous.previous.previous),'__file__':__file__,'role':role,'TARGET':TARGET,
        'generated':generated,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'qualify_fixed':qualify_fixed}
    exec(compile(source(),'<actual825e finite04bb publication>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
