"""Current distinct newrun full seal: independent normal terminal/rows, four ordinary identities."""
import inspect
import pg2025_fresh_resume_full_live_seal as previous
from pg2076_current_newrun_terminal_receipt import payload as terminal_payload
from pg2078_current_same_day_rows_oracle import source as row_source
from pyflakes.api import check

SLOT='pg2081-current-newrun-full-live-seal-v1'


def payload(binding):
    raw=previous.payload(binding)
    # Bind body fields before attaching immutable independent guard negatives.
    for old,new in [('pg2025-fresh-resume-full-live-seal-v1',SLOT),('pg2015-completed-run-fresh-resume-once-v1/before.private.json','pg2072-current-noargs-newrun-once-v1/before.private.json'),('fd6412f31de9af59219a0fe28f49ce0d073b074a7ff83ca3516a22e462568b83','796965f389b631bf8abb49f6cbccf88955fbf3afe39edec0194316df35248a05'),('4148e3e8-f107-431a-ab27-d6e6d1f1772e',binding['run']),('2026-10-12T18:20:32.598894Z',binding['cutoff']),('e31b627c-c0e2-4120-bd64-c0777479e800',binding['activation'])]:
        if old not in raw:raise ValueError('one current newrun fullseal body role required')
        raw=raw.replace(old,new)
    guard=terminal_payload(binding)
    marker="out=pathlib.Path('/var/lib/pgpt-s1-preservation/pg2076-current-newrun-terminal-receipt-v1')"
    if guard.count(marker)!=1:raise ValueError('one independent terminal proof-write boundary required')
    raw=previous.constant(raw,'GUARD',guard[:guard.index(marker)])
    oracle=row_source().replace('def qualify(before,now,run,cutoff,upper):','def qualify_current(before,now,run,cutoff,upper):')
    oracle+='\ndef qualify(old,new,cutoff,done,upper):\n    require(instant(cutoff)<=instant(done)<=instant(upper))\n    return qualify_current(old,new,'+repr(binding['run'])+',cutoff,upper)\n'
    raw=previous.constant(raw,'ORACLE',oracle)
    if check(raw,'<actual distinct current fullseal>'):raise ValueError('all actual fullseal exports required')
    compile(raw,'<current distinct newrun fullseal>','exec');return raw


def entry():
    raw=inspect.getsource(previous.main)
    for old,new in [('pg2021-fresh-resume-terminal-receipt-v1','pg2076-current-newrun-terminal-receipt-v1'),('pg2023-fresh-resume-rows-oracle-v1','pg2079-current-same-day-rows-capture-v1'),('pg2019-fresh-resume-live-binding-complete-v1','pg2074-current-newrun-live-binding-v1')]:raw=raw.replace(old,new)
    raw=raw.replace("payload(live['binding'])","payload({**live['binding'],'rootPid':live['rootPid']})")
    ns={**previous.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<newrun current fullseal entry>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
