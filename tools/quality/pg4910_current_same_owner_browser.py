"""Unchanged twelve Browser assertions on actual04bb Root's same owned services."""
import inspect
import types
import pg4764_new_current_same_owner_browser as previous
import pg4900_current_admission_image as admission
import pg4902_current_genuine_terminal as terminal
import pg4906_current_whole_seal as seal
import pg4908_current_browser_ready as ready

SLOT='pg4910-current-same-owner-browser-v2'
SOURCE=admission.SOURCE


def receipt(slot):return types.FunctionType(previous.previous.receipt.__code__,{**vars(previous.previous),'SOURCE':SOURCE})(slot)


def current_guard(raw):
    old='/opt/schubert-nk/releases/0.1.0-PG3976'
    if raw.count(old)!=1 or '/opt/schubert-nk/releases/0.1.0-PG4860' in raw:
        raise ValueError('one exact prior Browser release authority')
    return raw.replace(old,'/opt/schubert-nk/releases/0.1.0-PG4860',1)


def guard():
    whole,term=receipt(seal.SLOT),receipt(terminal.TERM)
    if not(whole['genuineCompletion']['genuineRootDone']and whole['genuineCompletion']['completionCode']==term['completionCode']):
        raise ValueError('same actual current terminal and whole seal')
    fn=types.FunctionType(previous.previous.previous.guard.__code__,{**vars(previous.previous.previous),'SOURCE':SOURCE,'BOM':admission.BOM})
    return current_guard(terminal.bind(admission.entry.observer.bind(fn(whole,term,admission.live()))))


def main():
    admission.authenticate_host()
    raw=inspect.getsource(previous.previous.main).replace('shared=ready.previous.previous.previous','shared=ready.shared')
    ns={**vars(previous.previous),'SLOT':SLOT,'SOURCE':SOURCE,'ready':ready,'guard':guard}
    exec(compile(raw,'<current04bb same-owner real Browser>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
