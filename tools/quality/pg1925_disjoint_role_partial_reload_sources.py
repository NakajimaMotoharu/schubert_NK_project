"""New current and foreign old current are independent literal roles, not global swaps."""
import pg1919_valid_epoch_partial_reload_sources as prior
from pg1877_warning_publication_sources import once

TOOLS='pg1925-partial-reload-tools-v1'
SAVE='pg1929-partial-reload-v1'
CLASS='Pg1925PartialReload'
BEFORE=prior.BEFORE
BOM=prior.BOM


def bind(raw):return raw.replace('pg1919','pg1925').replace('Pg1919','Pg1925').replace('PG1919','PG1925').replace('pg1923','pg1929')


def sources():
    s={bind(n):bind(r)for n,r in prior.sources().items()};key='Pg1925CurrentIdentityTest.java'
    changes=[('new String[]{"PG1292","PG1846",null}','new String[]{"PG1292","PG1638",null}'),('new String[]{"pg1292","pg1846",null}','new String[]{"pg1292","pg1638",null}'),('new String[]{"769ddb15cd735c25fef581b5f9850ef9d0053c0f","0fd734195b4d5338f6b7e860e087cce561d49562",null}','new String[]{"769ddb15cd735c25fef581b5f9850ef9d0053c0f","2741c4546afad6c1e8b6efbd53dfb58144edf7bb",null}'),('Path.of("/opt/schubert-nk/releases/0.1.0-PG1846"),null}','Path.of("/opt/schubert-nk/releases/0.1.0-PG1638"),null}')]
    for old,new in changes:s[key]=once(s[key],old,new)
    return s
