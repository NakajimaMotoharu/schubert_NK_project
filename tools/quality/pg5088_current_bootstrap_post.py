"""Independent current captured20/credentials retired/allresources0; GC never proves success."""
import inspect
from types import SimpleNamespace
import pg4828_new_current_bootstrap_post as template
import pg5082_current_bootstrap_sources as role
import pg5086_current_bootstrap_dispatch as dispatch

SLOT = 'pg5088-current-bootstrap-post-v1'


def source():
    return inspect.getsource(template.payload).replace('pg4820', 'pg5082')


def payload():
    current_dispatch = SimpleNamespace(fixed=dispatch.namespace()['fixed'], SLOT=dispatch.SLOT)
    current_role = SimpleNamespace(**{**vars(role), 'template': role.previous.previous.template})
    ns = {**vars(template), 'role': current_role, 'dispatch': current_dispatch, 'SLOT': SLOT}
    exec(compile(source(), '<current actual20 full independent post>', 'exec'), ns)
    return ns['payload']()


if __name__ == '__main__':
    raise SystemExit(role.before.admission.execute(SLOT, payload(), 120))
