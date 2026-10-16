"""Unchanged twelve real Browser assertions, new genuine Root's same ordinary owners."""
import inspect
import types
import pg4270_current_same_owner_browser as previous
import pg4752_new_current_admission_image as admission
import pg4754_new_current_terminal as terminal
import pg4760_new_current_whole_seal as seal
import pg4762_new_current_browser_ready as ready

SLOT='pg4764-new-current-same-owner-browser-v1'
SOURCE=admission.SOURCE


def receipt(slot):return types.FunctionType(previous.receipt.__code__,{**vars(previous),'SOURCE':SOURCE})(slot)


def guard():
    whole,term=receipt(seal.SLOT),receipt(terminal.TERM)
    if not(whole['genuineCompletion']['genuineRootDone']and whole['genuineCompletion']['completionCode']==term['completionCode']):raise ValueError('same genuine current terminal and whole seal first')
    fn=types.FunctionType(previous.previous.guard.__code__,{**vars(previous.previous),'SOURCE':SOURCE,'BOM':admission.BOM})
    return terminal.bind(admission.entry.observer.bind(fn(whole,term,admission.live())))


def main():
    admission.authenticate_host()
    raw=inspect.getsource(previous.main).replace('shared=ready.previous.previous.previous','shared=ready.shared')
    ns={**vars(previous),'SLOT':SLOT,'SOURCE':SOURCE,'ready':ready,'guard':guard}
    exec(compile(raw,'<new source same-owner actual Browser transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
