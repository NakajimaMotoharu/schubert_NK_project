"""One host-only new candidate after genuine3717, no VM authorization or old native."""
import ast
import hashlib
import inspect
import json
import re
import pg3748_hygiene_signed_candidate as previous
import pg3966_literal_invariant_full_six as whole
import pg3968_literal_invariant_whole_qualification as qualification
from pg2428_question_signed_candidate import verify_container

prior = previous.previous.prior
W, P, T = prior.W, prior.P, prior.T
SOURCE = whole.SOURCE
OLD_SOURCE = previous.SOURCE
OLD_BOM = '652915c694fe6120af81587195150d7df8bcc411b7eb4f5d74cf3f71fd87517b'
OLD = W / 'pg3748-release-v1'; NEXT = W / 'pg3976-release-v1'
FROZEN = W / 'pg3976-frozen-six-v1'; SIG = P / 'pg3976-manifest-v1.sig'
GATE = None


def require(value):
    if not value: raise ValueError('exact3717 signed Main boundary refused')


def validate_gate(outer, source):
    require(type(outer) is dict and type(outer.get('actualExit')) is int and outer['actualExit'] == 0 and type(outer.get('result')) is dict)
    gate = outer['result']
    expected = {'actualExit': 0, 'productionSource': source, 'tests': 3717, 'suites': 545, 'mainClasses': 1643,
                'FESFlakyNotRun': 0, 'staticSixModules': 0, 'allSixMainBuildsPassed': True, 'allOriginalCaseIdentitiesRetained': True,
                'oldNativeImported': False, 'candidateNativePending': True, 'F03Accepted': False, 'formalAccepted': False, 'global100': False}
    require(all(type(gate.get(k)) is type(v) and gate[k] == v for k, v in expected.items()))
    require(gate.get('newCases') == [list(v) for v in whole.NEW_CASES])
    require({m: (v['tests'], v['suites'], v['mainClasses']) for m, v in gate['modules'].items()} == whole.EXPECTED)
    require(set(gate['jarHashes']) == set(prior.MODULES) and all(re.fullmatch('[0-9a-f]{64}', h) for h in gate['jarHashes'].values()))
    require(set(gate['allPhysicalMainSha256']) == set(gate['jarHashes']) and sum(len(v) for v in gate['allPhysicalMainSha256'].values()) == 1643)
    rows = gate['changedClasses']; require(type(rows) is list and bool(rows)); seen = set()
    for row in rows:
        key = row['module'] + ':' + row['class']
        require(row['module'] in gate['jarHashes'] and key not in seen and row['class'].endswith('.class') and row['sourcePath'].startswith('src/schubert-nk-' + row['module'] + '/src/main/java/'))
        seen.add(key)
        require(re.fullmatch('[0-9a-f]{64}', row['oldSha256']) and gate['allPhysicalMainSha256'][row['module']].get(row['class']) == row['newSha256'] and row['oldSha256'] != row['newSha256'])
    return gate


def verify_delta(before, after):
    require(GATE is not None and set(before) == set(after) == set(prior.MODULES))
    require(after == GATE['allPhysicalMainSha256'])
    actual = {}
    for module in before:
        require(before[module].keys() == after[module].keys())
        for name, digest in before[module].items():
            if digest != after[module][name]: actual[module + ':' + name] = (digest, after[module][name])
    require(actual == {r['module'] + ':' + r['class']: (r['oldSha256'], r['newSha256']) for r in GATE['changedClasses']})
    require(sum(len(v) for v in after.values()) == 1643)
    return 1643


def qualification_matches(outer):
    original = json.loads((W / 'pg3966-server-six-v1/manifest.safe.json').read_bytes())
    raw = qualification.qualification_payload(original)
    return (W / 'pg3968-literal-invariant-whole-qualified-v1/qualify.private.py').read_text() == raw and hashlib.sha256(raw.encode()).hexdigest() == outer['payloadSha256']


def receive(module):
    require(GATE is not None and module in prior.MODULES)
    raw = inspect.getsource(prior.transfer.receive).replace('PG1532', 'PG3966').replace('pg1535', 'pg3976')
    namespace = {**prior.transfer.__dict__, 'FROZEN': FROZEN}
    exec(compile(raw, '<one qualified3717 Jar transfer>', 'exec'), namespace)
    path = namespace['receive'](module)
    old_path = {'api': 'api/api.jar', 'web': 'web/web.jar', 'batch': 'operations/batch.jar'}.get(module)
    if old_path is None: old_path = next(r['path'] for r in json.loads((OLD / 'RELEASE-MANIFEST.json').read_bytes())['artifacts'] if r['path'].endswith('/' + path.name))
    verify_container(OLD / old_path, path, {r['class'] for r in GATE['changedClasses'] if r['module'] == module})
    return path


def main_source():
    raw = previous.main_source()
    replacements = {'pg3748': 'pg3976', 'PG3748': 'PG3976', 'pg3420': 'pg3748', 'PG3420': 'PG3748', previous.SOURCE: SOURCE,
                    'pg3738-hygiene-whole-qualified-v1': 'pg3968-literal-invariant-whole-qualified-v1'}
    for index, (old, _) in enumerate(replacements.items()): raw = raw.replace(old, '__CURRENT_SIGN_' + str(index) + '__')
    for index, (_, new) in enumerate(replacements.items()): raw = raw.replace('__CURRENT_SIGN_' + str(index) + '__', new)
    tree = ast.parse(raw)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and type(node.value) is int and node.value == 3714: node.value = 3717
    return ast.unparse(ast.fix_missing_locations(tree))


def main():
    global GATE
    whole.validate(prior.subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=T, text=True).strip())
    outer = json.loads((W / 'pg3968-literal-invariant-whole-qualified-v1/manifest.safe.json').read_bytes())
    GATE = validate_gate(outer, SOURCE); require(qualification_matches(outer))
    diagnostic = json.loads((W / 'pg3970-current-main-static-v1/manifest.safe.json').read_bytes())
    require(diagnostic['actualExit'] == 0 and diagnostic['productionSource'] == SOURCE and diagnostic['result']['pmd']['processingErrors'] == 0 and diagnostic['result']['checkstyle']['findings'] == 0)
    namespace = {**prior.__dict__, '__file__': __file__, 'PRODUCTION': SOURCE, 'OLD_SOURCE': OLD_SOURCE, 'OLD_BOM': OLD_BOM,
                 'OLD': OLD, 'NEXT': NEXT, 'FROZEN': FROZEN, 'SIG': SIG, 'validate_gate': validate_gate, 'verify_delta': verify_delta,
                 'receive': receive, 'qualification_matches': qualification_matches}
    exec(compile(main_source(), '<host-only new3717 candidate>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__': raise SystemExit(main())
