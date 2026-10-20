"""Observe this original3967 only; no PT/start/stop/VM/DB/raw-log action."""
import inspect
import json
import re
import pg5754_whole_observation as previous
from pg5832_isolation_whole import SOURCE,W,SLOT


def observer_source(begin):
    if begin['source']!=SOURCE or(begin['tests'],begin['suites'],begin['mainClasses'])!=(3967,590,1666)or re.fullmatch('[0-9a-f]{64}',begin['archiveSha256'])is None:raise ValueError('original local source/archive/run first')
    raw=inspect.getsource(previous.main)
    for old,new in(('PG5754','PG5832'),('pg5754-private-contract-six-v1',SLOT),('pg5754-full.py','pg5832-full.py'),('9463db1ac23437043facf95b87f64b9fc7e758bd',SOURCE),('b94847186cc164d5ded59168516bf93fc1b548add3ccfd7fc89b085899fcd728',begin['archiveSha256'])):
        if old not in raw:raise ValueError('original observer binding')
        raw=raw.replace(old,new)
    compile(raw,'<original3967 metadata and XML counts>','exec');return raw


def main():
    begin=json.loads((W/SLOT/'begin.safe.json').read_bytes());scope=dict(vars(previous))
    exec(compile(observer_source(begin),'<original3967 observation>','exec'),scope)
    return scope['main']()


if __name__=='__main__':main()
