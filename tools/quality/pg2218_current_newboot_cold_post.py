"""Separate independent current full finite-preparation post; no prepare replay."""
import inspect
from pyflakes.api import check
import pg1453_current_cold_post as prior
from pg2208_current_newboot_cold_sources import observer,bindings,PREPARED
from pg1446_current_cold_stage import W

SLOT='pg2218-current-newboot-cold-independent-post-v1'


def payload():
    prefix=observer().split('import dbus,time,sys,types\n',1)[0]
    body=bindings(prior.BODY).replace('pg1453-current-cold-independent-post-v1',SLOT).replace('PG1453-current-cold-independent-post-v1','PG2218-current-newboot-cold-independent-post-v1').replace('pg1452-current-cold-prepared-v1',PREPARED)
    done='59f3b40104a9ea940779caac6aad6be6873e87f465a626e6f7860833c02d70a2'
    if body.count(done)!=1:raise ValueError('one exact old original proof required')
    body=body.replace(done,'25282e2790274c2564332c128125d3f18c77b78982aad4f96eb84c463ab3c91c')
    raw=prefix+'\n'+body
    if check(raw,'<whole actual current finite post>'):raise ValueError('whole actual namespace required')
    compile(raw,'<independent current finite post>','exec');return raw


def main():
    raw=inspect.getsource(prior.main).replace('pg1452-current-cold-owned-prepare-v1','pg2212-current-newboot-cold-owned-prepare-v1').replace('pg1453-current-cold-independent-post-v1',SLOT)
    ns={**prior.__dict__,'W':W,'payload':payload}
    exec(compile(raw,'<current finite post transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
