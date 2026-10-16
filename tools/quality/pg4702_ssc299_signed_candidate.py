"""Host candidate only: exact SSC299 physical difference, never OS authority."""
import ast
import hashlib
import inspect
import json
import re
import pg4432_shared_manager_signed_candidate as old
from pg4694_ssc299_full import SOURCE, ROOT, W
from pg4696_ssc299_whole_qualification import NEW_CASES, MODIFIED, INTERFACES, physical_difference

prior = old.prior
P, T = old.P, ROOT
OLD_SOURCE = old.SOURCE
OLD_BOM = '93807abdd4db24ad300b93d95d844ea21e64487dc5cf24b815c15db34305d3de'
OLD = W / 'pg4432-release-v1'
NEXT = W / 'pg4702-release-v1'
FROZEN = W / 'pg4702-frozen-six-v1'
SIG = P / 'pg4702-manifest-v1.sig'
GATE = None
require, grouped = old.require, old.grouped


def validate_gate(outer, source):
    require(type(outer) is dict and type(outer.get('actualExit')) is int and outer['actualExit'] == 0)
    gate = outer['result']
    expected = {'actualExit': 0, 'productionSource': source, 'tests': 3739, 'suites': 549,
                'mainClasses': 1646, 'FESFlakyNotRun': 0, 'staticSixModules': 0,
                'allSixMainBuildsPassed': True, 'allOriginalCaseIdentitiesRetained': True,
                'oldNativeImported': False, 'candidateNativePending': True,
                'F03Accepted': False, 'formalAccepted': False, 'global100': False}
    require(all(type(gate.get(k)) is type(v) and gate[k] == v for k, v in expected.items()))
    require(gate['testClassAliases'] == {} and gate['newCases'] == [list(v) for v in NEW_CASES])
    require(set(gate['jarHashes']) == set(prior.MODULES)
            and all(re.fullmatch('[a-f0-9]{64}', h) for h in gate['jarHashes'].values()))
    actual = grouped(gate['allPhysicalMainSha256'])
    require(sum(map(len, actual.values())) == 1646
            and sum(r['tests'] for r in gate['modules'].values()) == 3739
            and sum(r['suites'] for r in gate['modules'].values()) == 549)
    require(all(gate['modules'][m]['mainClasses'] == len(actual[m]) for m in prior.MODULES))
    rows = gate['changedClasses']
    require(len(rows) == 8 and len({r['class'] for r in rows}) == 8
            and {r['class'] for r in rows if r['action'] == 'MODIFIED'} == MODIFIED
            and {r['class'] for r in rows if r['action'] == 'ADDED_INTERNAL_INTERFACE'} == INTERFACES)
    return gate


def verify_delta(before, after):
    require(GATE is not None and after == grouped(GATE['allPhysicalMainSha256']))
    require(set(before) == set(after) == set(prior.MODULES))
    flat = lambda x: {m + ':' + n: h for m, rows in x.items() for n, h in rows.items()}
    rows, unchanged = physical_difference(flat(before), flat(after), GATE['allPhysicalMainSha256'])
    require(rows == GATE['changedClasses'] and unchanged == 1638)
    return 1646


def qualification_matches(outer):
    script = W / 'pg4696-ssc299-whole-qualified-v1/qualify.private.py'
    return (hashlib.sha256(script.read_bytes()).hexdigest() == outer['payloadSha256']
            and outer['wholeReplayed'] is False)


def receive(module):
    require(GATE is not None and module in prior.MODULES)
    raw = inspect.getsource(old.receive).replace('PG4420', 'PG4694').replace('pg4432', 'pg4702')
    ns = {**vars(old), 'prior': prior, 'GATE': GATE, 'FROZEN': FROZEN, 'OLD': OLD}
    exec(compile(raw, '<exact candidate Jar transfer>', 'exec'), ns)
    return ns['receive'](module)


def main_source():
    raw = old.main_source()
    changes = {'pg4432': 'pg4702', 'PG4432': 'PG4702', 'pg3976': 'pg4432', 'PG3976': 'PG4432',
               old.SOURCE: SOURCE, 'pg4428-shared-manager-whole-qualified-v1': 'pg4696-ssc299-whole-qualified-v1'}
    for i, k in enumerate(changes): raw = raw.replace(k, '__CANDIDATE4702_' + str(i) + '__')
    for i, value in enumerate(changes.values()): raw = raw.replace('__CANDIDATE4702_' + str(i) + '__', value)
    requirement = "{'VERSION', 'operations/batch.jar', 'operations/lib/schubert-nk-bootstrap-0.1.0-SNAPSHOT.jar'} <= changed"
    require(raw.count(requirement) == 1)
    raw = raw.replace(requirement, "{'VERSION', 'operations/batch.jar'} <= changed")
    tree = ast.parse(raw)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and type(node.value) is int and node.value in {3721, 545, 1644}:
            node.value = {3721: 3739, 545: 549, 1644: 1646}[node.value]
        if isinstance(node, ast.Dict):
            for i, key in enumerate(node.keys):
                if isinstance(key, ast.Constant) and key.value == 'addedClasses': node.values[i] = ast.Constant(2)
    # Preserve the process-order nonconformance explicitly, not as a passed gate.
    raw = ast.unparse(ast.fix_missing_locations(tree))
    boundary = "'formalAccepted': False}"
    require(raw.count(boundary) == 1)
    return raw.replace(boundary, "'formalAccepted': False, 'allSixFormatBeforeAnyPt': False, 'formatOrderIssue': 'BUG1381/YKT1147'}")


def main():
    global GATE
    outer = json.loads((W / 'pg4696-ssc299-whole-qualified-v1/manifest.safe.json').read_bytes())
    GATE = validate_gate(outer, SOURCE); require(qualification_matches(outer))
    diagnostic = json.loads((W / 'pg4700-ssc299-static-v1/manifest.safe.json').read_bytes())
    require(diagnostic['actualExit'] == 0 and diagnostic['productionSource'] == SOURCE
            and diagnostic['result']['sameCurrentSixJarAbi'] is True
            and diagnostic['result']['pmd']['processingErrors'] == 0
            and diagnostic['result']['checkstyle']['findings'] == 0)
    ns = {**vars(prior), '__file__': __file__, 'PRODUCTION': SOURCE, 'OLD_SOURCE': OLD_SOURCE,
          'OLD_BOM': OLD_BOM, 'OLD': OLD, 'NEXT': NEXT, 'FROZEN': FROZEN, 'SIG': SIG,
          'validate_gate': validate_gate, 'verify_delta': verify_delta, 'receive': receive,
          'qualification_matches': qualification_matches}
    exec(compile(main_source(), '<host-only SSC299 signed candidate>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__': raise SystemExit(main())
