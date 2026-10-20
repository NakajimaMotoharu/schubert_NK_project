"""Observe the original3955 host run only; no PT/start/stop/VM/database/rawlog action."""
import inspect
import json
import re
import pg5754_whole_observation as prior
from pg5808_rollback_whole import SOURCE,W,SLOT


def observer_source(begin):
    if begin['source']!=SOURCE or(begin['tests'],begin['suites'],begin['mainClasses'])!=(3955,587,1665)or re.fullmatch('[0-9a-f]{64}',begin['archiveSha256'])is None:raise ValueError('actual original local source/archive/inventory first')
    raw=inspect.getsource(prior.main)
    for old,new in(('PG5754','PG5808'),('pg5754-private-contract-six-v1',SLOT),('pg5754-full.py','pg5808-full.py'),('9463db1ac23437043facf95b87f64b9fc7e758bd',SOURCE),('b94847186cc164d5ded59168516bf93fc1b548add3ccfd7fc89b085899fcd728',begin['archiveSha256'])):
        if old not in raw:raise ValueError('one complete known original observer binding')
        raw=raw.replace(old,new)
    if 'PG5754'in raw or'pg5754'in raw:raise ValueError('no obsolete uppercase/lowercase identity')
    compile(raw,'<only original3955 metadata and XML counts>','exec');return raw


def main():
    begin=json.loads((W/SLOT/'begin.safe.json').read_bytes());scope=dict(vars(prior))
    exec(compile(observer_source(begin),'<only original3955 observation>','exec'),scope)
    return scope['main']()


if __name__=='__main__':main()
