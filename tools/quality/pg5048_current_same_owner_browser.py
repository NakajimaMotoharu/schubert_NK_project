"""Same actual four owners, unchanged12 cases, fresh exact owned SOCKS generation."""
import inspect
import json
import types
import pg4910_current_same_owner_browser as previous
import pg5036_current_admission_image as admission
import pg5038_current_genuine_terminal as terminal
import pg5042_current_newday_whole_seal as seal
import pg5046_current_browser_ready as ready
from pg5045_current_browser_socks import owned_socks

SLOT = 'pg5048-current-same-owner-browser-v1'
SOURCE = admission.SOURCE


def receipt(slot):
    value = json.loads((admission.W / slot / 'manifest.safe.json').read_bytes())
    if not (type(value.get('actualExit')) is int and value['actualExit'] == 0
            and value.get('source') == SOURCE and type(value.get('result')) is dict):
        raise ValueError('actual current phase receipt required')
    return {**value['result'], 'actualExit': value['actualExit'], 'productionSource': value['source']}


def current_guard(raw):
    old = '/opt/schubert-nk/releases/0.1.0-PG3976'
    new = '/opt/schubert-nk/releases/0.1.0-PG4980'
    if raw.count(old) != 1 or new in raw:
        raise ValueError('one exact prior Browser release authority')
    return raw.replace(old, new, 1)


def guard():
    whole, term = receipt(seal.SLOT), receipt(terminal.TERM)
    if not (whole['genuineCompletion']['genuineRootDone']
            and whole['genuineCompletion']['completionCode'] == term['completionCode']):
        raise ValueError('same actual genuine terminal and whole seal')
    template = previous.previous.previous.previous
    fn = types.FunctionType(template.guard.__code__, {**vars(template), 'SOURCE': SOURCE, 'BOM': admission.BOM})
    return current_guard(terminal.bind(admission.entry.observer.bind(fn(whole, term, admission.live()))))


def main():
    admission.authenticate_host()
    template = previous.previous.previous
    raw = inspect.getsource(template.main).replace('shared=ready.previous.previous.previous', 'shared=ready.shared')
    # Use the exact original proof function with fresh-generation expected data;
    # do not mutate the historical module's global EXPECTED or receipt path.
    raw = raw.replace('previous.previous.owned_socks()', 'owned_socks()')
    ns = {**vars(template), 'SLOT': SLOT, 'SOURCE': SOURCE, 'ready': ready,
          'guard': guard, 'owned_socks': owned_socks}
    exec(compile(raw, '<same four owners/new actual Browser route>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
