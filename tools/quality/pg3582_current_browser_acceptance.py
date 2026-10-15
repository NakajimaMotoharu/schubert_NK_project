"""Independent current completed-resume terminal/all24/whole Root seal; no mutation."""
import inspect
import json
import sys
import types
from pyflakes.api import check
import pg3472_outbox_acceptance as previous
import pg2023_fresh_resume_rows_oracle as rows_template
from pg2025_fresh_resume_full_live_seal import constant
from pg3564_current_browser_resume_sources import SOURCE,BOM,RUN,BOOT
from pg3574_current_browser_resume_once import SLOT as ONCE
from pg3576_current_browser_live_binding import SLOT as LIVE
from pg1446_current_cold_stage import W

TERM='pg3582-current-browser-terminal-v1'
ROWS='pg3584-current-browser-root-rows-v1'
SEAL='pg3586-current-browser-root-full-seal-v1'
BEFORE='47ece6dcbeea49f23b6dc2a2bfca4fdfe4dcc02d8b846f7992a6c590b5dea0cd'


def bind(raw):
    for a,b in [(previous.TERM,TERM),(previous.ROWS,ROWS),(previous.SEAL,SEAL),
                (previous.ONCE,ONCE),(previous.LIVE,LIVE),('pg3462-parent-watch-v1','pg3572-parent-watch-v1')]:raw=raw.replace(a,b)
    return raw


def live():
    value=json.loads((W/LIVE/'manifest.safe.json').read_bytes())
    if not(value['actualExit']==0 and value['productionSource']==SOURCE and value['binding']['run']==RUN and value['binding']['activation']!='225691a3-e748-42c4-8972-5ffda5de893d'):
        raise ValueError('current new actual activation of selected completed run required')
    return value


def terminal_payload(binding):return bind(previous.terminal_payload(binding))


def oracle_source():
    raw=rows_template.oracle_source()
    marker="progress[0]['protected_count']==4"
    if raw.count(marker)!=1:raise ValueError('one explicitly independent completed progress count required')
    return raw.replace(marker,"progress[0]['protected_count']==10")


def rows_payload():
    binding=live()['binding'];once=json.loads((W/ONCE/'manifest.safe.json').read_bytes())
    raw=rows_template.payload().replace(rows_template.oracle_source(),oracle_source())
    for a,b in [(rows_template.SLOT,ROWS),('pg2015-completed-run-fresh-resume-once-v1',ONCE),
                ('3d69f5af-6bac-46b1-a540-7591c4a79a0d',BOOT),
                ('fd6412f31de9af59219a0fe28f49ce0d073b074a7ff83ca3516a22e462568b83',BEFORE),
                ('4148e3e8-f107-431a-ab27-d6e6d1f1772e',RUN),
                ('e31b627c-c0e2-4120-bd64-c0777479e800',binding['activation']),
                ('2026-10-12T18:20:32.598894Z',binding['cutoff']),
                ('2026-10-13T01:15:32.188849+00:00',once['startedUTC'])]:
        if a not in raw:raise ValueError('exact independent resume rows binding required '+a[:32])
        raw=raw.replace(a,b)
    if check(raw,'<current fresh resume all24>'):raise ValueError('complete all24 globals required')
    compile(raw,'<current resume independent all24>','exec');return raw


def seal_payload(binding):
    # Use the latest current-signed seal's actual reader, replacing the complete
    # nested new-day oracle, never partially altering its observed expectations.
    fn=types.FunctionType(previous.old_seal.payload.__code__,{**previous.old_seal.__dict__,
        'SOURCE':SOURCE,'SLOT':SEAL,'TERM':TERM,'before':lambda:BEFORE,
        'terminal':lambda b,bom:terminal_payload(b)})
    raw=bind(previous.bind(fn(binding,BOM)))
    marker="out=pathlib.Path('/var/lib/pgpt-s1-preservation/"+TERM+"')"
    guard=terminal_payload(binding)
    if guard.count(marker)!=1:raise ValueError('one complete new terminal guard required')
    raw=constant(raw,'GUARD',guard[:guard.index(marker)])
    once=json.loads((W/ONCE/'manifest.safe.json').read_bytes())
    oracle=oracle_source().replace('def qualify(old,new,run,cutoff,lower,upper):','def qualify_resume(old,new,run,cutoff,lower,upper):')
    oracle+="\ndef qualify(old,new,cutoff,done,upper):\n require(instant(cutoff)<=instant(done)<=instant(upper))\n return qualify_resume(old,new,"+repr(RUN)+",cutoff,"+repr(once['startedUTC'])+",upper)\n"
    raw=constant(raw,'ORACLE',oracle)
    if check(raw,'<complete current Root resume seal>'):raise ValueError('complete actual whole seal globals required')
    compile(raw,'<current whole resume seal>','exec');return raw


def entry(phase):
    modules={'terminal':(previous.old_terminal,TERM,terminal_payload),'rows':(previous.old_rows,ROWS,rows_payload),'seal':(previous.old_seal,SEAL,seal_payload)}
    if phase not in modules:raise ValueError('explicit terminal/rows/seal required')
    module,slot,payload=modules[phase]
    raw=inspect.getsource(module.entry)
    for a,b in [('pg2686-operation-current-live-binding-v1',LIVE),('pg2682-parent-watch-v1','pg3572-parent-watch-v1'),('pg2702-operation-current-rows-v1',ROWS),('pg2700-operation-current-terminal-v1',TERM)]:raw=raw.replace(a,b)
    ns={**module.__dict__,'SOURCE':SOURCE,'SLOT':slot,'TERM':TERM,'payload':payload}
    exec(compile(raw,'<current new resume independent phase>','exec'),ns);return ns['entry']()


if __name__=='__main__':raise SystemExit(entry(sys.argv[1])())
