"""Independent actual current fresh resume terminal; no start/stop authority."""
import inspect
from pyflakes.api import check
import pg2021_fresh_resume_terminal_receipt as previous
from pg2360_current_completed_resume_once import SOURCE,BOM

SLOT='pg2364-current-resume-terminal-v1'


def bind(raw):
    return raw.replace('9adbf05a-61d0-408b-b51d-ab19c7e5b16a','9be93262-fbb2-438f-b2b0-c4a27f5563a4').replace('PG1846','PG2126').replace('ee75d0cd61457462eca59e67f5af2d8e677427071514940f3fb594ba93a026d7',BOM).replace('0fd734195b4d5338f6b7e860e087cce561d49562',SOURCE).replace(previous.SLOT,SLOT).replace("pathlib.Path('/proc/503613')","pathlib.Path('/proc',str(BINDING['rootPid']))")


def payload(binding):
    raw='BINDING='+repr(binding)+'\n'+bind(inspect.getsource(previous.classify))+'\n'+bind(previous.GUEST)
    if check(raw,'<current fresh terminal full closure>'):raise ValueError('all current terminal globals required')
    compile(raw,'<actual current fresh terminal>','exec');return raw


def main():
    raw=inspect.getsource(previous.main).replace('pg2019-fresh-resume-live-binding-complete-v1','pg2362-current-resume-live-binding-v1').replace('pg2010-parent-watch-v1','pg2358-parent-watch-v1').replace("payload(actual['binding'])","payload({**actual['binding'],'rootPid':actual['rootPid']})")
    ns={**previous.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<current independent terminal transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
