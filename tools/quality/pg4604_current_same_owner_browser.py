"""The unchanged twelve real-browser oracles for this new Root's same four owners."""
import inspect
import types
import pg4270_current_same_owner_browser as previous
import pg4586_current_independent_acceptance as accepted
import pg4584_current_admission_image as admission
import pg4602_current_browser_ready as ready

SLOT='pg4604-current-same-owner-browser-v1'
SOURCE=admission.SOURCE


def receipt(slot):return types.FunctionType(previous.receipt.__code__,{**vars(previous),'SOURCE':SOURCE}) (slot)


def guard():
    seal,term=receipt(accepted.SEAL),receipt(accepted.TERM)
    if not seal['genuineCompletion']['genuineRootDone']or seal['genuineCompletion']['completionCode']!=term['completionCode']:raise ValueError('same genuine terminal/seal first')
    fn=types.FunctionType(previous.previous.guard.__code__,{**vars(previous.previous),'SOURCE':SOURCE,'BOM':admission.BOM})
    return admission.entry.observer.bind(fn(seal,term,admission.live()))


def main():
    raw=inspect.getsource(previous.main).replace('shared=ready.previous.previous.previous','shared=ready.shared')
    ns={**vars(previous),'SLOT':SLOT,'SOURCE':SOURCE,'ready':ready,'guard':guard}
    exec(compile(raw,'<new964e same-owner actual Browser transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
