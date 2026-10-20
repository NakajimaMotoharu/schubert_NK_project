"""Observe only the authenticated original3971; no test/start/stop/runtime/raw-log action."""
import inspect
import json
import re
import pg5754_whole_observation as previous
from pg5860_terminal_whole import SOURCE,W,SLOT


def observer_source(begin):
    if begin['source']!=SOURCE or(begin['tests'],begin['suites'],begin['mainClasses'])!=(3971,592,1666)or re.fullmatch('[0-9a-f]{64}',begin['archiveSha256'])is None:raise ValueError('original local source/archive/run')
    raw=inspect.getsource(previous.main)
    for old,new in(('PG5754','PG5860'),('pg5754-private-contract-six-v1',SLOT),('pg5754-full.py','pg5860-full.py'),('9463db1ac23437043facf95b87f64b9fc7e758bd',SOURCE),('b94847186cc164d5ded59168516bf93fc1b548add3ccfd7fc89b085899fcd728',begin['archiveSha256'])):
        if old not in raw:raise ValueError('exact original observer binding')
        raw=raw.replace(old,new)
    compile(raw,'<original3971 metadata/XML counts>','exec');return raw


def main():
    begin=json.loads((W/SLOT/'begin.safe.json').read_bytes());scope=dict(vars(previous))
    exec(compile(observer_source(begin),'<original3971 observation>','exec'),scope)
    return scope['main']()


if __name__=='__main__':main()
