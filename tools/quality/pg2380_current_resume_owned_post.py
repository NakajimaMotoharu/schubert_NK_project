"""Independent current-generation stopped post, with no repeated stop/start action."""
import inspect
import json
import re
from pyflakes.api import check
import pg2280_current_signed_owned_post as previous
from pg2374_current_resume_owned_sources import context,TOOLS,SOURCE,BOM
from pg1446_current_cold_stage import W

SLOT='pg2380-current-resume-owned-post-v1'


def emit(seals,ctx,live):
    old_before,old_owned,old_done,old_utc=previous.prior.context();before,owned,done,utc=ctx
    old_live=json.loads((W/'pg2230-newboot-current-live-binding-v1/manifest.safe.json').read_bytes());old_b=old_live['binding'];b=live['binding']
    raw=previous.payload(seals)
    pairs=[(previous.TOOLS,TOOLS),('pg2274','pg2374'),('Pg2274','Pg2374'),('PG2274','PG2374'),(previous.SLOT,SLOT),('PG2281-current-signed-owned-post-v2','PG2380-current-resume-owned-post-v1'),('pg2242-newboot-fresh-day-full-seal-v1','pg2368-current-resume-full-seal-v1'),(old_before,before),(old_utc,utc)]
    pairs.extend((old_b[k],b[k])for k in ['invocation','run','cutoff','activation'])
    numbers={str(old_b['start']):str(b['start']),str(old_b['start']+1800000000):str(b['start']+1800000000),old_b['job']:b['job'],str(old_live['rootPid']):str(live['rootPid']),str(old_done['endMonotonicUs']):str(done['endMonotonicUs'])}
    for unit,v in old_owned.items():pairs.append((v[1],owned[unit][1]));numbers[v[0]]=owned[unit][0]
    for a,z in pairs:raw=raw.replace(a,z)
    for a,z in numbers.items():raw=re.sub(r'\b'+re.escape(a)+r'\b',z,raw)
    # The stop's own sealed snapshot is not the independent pre-stop oracle.
    # Bind unchanged durable/DB fields back to the separately authenticated
    # current full-seal image, never to a historical successful stop.
    marker="after = json.loads(sealed("
    start=raw.index(marker);end=raw.index('\n',start)
    guard="\noriginal_raw=(base/'pg2368-current-resume-full-seal-v1/before.private.json').read_bytes()\nrequire(hashlib.sha256(original_raw).hexdigest()=="+repr(before)+")\noriginal=json.loads(original_raw)\nrequire(original['source']=="+repr(SOURCE)+" and original['manifestSha256']=="+repr(BOM)+")\nrequire(before['rows']==original['rows'] and before['startup']==original['startup'])\nrequire(before['originals']==original['durable']['originals'] and before['backup']==original['durable']['backup'])\nrequire(before['extraDurable']=={k:original['durable'][k]for k in ['credentials','oldProofs']})\n"
    raw=raw[:end]+guard+raw[end:]
    if check('HASHES={}\nRECEIPT="fixed"\n'+raw,'<current independent stopped post>'):raise ValueError('all current stopped globals required')
    compile(raw,'<current all asset stopped post>','exec');return raw


def payload(seals):
    live=json.loads((W/'pg2362-current-resume-live-binding-v1/manifest.safe.json').read_bytes())
    return emit(seals,context(),live)


def entry():
    raw=inspect.getsource(previous.prior.prior.prior.previous.main)
    for a,z in [('pg2038-stop-v1','pg2376-stop-v1'),('pg2031-frozen-v1','pg2375-frozen-v1'),('pg2030_parent_receipt.py','pg2374_parent_receipt.py'),('pg2030-native-stop-v1','pg2374-native-stop-v1')]:raw=raw.replace(a,z)
    ns={**previous.prior.prior.prior.previous.__dict__,'SLOT':SLOT,'TOOLS':TOOLS,'SOURCE':SOURCE,'BOM':BOM,'payload':payload}
    exec(compile(raw,'<current separate stopped entry>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
