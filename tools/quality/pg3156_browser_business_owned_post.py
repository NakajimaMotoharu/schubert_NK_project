"""Separate whole post of actual Browser-owned stop; retains qualified UI row deltas."""
import inspect
import pg3012_current_resume_owned_post as previous
from pg3150_browser_business_owned_sources import context, TOOLS, SOURCE, bind, BOM

SLOT = 'pg3156-browser-business-owned-post-v1'


def namespace():
    base = previous.previous.prior.previous
    ns = {**base.__dict__, 'context': context, 'TOOLS': TOOLS, 'SOURCE': SOURCE, 'SLOT': SLOT, 'candidate_bom': lambda: BOM}
    for fn in [base.emit, base.payload, base.entry]:
        exec(compile(bind(inspect.getsource(fn)), '<actual Browser owned separate post>', 'exec'), ns)
    original = ns['emit']
    ns['emit'] = lambda *args, **kwargs: bind(original(*args, **kwargs))
    return ns


def emit(seals, ctx, live):
    return namespace()['emit'](seals, ctx, live, BOM)


def payload(seals):
    return namespace()['payload'](seals)


def entry():
    return namespace()['entry']()


if __name__ == '__main__':
    raise SystemExit(entry()())
