"""Independent current original/24/native/all resource post; no lifecycle mutation."""
import inspect
import pg4048_literal_invariant_owned_post as previous
import pg2560_strict_current_owned_post as entry_source
import pg4772_new_current_owned_sources as role
from pg4752_new_current_admission_image import live,authenticate_host

SLOT='pg4778-new-current-owned-post-v1'


def namespace():
    ns={**vars(previous),'role':role,'SLOT':SLOT}
    exec(compile(inspect.getsource(previous.namespace),'<new normal owned full post>','exec'),ns)
    result=ns['namespace']()
    def payload(seals):
        b=live();qualified={'binding':{k:v for k,v in b.items()if k!='rootPid'},'rootPid':b['rootPid']}
        return result['emit'](seals,role.context(),qualified)
    result['payload']=payload
    raw=role.bind(inspect.getsource(entry_source.entry));env={**result['entry'].__globals__,'payload':payload}
    exec(compile(raw,'<original independent post entry factory>','exec'),env)
    if env['entry'].__code__.co_code!=result['entry'].__code__.co_code or env['entry'].__code__.co_consts!=result['entry'].__code__.co_consts:raise ValueError('exact actual post factory first')
    before="('pg2038-stop-v1', 'pg4776-stop-v1')"
    if raw.count(before)!=1:raise ValueError('one exact host stop receipt role')
    raw=raw.replace(before,"('pg2038-stop-v1', 'pg4806-stop-v1')",1)
    exec(compile(raw,'<actual successful continuation post factory>','exec'),env)
    result['entry']=env['entry'];return result


if __name__=='__main__':authenticate_host();raise SystemExit(namespace()['entry']()())
