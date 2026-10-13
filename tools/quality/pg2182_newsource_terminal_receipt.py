"""New-source distinct run genuine normal DONE/PID1 receipt; no lifecycle writes."""
import inspect
import pg2076_current_newrun_terminal_receipt as prior
from pg2176_newsource_normal_observer import SOURCE,BOM

SLOT='pg2182-newsource-terminal-receipt-v1'


def payload(binding):
    raw=prior.payload(binding).replace(prior.SLOT,SLOT)
    for old,new in [('PG1846','PG2126'),('0fd734195b4d5338f6b7e860e087cce561d49562',SOURCE),('ee75d0cd61457462eca59e67f5af2d8e677427071514940f3fb594ba93a026d7',BOM)]:raw=raw.replace(old,new)
    reject="if type(binding)is not dict or binding.get('run')=='4148e3e8-f107-431a-ab27-d6e6d1f1772e'or binding.get('activation')=='e31b627c-c0e2-4120-bd64-c0777479e800':"
    if raw.count(reject)!=1:raise ValueError('exact distinct run guard required')
    return raw.replace(reject,"if type(binding)is not dict or binding.get('run')in {'4148e3e8-f107-431a-ab27-d6e6d1f1772e','a31dd6da-cf4c-4d0f-ab7c-5c8bb59c0b75'}or binding.get('activation')in {'e31b627c-c0e2-4120-bd64-c0777479e800','9026b2ab-bb42-49cd-a2bd-4c661049dce3'}:")


def entry():
    raw=inspect.getsource(prior.previous.main).replace('pg2019-fresh-resume-live-binding-complete-v1','pg2180-newsource-live-binding-v1').replace('pg2010-parent-watch-v1','pg2176-parent-watch-v1')
    raw=raw.replace("payload(actual['binding'])","payload({**actual['binding'],'rootPid':actual['rootPid']})")
    ns={**prior.previous.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<current newsource normal receipt entry>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
