"""All24 Root-only oracle before any planned authenticated Browser writes."""
import inspect
import json
from pyflakes.api import check
import pg2994_current_resume_rows as previous
from pg1446_current_cold_stage import W

SLOT = 'pg3132-browser-resume-rows-v1'


def rebind(raw, activation, started):
    old_once = json.loads((W / 'pg2984-current-fresh-resume-once-v1/manifest.safe.json').read_bytes())
    for old, new in [
        (previous.SLOT, SLOT), ('pg2984-current-fresh-resume-once-v1', 'pg3122-prepared-browser-resume-once-v1'),
        ('d10735e678e5053c0c96c55a42f65f2302132cfae902edd81dffbc2275c4c4ac', 'f041e0b3318db88e7b94cd40a23d28ba7e630d405e1b13f9ae397f03a1312f24'),
        ('0ac69fb7-3cb7-4d33-b2d9-4733fba5a4cf', activation), (old_once['startedUTC'], started),
    ]:
        if old not in raw:
            raise ValueError('complete current rows binding required: ' + old[:36])
        raw = raw.replace(old, new)
    if check(raw, '<new current Root all24 oracle>'):
        raise ValueError('complete independent all24 namespace required')
    compile(raw, '<new current Root all24 oracle>', 'exec')
    return raw


def payload():
    live = json.loads((W / 'pg3124-browser-resume-live-binding-v1/manifest.safe.json').read_bytes())
    once = json.loads((W / 'pg3122-prepared-browser-resume-once-v1/manifest.safe.json').read_bytes())
    if live['actualExit'] != 0 or once['actualExit'] != 0 or live['productionSource'] != previous.SOURCE:
        raise ValueError('actual new reserved Root identity required')
    return rebind(previous.payload(), live['binding']['activation'], once['startedUTC'])


def main():
    raw = inspect.getsource(previous.main).replace('pg2992-current-resume-terminal-v1', 'pg3130-browser-resume-terminal-v1')
    ns = {**previous.__dict__, 'SLOT': SLOT, 'payload': payload}
    exec(compile(raw, '<new current all24 Root transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
