"""Same independent full72 post plus PID1 RO mount and genuine normal receipt."""
import json
from pyflakes.api import check
import pg4870_ssc301_302_unused_post as unused_post
import pg4872_ssc301_302_ro_sources as role
from pg3786_hygiene_ro_post import EXTRA

SLOT='pg4878-ssc301-302-ro-independent-post-v1'


def payload():
    role.qualify();raw=unused_post.payload()
    marker='save=base/'+repr(unused_post.SLOT)
    if raw.count(marker)!=1:raise ValueError('one private evidence-only RO output')
    raw=raw.replace(marker,'save=base/'+repr(SLOT),1)
    extra=EXTRA.replace('PG3748','PG4860').replace('pg3784-hygiene-ro-completed-v1',role.SAVE)
    marker="    proof = {p.name: {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size} for p in root.iterdir() if p.is_file()}"
    if raw.count(marker)!=1:raise ValueError('one held-tenRef candidate RO proof boundary')
    raw=raw.replace(marker,'\n'.join('    '+line for line in extra.strip().splitlines())+'\n'+marker,1)
    marker="**candidate_post,'newTenReferencesReturnedNormally':len(refs)==10"
    if raw.count(marker)!=1:raise ValueError('one after-normal-close result')
    raw=raw.replace(marker,marker+",'candidateHostReadonlyVerified':True",1)
    if check(raw,'<whole72/24/187 PID1RO independent post>'):raise ValueError('complete emitted static0')
    return raw


def main():
    actual=json.loads((role.W/'pg4876-prepare-ro-v1.safe.json').read_bytes())
    if not(type(actual.get('actualExit'))is int and actual['actualExit']==0 and actual.get('sourceQualified')is True
           and actual.get('candidateSource')==role.SOURCE and actual.get('currentApprovalEpochChanged')is False):
        raise ValueError('actual current825e/newcandidate RO completion first')
    return unused_post.current.completed.role.before.admission.execute(SLOT,payload(),180)


if __name__=='__main__':raise SystemExit(main())
