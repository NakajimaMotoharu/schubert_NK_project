"""First new-source cohort only; all34 historical streams remain preserved, never credited."""
import inspect
import json
import types
from pyflakes.api import check
import pg3530_outbox_current_native_catalog as previous
import pg3808_hygiene_acceptance as root
from pg3802_hygiene_current_noargs_once import SLOT as ONCE
from pg3806_hygiene_admission_before import before
from pg3822_hygiene_owned_sources import SOURCE,BOM,TOOLS
from pg3788_hygiene_publication_sources import BOOT
from pg1446_current_cold_stage import W

SLOT='pg3830-hygiene-native-catalog-v1'


def qualify_context(live,terminal,binding,end):
    if type(binding)is not dict or binding!=live.get('binding')or type(end)is not int or end!=terminal.get('endMonotonicUs')or live.get('actualExit')!=0 or terminal.get('actualExit')!=0 or live.get('productionSource')!=SOURCE or terminal.get('productionSource')!=SOURCE or terminal.get('genuineParentDone')is not True:raise ValueError('same actual newsource Root and genuine terminal required')


def current(binding,end):
    live=json.loads((W/root.LIVE/'manifest.safe.json').read_bytes());terminal=json.loads((W/root.TERM/'manifest.safe.json').read_bytes());qualify_context(live,terminal,binding,end)


def catalog_source(receipt,binding,end):
    function=previous.catalog_source
    values={**function.__globals__,'current':current,'SOURCE':SOURCE,'BOM':BOM,'TOOLS':TOOLS,'BOOT':BOOT,'ONCE':ONCE,'before':before}
    raw=types.FunctionType(function.__code__,values)(receipt,binding,end)
    header=receipt+'\n'
    if not raw.startswith(header):raise ValueError('exact new terminal classifier prefix required')
    raw=raw[len(header):]
    marker="require(len(frozen['native'])==35 and sum(pathlib.Path(p).suffix=='.exec'for p in frozen['native'])==22)"
    if raw.count(marker)!=1:raise ValueError('one original native count contract')
    raw=raw.replace(marker,"require(sum(pathlib.Path(p).suffix=='.exec'for p in frozen['native'])==34 and all(pathlib.Path(p).is_relative_to('/run/schubert-nk/pt-coverage')for p in frozen['native']))")
    raw=raw.replace('require(len(old)==22)','require(len(old)==34)').replace('oldSource22CopiesPreserved','all34BeforeCopiesPreserved')
    for a,b in [('pg3520','pg3822'),('Pg3520','Pg3822'),('PG3520','PG3822')]:raw=raw.replace(a,b)
    raw=header+raw
    if check('SEALS={}\n'+raw,'<newsource native eligibility>'):raise ValueError('whole actual native namespace required')
    compile(raw,'<same-source ten points and historical34 copies only>','exec');return raw


def main():
    live=json.loads((W/root.LIVE/'manifest.safe.json').read_bytes());terminal=json.loads((W/root.TERM/'manifest.safe.json').read_bytes());current(live['binding'],terminal['endMonotonicUs'])
    raw=inspect.getsource(previous.transport.main).replace('pg2040-fresh-normal-warning-terminal-post-v1','pg3828-hygiene-owned-post-v1').replace('pg2030_parent_receipt.py','pg3822_parent_receipt.py')
    values={**previous.transport.__dict__,'SOURCE':SOURCE,'TOOLS':TOOLS,'SLOT':SLOT,'catalog_source':lambda receipt:catalog_source(receipt,live['binding'],terminal['endMonotonicUs'])}
    exec(compile(raw,'<newsource native catalog after exact owned post>','exec'),values);return values['main']()


if __name__=='__main__':raise SystemExit(main())
