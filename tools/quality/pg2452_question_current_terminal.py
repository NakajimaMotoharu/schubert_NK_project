"""Independent genuine new current Root terminal, no lifecycle authority."""
import inspect
import pg2182_newsource_terminal_receipt as prior
from pg2446_question_current_observer import SOURCE,BOM

SLOT='pg2452-question-current-terminal-v1'


def payload(binding):
    raw=prior.payload(binding).replace(prior.SLOT,SLOT).replace('PG2126','PG2428').replace(
        '3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8',SOURCE).replace(
        '62213f357c9dab3b00b557549426b091a03ace6557a62f4410999a02028a332c',BOM)
    marker="raise ValueError('distinct noargs newrun receipt required')"
    # Reject the last old-source logical run independently of current observed IDs.
    raw=raw.replace(marker,marker+"\n    if binding.get('run')=='91f5484b-9702-4c7c-97f3-dd5110a853f9'or binding.get('activation')=='e1429ac8-f3dd-4e8c-83d2-1926c4ba8440':raise ValueError('old-source completion is not current')")
    compile(raw,'<current genuine terminal>','exec');return raw


def entry():
    raw=inspect.getsource(prior.prior.previous.main).replace('pg2019-fresh-resume-live-binding-complete-v1','pg2450-question-current-live-binding-v1').replace('pg2010-parent-watch-v1','pg2446-parent-watch-v1')
    raw=raw.replace("payload(actual['binding'])","payload({**actual['binding'],'rootPid':actual['rootPid']})")
    ns={**prior.prior.previous.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<current genuine terminal observer entry>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
