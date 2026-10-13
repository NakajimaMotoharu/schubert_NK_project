"""Direct six actual ABI on current qualified completed-run source, no VM mutation."""
import inspect
import pg1914_direct_partial_reload_compile as prior
from pg1980_fresh_completed_resume_sources import sources,TOOLS,BEFORE,BOM
from pg1877_warning_publication_sources import once

TARGET=prior.W/TOOLS


def main():
    raw=inspect.getsource(prior.main).replace('pg1913','pg1980').replace('Pg1913PartialReload','Pg1980FreshResumePreparation').replace('Pg1913','Pg1980').replace('pg1914-','pg1982-').replace('pg1904-partial-recovery-closed-post-v1','pg1963-reload-ref-scoped-full-post-v1')
    raw=once(raw,"post['partialUnitExchangedNotReloaded']is not True or post['normalSingleReload']is not False","post['normalSingleReload']is not True or post['oldReloadToolCloseUnknownRetained']is not True")
    ns={**prior.__dict__,'sources':sources,'TOOLS':TOOLS,'TARGET':TARGET,'BEFORE':BEFORE,'BOM':BOM}
    exec(compile(inspect.getsource(prior.write),'<new-only nested writer>','exec'),ns)
    exec(compile(raw,'<direct current freshresume six ABI>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
