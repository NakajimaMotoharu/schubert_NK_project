"""Actual new current owner graph ABI only, no Production recompilation."""
import inspect
import pg2892_network_owned_compile as previous
from pg3006_current_resume_owned_sources import sources, context, SOURCE, TOOLS, bind


def main():
    base = previous.prior.previous
    raw = bind(inspect.getsource(base.main))
    ns = {**base.__dict__, 'sources': sources, 'context': context, 'SOURCE': SOURCE, 'TOOLS': TOOLS}
    exec(compile(raw, '<actual current fresh owned ABI>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
