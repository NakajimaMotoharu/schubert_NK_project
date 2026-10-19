"""Independent candidate PID1 RO mount plus unchanged current full11/native94."""
import json
from pyflakes.api import check
import pg5614_current_unused_post as unused_post
import pg5616_current_ro_sources as role
from pg3786_hygiene_ro_post import EXTRA

SLOT='pg5622-current-ro-independent-post-v1'


def payload():
    role.qualify();raw=unused_post.payload()
    marker='NEW_SLOT='+repr(unused_post.SLOT)
    if raw.count(marker)!=1:raise ValueError('one new RO post output identity')
    raw=raw.replace(marker,'NEW_SLOT='+repr(SLOT),1)
    extra='from pathlib import Path\n'+EXTRA.replace('PG3748','PG5598').replace('pg3784-hygiene-ro-completed-v1',role.SAVE)
    marker='    destination = base / NEW_SLOT'
    if raw.count(marker)!=1:raise ValueError('one still-held tenRef RO boundary')
    raw=raw.replace(marker,'\n'.join('    '+line if line else line for line in extra.strip().splitlines())+'\n'+marker,1)
    marker="'candidateUnusedOnly':True"
    if raw.count(marker)!=1:raise ValueError('one RO completion flag after all Ref normal return')
    raw=raw.replace(marker,marker+",'candidateHostReadonlyVerified':True",1)
    if check(raw,'<full11/native94/candidate PID1RO standalone>'):raise ValueError('complete independent RO post before stage')
    compile(raw,'<candidateRO, no publication/start permission>','exec')
    return raw


def main():
    value=json.loads((role.W/'pg5620-prepare-ro-v1.safe.json').read_bytes())
    wanted={'actualExit':0,'sourceQualified':True,'candidateSource':role.SOURCE,'currentApprovalEpochChanged':False}
    if any(type(value.get(k))is not type(v)or value[k]!=v for k,v in wanted.items()):raise ValueError('actual original RO prepare first')
    return unused_post.capture.admission.execute(SLOT,payload(),240)


if __name__=='__main__':raise SystemExit(main())
