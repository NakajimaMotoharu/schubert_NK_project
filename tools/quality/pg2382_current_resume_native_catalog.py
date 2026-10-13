"""Ten actual current activation points; previous same-source copies preserved, not imported."""
import inspect
import json
from pyflakes.api import check
import pg2254_newboot_native_catalog as previous
from pg2374_current_resume_owned_sources import SOURCE,TOOLS
from pg2360_current_completed_resume_once import BEFORE,NATIVE,RUN
from pg1446_current_cold_stage import W

SLOT='pg2382-current-resume-native-catalog-v1'


def catalog_source(receipt,binding,end):
    raw=previous.catalog_source(receipt,binding,end)
    # Prefix contains the independently qualified negative receipt; do not
    # replace its UUIDs when rebinding positive current body declarations.
    header=receipt+'\n'
    if not raw.startswith(header):raise ValueError('immutable receipt prefix required')
    raw=raw[len(header):].replace(previous.TOOLS,TOOLS).replace('pg2246','pg2374').replace('Pg2246','Pg2374').replace('PG2246','PG2374')
    start=raw.index('frozen=json.loads(');end_marker=raw.index("native=pathlib.Path",start)
    admission="""frozen_raw=(base/'pg2360-current-completed-resume-once-v1/before.private.json').read_bytes()
require(hashlib.sha256(frozen_raw).hexdigest()==BEFORE_SHA)
frozen=json.loads(frozen_raw);require(len(frozen['rows'])==24 and len(frozen['units'])==10)
issued=json.loads((base/'pg2360-current-completed-resume-once-v1/external-start-guard.private.json').read_bytes())
require(issued['source']==SOURCE and issued['freshCompletedRunResume']is True and issued['selectedRun']==RUN_ID and issued['originalBudgetSeconds']==1800 and issued['replayAllowed']is False)
old=json.loads((base/'pg2360-current-completed-resume-once-v1/native-before-manifest.private.json').read_bytes());require(len(old)==10)
snapshot_raw=(base/'pg2356-current-runtime-verification-post-v1/after.private.json').read_bytes()
require(hashlib.sha256(snapshot_raw).hexdigest()=='60bfaf9b2f28277088bcea565d920a6cd495914a58cf8ce9d6c90fe28f9045af')
snapshot=json.loads(snapshot_raw);require(snapshot['before']==frozen and hashlib.sha256(json.dumps(snapshot['native'],sort_keys=True).encode()).hexdigest()==NATIVE_SHA)
for relative,item in old.items():
 p=base/'pg2360-current-completed-resume-once-v1/native-before-private'/relative
 require(not pathlib.PurePosixPath(relative).is_absolute()and '..'not in pathlib.PurePosixPath(relative).parts)
 s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and s.st_size==item['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']and not os.listxattr(p))
 original=snapshot['native']['/run/schubert-nk/pt-coverage/'+relative]
 require(original['sha256']==item['sha256']and original['metadata'][6]==item['bytes'])
"""
    raw=raw[:start]+admission+raw[end_marker:]
    raw=raw.replace("'currentBootHadNoHistoricalNative':True","'priorSameSourceTenCopiesPreserved':True,'priorSameSourcePointsImported':False")
    raw='import os\nBEFORE_SHA='+repr(BEFORE)+'\nNATIVE_SHA='+repr(NATIVE)+'\nSOURCE='+repr(SOURCE)+'\nRUN_ID='+repr(RUN)+'\n'+raw
    raw=header+raw
    if check('SEALS={}\n'+raw,'<current resume native full closure>'):raise ValueError('all current native globals required')
    compile(raw,'<actual current ten native points>','exec');return raw


def main():
    live=json.loads((W/'pg2362-current-resume-live-binding-v1/manifest.safe.json').read_bytes())
    term=json.loads((W/'pg2364-current-resume-terminal-v1/manifest.safe.json').read_bytes())
    if live['actualExit']!=0 or term['actualExit']!=0:raise ValueError('actual current normal terminal required')
    raw=inspect.getsource(previous.transport.main).replace('pg2040-fresh-normal-warning-terminal-post-v1','pg2380-current-resume-owned-post-v1').replace('pg2030_parent_receipt.py','pg2374_parent_receipt.py')
    ns={**previous.transport.__dict__,'SOURCE':SOURCE,'TOOLS':TOOLS,'SLOT':SLOT,'catalog_source':lambda receipt:catalog_source(receipt,live['binding'],term['endMonotonicUs'])}
    exec(compile(raw,'<current actual native catalog transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
