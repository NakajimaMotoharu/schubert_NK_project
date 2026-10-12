"""Direct new-only six-ABI freeze after independently closed partial; no guest mutation."""
import inspect
import pg1879_warning_publication_compile as prior
from pg1907_partial_reload_sources import sources,TOOLS,BEFORE,bind
from pg1877_warning_publication_sources import once

TARGET=prior.W/TOOLS


def main():
    raw=inspect.getsource(prior.main)
    begin=raw.index("    if post['actualExit']")
    end=raw.index('    os.umask',begin)
    raw=raw[:begin]+"""    if post['actualExit']!=0 or post['partialUnitExchangedNotReloaded']is not True or post['normalSingleReload']is not False or post['allClientAdvisoryFlock0']is not True or post['productionSource']!=CANDIDATE or post['privateBeforeSha256']!=BEFORE or post['whole187SignedArtifactBytesVerified']is not True or candidate['manifestSha256']!=BOM or prior['actualExit']!=0:raise ValueError('actual closed newcurrent/Unit partial required')
"""+raw[end:]
    raw=once(raw,",('transition','Pg1877TransitionTest')",'')
    raw=bind(raw).replace('pg1879-','pg1908-').replace('pg1876-warning-candidate-ro-post-v1','pg1904-partial-recovery-closed-post-v1')
    raw=raw.replace("'productionSource':OLD","'productionSource':CANDIDATE")
    ns={**prior.__dict__,'sources':sources,'TOOLS':TOOLS,'TARGET':TARGET,'BEFORE':BEFORE}
    exec(compile(inspect.getsource(prior.write),'<new reload-only nested writer>','exec'),ns)
    exec(compile(raw,'<direct partial reload compiler>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
