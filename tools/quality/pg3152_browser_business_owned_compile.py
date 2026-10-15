"""Normal current fixed ownership ABI, never a new Production build/signature."""
import inspect
import pg3008_current_resume_owned_compile as previous
from pg3150_browser_business_owned_sources import sources, context, SOURCE, TOOLS, bind


def main():
    base = previous.previous.prior.previous
    ns = {**base.__dict__, 'sources': sources, 'context': context, 'SOURCE': SOURCE, 'TOOLS': TOOLS}
    exec(compile(bind(inspect.getsource(base.main)), '<actual Browser ownership ABI>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
