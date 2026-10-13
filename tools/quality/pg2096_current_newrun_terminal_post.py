"""Separate exact newrun stopped rows/assets/native/current ten kernel/actor/resource post."""
import inspect
import re
import pg2040_fresh_normal_warning_terminal_post as previous
from pg2090_current_newrun_owned_stop_sources import context,TOOLS

SLOT='pg2096-current-newrun-terminal-post-v1'


def payload(seals):
    before,owned,done,utc=context();old_before,old_owned,old_done,old_utc=previous.context()
    raw=previous.payload(seals)
    pairs=[('pg2030','pg2090'),('Pg2030','Pg2090'),('PG2030','PG2090'),('pg2090-fresh-normal-warning-owned-stop-tools-v1',TOOLS),(old_before,before),(old_utc,utc),('pg2025-fresh-resume-full-live-seal-v1','pg2085-native-augmented-newrun-full-seal-v1'),(previous.SLOT,SLOT),('1eb0d77ce4704e7481ecc07beddcdf0c','2c37fef2a2ff48e7b6a05cfc23f84c19'),('4148e3e8-f107-431a-ab27-d6e6d1f1772e','a31dd6da-cf4c-4d0f-ab7c-5c8bb59c0b75'),('2026-10-12T18:20:32.598894Z','2026-10-13T03:08:18.452473Z'),('e31b627c-c0e2-4120-bd64-c0777479e800','9026b2ab-bb42-49cd-a2bd-4c661049dce3')]
    numbers={'106318294326':'113070840714','108118294326':'114870840714','187092':'204748','503613':'588342',str(old_done['endMonotonicUs']):str(done['endMonotonicUs'])}
    for u,v in old_owned.items():pairs.append((v[1],owned[u][1]));numbers[v[0]]=owned[u][0]
    for old,new in pairs:raw=raw.replace(old,new)
    for old,new in numbers.items():raw=re.sub(r'\b'+re.escape(old)+r'\b',new,raw)
    from pyflakes.api import check
    if check('HASHES={}\nRECEIPT="fixed"\n'+raw,'<whole current newrun terminal post>'):raise ValueError('all actual post globals required')
    compile(raw,'<current newrun all stopped post>','exec');return raw


def entry():
    raw=inspect.getsource(previous.main)
    for old,new in [('pg2038-stop-v1','pg2092-stop-v1'),('pg2031-frozen-v1','pg2091-frozen-v1'),('pg2030_parent_receipt.py','pg2090_parent_receipt.py'),('pg2030-native-stop-v1','pg2090-native-stop-v1')]:raw=raw.replace(old,new)
    ns={**previous.__dict__,'SLOT':SLOT,'TOOLS':TOOLS,'payload':payload}
    exec(compile(raw,'<new current stopped post entry>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
