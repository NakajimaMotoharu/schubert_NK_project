"""Actual new source A01 while same captured parent owns ordinary peers."""
import inspect
import pg2550_strict_current_a01 as previous
from pg2674_operation_publication_sources import production,candidate_bom

SOURCE=production()


def code():
    raw=inspect.getsource(previous.code)
    for a,b in [('pg2542-strict-current-live-binding-v1','pg2686-operation-current-live-binding-v1'),
      ('PG2550','PG2720'),('pg2550','pg2720'),('pg2538','pg2682'),
      ('pg2540-strict-current-noargs-once-v1','pg2684-operation-current-noargs-once-v1'),
      ('pg2536-strict-normal-publication-post-v1','pg2680-operation-publication-post-v1'),('PG2512','PG2654')]:raw=raw.replace(a,b)
    ns={**previous.__dict__,'SOURCE':SOURCE,'candidate_bom':candidate_bom}
    exec(compile(raw,'<sameactualroot new A01 driver producer>','exec'),ns);return ns['code']()


if __name__=='__main__':
    ns={'__file__':__file__,'__name__':'operation_current_a01'}
    exec(compile(code(),'<newsource A01 unchanged Current driver>','exec'),ns);ns['main']()
