"""Independent genuine a9/day15 DONE and captured PID1 Job/Invocation; no lifecycle writes."""
import inspect
import pg2700_operation_current_terminal as prior
import pg2021_fresh_resume_terminal_receipt as transport
from pg2862_network_newcurrent_observer import SOURCE,BOM

SLOT='pg2878-network-newcurrent-terminal-v1'


def payload(binding):
    if binding.get('run')=='77601cf8-0ade-40fd-813f-c81d5210845e'or binding.get('activation')=='26250063-8755-43b6-9ac7-f76d5eee7257':
        raise ValueError('old completed data is never current terminal')
    raw=prior.payload(binding,BOM)
    for a,b in [(prior.SLOT,SLOT),(prior.SOURCE,SOURCE),('PG2654','PG2802')]:raw=raw.replace(a,b)
    from pyflakes.api import check
    if check(raw,'<whole a9 captured newrun terminal>'):raise ValueError('complete genuine terminal namespace required')
    compile(raw,'<actual same Source/root/PID1 terminal>','exec');return raw


def main():
    raw=inspect.getsource(transport.main).replace('pg2019-fresh-resume-live-binding-complete-v1','pg2874-network-newcurrent-live-binding-v1').replace('pg2010-parent-watch-v1','pg2862-parent-watch-v1')
    raw=raw.replace("payload(actual['binding'])","payload({**actual['binding'],'rootPid':actual['rootPid']})")
    ns={**transport.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<new genuine terminal readonly dispatcher>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
