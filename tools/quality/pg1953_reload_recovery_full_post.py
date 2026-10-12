"""Separate full closed-resource post; issued reload kept, old tool UNKNOWN not normalized."""
import inspect
import pg1904_partial_recovery_post as prior
from pg1949_reload_retained_full_proof import snapshot_source

SLOT='pg1953-reload-recovery-full-post-v1'


def payload():
    raw=snapshot_source()
    raw+="require(not pathlib.Path('/proc/495729').exists()and not pathlib.Path('/proc/495760').exists())\n"
    from pg1899_partial_publication_snapshot import payload as partial
    original=partial();tail=original[original.index("save=base/'pg1896-complete-publication-full-post-v1'"):]
    tail=tail.replace('pg1896-complete-publication-full-post-v1',SLOT).replace("'normalSingleReload':True","'normalSingleReload':True,'oldReloadToolCloseUnknownRetained':True,'existingUnitNoReexchange':True,'allRecoveryScopesReturnedNormally':True")
    raw+=tail
    from pyflakes.api import check
    if check(raw,'<actual full reload recovery post>'):raise ValueError('all actual post globals required')
    compile(raw,'<independent full reload recovery>','exec');return raw


def main():
    raw=inspect.getsource(prior.main).replace('pg1903-partial-pair-once-handoff-v1','pg1950-reload-pair-once-handoff-v1')
    ns={**prior.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<actual separate reload recovery post>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
