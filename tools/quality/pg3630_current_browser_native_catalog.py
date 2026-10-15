"""Current completed-resume native generation only, original current28 copies retained."""
import inspect
import json
import types
from pyflakes.api import check
import pg3530_outbox_current_native_catalog as template
from pg3600_current_browser_owned_sources import SOURCE,BOM,TOOLS
import pg3582_current_browser_acceptance as root
from pg3574_current_browser_resume_once import SLOT as ONCE
from pg1446_current_cold_stage import W

SLOT='pg3630-current-browser-native-catalog-v1'


def current(binding,end):
    live=root.live();term=json.loads((W/root.TERM/'manifest.safe.json').read_bytes())
    if binding!=live['binding']or term['actualExit']!=0 or term['productionSource']!=SOURCE or not term['genuineParentDone']or type(end)is not int or end!=term['endMonotonicUs']:
        raise ValueError('same actual current Browser Root and genuine terminal required')


def catalog_source(receipt,binding,end):
    fn=template.catalog_source
    raw=types.FunctionType(fn.__code__,{**fn.__globals__,'current':current,'TOOLS':TOOLS,'ONCE':ONCE,'before':lambda:root.BEFORE},'current_resume_native_catalog')(receipt,binding,end)
    old="require(len(frozen['native'])==35 and sum(pathlib.Path(p).suffix=='.exec'for p in frozen['native'])==22)"
    new="require(sum(pathlib.Path(p).suffix=='.exec'for p in frozen['native'])==28 and all(pathlib.Path(p).is_relative_to('/run/schubert-nk/pt-coverage')for p in frozen['native']))"
    if raw.count(old)!=1:raise ValueError('one exact original-native physical count admission required')
    # Whole eleven-field SHA pins every directory and leaf too; no len35-era
    # directory assumption is substituted for the newly sealed full snapshot.
    raw=raw.replace(old,new).replace('require(len(old)==22)','require(len(old)==28)')
    old="issued['ordinaryNoargs']is True and issued['oldCompletedRunNotResumed']is True"
    new="issued['freshCompletedRunResume']is True and issued['newActivationByProduction']is True and issued['selectedRun']=='e1ee096d-370b-4ab9-915a-7c124207e854'"
    if raw.count(old)!=1:raise ValueError('one explicit current completed-resume admission required')
    raw=raw.replace(old,new).replace('pg3520','pg3600').replace('Pg3520','Pg3600').replace('PG3520','PG3600')
    raw=raw.replace('oldSource22CopiesPreserved','all28BeforeCopiesPreserved')
    if BOM not in raw:raise ValueError('same current BOM required in final catalog')
    if check('SEALS={}\n'+raw,'<complete current Browser native generation>'):raise ValueError('complete native catalog exports required')
    compile(raw,'<current Browser native generation>','exec');return raw


def main():
    live=root.live();term=json.loads((W/root.TERM/'manifest.safe.json').read_bytes());current(live['binding'],term['endMonotonicUs'])
    raw=inspect.getsource(template.transport.main).replace('pg2040-fresh-normal-warning-terminal-post-v1','pg3606-current-browser-owned-post-v1').replace('pg2030_parent_receipt.py','pg3600_parent_receipt.py')
    ns={**template.transport.__dict__,'SOURCE':SOURCE,'TOOLS':TOOLS,'SLOT':SLOT,'catalog_source':lambda receipt:catalog_source(receipt,live['binding'],term['endMonotonicUs'])}
    exec(compile(raw,'<current Browser native catalog transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
