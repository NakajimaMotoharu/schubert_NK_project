"""Six actual ABI for already-published file and remaining normal reload only."""
import inspect
import pg1914_direct_partial_reload_compile as prior
from pg2001_existing_runtime_finish_sources import sources,TOOLS,BEFORE,BOM
from pg1877_warning_publication_sources import once

TARGET=prior.W/TOOLS


def main():
    raw=inspect.getsource(prior.main).replace('pg1913','pg2001').replace('Pg1913PartialReload','Pg2001ExistingRuntimeFinish').replace('Pg1913','Pg2001').replace('pg1914-','pg2002-').replace('pg1904-partial-recovery-closed-post-v1','pg1995-partial-runtime-recovery-full-post-v1')
    raw=once(raw,"post['partialUnitExchangedNotReloaded']is not True or post['normalSingleReload']is not False","post['partialNewRuntimeFileNoReload']is not True or post['normalSingleRuntimeReload']is not False or post['normalSingleReload']is not True")
    ns={**prior.__dict__,'sources':sources,'TOOLS':TOOLS,'TARGET':TARGET,'BEFORE':BEFORE,'BOM':BOM}
    exec(compile(inspect.getsource(prior.write),'<new-only immutable nested writer>','exec'),ns)
    exec(compile(raw,'<actual existing runtime six ABI>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
