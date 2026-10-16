"""Host-only exact relocated Main candidate, never a deployment/Root permission."""
import ast
import hashlib
import inspect
import json
import re
import pg3976_literal_invariant_signed_candidate as previous
from pg4420_shared_manager_full import SOURCE, ROOT, W
from pg4426_relocated_jar_contract import verify_relocated_container

prior = previous.prior
P, T = prior.P, ROOT
OLD_SOURCE = previous.SOURCE
OLD_BOM = '0a409301e552d8019440edcbf096ad9b20c15b35c0ee6472cd9c4cef65bd8dab'
OLD = W / 'pg3976-release-v1'; NEXT = W / 'pg4432-release-v1'
FROZEN = W / 'pg4432-frozen-six-v1'; SIG = P / 'pg4432-manifest-v1.sig'
GATE = None


def require(value):
    if not value: raise ValueError('exact shared-manager signed candidate refused')


def grouped(flat):
    result = {m: {} for m in prior.MODULES}
    for name, digest in flat.items():
        module, member = name.split(':', 1)
        require(module in result and member.endswith('.class') and re.fullmatch('[0-9a-f]{64}', digest))
        result[module][member] = digest
    return result


def validate_gate(outer, source):
    require(type(outer) is dict and type(outer.get('actualExit')) is int and outer['actualExit'] == 0)
    gate = outer['result']
    expected = {'actualExit': 0, 'productionSource': source, 'tests': 3721, 'suites': 545, 'mainClasses': 1644,
                'FESFlakyNotRun': 0, 'staticSixModules': 0, 'allSixMainBuildsPassed': True,
                'allOriginalCaseIdentitiesRetained': True, 'oldNativeImported': False, 'candidateNativePending': True,
                'F03Accepted': False, 'formalAccepted': False, 'global100': False}
    require(all(type(gate.get(k)) is type(v) and gate[k] == v for k, v in expected.items()))
    from pg4422_shared_manager_whole_qualification import ALIASES, NEW_CASES
    require(gate['testClassAliases'] == ALIASES and gate['newCases'] == [list(v) for v in NEW_CASES])
    require(set(gate['jarHashes']) == set(prior.MODULES) and all(re.fullmatch('[0-9a-f]{64}', h) for h in gate['jarHashes'].values()))
    actual = grouped(gate['allPhysicalMainSha256'])
    require(sum(map(len, actual.values())) == 1644 and sum(r['tests'] for r in gate['modules'].values()) == 3721
            and sum(r['suites'] for r in gate['modules'].values()) == 545)
    require(all(gate['modules'][m]['mainClasses'] == len(actual[m]) for m in prior.MODULES))
    require(len({r['class'] for r in gate['changedClasses']}) == len(gate['changedClasses']))
    require([r['class'] for r in gate['changedClasses'] if r['action'] == 'ADDED_FIXED_ENUM'] ==
            ['bootstrap:dev/codex/schubert/nk/bootstrap/SystemManagerObservation$Service.class'])
    return gate


def verify_delta(before, after):
    require(GATE is not None and after == grouped(GATE['allPhysicalMainSha256']))
    require(set(before) == set(after) == set(prior.MODULES) and sum(map(len, before.values())) == 1643)
    oldflat = {m + ':' + n: h for m, rows in before.items() for n, h in rows.items()}
    actual = dict(oldflat)
    for row in GATE['changedClasses']:
        old = row['oldClass']; new = row['class']
        if old is not None:
            require(actual.pop(old) == row['oldSha256'])
        else:
            require(row['oldSha256'] is None and row['action'] == 'ADDED_FIXED_ENUM')
        require(new not in actual and GATE['allPhysicalMainSha256'][new] == row['newSha256'])
        actual[new] = row['newSha256']
    require(actual == GATE['allPhysicalMainSha256'])
    return 1644


def qualification_matches(outer):
    original = W / 'pg4422-shared-manager-whole-qualified-v1/qualify.private.py'
    return hashlib.sha256(original.read_bytes()).hexdigest() == outer['payloadSha256'] and outer['originalWholeReplayed'] is False


def receive(module):
    require(GATE is not None and module in prior.MODULES)
    raw = inspect.getsource(prior.transfer.receive).replace('PG1532', 'PG4420').replace('pg1535', 'pg4432')
    namespace = {**prior.transfer.__dict__, 'FROZEN': FROZEN}
    exec(compile(raw, '<exact qualified3721 Jar receive>', 'exec'), namespace)
    path = namespace['receive'](module)
    oldpath = {'api': 'api/api.jar', 'web': 'web/web.jar', 'batch': 'operations/batch.jar'}.get(module)
    if oldpath is None:
        oldpath = next(r['path'] for r in json.loads((OLD / 'RELEASE-MANIFEST.json').read_bytes())['artifacts'] if r['path'].endswith('/' + path.name))
    before = prior.class_inventory(OLD / oldpath)
    after = grouped(GATE['allPhysicalMainSha256'])[module]
    verify_relocated_container(OLD / oldpath, path, before, after)
    return path


def main_source():
    raw = previous.main_source()
    substitutions = {'pg3976': 'pg4432', 'PG3976': 'PG4432', 'pg3748': 'pg3976', 'PG3748': 'PG3976',
                     previous.SOURCE: SOURCE, 'pg3968-literal-invariant-whole-qualified-v1': 'pg4428-shared-manager-whole-qualified-v1'}
    for i, old in enumerate(substitutions): raw = raw.replace(old, '__SIGN4432_' + str(i) + '__')
    for i, new in enumerate(substitutions.values()): raw = raw.replace('__SIGN4432_' + str(i) + '__', new)
    required = "{'VERSION', 'api/api.jar'} <= changed"
    require(raw.count(required) == 1)
    raw = raw.replace(required, "{'VERSION', 'operations/batch.jar', 'operations/lib/schubert-nk-bootstrap-0.1.0-SNAPSHOT.jar'} <= changed", 1)
    tree = ast.parse(raw)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and type(node.value) is int and node.value in (3717, 1643):
            node.value = {3717: 3721, 1643: 1644}[node.value]
        if isinstance(node, ast.Dict):
            for index, key in enumerate(node.keys):
                if isinstance(key, ast.Constant) and key.value == 'addedClasses': node.values[index] = ast.Constant(1)
    return ast.unparse(ast.fix_missing_locations(tree))


def main():
    global GATE
    outer = json.loads((W / 'pg4428-shared-manager-whole-qualified-v1/manifest.safe.json').read_bytes())
    GATE = validate_gate(outer, SOURCE); require(qualification_matches(outer))
    diagnostic = json.loads((W / 'pg4424-shared-manager-static-v1/manifest.safe.json').read_bytes())
    require(diagnostic['actualExit'] == 0 and diagnostic['productionSource'] == SOURCE
            and diagnostic['result']['sameCurrentSixJarAbi'] is True and diagnostic['result']['pmd']['processingErrors'] == 0
            and diagnostic['result']['checkstyle']['findings'] == 0)
    namespace = {**prior.__dict__, '__file__': __file__, 'PRODUCTION': SOURCE, 'OLD_SOURCE': OLD_SOURCE, 'OLD_BOM': OLD_BOM,
                 'OLD': OLD, 'NEXT': NEXT, 'FROZEN': FROZEN, 'SIG': SIG, 'validate_gate': validate_gate,
                 'verify_delta': verify_delta, 'receive': receive, 'qualification_matches': qualification_matches}
    exec(compile(main_source(), '<host-only shared reader candidate>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
