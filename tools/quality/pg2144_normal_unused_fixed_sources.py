"""BUG1213 normal parent literal fix in a new-only whole unused graph."""
from pg2132_current_normal_unused_sources import sources as prior, BEFORE

TOOLS='pg2144-current-normal-unused-tools-v1'
SAVE='pg2148-current-normal-unused-placement-v1'
ARCHIVE='pg2146-current-normal-release-v1.tar'
REMOTE='/home/ubuntu/pg2146-current-normal-input-v1'


def bind(raw):
    for old,new in [('pg2132','pg2144'),('Pg2132','Pg2144'),('PG2132','PG2144'),('pg2136','pg2148'),('PG2136','PG2148'),('pg2134','pg2146'),('PG2134','PG2146')]:raw=raw.replace(old,new)
    return raw


def sources(bom,before=BEFORE):
    result={bind(n):bind(raw)for n,raw in prior(bom,before).items()}
    name='pg2144_native_refs.py';raw=result[name]
    old="parent_config=={'Type':'oneshot','SuccessExitStatus':''}"
    if raw.count(old)!=1:raise ValueError('one obsolete warning setting boundary required')
    result[name]=raw.replace(old,"parent_config=={'Type':'oneshot','SuccessExitStatus':'10'}")
    for raw in result.values():
        if "parent_config=={'Type':'oneshot','SuccessExitStatus':''}"in raw:
            raise ValueError('old warning setting must not survive normal graph')
    return result
