"""Fixed three public identifier findings; source data only, no imports/invocations of targets."""
import ast
import datetime
import hashlib
import json
from pathlib import Path
import platform
import re
import sys

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/PG22160-g07-three-public-test-symbols-v1'
SOURCE = 'tools/quality/019_test_evidence_set.py'
SOURCE_SHA = '71e94fcef80773abc1990428025223b8bececf8ad85cd122a645be4ad23b428a'
CLASSES = {
  2249: 'dev.codex.schubert.nk.api.bootstrap.ApiNonSecretConfigTest',
  2351: 'dev.codex.schubert.nk.bootstrap.ReleaseApprovalTest',
  2353: 'dev.codex.schubert.nk.bootstrap.ReleaseSignatureVerifierTest',
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def checked(path, expected):
    data = path.read_bytes()
    assert sha(data) == expected
    return json.loads(data)


def proven(captures, expected, declared):
    return bool(captures) and captures <= expected and captures <= declared


def main():
    assert not OUT.exists()
    # Recurrence/negative checks are tool logic only; never Product tests.
    assert proven({'methodA'}, {'methodA'}, {'methodA'})
    assert not proven(set(), {'methodA'}, {'methodA'})
    assert not proven({'unknown'}, {'methodA'}, {'methodA'})
    assert not proven({'methodA', 'unknown'}, {'methodA'}, {'methodA', 'unknown'})
    assert not proven({'methodA'}, {'methodA'}, set())
    assert proven({'methodA'}, {'methodA', 'other'}, {'methodA'})
    shapes_path = BASE / 'PG9888-g07-capture-shape-v1/manifest.json'
    shapes = checked(shapes_path, '6043b800e9bd89d1fff646dbb7dda064a78ec028a4730e6903cba9c7380871eb')
    pending_path = shapes_path.parent / 'residual-metadata-shapes.json'
    pending = checked(pending_path, shapes['residualMetadataSha256'])
    assert len(pending) == 4493
    selected = [row for row in pending if row['path'] == SOURCE]
    assert len(selected) == 3 and {row['startLine'] for row in selected} == set(CLASSES)
    rule_path = BASE / 'PG8979-gitleaks-rule-provenance-v1/manifest.json'
    rules = checked(rule_path, '97b57201394a789a6871fa2f73b6521d71e48e5452ff2b426a6e23e4ca580c8a')
    regex = re.compile(rules['rules']['generic-api-key']['regex'], re.ASCII)
    raw = (ROOT / SOURCE).read_bytes()
    assert sha(raw) == SOURCE_SHA
    text = raw.decode('utf-8')
    lines = text.splitlines(keepends=True)
    tree = ast.parse(text)
    proofs = []
    source_hashes = {SOURCE: SOURCE_SHA}
    for row in selected:
        line = row['startLine']
        assert line == row['endLine'] and row['inputSha256'] == SOURCE_SHA
        assert row['ruleId'] == 'generic-api-key' and row['disposition'] == 'UNCLASSIFIED'
        statements = [n for n in ast.walk(tree) if isinstance(n, ast.Expr)
                      and n.lineno <= line <= n.end_lineno]
        statement = min(statements, key=lambda n: n.end_lineno - n.lineno)
        call = statement.value
        assert isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
        assert call.func.attr == 'append' and isinstance(call.func.value, ast.Name)
        assert call.func.value.id == 'groups' and len(call.args) == 1 and not call.keywords
        classname, expected_count, methods = ast.literal_eval(call.args[0])
        assert classname == CLASSES[line] and expected_count == 1
        assert isinstance(methods, tuple) and all(isinstance(v, str) and v.isidentifier() for v in methods)
        java_path = 'src/schubert-nk-bootstrap/src/test/java/' + classname.replace('.', '/') + '.java'
        assert not any(part in java_path for part in ('RootFailedStart', 'SnapshotKeyCloseWitness'))
        java = (ROOT / java_path).read_bytes()
        source_hashes[java_path] = sha(java)
        declarations = {m.group(1): java.decode('utf-8').count('\n', 0, m.start(1)) + 1
                        for m in re.finditer(r'@Test\s+void\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*\(\s*\)\s*\{', java.decode('utf-8'))}
        low = max(0, line - 2)
        window = ''.join(lines[low:row['endLine'] + 1])
        exact = set()
        for match in regex.finditer(window):
            start = low + window.count('\n', 0, match.start(1)) + 1
            end = low + window.count('\n', 0, match.end(1)) + 1
            if line <= start <= end <= row['endLine']:
                exact.add(match.group(1))
        assert len(exact) == row['uniqueExactCaptureCount'] == 1
        assert proven(exact, set(methods), set(declarations))
        proofs.append(dict(**{k: row[k] for k in ('path', 'ruleId', 'startLine', 'endLine', 'inputSha256')},
                           disposition='FALSE_POSITIVE_PROVEN_PUBLIC_TEST_METHOD_IDENTIFIER',
                           proofKind='EXPECTED_METHOD_TUPLE_AND_REAL_TEST_DECLARATION',
                           fullExactCaptureClosure=True, capturesProven=1,
                           sourceStatementLines=[statement.lineno, statement.end_lineno],
                           declarationPath=java_path, declarationSourceSha256=sha(java),
                           declarationLines=sorted(declarations[v] for v in exact)))
    OUT.mkdir()
    write = lambda p, value: p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    write(OUT / 'updates.json', proofs)
    result = dict(atJST=datetime.datetime.now().astimezone().isoformat(), actualExit=0,
                  command=[sys.executable, '-B', str(Path(__file__).relative_to(ROOT))],
                  os=platform.platform(), python=platform.python_version(),
                  scriptSha256=sha(Path(__file__).read_bytes()), sourceHashes=source_hashes,
                  source='fb9fce0f91de3d9fdfa634fe277592700f915e45',
                  contentCommit='05d73a7974da8df92228160b96d91e7a006768f3',
                  evaluationCoreMain='7aed8eace7c844c2f79f2e39db766faf914890d5',
                  originalResidualManifestSha256=sha(shapes_path.read_bytes()),
                  originalResidualMetadataSha256=sha(pending_path.read_bytes()),
                  ruleProvenanceSha256=sha(rule_path.read_bytes()),
                  updatesSha256=sha((OUT / 'updates.json').read_bytes()),
                  additionalFalsePositives=3, previousUnclassified=4493,
                  remainingUnclassified=4490, binaryClosed=0, binaryTotal=22,
                  actualSecretCount=None, toolLogicChecks=6, productTestsExecuted=0,
                  capturedValuesWritten=False, captureValueHashesWritten=False,
                  scannerExecuted=False, javaExecuted=False, targetOperation=False,
                  newAccepted=0, currentSourceWholeG07Qualified=False)
    write(OUT / 'manifest.json', result)
    print(json.dumps(dict(actualExit=0, classified=3, remaining=4490,
                          manifestSha256=sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
