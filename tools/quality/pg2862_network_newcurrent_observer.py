"""Immutable read-only newboot/currenta9 observer; no start/stop/budget renewal."""
import pg2682_operation_current_observer as prior
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate
import pg2852_network_cold_publication_sources as s

SOURCE=s.unused.CANDIDATE
BOM=s.unused.DIGEST


def source():
    raw=prior.source(BOM)
    for a,b in [('pg2682','pg2862'),('PG2682','PG2862'),(prior.SOURCE,SOURCE),('PG2654','PG2802'),
        ('b2d6f605-61cf-425f-8fbd-12d606f6ee66',s.unused.current.BOOT),
        ('pg2680-operation-publication-post-v1','pg2860-network-cold-publication-independent-post-v1')]:raw=raw.replace(a,b)
    compile(raw,'<newboot currenta9 immutable observation>','exec');return raw


def namespace():
    ns={'__file__':str(prior.previous.previous.R/'pg2862_network_newcurrent_observer.py'),'__name__':'newboot_currenta9_observer'}
    exec(compile(source(),'<newboot currenta9 observer>','exec'),ns);return ns


def main():
    import sys
    ns=namespace()
    if sys.argv[1:]==['stage']:
        with management_gate(P/'current-management-critical.lock'):ns['main']()
    else:ns['main']()


if __name__=='__main__':main()
