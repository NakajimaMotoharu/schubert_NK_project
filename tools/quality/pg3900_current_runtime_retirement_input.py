"""Fresh current VM and exact stopped10/runtime input, data only and no retire authority."""
import inspect
import json
import pg3660_current_runtime_retirement_readonly as previous
from pg3876_current_resume_owned_sources import SOURCE,BOM
from pg1446_current_cold_stage import W

SLOT='pg3900-current-runtime-retirement-input-v1'
BASE='/var/lib/pgpt-s1-preservation/pg3876-native-stop-v1/after.private.json'
SHA='d6551955e6a99da0e1250cb94a932eeabc65d3078ea55edc6371b629fd45a6d8'


def payload():
    post=json.loads((W/'pg3882-current-resume-owned-post-v1/manifest.safe.json').read_bytes())
    if post['actualExit']!=0 or post['productionSource']!=SOURCE or not post['allClientAdvisoryFlock0']or post['proofHashes']['after.private.json']['sha256']!=SHA or post['nativePhysicalFiles']!=46:
        raise ValueError('actual current complete stopped/resource/native post required')
    raw=previous.payload()
    for old,new in [('pg3600-native-stop-v1/after.private.json','pg3876-native-stop-v1/after.private.json'),
                    ('e12ce6adc3a4c1641f099a4f01d4c35a7728a6a06c8bd68876e1fcdd7169d38e',SHA),
                    ('PG3420','PG3748'),('dc535a48a8d8d46ae5c33a442143e376c59b882a1e098ea7579e3f070fe92d72',BOM),
                    ('4856b3fcaeb4cae983d77757a38dc0bf56a693e2',SOURCE),('zz-pg3564-once-resume.conf','zz-pg3844-once-resume.conf')]:
        if old not in raw:raise ValueError('exact current stopped/runtime data role required '+old)
        raw=raw.replace(old,new)
    compile(raw,'<fresh current exact10/runtime read only>','exec');return raw


def main():
    transport=previous.transport
    values={**transport.__dict__,'SOURCE':SOURCE,'BOM':BOM,'SLOT':SLOT,'payload':payload}
    exec(compile(inspect.getsource(transport.main),'<fresh current VM runtime data observer>','exec'),values)
    return values['main']()


if __name__=='__main__':raise SystemExit(main())
