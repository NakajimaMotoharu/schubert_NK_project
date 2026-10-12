"""Same proven direct compiler body and new nested TARGET; no inherited admission."""
import inspect
import pg1914_direct_partial_reload_compile as prior
from pg1919_valid_epoch_partial_reload_sources import sources,TOOLS,bind

TARGET=prior.W/TOOLS


def main():
    raw=bind(inspect.getsource(prior.main)).replace('pg1914-','pg1920-')
    ns={**prior.__dict__,'sources':sources,'TOOLS':TOOLS,'TARGET':TARGET}
    exec(compile(inspect.getsource(prior.write),'<new-only exact nested writer>','exec'),ns)
    exec(compile(raw,'<actual direct valid epoch ABI>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
