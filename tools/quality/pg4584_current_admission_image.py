"""Authenticate actual new Root's immutable before; old native58 is data, not new credit."""
import inspect
import types
import pg4260_stable_admission_image as previous
import pg4576_current_fresh_noargs_once as entry
import pg4578_current_live_binding as binding
from pg4434_current_candidate_admission_read import authenticate_host

SLOT='pg4584-current-admission-image-v1'
SOURCE,BOM,ONCE,LIVE=entry.SOURCE,entry.BOM,entry.SLOT,binding.SLOT
PUBLICATION='f14b97d22963b2ad3eeea7dbcb5087fcb6885047d965256ffca444fbf1f306b5'
PUBLICATION_PATH='pg4552-failed-current-publication-post-v1/second-full11.private.json'


def project(value,publication):
    raw=inspect.getsource(previous.project).replace('!=52','!=58').replace('all52','all58')
    ns={};exec(compile(raw,'<actual field-only admission view58>','exec'),ns);return ns['project'](value,publication)


def payload(observed):
    raw=previous.payload(observed)
    for old,new in [(previous.ONCE,ONCE),(previous.SOURCE,SOURCE),(previous.BOM,BOM),(previous.PUBLICATION,PUBLICATION),
        ('pg4008-literal-invariant-publication-independent-post-v1/after.private.json',PUBLICATION_PATH),('!=52','!=58'),('all52','all58'),("'nativeExecEntries':52","'nativeExecEntries':58")]:raw=raw.replace(old,new)
    return raw


def live():
    ns={**vars(previous.previous),'SOURCE':SOURCE,'LIVE':LIVE}
    return types.FunctionType(previous.live.__code__,ns)()


def before():
    ns={**vars(previous.previous),'SLOT':SLOT,'SOURCE':SOURCE,'live':live}
    raw=inspect.getsource(previous.previous.before)
    exec(compile(raw,'<actual immutable before receipt>','exec'),ns);return ns['before']()


def execute(slot,raw,timeout=60):
    authenticate_host()
    return types.FunctionType(previous.execute.__code__,{**vars(previous.previous),'SOURCE':SOURCE})(slot,raw,timeout)


if __name__=='__main__':raise SystemExit(execute(SLOT,payload(live())))
