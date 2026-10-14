"""Strict ten actual current activation points; pre-resume ten copies remain data only."""
import inspect
import json
from pyflakes.api import check
import pg2382_current_resume_native_catalog as previous
from pg1446_current_cold_stage import W
from pg3006_current_resume_owned_sources import SOURCE, TOOLS, BOM

SLOT = 'pg3022-current-resume-native-catalog-v1'


def catalog_source(receipt, binding, end):
    raw = previous.catalog_source(receipt, binding, end)
    header = receipt + '\n'
    if not raw.startswith(header):
        raise ValueError('immutable actual receipt prefix required')
    raw = raw[len(header):]
    for a, b in [(previous.TOOLS, TOOLS), ('pg2374', 'pg3006'), ('Pg2374', 'Pg3006'), ('PG2374', 'PG3006'), (previous.SOURCE, SOURCE), ('pg2360-current-completed-resume-once-v1', 'pg2984-current-fresh-resume-once-v1'), (previous.BEFORE, 'd10735e678e5053c0c96c55a42f65f2302132cfae902edd81dffbc2275c4c4ac'), (previous.NATIVE, '96757f38127024e527c5356308e1d6337fb1bb50b2e258283bf2d2fc00376423'), (previous.RUN, '0dc63b79-3f9a-450c-b2a6-56f86272d272'), ('b2d6f605-61cf-425f-8fbd-12d606f6ee66', '79a3260a-e16d-42bf-942a-b914ed144c28'), ('b2d6f60561cf425f8fbd12d606f6ee66', '79a3260ae16d42bf942ab914ed144c28')]:
        raw = raw.replace(a, b)
    start = raw.index("snapshot_raw=(base/'pg2356-current-runtime-verification-post-v1/after.private.json')")
    end_marker = "for relative,item in old.items():"
    finish = raw.index(end_marker, start)
    anchor = """snapshot_raw=(base/'pg2964-retained-full-pair-proof-v1/proof.private.json').read_bytes()
require(hashlib.sha256(snapshot_raw).hexdigest()=='c1170b22495c28a114640f2f1153c92c9fa673431b0fc35e4e0039d0ca9cb510')
snapshot=json.loads(snapshot_raw);require(snapshot['signals0']is True and snapshot['all24And187OriginalBackupUnchanged']is True and hashlib.sha256(json.dumps(snapshot['native'],sort_keys=True).encode()).hexdigest()==NATIVE_SHA)
require(issued['manifestSha256']==CURRENT_BOM)
"""
    raw = 'CURRENT_BOM=' + repr(BOM) + '\n' + raw[:start] + anchor + raw[finish:]
    raw = header + raw
    if check('SEALS={}\n' + raw, '<actual current resume ten native points>'):
        raise ValueError('complete actual catalog exports required')
    compile(raw, '<actual current resume ten native points>', 'exec')
    return raw


def main():
    live = json.loads((W / 'pg2990-current-resume-live-binding-v1/manifest.safe.json').read_bytes())
    term = json.loads((W / 'pg2992-current-resume-terminal-v1/manifest.safe.json').read_bytes())
    if live['actualExit'] != 0 or term['actualExit'] != 0 or live['productionSource'] != SOURCE or term['productionSource'] != SOURCE:
        raise ValueError('actual current normal terminal required')
    raw = inspect.getsource(previous.previous.transport.main).replace('pg2040-fresh-normal-warning-terminal-post-v1', 'pg3012-current-resume-owned-post-v1').replace('pg2030_parent_receipt.py', 'pg3006_parent_receipt.py')
    ns = {**previous.previous.transport.__dict__, 'SOURCE': SOURCE, 'TOOLS': TOOLS, 'SLOT': SLOT, 'catalog_source': lambda receipt: catalog_source(receipt, live['binding'], term['endMonotonicUs'])}
    exec(compile(raw, '<current actual native catalog transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
