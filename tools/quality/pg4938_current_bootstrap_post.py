"""SSC303 actual captured20 then current whole/credentials/resources, never GC success."""
import inspect
from types import SimpleNamespace
import pg4828_new_current_bootstrap_post as previous
import pg4932_current_bootstrap_sources as role
import pg4936_current_bootstrap_dispatch as dispatch

SLOT='pg4938-current-bootstrap-post-v1'


def source():return inspect.getsource(previous.payload).replace('pg4820','pg4932')


def payload():
    current_dispatch=SimpleNamespace(fixed=dispatch.namespace()['fixed'],SLOT=dispatch.SLOT)
    current_role=SimpleNamespace(**{**vars(role),'template':role.previous.template})
    ns={**vars(previous),'role':current_role,'dispatch':current_dispatch,'SLOT':SLOT}
    exec(compile(source(),'<current captured20 full independent post>','exec'),ns)
    return ns['payload']()


if __name__=='__main__':raise SystemExit(role.before.admission.execute(SLOT,payload(),120))
