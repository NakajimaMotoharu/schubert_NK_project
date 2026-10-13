"""Immutable current PG2126 read-only observer after qualified finite publication."""
from pg2070_current_newrun_observer import source as previous,R
from pg2132_current_normal_unused_sources import production
from pg2170_normal_publication_sources import BOM

SOURCE=production()


def source():
    raw=previous()
    for old,new in [('pg2070','pg2176'),('PG2070','PG2176'),('0fd734195b4d5338f6b7e860e087cce561d49562',SOURCE),('ee75d0cd61457462eca59e67f5af2d8e677427071514940f3fb594ba93a026d7',BOM),('PG1846','PG2126'),('pg2068-retained-backup-replay-history-post-v1','pg2174-normal-publication-full-post-v1')]:raw=raw.replace(old,new)
    compile(raw,'<current newsource normal observer>','exec');return raw


def namespace():
    ns={'__file__':str(R/'pg2176_newsource_normal_observer.py'),'__name__':'newsource_normal_observer'}
    exec(compile(source(),'<current immutable normal observer>','exec'),ns);return ns


if __name__=='__main__':namespace()['main']()
