"""Host-only exact SSC301/302 candidate; no guest authority or F03 acceptance."""
import ast
import hashlib
import inspect
import json
import re
import pg4702_ssc299_signed_candidate as old
from pg4844_ssc301_302_full import SOURCE, ROOT, W
from pg4846_ssc301_302_whole_qualification import NEW_CASES, MODIFIED, INTERFACES, physical_difference

prior = old.prior
P, T = old.P, ROOT
OLD_SOURCE = old.SOURCE
OLD_BOM = 'f1f6743f8ebe099a8804623f5efef263fa046ca66c46004ade5d469f755fbd80'
OLD, NEXT = W / 'pg4702-release-v1', W / 'pg4860-release-v1'
FROZEN, SIG = W / 'pg4860-frozen-six-v1', P / 'pg4860-manifest-v1.sig'
GATE = None
require, grouped = old.require, old.grouped


def validate_gate(outer, source):
    require(type(outer) is dict and type(outer.get('actualExit')) is int and outer['actualExit'] == 0)
    gate = outer['result']
    expected = {'actualExit': 0, 'productionSource': source, 'tests': 3761, 'suites': 551,
                'mainClasses': 1647, 'FESFlakyNotRun': 0, 'staticSixModules': 0,
                'allSixMainBuildsPassed': True, 'allSixFormatBeforeAnyPt': True,
                'allOriginalCaseIdentitiesRetained': True, 'oldNativeImported': False,
                'candidateNativePending': True, 'F03Accepted': False, 'formalAccepted': False, 'global100': False}
    require(all(type(gate.get(k)) is type(v) and gate[k] == v for k, v in expected.items()))
    require(gate['newCases'] == [list(v) for v in NEW_CASES] and gate['testClassAliases'] == {})
    require(set(gate['jarHashes']) == set(prior.MODULES) and all(re.fullmatch('[a-f0-9]{64}', h) for h in gate['jarHashes'].values()))
    actual = grouped(gate['allPhysicalMainSha256'])
    require(sum(map(len, actual.values())) == 1647 and sum(v['tests'] for v in gate['modules'].values()) == 3761
            and sum(v['suites'] for v in gate['modules'].values()) == 551
            and all(gate['modules'][m]['mainClasses'] == len(actual[m]) for m in prior.MODULES))
    rows = gate['changedClasses']
    require(len(rows) == len({r['class'] for r in rows}) == 3
            and {r['class'] for r in rows if r['action'] == 'MODIFIED'} == MODIFIED
            and {r['class'] for r in rows if r['action'] == 'ADDED_INTERNAL_INTERFACE'} == INTERFACES)
    require(re.fullmatch('[a-f0-9]{64}', gate['formatBeforePtProofSha256']) is not None)
    return gate


def verify_delta(before, after):
    require(GATE is not None and set(before) == set(after) == set(prior.MODULES))
    flat = lambda x: {m + ':' + n: h for m, rows in x.items() for n, h in rows.items()}
    rows, unchanged = physical_difference(flat(before), flat(after), GATE['allPhysicalMainSha256'])
    require(rows == GATE['changedClasses'] and unchanged == 1644)
    return 1647


def qualification_matches(outer):
    raw = (W / 'pg4846-ssc301-302-whole-qualified-v1/qualify.private.py').read_bytes()
    return hashlib.sha256(raw).hexdigest() == outer['payloadSha256'] and outer['wholeReplayed'] is False


def receive(module):
    require(GATE is not None and module in prior.MODULES)
    raw = inspect.getsource(old.old.receive).replace('PG4420', 'PG4844').replace('pg4432', 'pg4860')
    namespace = {**vars(old.old), 'prior': prior, 'GATE': GATE, 'FROZEN': FROZEN, 'OLD': OLD}
    exec(compile(raw, '<exact independently qualified3761 Jar>', 'exec'), namespace)
    return namespace['receive'](module)


def main_source():
    raw = old.main_source()
    changes = {'pg4702': 'pg4860', 'PG4702': 'PG4860', 'pg4432': 'pg4702', 'PG4432': 'PG4702',
               old.SOURCE: SOURCE, 'pg4696-ssc299-whole-qualified-v1': 'pg4846-ssc301-302-whole-qualified-v1'}
    for i, key in enumerate(changes): raw = raw.replace(key, '__SIGN4860_' + str(i) + '__')
    for i, value in enumerate(changes.values()): raw = raw.replace('__SIGN4860_' + str(i) + '__', value)
    tree = ast.parse(raw)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and type(node.value) is int and node.value in {3739, 549, 1646}:
            node.value = {3739: 3761, 549: 551, 1646: 1647}[node.value]
        if isinstance(node, ast.Dict):
            for i, key in enumerate(node.keys):
                if isinstance(key, ast.Constant) and key.value == 'addedClasses': node.values[i] = ast.Constant(1)
                if isinstance(key, ast.Constant) and key.value == 'allSixFormatBeforeAnyPt': node.values[i] = ast.Constant(True)
                if isinstance(key, ast.Constant) and key.value == 'formatOrderIssue': node.values[i] = ast.Constant(None)
    raw = ast.unparse(ast.fix_missing_locations(tree))
    marker = "{'VERSION', 'operations/batch.jar'} <= changed"
    require(raw.count(marker) == 1)
    return raw.replace(marker, "{'VERSION', 'api/api.jar', 'operations/batch.jar'} <= changed", 1)


def main():
    global GATE
    outer = json.loads((W / 'pg4846-ssc301-302-whole-qualified-v1/manifest.safe.json').read_bytes())
    GATE = validate_gate(outer, SOURCE); require(qualification_matches(outer))
    diagnostic = json.loads((W / 'pg4856-static-completion-v1/manifest.safe.json').read_bytes())
    require(diagnostic['actualExit'] == 0 and diagnostic['productionSource'] == SOURCE
            and diagnostic['result']['sameCurrentSixJarAbi'] is True
            and diagnostic['result']['pmd']['processingErrors'] == 0
            and diagnostic['result']['checkstyle']['actualExit'] == 0
            and diagnostic['result']['checkstyle']['findings'] == 0
            and diagnostic['result']['F03Accepted'] is False)
    ns = {**vars(prior), '__file__': __file__, 'PRODUCTION': SOURCE, 'OLD_SOURCE': OLD_SOURCE,
          'OLD_BOM': OLD_BOM, 'OLD': OLD, 'NEXT': NEXT, 'FROZEN': FROZEN, 'SIG': SIG,
          'validate_gate': validate_gate, 'verify_delta': verify_delta, 'receive': receive,
          'qualification_matches': qualification_matches}
    exec(compile(main_source(), '<host-only SSC301302 signed candidate>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__': raise SystemExit(main())
