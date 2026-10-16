"""Same full independent unused checks plus PID1 read-only mount and normal receipt."""
import json
from pyflakes.api import check
import pg4712_ssc299_unused_post as unused_post
import pg4714_ssc299_ro_sources as role
from pg3786_hygiene_ro_post import EXTRA as original_extra
from pg4584_current_admission_image import execute

SLOT='pg4720-ssc299-ro-independent-post-v1'


def payload():
    role.qualify();raw=unused_post.payload()
    for before,after in [("save = base / '"+unused_post.SLOT+"'","save = base / '"+SLOT+"'"),
                         ("'run': 'PG4712-ssc299-unused-post-v1'","'run': 'PG4720-ssc299-ro-independent-post-v1'")]:
        if raw.count(before)!=1:raise ValueError('one evidence-only RO output boundary')
        raw=raw.replace(before,after,1)
    extra=original_extra.replace('PG3748','PG4702').replace('pg3784-hygiene-ro-completed-v1',role.SAVE)
    point="    proof = {p.name: {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size} for p in root.iterdir() if p.is_file()}"
    if raw.count(point)!=1:raise ValueError('one before-owned-ref-close proof boundary')
    raw=raw.replace(point,'\n'.join('    '+line for line in extra.strip().splitlines())+'\n'+point,1)
    point='result["newTenReferencesReturnedNormally"]=len(refs)==10'
    if raw.count(point)!=1:raise ValueError('one after-normal-close success boundary')
    raw=raw.replace(point,point+'\nresult["candidateHostReadonlyVerified"]=True',1)
    if check(raw,'<full normal RO independent post>'):raise ValueError('all emitted globals required')
    compile(raw,'<candidate187 PID1RO/current full preservation>','exec')
    return raw


def main():
    actual=json.loads((role.W/'pg4718-prepare-ro-v1.safe.json').read_bytes())
    if not(type(actual.get('actualExit'))is int and actual['actualExit']==0
           and actual.get('sourceQualified')is True and actual.get('candidateSource')==role.SOURCE
           and actual.get('currentApprovalEpochChanged')is False):raise ValueError('genuine original RO action first')
    return execute(SLOT,payload(),180)


if __name__=='__main__':raise SystemExit(main())
