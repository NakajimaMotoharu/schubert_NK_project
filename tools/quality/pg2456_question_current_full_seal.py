"""Whole new current source/run, genuine terminal, all24 and ordinary four owners."""
import inspect
from pyflakes.api import check
import pg2186_newsource_full_live_seal as prior
from pg2452_question_current_terminal import payload as terminal_payload,SLOT as TERM
from pg2454_question_current_rows import BEFORE
from pg2446_question_current_observer import SOURCE,BOM,BOOT

SLOT='pg2456-question-current-full-seal-v1'


def payload(binding):
    raw=prior.payload(binding)
    for a,b in [(prior.SLOT,SLOT),('pg2178-newsource-noargs-once-v1','pg2448-question-current-noargs-once-v1'),
                (prior.BEFORE,BEFORE),('3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8',SOURCE),
                ('62213f357c9dab3b00b557549426b091a03ace6557a62f4410999a02028a332c',BOM),
                ('PG2126','PG2428'),('pg2126-manifest.sig','pg2428-manifest.sig'),
                ('3d69f5af-6bac-46b1-a540-7591c4a79a0d',BOOT),
                ('3d69f5af6bac46b1a5407591c4a79a0d',BOOT.replace('-',''))]:raw=raw.replace(a,b)
    guard=terminal_payload(binding);marker="out=pathlib.Path('/var/lib/pgpt-s1-preservation/"+TERM+"')"
    if guard.count(marker)!=1:raise ValueError('one current terminal boundary required')
    raw=prior.prior.previous.previous.constant(raw,'GUARD',guard[:guard.index(marker)])
    if check(raw,'<whole new current source fullseal>'):raise ValueError('whole current namespace required')
    compile(raw,'<whole new current source fullseal>','exec');return raw


def entry():
    raw=inspect.getsource(prior.prior.previous.previous.main)
    for a,b in [('pg2021-fresh-resume-terminal-receipt-v1',TERM),
                ('pg2023-fresh-resume-rows-oracle-v1','pg2454-question-current-rows-v1'),
                ('pg2019-fresh-resume-live-binding-complete-v1','pg2450-question-current-live-binding-v1')]:raw=raw.replace(a,b)
    raw=raw.replace("payload(live['binding'])","payload({**live['binding'],'rootPid':live['rootPid']})")
    ns={**prior.prior.previous.previous.__dict__,'SLOT':SLOT,'SOURCE':SOURCE,'payload':payload}
    exec(compile(raw,'<new current whole acceptance capture>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
