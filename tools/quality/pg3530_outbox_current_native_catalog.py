"""Current4856 native eligibility only; preserve olda9 copies, never import them."""
import inspect
import json
from pyflakes.api import check
import pg2254_newboot_native_catalog as template
import pg2042_fresh_normal_warning_native_catalog as transport
from pg3520_outbox_owned_sources_v2 import SOURCE, BOM, TOOLS
from pg3434_current_outbox_candidate_sources import BOOT
from pg3470_outbox_admission_before import before
from pg1446_current_cold_stage import W

SLOT = 'pg3530-outbox-current-native-catalog-v1'
ONCE = 'pg3464-outbox-current-noargs-once-v1'


def current(binding, end):
    live=json.loads((W/'pg3466-outbox-current-live-binding-v1/manifest.safe.json').read_bytes())
    term=json.loads((W/'pg3472-outbox-current-terminal-v1/manifest.safe.json').read_bytes())
    if (type(binding)is not dict or binding!=live['binding']or type(end)is not int
            or end!=term['endMonotonicUs']or live['actualExit']!=0 or term['actualExit']!=0
            or term['productionSource']!=SOURCE or not term['genuineParentDone']):
        raise ValueError('same actual current Root and terminal required')


def catalog_source(receipt, binding, end):
    current(binding,end)
    header=receipt+'\n';raw=template.catalog_source(receipt,binding,end)
    if not raw.startswith(header):raise ValueError('immutable qualified receipt prefix required')
    raw=raw[len(header):]
    for old,new in [(template.TOOLS,TOOLS),('pg2246','pg3520'),('Pg2246','Pg3520'),
                    ('PG2246','PG3520'),(template.SOURCE,SOURCE),(template.BOOT,BOOT),
                    (template.BOOT.replace('-',''),BOOT.replace('-',''))]:raw=raw.replace(old,new)
    start=raw.index('frozen=json.loads(');end_admission=raw.index('native=pathlib.Path',start)
    admission=r'''
frozen_raw=(base/ONCE/'before.private.json').read_bytes()
require(hashlib.sha256(frozen_raw).hexdigest()==BEFORE)
frozen=json.loads(frozen_raw)
require(set(frozen)=={'backup','configuration','extraDurable','native','originals','pid1','rows','runtime','startup','unitFilesActual','units'}and len(frozen['rows'])==24)
require(len(frozen['native'])==35 and sum(pathlib.Path(p).suffix=='.exec'for p in frozen['native'])==22)
issued=json.loads((base/ONCE/'external-start-guard.private.json').read_bytes())
require(issued['source']==CURRENT_SOURCE and issued['manifestSha256']==CURRENT_BOM and issued['ordinaryNoargs']is True and issued['oldCompletedRunNotResumed']is True and issued['originalBudgetSeconds']==1800 and issued['attemptReserved']is True and issued['replayAllowed']is False)
old=json.loads((base/ONCE/'native-before-manifest.private.json').read_bytes());require(len(old)==22)
for relative,item in old.items():
 require(not pathlib.PurePosixPath(relative).is_absolute()and '..'not in pathlib.PurePosixPath(relative).parts)
 p=base/ONCE/'native-before-private'/relative;s=p.lstat()
 require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and s.st_size==item['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']and not os.listxattr(p))
 original=frozen['native']['/run/schubert-nk/pt-coverage/'+relative]
 require(original['sha256']==item['sha256']and original['metadata'][6]==item['bytes'])
'''
    raw=raw[:start]+admission+raw[end_admission:]
    raw=raw.replace("'currentBootHadNoHistoricalNative':True", "'oldSource22CopiesPreserved':True,'oldSourceNativeImported':False")
    raw='\n'.join(['import os',"ONCE="+repr(ONCE),"BEFORE="+repr(before()),"CURRENT_SOURCE="+repr(SOURCE),"CURRENT_BOM="+repr(BOM)])+'\n'+raw
    if any(x in raw for x in ['pg2246','pg2227',template.SOURCE,template.BOOT,'currentBootHadNoHistoricalNative']):
        raise ValueError('historical positive catalog role leaked')
    raw=header+raw
    if check('SEALS={}\n'+raw,'<current4856 independent native catalog>'):
        raise ValueError('complete emitted catalog globals required')
    compile(raw,'<current4856 native eligibility>','exec');return raw


def main():
    live=json.loads((W/'pg3466-outbox-current-live-binding-v1/manifest.safe.json').read_bytes())
    term=json.loads((W/'pg3472-outbox-current-terminal-v1/manifest.safe.json').read_bytes())
    current(live['binding'],term['endMonotonicUs'])
    raw=inspect.getsource(transport.main).replace('pg2040-fresh-normal-warning-terminal-post-v1','pg3526-outbox-owned-post-v2').replace('pg2030_parent_receipt.py','pg3520_parent_receipt.py')
    ns={**transport.__dict__,'SOURCE':SOURCE,'TOOLS':TOOLS,'SLOT':SLOT,
        'catalog_source':lambda receipt:catalog_source(receipt,live['binding'],term['endMonotonicUs'])}
    exec(compile(raw,'<current4856 native read-only transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
