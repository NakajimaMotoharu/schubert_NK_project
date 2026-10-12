"""PG-D412 exact artifact delta. Qualification is not deployment authority."""
import types
from pg1534_filesystem_candidate_contract import algorithm, MODULES

CHANGED = {'api': frozenset('dev/codex/schubert/nk/api/bootstrap/' + n + '.class'
                          for n in ['ApiProcessMain', 'ApiProcessLifetime', 'ApiProcessLifetime$1'])}
ADDED = {'api': frozenset('dev/codex/schubert/nk/api/bootstrap/ApiTerminalCapture' + n + '.class'
                        for n in ['', '$Factory', '$Open', '$Capture', '$Operation', '$Owner'])}


def verify_delta(old, candidate):
    return types.FunctionType(algorithm.__code__, {**algorithm.__globals__, 'CHANGED': CHANGED, 'ADDED': ADDED}, algorithm.__name__)(old, candidate)


def validate_gate(outer, source):
    expected = {'actualExit': 0, 'productionSource': source, 'tests': 3596, 'suites': 532,
                'mainClasses': 1643, 'FESFlakyNotRun': 0, 'staticSixModules': 0,
                'classifierFourCounters100': True, 'global100': False, 'formalAccepted': False}
    if type(outer) is not dict or type(outer.get('actualExit')) is not int or outer['actualExit'] != 0:
        raise ValueError('independent actual whole qualification required')
    gate = outer.get('result')
    if type(gate) is not dict or any(type(gate.get(k)) is not type(v) or gate[k] != v for k, v in expected.items()):
        raise ValueError('newSource exact whole quality required')
    hashes = gate.get('jarHashes')
    if type(hashes) is not dict or set(hashes) != set(MODULES) or any(type(h) is not str or len(h) != 64 or set(h) - set('0123456789abcdef') for h in hashes.values()):
        raise ValueError('exact six qualified hashes required')
    return gate
