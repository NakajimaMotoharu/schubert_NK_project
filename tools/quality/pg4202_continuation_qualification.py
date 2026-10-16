"""Qualify current76 tools once and publish only safe completed receipts; no VM actions."""
import hashlib
import inspect
import json
from pathlib import Path
import pg4190_partial_recovery_qualification as previous
from pg4192_publish_partial_qualification import main as publish_previous
import pg4200_metadata_continuation as continuation
from pyflakes.api import check


def main():
    ns={**vars(previous),'EXTRA':previous.EXTRA+['pg4200_metadata_continuation_test']}
    raw=inspect.getsource(previous.main).replace("'pg4190-partial-recovery-qualification-v1'","'pg4202-continuation-qualification-v1'")
    exec(compile(raw,'<76 tool qualification>','exec'),ns);ns['main']()
    if check(continuation.payload(),'<complete SSC289 continuation>'):raise ValueError('current complete continuation static0 required')
    paths=[Path(__file__),Path(continuation.__file__),Path(continuation.__file__).with_name('pg4200_metadata_continuation_test.py')]
    for p in paths:
        if check(p.read_text(),str(p)):raise ValueError('new host static0 required')
    publish_ns={**vars(__import__('pg4192_publish_partial_qualification')),
                'SLOTS':['pg4152-exact-failed-done-recover-v1','pg4196-partial-handoff-read-v1',
                         'pg4200-metadata-continuation-v1-stage','pg4200-metadata-continuation-v1-proof','pg4202-continuation-qualification-v1']}
    raw=inspect.getsource(publish_previous).replace('PG4192-partial-recovery-qualification-v1','PG4204-metadata-continuation-qualification-v1').replace('pg4190-partial-recovery-qualification-v1','pg4202-continuation-qualification-v1')
    raw=raw.replace('9d300bd12881a2fae3a1b42654c10cc9eb105e47',continuation.DESIGN_MAIN).replace('/pull/134','/pull/135')
    exec(compile(raw,'<safe continuation receipts>','exec'),publish_ns);publish_ns['main']()
    value={'actualExit':0,'continuationSha256':hashlib.sha256(continuation.payload().encode()).hexdigest(),'hostSourceHashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths},'productionPtAdded':0}
    (previous.W/'pg4202-continuation-qualification-v1/continuation.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k!='hostSourceHashes'}));return 0


if __name__=='__main__':raise SystemExit(main())
