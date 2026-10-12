"""New-only fixture envelope: INVALID selection and ISSUED-only hash are independent."""
import pg1913_direct_partial_reload_sources as prior
from pg1877_warning_publication_sources import once

TOOLS='pg1919-partial-reload-tools-v1'
SAVE='pg1923-partial-reload-v1'
CLASS='Pg1919PartialReload'
BEFORE=prior.BEFORE
BOM=prior.BOM


def bind(raw):return raw.replace('pg1913','pg1919').replace('Pg1913','Pg1919').replace('PG1913','PG1919').replace('pg1917','pg1923')


def sources():
    result={bind(n):bind(r)for n,r in prior.sources().items()}
    key='Pg1919OriginalTupleTest.java'
    result[key]=once(result[key],'state==StartupPermitRecords.State.INVALID?Optional.of','state==StartupPermitRecords.State.ISSUED?Optional.of')
    return result
