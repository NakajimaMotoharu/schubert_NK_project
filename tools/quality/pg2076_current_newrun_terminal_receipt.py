"""Independent distinct newrun normal terminal receipt; previous logicalrun is not this acceptance."""
import inspect
from pyflakes.api import check
import pg2021_fresh_resume_terminal_receipt as previous
from pg2070_current_newrun_observer import SOURCE

SLOT='pg2076-current-newrun-terminal-receipt-v1'


def classify(binding,state,rows,done):
    if type(binding)is not dict or binding.get('run')=='4148e3e8-f107-431a-ab27-d6e6d1f1772e'or binding.get('activation')=='e31b627c-c0e2-4120-bd64-c0777479e800':raise ValueError('distinct noargs newrun receipt required')
    return _normal_classify(binding,state,rows,done)


_normal_classify=previous.classify


def payload(binding):
    source=inspect.getsource(previous.classify).replace('def classify(','def _normal_classify(',1)+'\n'+inspect.getsource(classify)
    guest=previous.GUEST.replace(previous.SLOT,SLOT)
    old="not pathlib.Path('/proc/503613').exists()"
    if guest.count(old)!=1:raise ValueError('one actual newRoot process-gone boundary required')
    guest=guest.replace(old,"not pathlib.Path('/proc',str(BINDING['rootPid'])).exists()")
    raw='BINDING='+repr(binding)+'\n'+source+'\n'+guest
    if check(raw,'<actual distinct newrun terminal>'):raise ValueError('whole terminal exports required')
    compile(raw,'<newrun independent normal receipt>','exec');return raw


def entry():
    raw=inspect.getsource(previous.main).replace('pg2019-fresh-resume-live-binding-complete-v1','pg2074-current-newrun-live-binding-v1').replace('pg2010-parent-watch-v1','pg2070-parent-watch-v1')
    raw=raw.replace("payload(actual['binding'])","payload({**actual['binding'],'rootPid':actual['rootPid']})")
    ns={**previous.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<distinct current newrun receipt entry>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
