"""Independent current original/24/native/resources post; no restart or Root authority."""
import inspect
import pg4048_literal_invariant_owned_post as previous
import pg4652_current_owned_sources as role
from pg4584_current_admission_image import live

SLOT='pg4658-current-owned-post-v1'


def namespace():
    ns={**vars(previous),'role':role,'SLOT':SLOT}
    exec(compile(inspect.getsource(previous.namespace),'<new current independent owned post>','exec'),ns)
    result=ns['namespace']()
    def payload(seals):
        b=live();value={'binding':{k:v for k,v in b.items()if k!='rootPid'},'rootPid':b['rootPid']}
        return result['emit'](seals,role.context(),value)
    result['payload']=payload;return result


if __name__=='__main__':raise SystemExit(namespace()['entry']()())
