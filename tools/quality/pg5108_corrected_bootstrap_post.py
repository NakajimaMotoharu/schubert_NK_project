"""Independent corrected20 captured terminal before currentGC/all-resources, unchanged oracle."""
import inspect
from types import SimpleNamespace
import pg4828_new_current_bootstrap_post as template
import pg5102_corrected_bootstrap_sources as role
import pg5106_corrected_bootstrap_dispatch as dispatch

SLOT = 'pg5108-corrected-bootstrap-post-v1'


def payload():
    current_dispatch = SimpleNamespace(fixed=dispatch.namespace()['fixed'], SLOT=dispatch.SLOT)
    current_role = SimpleNamespace(**{**vars(role), 'template': role.previous.previous.previous.template})
    ns = {**vars(template), 'role': current_role, 'dispatch': current_dispatch, 'SLOT': SLOT}
    raw = inspect.getsource(template.payload).replace('pg4820', 'pg5102')
    exec(compile(raw, '<same source corrected20 independent post>', 'exec'), ns)
    return ns['payload']()


if __name__ == '__main__':
    raise SystemExit(role.before.admission.execute(SLOT, payload(), 180))
