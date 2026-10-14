"""Independent newboot finite preparation post, never repeat preparation."""
import inspect
from pyflakes.api import check
import pg1453_current_cold_post as prior
import pg2208_current_newboot_cold_sources as historical
from pg2816_network_current_cold_sources import observer,bindings,PREPARED,DONE_SHA
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate

SLOT='pg2830-network-current-cold-independent-post-v1'


def payload():
    prefix=observer().split('import dbus,time,sys,types\n',1)[0]
    body=bindings(historical.bindings(prior.BODY))
    body=body.replace('pg1453-current-cold-independent-post-v1',SLOT).replace('PG1453-current-cold-independent-post-v1','PG2830-network-current-cold-independent-post-v1')
    body=body.replace('pg1452-current-cold-prepared-v1',PREPARED)
    old='59f3b40104a9ea940779caac6aad6be6873e87f465a626e6f7860833c02d70a2'
    if body.count(old)!=1:raise ValueError('one original Done SHA boundary required')
    body=body.replace(old,DONE_SHA)
    code=prefix+'\n'+body
    if check(code,'<independent finite current cold post>'):raise ValueError('complete independent post namespace required')
    compile(code,'<current finite cold independent post>','exec');return code


def main():
    raw=inspect.getsource(prior.main).replace('pg1452-current-cold-owned-prepare-v1','pg2822-network-current-cold-owned-prepare-v1').replace('pg1453-current-cold-independent-post-v1',SLOT)
    ns={**prior.__dict__,'payload':payload,'W':W}
    exec(compile(raw,'<newboot independent full post>','exec'),ns)
    with management_gate(P/'current-management-critical.lock'):return ns['main']()


if __name__=='__main__':raise SystemExit(main())
