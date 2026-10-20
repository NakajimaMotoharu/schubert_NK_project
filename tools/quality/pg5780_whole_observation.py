"""Observe only original PG5780 host job; never starts tests, services, VM or recovery."""
import inspect
import json
import re
import pg5754_whole_observation as prior
from pg5780_jms_primary_whole import SOURCE,W,SLOT


def observer_source(begin):
    if begin['source']!=SOURCE or(begin['tests'],begin['suites'],begin['mainClasses'])!=(3939,583,1664)or re.fullmatch('[0-9a-f]{64}',begin['archiveSha256'])is None:raise ValueError('actual original local begin first')
    raw=inspect.getsource(prior.main)
    for old,new in(('PG5754','PG5780'),('pg5754-private-contract-six-v1',SLOT),('pg5754-full.py','pg5780-full.py'),('9463db1ac23437043facf95b87f64b9fc7e758bd',SOURCE),('b94847186cc164d5ded59168516bf93fc1b548add3ccfd7fc89b085899fcd728',begin['archiveSha256'])):
        if old not in raw:raise ValueError('one known original observer binding')
        raw=raw.replace(old,new)
    if 'PG5754'in raw or'pg5754'in raw:raise ValueError('no residual old label/path in current observer')
    return raw


def main():
    begin=json.loads((W/SLOT/'begin.safe.json').read_bytes());raw=observer_source(begin)
    scope=dict(vars(prior));exec(compile(raw,'<only originalPG5780 metadata/XML counts>','exec'),scope)
    return scope['main']()


if __name__=='__main__':main()
