"""Observe only the original current3973 identity and artifacts; no PT/start/stop/runtime action."""
import inspect
import json
import re
import pg5754_whole_observation as previous
from pg5926_api_storage_whole import SOURCE, W, SLOT


def observer_source(begin):
    if begin['source'] != SOURCE or (begin['tests'], begin['suites'], begin['mainClasses']) != (3973, 592, 1666) or re.fullmatch('[0-9a-f]{64}', begin['archiveSha256']) is None:
        raise ValueError('original source/run/archive binding')
    raw = inspect.getsource(previous.main)
    for old, new in (('PG5754', 'PG5926'), ('pg5754-private-contract-six-v1', SLOT), ('pg5754-full.py', 'pg5926-full.py'), ('9463db1ac23437043facf95b87f64b9fc7e758bd', SOURCE), ('b94847186cc164d5ded59168516bf93fc1b548add3ccfd7fc89b085899fcd728', begin['archiveSha256'])):
        if old not in raw:
            raise ValueError('exact original observation binding')
        raw = raw.replace(old, new)
    compile(raw, '<original current3973 metadata/XML>', 'exec')
    return raw


def main():
    begin = json.loads((W / SLOT / 'begin.safe.json').read_bytes())
    scope = dict(vars(previous))
    exec(compile(observer_source(begin), '<original current3973 observation>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    main()
