"""Isolated eligibility projection against fresh3653/current native9, no lifecycle replay."""
import inspect
import json
from pyflakes.api import check
import pg2292_morning_guard_selected as previous
import pg2220_root_uid_host_selected as transport
from pg2578_current_jdbc_group_full_six import SOURCE

FILES = [previous.FILES[0], 'tools/quality/vm/050_s1/Pg2588RetentionEligibilityLauncher.java', *previous.FILES[2:]]


def native_input():
    w = transport.W
    receipt = json.loads((w / 'pg2582-current-jdbc-group-native-qualified-v1/manifest.safe.json').read_bytes())
    inputs = json.loads((w / 'pg2582-current-jdbc-group-native-qualified-v1/input.safe.json').read_bytes())
    full = json.loads((w / 'pg2579-current-jdbc-group-full-qualified-v1/manifest.safe.json').read_bytes())
    result = receipt['result']
    if (type(receipt.get('actualExit')) is not int or receipt['actualExit'] != 0
            or receipt.get('productionSource') != SOURCE or result['classByteMismatch'] != 0
            or result['currentNativeStreams'] != 9 or result['inspectorLatestClosingOnly'] is not True
            or result['inspectorProbeMonotonic'] is not True or inputs['qualifiedFull'] != full['result']
            or full['result']['tests'] != 3653 or result['all1643MainMembersIdentical'] != 1643):
        raise ValueError('actual same Main fresh full and latest nine qualification required')
    files = {str(n) + '.exec': p['sha256'] for n, p in enumerate(inputs['selected'])
             if not (p['unit'] == 'schubert-nk-inbox-inspector.service' and p['relative'].endswith('.terminal.exec'))}
    if len(files) != 9:
        raise ValueError('exact latest nine required')
    return {'manifestSha256': receipt['manifestSha256'], 'files': files}


def server():
    raw = previous.server().replace('PG2292', 'PG2588').replace(
        'Pg2292MorningGuardLauncher', 'Pg2588RetentionEligibilityLauncher').replace(
        'source-full-PG2228', 'source-full-PG2578').replace('PG2284-native-v1', 'PG2582-native-v1')
    for before, after in [('tests2 failures0', 'tests1 failures0'), ("'tests':'2'", "'tests':'1'"),
                          ("len(x.findall('testcase'))==2", "len(x.findall('testcase'))==1"),
                          ("'tests':2", "'tests':1")]:
        raw = raw.replace(before, after)
    if check('INPUT={}\n' + raw, '<current eligibility whole namespace>'):
        raise ValueError('whole selected namespace required')
    compile(raw, '<current eligibility isolated server>', 'exec')
    return raw


def main():
    raw = inspect.getsource(transport.main).replace('PG2220', 'PG2588').replace(
        'pg2220', 'pg2588').replace('pg2125-metadata-boundary-full-qualified-v1',
                                   'pg2579-current-jdbc-group-full-qualified-v1')
    raw = raw.replace(",'libraries':libs}", ",'libraries':libs,'native':native_input()}")
    ns = {**transport.__dict__, 'SOURCE': SOURCE, 'FILES': FILES,
          'SLOT': 'pg2588-retention-eligibility-selected-v1', 'SERVER': server(), 'native_input': native_input}
    exec(compile(raw, '<fixed current eligibility transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
