"""Independent actual current post; explicit live receipt view, no restart authority."""
import inspect
import pg4048_literal_invariant_owned_post as previous
import pg4282_current_owned_sources as role
from pg4260_stable_admission_image import live

SLOT='pg4288-current-owned-post-v1'


def namespace():
    ns={**vars(previous),'role':role,'SLOT':SLOT}
    exec(compile(inspect.getsource(previous.namespace),'<current independent post namespace>','exec'),ns)
    result=ns['namespace']()
    def payload(seals):
        b=live();value={'binding':{k:v for k,v in b.items()if k!='rootPid'},'rootPid':b['rootPid']}
        return result['emit'](seals,role.context(),value)
    result['payload']=payload
    return result


if __name__=='__main__':raise SystemExit(namespace()['entry']()())
