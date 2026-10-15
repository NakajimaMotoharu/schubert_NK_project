"""New-only immutable owned stop, admitted only after complete Browser seal."""
import inspect
import pg3010_current_resume_owned_dispatch as previous
from pg3150_browser_business_owned_sources import sources, context, SOURCE, TOOLS, bind, BOM
from pg3146_browser_business_full_seal import payload as seal_payload

GUEST = '/var/lib/pgpt-s1-preservation/' + TOOLS
REMOTE = '/home/ubuntu/pg3154-browser-business-owned-stage-v1'
ARCHIVE = 'pg3154-v1-' + TOOLS + '.tar'
POST_SLOT = 'pg3146-browser-business-full-seal-v1'


def namespace():
    base = previous.previous.prior.previous
    ns = {**base.__dict__, 'GUEST': GUEST, 'REMOTE': REMOTE, 'ARCHIVE': ARCHIVE, 'POST_SLOT': POST_SLOT, 'sources': sources, 'context': context, 'SOURCE': SOURCE, 'TOOLS': TOOLS, 'candidate_bom': lambda: BOM, 'payload': seal_payload}
    for fn in [base.stage, base.post_payload, base.run_source, base.run_action, base.main]:
        exec(compile(bind(inspect.getsource(fn)), '<closed actual Browser owned dispatch>', 'exec'), ns)
    stage, run = ns['stage'], ns['run_source']
    ns['stage'] = lambda: bind(stage())
    ns['run_source'] = lambda: bind(run())
    return ns


def stage():
    return namespace()['stage']()


def run_source():
    return namespace()['run_source']()


def main():
    return namespace()['main']()


if __name__ == '__main__':
    raise SystemExit(main())
