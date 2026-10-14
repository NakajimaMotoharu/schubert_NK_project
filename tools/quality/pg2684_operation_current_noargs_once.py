"""Fresh resource candidate ordinary admission; old completed run never resumed."""
import inspect
import pg2540_strict_current_noargs_once as previous
from pg2682_operation_current_observer import namespace,SOURCE
from pg2674_operation_publication_sources import candidate_bom
from pg2680_operation_publication_post import payload as full_post

SLOT='pg2684-operation-current-noargs-once-v2'


def body(bom=None):
    if bom is None:bom=candidate_bom()
    raw=previous.body(bom)
    for a,b in [('pg2538','pg2682'),(previous.SLOT,SLOT),(previous.SOURCE,SOURCE),
      ('PG2512','PG2654'),('require(len(records)==22)','require(len(records)==28)')]:
        if a not in raw:raise ValueError('exact new ordinary admission source boundary required')
        raw=raw.replace(a,b)
    return raw


def payload(hashes):
    raw=inspect.getsource(previous.previous.prior.payload).replace('pg2174-normal-publication-full-post-v1','pg2680-operation-publication-post-v1')
    ns={**previous.previous.prior.__dict__,'full_post':full_post,'body':body}
    exec(compile(raw,'<whole actual new operation admission projection>','exec'),ns);return ns['payload'](hashes)


def main():
    bom=candidate_bom();raw=inspect.getsource(previous.previous.prior.main)
    for a,b in [('pg2176','pg2682'),('pg2174-normal-publication-full-post-v1','pg2680-operation-publication-post-v1')]:raw=raw.replace(a,b)
    ns={**previous.previous.prior.__dict__,'namespace':namespace,'SOURCE':SOURCE,'BOM':bom,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<new source single admission transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
