"""New-only direct reload profile after host-prefix failure; actual bytes remain immutable."""
from pg1907_partial_reload_sources import sources as previous,BEFORE as BEFORE
from pg1877_warning_publication_sources import BOM as BOM

TOOLS='pg1913-partial-reload-tools-v1'
SAVE='pg1917-partial-reload-v1'
CLASS='Pg1913PartialReload'


def bind(raw):
    return raw.replace('pg1907','pg1913').replace('Pg1907','Pg1913').replace('PG1907','PG1913').replace('pg1911','pg1917')


def sources():return {bind(n):bind(v)for n,v in previous().items()}
