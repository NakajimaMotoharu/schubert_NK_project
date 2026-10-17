"""SSC303 actual captured20 then current whole/credentials/resources, never GC success."""
import inspect
import pg4828_new_current_bootstrap_post as previous
import pg4932_current_bootstrap_sources as role
import pg4936_current_bootstrap_dispatch as dispatch

SLOT='pg4938-current-bootstrap-post-v1'


def source():return inspect.getsource(previous.payload).replace('pg4820','pg4932')


def payload():
    ns={**vars(previous),'role':role,'dispatch':dispatch,'SLOT':SLOT}
    exec(compile(source(),'<current captured20 full independent post>','exec'),ns)
    return ns['payload']()


if __name__=='__main__':raise SystemExit(role.before.admission.execute(SLOT,payload(),120))
