"""New immutable current fresh-resume owned stage/stop; no Root restart authority."""
import inspect
import pg2894_network_owned_dispatch as previous
from pg3006_current_resume_owned_sources import sources, context, SOURCE, TOOLS, bind
from pg2982_current_resume_observer import BOM
from pg3000_current_resume_full_seal import payload as seal_payload

GUEST = '/var/lib/pgpt-s1-preservation/' + TOOLS
REMOTE = '/home/ubuntu/pg3010-current-resume-owned-stage-v1'
ARCHIVE = 'pg3010-v1-' + TOOLS + '.tar'
POST_SLOT = 'pg3000-current-resume-full-seal-v1'


def namespace():
    base = previous.prior.previous
    ns = {**base.__dict__, 'GUEST': GUEST, 'REMOTE': REMOTE, 'ARCHIVE': ARCHIVE, 'POST_SLOT': POST_SLOT, 'sources': sources, 'context': context, 'SOURCE': SOURCE, 'TOOLS': TOOLS, 'candidate_bom': lambda: BOM, 'payload': seal_payload}
    for fn in [base.stage, base.post_payload, base.run_source, base.run_action, base.main]:
        exec(compile(bind(inspect.getsource(fn)), '<closed current fresh owned dispatch>', 'exec'), ns)
    stage = ns['stage']
    run = ns['run_source']
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
