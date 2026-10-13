"""Separate all-resource post of pending runtime file; no existing reload/start repeated."""
import inspect
from pg1991_fresh_runtime_partial_full_proof import payload as proof
from pg1963_reload_ref_scoped_full_post import payload as closed
import pg1904_partial_recovery_post as prior

SLOT='pg1995-partial-runtime-recovery-full-post-v1'


def payload():
    raw=proof();raw=raw[:raw.index("tool=base/'pg1980-fresh-resume-tools-v1'")]
    raw=raw.replace("lines[-2:] == [b'1', b'1']","lines[-2:] == [b'0', b'0']")
    reference=closed();start=reference.index("        for name in ('maintenance.lock', 'startup-admission.lock'):");end=reference.index("        require(tree(pathlib.Path('/run/systemd/system'))",start)
    marker="        for name in ('maintenance.lock','startup-admission.lock'):owned_lock(name)\n"
    if raw.count(marker)!=1:raise ValueError('one closed lock-resource scope required')
    raw=raw.replace(marker,reference[start:end])
    tail=reference[reference.index("save=base/'pg1963-reload-ref-scoped-full-post-v1'"):]
    tail=tail.replace('pg1963-reload-ref-scoped-full-post-v1',SLOT).replace("'normalSingleReload':True","'normalSingleReload':True,'normalSingleRuntimeReload':False,'partialNewRuntimeFileNoReload':True,'old1983CloseUnknownRetained':True")
    raw+="require(not pathlib.Path('/proc/498727').exists()and not pathlib.Path('/proc/498758').exists())\n"+tail
    from pyflakes.api import check
    if check(raw,'<actual closed partial runtime full post>'):raise ValueError('all actual post globals required')
    compile(raw,'<current pending-runtime whole resource post>','exec');return raw


def main():
    raw=inspect.getsource(prior.main).replace('pg1903-partial-pair-once-handoff-v1','pg1993-partial-runtime-pair-once-handoff-v1')
    ns={**prior.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<actual partial runtime separate post>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
