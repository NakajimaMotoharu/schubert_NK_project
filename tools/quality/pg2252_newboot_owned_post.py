"""Independent current-boot all-assets stopped post; no lifecycle replay."""
import inspect
import json
import re
from pyflakes.api import check
import pg2194_newsource_owned_stop_post as prior
from pg2246_newboot_owned_sources import context,TOOLS,SOURCE,BOM
from pg2208_current_newboot_cold_sources import BOOT
from pg1446_current_cold_stage import W

SLOT='pg2252-newboot-owned-stop-post-v1'


def emit_payload(seals,new_context,live):
    before,owned,done,utc=new_context;old_before,old_owned,old_done,old_utc=prior.context()
    old_live=json.loads((W/'pg2180-newsource-live-binding-v1/manifest.safe.json').read_bytes());old_b=old_live['binding'];b=live['binding']
    raw=prior.payload(seals)
    pairs=[(prior.TOOLS,TOOLS),('pg2188','pg2246'),('Pg2188','Pg2246'),('PG2188','PG2246'),(old_before,before),(old_utc,utc),('pg2186-newsource-full-live-seal-v1','pg2242-newboot-fresh-day-full-seal-v1'),(prior.SLOT,SLOT),('3d69f5af-6bac-46b1-a540-7591c4a79a0d',BOOT),('3d69f5af6bac46b1a5407591c4a79a0d',BOOT.replace('-',''))]
    pairs.extend((old_b[k],b[k])for k in ['invocation','run','cutoff','activation'])
    numbers={str(old_b['start']):str(b['start']),str(old_b['start']+1800000000):str(b['start']+1800000000),old_b['job']:b['job'],str(old_live['rootPid']):str(live['rootPid']),str(old_done['endMonotonicUs']):str(done['endMonotonicUs'])}
    for unit,v in old_owned.items():pairs.append((v[1],owned[unit][1]));numbers[v[0]]=owned[unit][0]
    for old,new in pairs:raw=raw.replace(old,new)
    for old,new in numbers.items():raw=re.sub(r'\b'+re.escape(old)+r'\b',new,raw)
    raw=raw.replace('PG2040-fresh-normal-warning-terminal-post-v1','PG2252-newboot-owned-stop-post-v1')
    if check('HASHES={}\nRECEIPT="actual"\n'+raw,'<current newboot all stopped post>'):raise ValueError('whole stopped exports required')
    compile(raw,'<current independent stopped post>','exec');return raw


def payload(seals):
    live=json.loads((W/'pg2230-newboot-current-live-binding-v1/manifest.safe.json').read_bytes())
    return emit_payload(seals,context(),live)


def entry():
    raw=inspect.getsource(prior.prior.previous.main)
    for old,new in [('pg2038-stop-v1','pg2248-stop-v1'),('pg2031-frozen-v1','pg2247-frozen-v1'),('pg2030_parent_receipt.py','pg2246_parent_receipt.py'),('pg2030-native-stop-v1','pg2246-native-stop-v1')]:raw=raw.replace(old,new)
    ns={**prior.prior.previous.__dict__,'SLOT':SLOT,'TOOLS':TOOLS,'SOURCE':SOURCE,'BOM':BOM,'payload':payload}
    exec(compile(raw,'<current newboot independent stopped post entry>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
