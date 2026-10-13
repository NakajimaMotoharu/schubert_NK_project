"""Current newrun ten native points; old32 private copies retained, receipt negatives untouched."""
import inspect
import pg2046_receipt_preserving_current_native_catalog as previous
import pg2042_fresh_normal_warning_native_catalog as transport
from pyflakes.api import check
from pg2090_current_newrun_owned_stop_sources import SOURCE,TOOLS

SLOT='pg2100-current-newrun-native-catalog-v1'


def catalog_source(receipt):
    raw=previous.catalog_source(receipt);header=receipt+'\n'
    if not raw.startswith(header):raise ValueError('one immutable independent receipt header required')
    raw=raw[len(header):]
    pairs=[('pg2030-native-stop-v1','pg2090-native-stop-v1'),('pg2015-completed-run-fresh-resume-once-v1','pg2072-current-noargs-newrun-once-v1'),('oldTwentySixArchiveUnchanged','oldThirtyTwoArchiveUnchanged'),('len(old)==26','len(old)==32'),('e31b627c-c0e2-4120-bd64-c0777479e800','9026b2ab-bb42-49cd-a2bd-4c661049dce3'),('106318294326','113070840714'),('107890801314','114755353173'),('187092','204748'),('d6efa3f26d864704b015faa0625da1c0','2aae1ec09dc34e6281742e0127ceee25'),('187550','205206'),('187697','205353'),('106418451508','113189783801'),('106423392924','113203458561'),('106424517287','113204805978'),('106424518430','113204808054')]
    for old,new in pairs:
        if old not in raw:raise ValueError('one actual current native positive binding required: '+old)
        raw=raw.replace(old,new)
    raw=header+raw
    if check('SEALS={}\n'+raw,'<actual distinct newrun native catalog>'):raise ValueError('all actual catalog globals required')
    compile(raw,'<actual current newrun native catalog>','exec');return raw


def entry():
    raw=inspect.getsource(transport.main).replace('pg2040-fresh-normal-warning-terminal-post-v1','pg2096-current-newrun-terminal-post-v1').replace('pg2030_parent_receipt.py','pg2090_parent_receipt.py')
    ns={**transport.__dict__,'SOURCE':SOURCE,'TOOLS':TOOLS,'SLOT':SLOT,'catalog_source':catalog_source}
    exec(compile(raw,'<current newrun native catalog entry>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
