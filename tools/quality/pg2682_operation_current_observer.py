"""New source read-only observer; no business start/stop authority."""
import pg2538_strict_current_observer as previous
from pg2674_operation_publication_sources import candidate_bom,production

SOURCE=production()


def source(bom=None):
    if bom is None:bom=candidate_bom()
    raw=previous.source(bom)
    for a,b in [('pg2538','pg2682'),('PG2538','PG2682'),
      ('pg2536-strict-normal-publication-post-v1','pg2680-operation-publication-post-v1'),
      (previous.SOURCE,SOURCE),('PG2512','PG2654')]:raw=raw.replace(a,b)
    compile(raw,'<new resource current read-only observer>','exec');return raw


def namespace():
    ns={'__file__':str(previous.previous.R/'pg2682_operation_current_observer.py'),'__name__':'operation_current_observer'}
    exec(compile(source(),'<new current operation observer>','exec'),ns);return ns


if __name__=='__main__':namespace()['main']()
