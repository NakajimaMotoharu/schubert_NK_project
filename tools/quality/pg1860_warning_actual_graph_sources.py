"""New-only namespace after host graph failure; all Root identities unchanged."""
from pg1855_warning_nested_unused_sources import sources as previous

TOOLS='pg1860-warning-unused-tools-v1'
REMOTE='/home/ubuntu/pg1862-warning-input-v1'
ARCHIVE='pg1862-warning-release-v1.tar'


def bind(raw):
    for old,new in [('pg1858','pg1864'),('PG1858','PG1864'),('pg1857','pg1862'),('PG1857','PG1862'),('pg1855','pg1860'),('Pg1855','Pg1860'),('PG1855','PG1860')]:raw=raw.replace(old,new)
    return raw


def sources(bom,before):return {bind(n):bind(raw)for n,raw in previous(bom,before).items()}
