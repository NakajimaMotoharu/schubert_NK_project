"""Actual new current ten points; preserve old-source sixteen copies, never import them."""
import inspect
import json
from pyflakes.api import check
import pg2254_newboot_native_catalog as prior
from pg2458_question_current_owned_sources import SOURCE,TOOLS
from pg2454_question_current_rows import BEFORE
from pg1446_current_cold_stage import W

SLOT='pg2466-question-current-native-catalog-v1'


def catalog_source(receipt,binding,end):
    raw=prior.catalog_source(receipt,binding,end);header=receipt+'\n'
    if not raw.startswith(header):raise ValueError('independent receipt prefix required')
    raw=raw[len(header):].replace(prior.TOOLS,TOOLS).replace('pg2246','pg2458').replace('Pg2246','Pg2458').replace('PG2246','PG2458')
    start=raw.index('frozen=json.loads(');stop=raw.index('native=pathlib.Path',start)
    admission="""frozen_raw=(base/'pg2448-question-current-noargs-once-v1/before.private.json').read_bytes()
require(hashlib.sha256(frozen_raw).hexdigest()==BEFORE_SHA)
frozen=json.loads(frozen_raw);require(len(frozen['rows'])==24 and len(frozen['units'])==10)
issued=json.loads((base/'pg2448-question-current-noargs-once-v1/external-start-guard.private.json').read_bytes())
require(issued['source']==SOURCE and issued['ordinaryNoargs']is True and issued['oldCompletedRunNotResumed']is True and issued['originalBudgetSeconds']==1800 and issued['replayAllowed']is False)
old=json.loads((base/'pg2448-question-current-noargs-once-v1/native-before-manifest.private.json').read_bytes());require(len(old)==16)
for relative,item in old.items():
 require(not pathlib.PurePosixPath(relative).is_absolute()and '..'not in pathlib.PurePosixPath(relative).parts)
 p=base/'pg2448-question-current-noargs-once-v1/native-before-private'/relative
 s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and s.st_size==item['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']and not os.listxattr(p))
 original=frozen['native']['/run/schubert-nk/pt-coverage/'+relative]
 require(original['sha256']==item['sha256']and original['metadata'][6]==item['bytes'])
"""
    raw=raw[:start]+admission+raw[stop:]
    raw=raw.replace("'currentBootHadNoHistoricalNative':True","'priorOldSourceSixteenCopiesPreserved':True,'priorOldSourcePointsImported':False")
    raw=header+'import os\nBEFORE_SHA='+repr(BEFORE)+'\nSOURCE='+repr(SOURCE)+'\n'+raw
    if check('SEALS={}\n'+raw,'<new current actual point catalogue>'):raise ValueError('all actual point globals required')
    compile(raw,'<new current actual native points>','exec');return raw


def main():
    live=json.loads((W/'pg2450-question-current-live-binding-v1/manifest.safe.json').read_bytes())
    term=json.loads((W/'pg2452-question-current-terminal-v1/manifest.safe.json').read_bytes())
    if live['actualExit']!=0 or term['actualExit']!=0:raise ValueError('actual current Root terminal required')
    raw=inspect.getsource(prior.transport.main).replace('pg2040-fresh-normal-warning-terminal-post-v1','pg2464-question-current-owned-post-v1').replace('pg2030_parent_receipt.py','pg2458_parent_receipt.py')
    ns={**prior.transport.__dict__,'SOURCE':SOURCE,'TOOLS':TOOLS,'SLOT':SLOT,
        'catalog_source':lambda receipt:catalog_source(receipt,live['binding'],term['endMonotonicUs'])}
    exec(compile(raw,'<new current point catalog observer>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
