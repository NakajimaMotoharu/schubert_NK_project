"""Actual newboot/a9 ten native points/latest nine; old native data never imported."""
import inspect
import json
from pyflakes.api import check
import pg2254_newboot_native_catalog as prior
from pg2890_network_owned_sources import SOURCE,TOOLS,bind
from pg1446_current_cold_stage import W
from pg2814_network_newboot_readonly import BOOT

SLOT='pg2906-network-current-native-catalog-v1'


def catalog_source(receipt,binding,end):
    raw=prior.catalog_source(receipt,binding,end)
    raw=bind(raw).replace(prior.TOOLS,TOOLS).replace('pg2246','pg2890').replace('Pg2246','Pg2890')
    raw=raw.replace(prior.BOOT,BOOT).replace(prior.BOOT.replace('-',''),BOOT.replace('-',''))
    start=raw.index('frozen=json.loads(');last=raw.index('native=pathlib.Path',start)
    original=json.loads((W/'pg2876-network-admission-original-v2/manifest.safe.json').read_bytes())['guest']['privateBeforeSha256']
    before="""frozen_raw=(base/'pg2872-network-newcurrent-noargs-once-v2/external-before.private.json').read_bytes()
require(hashlib.sha256(frozen_raw).hexdigest()==BEFORE_SHA)
frozen=json.loads(frozen_raw);require(set(frozen)=={'immutable','runtime','trees','observer'})
require(frozen['immutable']['boot']==BOOT_CURRENT and len(frozen['immutable']['rows'])==24)
require(set(frozen['runtime']['children'])=={'backup','cleanup','expiry','inspector','ordinary-api193','ordinary-bootstrap196','ordinary-inspector196','ordinary-web193','parent','root-api','root-api193','root-web193'}and all(v[5]==2 for v in frozen['runtime']['children'].values()))
issued=json.loads((base/'pg2872-network-newcurrent-noargs-once-v2/external-start-guard.private.json').read_bytes())
require(issued['source']==SOURCE_CURRENT and issued['boot']==BOOT_CURRENT and issued['ordinaryNoargs']is True and issued['oldCompletedRunNotResumed']is True and issued['originalBudgetSeconds']==1800 and issued['replayAllowed']is False)
native_before=json.loads((base/'pg2872-network-newcurrent-noargs-once-v2/native-before-manifest.private.json').read_bytes())
require(native_before=={'newBootRuntimeExecCount':0,'oldPreservedNativeImported':False})
old={} # Actual newboot before had empty native roles, not an old source stream.
"""
    raw=raw[:start]+before+raw[last:]
    raw='BEFORE_SHA='+repr(original)+'\nBOOT_CURRENT='+repr(BOOT)+'\nSOURCE_CURRENT='+repr(SOURCE)+'\n'+raw
    if check('SEALS={}\n'+raw,'<actual a9 currentboot ten points>'):raise ValueError('complete newboot catalog namespace required')
    compile(raw,'<current CRC session and Root/Inspector/Backup windows>','exec');return raw


def main():
    live=json.loads((W/'pg2874-network-newcurrent-live-binding-v1/manifest.safe.json').read_bytes())
    term=json.loads((W/'pg2878-network-newcurrent-terminal-v1/manifest.safe.json').read_bytes())
    if live.get('actualExit')!=0 or term.get('actualExit')!=0 or live['binding']['boot']!=BOOT.replace('-',''):
        raise ValueError('actual current Root/terminal boot required')
    raw=inspect.getsource(prior.transport.main)
    raw=raw.replace('pg2040-fresh-normal-warning-terminal-post-v1','pg2898-network-owned-post-v1').replace('pg2030_parent_receipt.py','pg2890_parent_receipt.py')
    ns={**prior.transport.__dict__,'SOURCE':SOURCE,'TOOLS':TOOLS,'SLOT':SLOT,
        'catalog_source':lambda receipt:catalog_source(receipt,live['binding'],term['endMonotonicUs'])}
    exec(compile(raw,'<newboot a9 actual current native catalogue>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
