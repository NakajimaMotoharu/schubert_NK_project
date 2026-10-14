"""Separate whole current resume owned-stop post; not a stop/reload operation."""
import inspect
import pg2898_network_owned_post as previous
from pg3006_current_resume_owned_sources import context, TOOLS, SOURCE, bind
from pg2982_current_resume_observer import BOM

SLOT = 'pg3012-current-resume-owned-post-v1'


def namespace():
    base = previous.prior.previous
    ns = {**base.__dict__, 'context': context, 'TOOLS': TOOLS, 'SOURCE': SOURCE, 'SLOT': SLOT, 'candidate_bom': lambda: BOM}
    for fn in [base.emit, base.payload, base.entry]:
        exec(compile(bind(inspect.getsource(fn)), '<actual current resume owned post>', 'exec'), ns)
    original = ns['emit']
    ns['emit'] = lambda *a, **kw: bind(original(*a, **kw))
    return ns


def emit(seals, ctx, live):
    return namespace()['emit'](seals, ctx, live, BOM)


def payload(seals):
    return namespace()['payload'](seals)


def entry():
    return namespace()['entry']()


if __name__ == '__main__':
    raise SystemExit(entry()())
