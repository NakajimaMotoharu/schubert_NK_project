"""New-only corrected capture: strict after10 plus all40 native from existing same-source proof."""
import inspect
from pyflakes.api import check
import pg3840_current_full11_baseline as previous
from current_after_native_schema import expand,require,KEYS,PREFIX
from pg1446_current_cold_stage import W

SLOT='pg3842-current-full11-native-baseline-v1'


def payload():
    raw=previous.payload().replace(previous.SLOT,SLOT)
    marker="expected=json.loads(afterraw);require(len(expected)==11 and len(expected['rows'])==24 and len(expected['units'])==10)"
    if raw.count(marker)!=1:raise ValueError('one explicit legacy after10 consumer boundary')
    import json
    catalog=json.loads((W/'pg3830-hygiene-native-catalog-v1/manifest.safe.json').read_bytes())
    if catalog['actualExit']!=0 or catalog['productionSource']!=previous.SOURCE or len(catalog['selected'])!=10 or len(catalog['excludedHistorical'])!=30:raise ValueError('actual current40 provenance required')
    classifier='import re,stat\nfrom pathlib import PurePosixPath\nKEYS='+repr(KEYS)+'\nPREFIX='+repr(PREFIX)+'\n'+inspect.getsource(require)+'\n'+inspect.getsource(expand)+'\n'
    # Run the schema helper in its own namespace; do not replace the existing
    # full reader's require/metadata/units/oracle definitions.
    extra="""expected=json.loads(afterraw)
native_original=json.loads(Path('/var/lib/pgpt-s1-preservation/pg3802-hygiene-current-noargs-once-v1/before.private.json').read_bytes())
original_raw=Path('/var/lib/pgpt-s1-preservation/pg3802-hygiene-current-noargs-once-v1/before.private.json').read_bytes();require(hashlib.sha256(original_raw).hexdigest()=='4eb5ac214713b201394035938cb931796f8ec3e0a81885e319ee2993500def76')
schema={};exec(SCHEMA,schema)
native_now=tree(Path('/run/schubert-nk/pt-coverage'))
for name in native_now:require(not os.listxattr(name))
expected=schema['expand'](expected,native_now,native_original['native'],SELECTED,EXCLUDED,40)
require(native_now==tree(Path('/run/schubert-nk/pt-coverage'))and len(expected['rows'])==24 and len(expected['units'])==10)
"""
    raw='SCHEMA='+repr(classifier)+'\nSELECTED='+repr(catalog['selected'])+'\nEXCLUDED='+repr(catalog['excludedHistorical'])+'\n'+raw.replace(marker,extra)
    if check(raw,'<strict after10 plus actual native40 full11>'):raise ValueError('whole corrected baseline namespace')
    compile(raw,'<new-only full11 actual capture>','exec');return raw


def main():
    namespace={**previous.previous.__dict__,'CURRENT':previous.SOURCE,'BOM':previous.BOM,'SLOT':SLOT,'payload':payload}
    exec(compile(inspect.getsource(previous.previous.main),'<new-only corrected full11 observer>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
