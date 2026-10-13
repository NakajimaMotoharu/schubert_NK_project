"""Immutable newboot current observer; stage is not an authorization or start.

PT-OPS-2224-001. Watch only when a separately qualified legitimate run is due.
"""
from pg1454_current_day_observer import source as prior,R
from pg2208_current_newboot_cold_sources import bindings


def source():
    raw=bindings(prior()).replace('pg1454','pg2224').replace('PG1454','PG2224')
    old='pg1453-current-cold-independent-post-v1/manifest.safe.json'
    if raw.count(old)!=1:raise ValueError('one newboot whole post prerequisite required')
    raw=raw.replace(old,'pg2218-current-newboot-cold-independent-post-v1/manifest.safe.json')
    compile(raw,'<newboot current immutable observer>','exec');return raw


def namespace():
    ns={'__file__':str(R/'pg2224_newboot_current_observer.py'),'__name__':'newboot_current_observer'}
    exec(compile(source(),'<newboot immutable observer>','exec'),ns);return ns


if __name__=='__main__':namespace()['main']()
