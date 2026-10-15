"""Actual Browser-owned closing native; immutable receipt and all sixteen prefiles.

SS342/343/355, 451; PT-OPS-3186-001. Only RO guest operations, never a new run.
"""
import inspect
import json
from pyflakes.api import check
import pg3022_current_resume_native_catalog as previous
import pg2042_fresh_normal_warning_native_catalog as transport
from pg2025_fresh_resume_full_live_seal import constant
from pg1446_current_cold_stage import W
from pg3150_browser_business_owned_sources import SOURCE, TOOLS

SLOT = 'pg3186-browser-native-catalog-v1'
ONCE = 'pg3144-current-parent-receipt-resume-once-v1'
BEFORE = 'f041e0b3318db88e7b94cd40a23d28ba7e630d405e1b13f9ae397f03a1312f24'
NATIVE = 'ab3fcad3e4f842562c7cd4cd77c5966b81ffba6534cf153c549cc1a5588aa4e2'


def current(binding, end):
    expected = json.loads((W / 'pg3124-browser-resume-live-binding-v1/manifest.safe.json').read_bytes())
    term = json.loads((W / 'pg3130-browser-resume-terminal-v1/manifest.safe.json').read_bytes())
    if (type(binding) is not dict or binding != expected['binding'] or type(end) is not int
            or end != term['endMonotonicUs'] or term['actualExit'] != 0
            or term['genuineParentDone'] is not True or term['productionSource'] != SOURCE):
        raise ValueError('actual same Browser Root generation and terminal required')


def catalog_source(receipt, binding, end):
    current(binding, end)
    header = receipt + '\n'
    raw = previous.catalog_source(receipt, binding, end)
    if not raw.startswith(header):
        raise ValueError('immutable actual owned receipt prefix required')
    raw = raw[len(header):]
    for old, new in [(previous.TOOLS, TOOLS), ('pg3006', 'pg3150'),
                     ('Pg3006', 'Pg3150'), ('PG3006', 'PG3150'),
                     ('pg2984-current-fresh-resume-once-v1', ONCE),
                     ('len(old)==10', 'len(old)==16'),
                     ('priorSameSourceTenCopiesPreserved', 'priorSameSourceSixteenCopiesPreserved')]:
        raw = raw.replace(old, new)
    raw = constant(raw, 'BEFORE_SHA', BEFORE)
    raw = constant(raw, 'NATIVE_SHA', NATIVE)
    start = raw.index('snapshot_raw=')
    finish = raw.index('for relative,item in old.items():', start)
    raw = raw[:start] + "snapshot=frozen\nrequire(set(snapshot)=={'backup','configuration','extraDurable','originals','pid1','rows','runtime','startup','unitFilesActual','units','native'} and len(snapshot['rows'])==24 and hashlib.sha256(json.dumps(snapshot['native'],sort_keys=True).encode()).hexdigest()==NATIVE_SHA)\nrequire(issued['manifestSha256']==CURRENT_BOM)\n" + raw[finish:]
    if 'pg3006' in raw or 'pg2984' in raw or 'pg2964' in raw:
        raise ValueError('historical positive native admission leaked')
    raw = header + raw
    if check('SEALS={}\n' + raw, '<complete current Browser native catalog>'):
        raise ValueError('complete native catalog namespace required')
    compile(raw, '<current ten points and sixteen retained copies>', 'exec')
    return raw


def main():
    live = json.loads((W / 'pg3124-browser-resume-live-binding-v1/manifest.safe.json').read_bytes())
    term = json.loads((W / 'pg3130-browser-resume-terminal-v1/manifest.safe.json').read_bytes())
    current(live['binding'], term['endMonotonicUs'])
    raw = inspect.getsource(transport.main)
    raw = raw.replace('pg2040-fresh-normal-warning-terminal-post-v1', 'pg3156-browser-business-owned-post-v1').replace('pg2030_parent_receipt.py', 'pg3150_parent_receipt.py')
    ns = {**transport.__dict__, 'SOURCE': SOURCE, 'TOOLS': TOOLS, 'SLOT': SLOT,
          'catalog_source': lambda receipt: catalog_source(receipt, live['binding'], term['endMonotonicUs'])}
    exec(compile(raw, '<Browser native RO transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
