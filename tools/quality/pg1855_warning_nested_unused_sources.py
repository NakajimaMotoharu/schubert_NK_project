"""New-only immutable profile after host nested-writer failure; Root UUID preserved."""
from pg1848_warning_signed_unused_sources import sources as previous

TOOLS='pg1855-warning-unused-tools-v1'
SAVE='pg1858-warning-unused-placement-v1'
REMOTE='/home/ubuntu/pg1857-warning-input-v1'
ARCHIVE='pg1857-warning-release-v1.tar'


def bind(raw):
    for old,new in [('pg1852','pg1858'),('PG1852','PG1858'),('pg1851','pg1857'),('PG1851','PG1857'),('pg1848','pg1855'),('Pg1848','Pg1855'),('PG1848','PG1855')]:raw=raw.replace(old,new)
    return raw


def sources(bom,before):return {bind(n):bind(raw)for n,raw in previous(bom,before).items()}
