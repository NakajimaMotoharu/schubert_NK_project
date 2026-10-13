"""Separate same-source stopped all asset/config/native post; no stop replay."""
import inspect
import re
import pg2096_current_newrun_terminal_post as prior
from pg2188_newsource_owned_stop_sources import context,TOOLS,SOURCE,BOM

SLOT='pg2194-newsource-owned-stop-post-v1'


def payload(seals):
    new_before,owned,done,utc=context();old_before,old_owned,old_done,old_utc=prior.context()
    live=prior.previous.json.loads((prior.previous.W/'pg2180-newsource-live-binding-v1/manifest.safe.json').read_bytes());b=live['binding']
    raw=prior.payload(seals)
    pairs=[('pg2090','pg2188'),('Pg2090','Pg2188'),('PG2090','PG2188'),('pg2188-current-newrun-owned-stop-tools-v1',TOOLS),(old_before,new_before),(old_utc,utc),('pg2085-native-augmented-newrun-full-seal-v1','pg2186-newsource-full-live-seal-v1'),('0fd734195b4d5338f6b7e860e087cce561d49562',SOURCE),('ee75d0cd61457462eca59e67f5af2d8e677427071514940f3fb594ba93a026d7',BOM),('PG1846','PG2126'),('pg1846-manifest.sig','pg2126-manifest.sig'),('2c37fef2a2ff48e7b6a05cfc23f84c19',b['invocation']),('a31dd6da-cf4c-4d0f-ab7c-5c8bb59c0b75',b['run']),('2026-10-13T03:08:18.452473Z',b['cutoff']),('9026b2ab-bb42-49cd-a2bd-4c661049dce3',b['activation']),(prior.SLOT,SLOT)]
    numbers={'113070840714':str(b['start']),'114870840714':str(b['start']+1800000000),'204748':b['job'],'588342':str(live['rootPid']),str(old_done['endMonotonicUs']):str(done['endMonotonicUs'])}
    for u,v in old_owned.items():pairs.append((v[1],owned[u][1]));numbers[v[0]]=owned[u][0]
    for old,new in pairs:raw=raw.replace(old,new)
    for old,new in numbers.items():raw=re.sub(r'\b'+re.escape(old)+r'\b',new,raw)
    from pyflakes.api import check
    if check('HASHES={}\nRECEIPT="real"\n'+raw,'<actual newsource independent stopped post>'):raise ValueError('whole actual exports required')
    compile(raw,'<actual newsource independent stopped post>','exec');return raw


def entry():
    raw=inspect.getsource(prior.previous.main)
    for old,new in [('pg2038-stop-v1','pg2190-stop-v1'),('pg2031-frozen-v1','pg2189-frozen-v1'),('pg2030_parent_receipt.py','pg2188_parent_receipt.py'),('pg2030-native-stop-v1','pg2188-native-stop-v1')]:raw=raw.replace(old,new)
    ns={**prior.previous.__dict__,'SLOT':SLOT,'TOOLS':TOOLS,'SOURCE':SOURCE,'payload':payload}
    exec(compile(raw,'<newsource current stopped post entry>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
