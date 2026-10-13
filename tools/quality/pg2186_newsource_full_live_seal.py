"""Same current source/run whole normal receipt, independent DB, owned four capture."""
import inspect
import pg2085_native_augmented_newrun_full_seal as prior
from pg2182_newsource_terminal_receipt import payload as terminal_payload,SLOT as TERM
from pg2184_newsource_same_day_rows import BEFORE
from pg2176_newsource_normal_observer import SOURCE,BOM

SLOT='pg2186-newsource-full-live-seal-v1'


def payload(binding):
    raw=prior.payload(binding)
    pairs=[('pg2085-native-augmented-newrun-full-seal-v1',SLOT),('pg2072-current-noargs-newrun-once-v1/before.private.json','pg2178-newsource-noargs-once-v1/before.private.json'),('796965f389b631bf8abb49f6cbccf88955fbf3afe39edec0194316df35248a05',BEFORE),('0fd734195b4d5338f6b7e860e087cce561d49562',SOURCE),('ee75d0cd61457462eca59e67f5af2d8e677427071514940f3fb594ba93a026d7',BOM),('PG1846','PG2126'),('pg1846-manifest.sig','pg2126-manifest.sig')]
    for old,new in pairs:
        if old not in raw:raise ValueError('current source-bound fullseal role missing '+old)
        raw=raw.replace(old,new)
    guard=terminal_payload(binding)
    marker="out=pathlib.Path('/var/lib/pgpt-s1-preservation/"+TERM+"')"
    if guard.count(marker)!=1:raise ValueError('one actual current terminal proof boundary required')
    raw=prior.previous.previous.constant(raw,'GUARD',guard[:guard.index(marker)])
    from pyflakes.api import check
    if check(raw,'<current newsource whole fullseal>'):raise ValueError('whole actual source namespace required')
    compile(raw,'<current newsource whole fullseal>','exec');return raw


def entry():
    raw=inspect.getsource(prior.previous.previous.main)
    for old,new in [('pg2021-fresh-resume-terminal-receipt-v1',TERM),('pg2023-fresh-resume-rows-oracle-v1','pg2184-newsource-same-day-rows-v1'),('pg2019-fresh-resume-live-binding-complete-v1','pg2180-newsource-live-binding-v1')]:raw=raw.replace(old,new)
    raw=raw.replace("payload(live['binding'])","payload({**live['binding'],'rootPid':live['rootPid']})")
    ns={**prior.previous.previous.__dict__,'SLOT':SLOT,'SOURCE':SOURCE,'payload':payload}
    exec(compile(raw,'<current newsource fullseal entry>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
