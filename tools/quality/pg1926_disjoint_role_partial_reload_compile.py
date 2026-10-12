"""Same direct six-ABI compiler, explicitly rebound actual writer and new immutable slot."""
import inspect
import pg1914_direct_partial_reload_compile as prior
from pg1925_disjoint_role_partial_reload_sources import sources,TOOLS

TARGET=prior.W/TOOLS


def main():
    raw=inspect.getsource(prior.main).replace('pg1913','pg1925').replace('Pg1913','Pg1925').replace('pg1914-','pg1926-')
    # bind() accepts1919 input only; the direct compiler is1913. Above literal
    # boundary is explicit; do not pass the wrong namespace to the source binder.
    ns={**prior.__dict__,'sources':sources,'TOOLS':TOOLS,'TARGET':TARGET}
    exec(compile(inspect.getsource(prior.write),'<new-only direct nested writer>','exec'),ns)
    exec(compile(raw,'<direct disjoint-role ABI>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
