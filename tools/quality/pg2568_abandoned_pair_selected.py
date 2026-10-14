"""Actual isolated PostgreSQL matrix; frozen a79 Main and current qualified nine streams."""
import inspect
import json
from pyflakes.api import check
import pg2292_morning_guard_selected as previous
from pg2564_strict_current_native_qualification import SOURCE

FILES = [previous.FILES[0], 'tools/quality/vm/050_s1/Pg2568AbandonedPairLauncher.java', *previous.FILES[2:]]


def native_input():
    w = previous.prior.W
    receipt = json.loads((w / 'pg2564-strict-current-native-qualified-v1/manifest.safe.json').read_bytes())
    inputs = json.loads((w / 'pg2564-strict-current-native-qualified-v1/input.safe.json').read_bytes())
    full = json.loads((w / 'pg2511-strict-reference-full-qualified-v1/manifest.safe.json').read_bytes())
    result = receipt['result']
    if (type(receipt.get('actualExit')) is not int or receipt['actualExit'] != 0
            or receipt.get('productionSource') != SOURCE or result['classByteMismatch'] != 0
            or result['currentNativeStreams'] != 9 or result['inspectorLatestClosingOnly'] is not True
            or result['inspectorProbeMonotonic'] is not True or inputs['qualifiedFull'] != full['result']):
        raise ValueError('actual same Main full3650 and qualified current latest nine required')
    files = {str(n) + '.exec': p['sha256'] for n, p in enumerate(inputs['selected'])
             if not (p['unit'] == 'schubert-nk-inbox-inspector.service' and p['relative'].endswith('.terminal.exec'))}
    if len(files) != 9:
        raise ValueError('exact current latest nine required')
    return {'manifestSha256': receipt['manifestSha256'], 'files': files}


def server():
    raw = previous.server().replace('PG2292', 'PG2568').replace(
        'Pg2292MorningGuardLauncher', 'Pg2568AbandonedPairLauncher').replace(
        'source-full-PG2228', 'source-full-PG2510').replace('PG2284-native-v1', 'PG2564-native-v1')
    for before, after in [('tests2 failures0', 'tests1 failures0'), ("'tests':'2'", "'tests':'1'"),
                          ("len(x.findall('testcase'))==2", "len(x.findall('testcase'))==1"),
                          ("'tests':2", "'tests':1")]:
        raw = raw.replace(before, after)
    if check('INPUT={}\n' + raw, '<isolated actual abandoned pair matrix>'):
        raise ValueError('complete selected server namespace required')
    compile(raw, '<fresh isolated pair readback>', 'exec')
    return raw


def main():
    raw = inspect.getsource(previous.prior.main).replace('PG2220', 'PG2568').replace(
        'pg2220', 'pg2568').replace('pg2125-metadata-boundary-full-qualified-v1',
                                   'pg2511-strict-reference-full-qualified-v1')
    raw = raw.replace(",'libraries':libs}", ",'libraries':libs,'native':native_input()}")
    ns = {**previous.prior.__dict__, 'SOURCE': SOURCE, 'FILES': FILES,
          'SLOT': 'pg2568-abandoned-pair-selected-v1', 'SERVER': server(), 'native_input': native_input}
    exec(compile(raw, '<fresh immutable current selected transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
