"""Only original5944 source/run/archive/owner and artifacts; no start/stop/PT."""
import json
import pg5926_whole_observation as previous
from pg5944_private_lock_whole import SOURCE, SLOT, W


def observer_source(begin):
    original = dict(begin, source=previous.SOURCE)
    raw = previous.observer_source(original).replace('PG5926', 'PG5944').replace('pg5926-api-storage-six-v1', SLOT).replace('pg5926-full.py', 'pg5944-full.py').replace(previous.SOURCE, SOURCE)
    if begin['source'] != SOURCE or 'PG5926' in raw or 'pg5926' in raw:
        raise ValueError('one original5944 binding')
    compile(raw, '<only original5944>', 'exec')
    return raw


def main():
    begin = json.loads((W/SLOT/'begin.safe.json').read_bytes()); scope = dict(vars(previous.previous))
    exec(compile(observer_source(begin), '<original5944 observation>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    main()
