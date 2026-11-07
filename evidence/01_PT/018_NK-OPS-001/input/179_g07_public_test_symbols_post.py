"""Independent source/rule/line/multiplicity check; no producer or target invocation."""
from collections import Counter
import ast
import datetime
import hashlib
import json
from pathlib import Path
import platform
import re
import sys

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence'
OUT = BASE / 'PG22162-g07-three-public-test-symbols-independent-v1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_bytes())


def key(row):
    return tuple(row[k] for k in ('path', 'ruleId', 'startLine', 'endLine', 'inputSha256'))


def main():
    assert not OUT.exists()
    producer = BASE / 'PG22160-g07-three-public-test-symbols-v1'
    p = producer / 'manifest.json'
    assert sha(p) == '54bceb160d7ebd82a051a897a799e4bbbebd8b77a1f15d7fe23f6c3ab91d0fca'
    m = load(p)
    assert m['actualExit'] == 0 and m['productTestsExecuted'] == 0
    assert sha(producer / 'updates.json') == m['updatesSha256']
    updates = load(producer / 'updates.json')
    shapes = BASE / 'provisional/PG9888-g07-capture-shape-v1'
    assert sha(shapes / 'manifest.json') == '6043b800e9bd89d1fff646dbb7dda064a78ec028a4730e6903cba9c7380871eb'
    sm = load(shapes / 'manifest.json')
    assert sha(shapes / 'residual-metadata-shapes.json') == sm['residualMetadataSha256']
    pending = load(shapes / 'residual-metadata-shapes.json')
    before = Counter(key(row) for row in pending)
    assert len(pending) == 4493 and len(updates) == 3
    selected = Counter(key(row) for row in updates)
    assert len(selected) == 3 and all(count == 1 and before[k] == 1 for k, count in selected.items())
    path = 'tools/quality/019_test_evidence_set.py'
    assert sha(ROOT / path) == '71e94fcef80773abc1990428025223b8bececf8ad85cd122a645be4ad23b428a'
    python = (ROOT / path).read_text()
    lines = python.splitlines(keepends=True)
    tree = ast.parse(python)
    function = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                    and n.name == 'test_deployment_inventory_and_nonpassing_cases')
    rule = BASE / 'provisional/PG8979-gitleaks-rule-provenance-v1/manifest.json'
    assert sha(rule) == '97b57201394a789a6871fa2f73b6521d71e48e5452ff2b426a6e23e4ca580c8a'
    rx = re.compile(load(rule)['rules']['generic-api-key']['regex'], re.ASCII)
    java_paths = {
      2249: 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiNonSecretConfigTest.java',
      2351: 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/ReleaseApprovalTest.java',
      2353: 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/ReleaseSignatureVerifierTest.java',
    }
    for update in updates:
        line = update['startLine']
        assert update['path'] == path and line == update['endLine'] and line in java_paths
        assert function.lineno < line < function.end_lineno
        statement = next(n for n in function.body if isinstance(n, ast.Expr)
                         and n.lineno <= line <= n.end_lineno)
        tuple_node = statement.value.args[0]
        assert isinstance(tuple_node, ast.Tuple) and len(tuple_node.elts) == 3
        methods_node = tuple_node.elts[2]
        assert isinstance(methods_node, ast.Tuple)
        expected = {n.value for n in methods_node.elts if isinstance(n, ast.Constant) and isinstance(n.value, str)}
        assert len(expected) == len(methods_node.elts)
        captures = set()
        for match in rx.finditer(''.join(lines[line - 2:line + 1])):
            low = line - 2
            region = ''.join(lines[low:line + 1])
            if low + region.count('\n', 0, match.start(1)) + 1 == line == low + region.count('\n', 0, match.end(1)) + 1:
                captures.add(match.group(1))
        assert len(captures) == 1 and captures <= expected
        java_path = java_paths[line]
        assert update['declarationPath'] == java_path
        assert not any(s in java_path for s in ('RootFailedStart', 'SnapshotKeyCloseWitness'))
        assert sha(ROOT / java_path) == update['declarationSourceSha256'] == m['sourceHashes'][java_path]
        java_lines = (ROOT / java_path).read_text().splitlines()
        witnessed = []
        for pos, text in enumerate(java_lines):
            declaration = re.fullmatch(r'\s*void\s+([\w$]+)\(\)\s*(?:throws\s+[\w., ]+\s*)?\{\s*', text)
            if declaration and declaration[1] in captures:
                assert java_lines[pos - 1].strip() == '@Test'
                witnessed.append(pos + 1)
        assert len(witnessed) == len(captures) and sorted(witnessed) == update['declarationLines']
        assert update['disposition'] == 'FALSE_POSITIVE_PROVEN_PUBLIC_TEST_METHOD_IDENTIFIER'
        assert update['fullExactCaptureClosure'] is True and update['capturesProven'] == 1
    remaining = before - selected
    assert sum(remaining.values()) == 4490 and m['remainingUnclassified'] == 4490
    assert m['actualSecretCount'] is None and m['binaryClosed'] == 0 and m['binaryTotal'] == 22
    assert m['capturedValuesWritten'] is False and m['captureValueHashesWritten'] is False
    OUT.mkdir()
    result = dict(atJST=datetime.datetime.now().astimezone().isoformat(), actualExit=0,
                  command=[sys.executable, '-B', str(Path(__file__).relative_to(ROOT))],
                  os=platform.platform(), python=platform.python_version(), scriptSha256=sha(Path(__file__)),
                  producerSha256=sha(p), originalMetadataSha256=sha(shapes / 'residual-metadata-shapes.json'),
                  matchedFindings=3, sourceAndExpectedTupleAndDeclarationVerified=True,
                  previousUnclassified=4493, remainingUnclassified=4490,
                  actualSecretCount=None, binaryClosed=0, binaryTotal=22,
                  scannerExecuted=False, productTestsExecuted=0, newAccepted=0,
                  valuesOrValueHashesWritten=False)
    (OUT / 'manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(actualExit=0, classified=3, remaining=4490,
                          manifestSha256=sha(OUT / 'manifest.json'))))


if __name__ == '__main__':
    main()
