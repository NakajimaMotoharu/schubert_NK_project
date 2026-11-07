"""Four fixed scanner findings are source-only selectors; no target imports or execution."""
import ast
import datetime
import hashlib
import json
from pathlib import Path
import re
import platform
import sys

R = Path(__file__).resolve().parents[4]
B = R/'evidence/01_PT/018_NK-OPS-001/evidence'
O = B/'PG22170-g07-four-selector-symbols-v1'
PINS = {
 'tools/quality/022_collect_inspector_launch_evidence.py': '054f3b586ad589abbd53c78a07326fd58493e20762ae69b0c7f9923c32551319',
 'tools/quality/pg6582_api_jdbc_domain_selected.py': 'affa4ca46d7cb7d63fff3668d40f1e0cf7772a617cfcf509ddbfe72bdd0102e4',
}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_bytes())


def main():
    assert not O.exists()
    shape = B/'provisional/PG9888-g07-capture-shape-v1'
    assert sha(shape/'manifest.json') == '6043b800e9bd89d1fff646dbb7dda064a78ec028a4730e6903cba9c7380871eb'
    sm = load(shape/'manifest.json')
    assert sha(shape/'residual-metadata-shapes.json') == sm['residualMetadataSha256']
    pending = load(shape/'residual-metadata-shapes.json')
    rows = [x for x in pending if x['path'] in PINS]
    assert len(rows) == 4
    rule = B/'provisional/PG8979-gitleaks-rule-provenance-v1/manifest.json'
    assert sha(rule) == '97b57201394a789a6871fa2f73b6521d71e48e5452ff2b426a6e23e4ca580c8a'
    regex = re.compile(load(rule)['rules']['generic-api-key']['regex'], re.ASCII)
    previous = B/'PG22162-g07-three-public-test-symbols-independent-v1/manifest.json'
    assert sha(previous) == 'f1f8a4b06622c0032f129c49c68fcfe204bcac8abfbf6054ee194c92bce7a7b8'
    assert load(previous)['remainingUnclassified'] == 4490
    updates = []
    sources = dict(PINS)
    for row in rows:
        path = row['path']
        assert sha(R/path) == PINS[path] == row['inputSha256']
        assert row['ruleId'] == 'generic-api-key' and row['disposition'] == 'UNCLASSIFIED'
        text = (R/path).read_text()
        tree = ast.parse(text)
        line = row['startLine']
        assert line == row['endLine']
        low = max(0, line-2)
        window = ''.join(text.splitlines(keepends=True)[low:line+1])
        captures = {m.group(1) for m in regex.finditer(window)
                    if low+window.count('\n', 0, m.start(1))+1 == line
                    == low+window.count('\n', 0, m.end(1))+1}
        assert len(captures) == row['uniqueExactCaptureCount'] == 1
        if path.endswith('022_collect_inspector_launch_evidence.py'):
            candidates = []
            for n in ast.walk(tree):
                if not isinstance(n, ast.Tuple) or not n.lineno <= line <= n.end_lineno:
                    continue
                try:
                    value = ast.literal_eval(n)
                except (ValueError, TypeError):
                    continue
                if (len(value) == 3 and isinstance(value[0], str) and value[0].startswith('dev.')
                        and value[1] == 1 and isinstance(value[2], tuple)
                        and captures <= set(value[2])):
                    candidates.append((value[0], n.lineno, n.end_lineno))
            assert len(candidates) == 1
            classname, first, last = candidates[0]
            java_path = 'src/schubert-nk-bootstrap/src/test/java/'+classname.replace('.', '/')+'.java'
            kind = 'PUBLIC_TEST_METHOD_IDENTIFIER'
        else:
            selector = next(n for n in tree.body if isinstance(n, ast.Assign)
                            and any(isinstance(k, ast.Name) and k.id == 'API' for k in n.targets))
            names = ast.literal_eval(selector.value)
            assert isinstance(names, set)
            names = [v for v in names if all(v == c or v.endswith('.'+c) for c in captures)]
            assert len(names) == 1 and all(re.fullmatch(r'[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*', c) for c in captures)
            classname = 'dev.codex.schubert.nk.'+names[0]
            assert classname == 'dev.codex.schubert.nk.api.persistence.BorrowedJdbcFatal329Test'
            java_path = 'src/schubert-nk-api/src/test/java/'+classname.replace('.', '/')+'.java'
            first, last = selector.lineno, selector.end_lineno
            kind = 'PUBLIC_TEST_CLASS_SELECTOR_DOT_SUFFIX'
        assert not any(x in java_path for x in ('RootFailedStart', 'SnapshotKeyCloseWitness', 'pg9892', 'private'))
        java = (R/java_path).read_text()
        sources[java_path] = sha(R/java_path)
        if kind == 'PUBLIC_TEST_METHOD_IDENTIFIER':
            declarations = {m.group(1): java.count('\n', 0, m.start(1))+1 for m in re.finditer(
                r'@Test\s+void\s+([A-Za-z_$][\w$]*)\s*\(\s*\)\s*\{', java)}
            assert captures <= set(declarations)
            declaration_lines = sorted(declarations[c] for c in captures)
        else:
            package, simple = classname.rsplit('.', 1)
            assert re.search(r'^package\s+'+re.escape(package)+r';', java, re.M)
            declaration = re.search(r'^(?:(?:public|final)\s+)*class\s+'+re.escape(simple)+r'\b', java, re.M)
            assert declaration
            declaration_lines = [java.count('\n', 0, declaration.start())+1]
        updates.append(dict(**{k: row[k] for k in ('path','ruleId','startLine','endLine','inputSha256')},
                            disposition='FALSE_POSITIVE_PROVEN_PUBLIC_DECLARED_TEST_SELECTOR',
                            proofKind=kind, fullExactCaptureClosure=True, capturesProven=1,
                            selectorLines=[first,last], declarationPath=java_path,
                            declarationSourceSha256=sources[java_path], declarationLines=declaration_lines))
    O.mkdir()
    write = lambda p,v: p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
    write(O/'updates.json', updates)
    result = dict(atJST=datetime.datetime.now().astimezone().isoformat(), actualExit=0,
                  command=[sys.executable,'-B',str(Path(__file__).relative_to(R))],
                  os=platform.platform(),python=platform.python_version(),scriptSha256=sha(Path(__file__)),
                  sourceHashes=sources,originalMetadataSha256=sha(shape/'residual-metadata-shapes.json'),
                  ruleProvenanceSha256=sha(rule),priorPostSha256=sha(previous),updatesSha256=sha(O/'updates.json'),
                  historicalScanSource='fb9fce0f91de3d9fdfa634fe277592700f915e45',
                  contentCommit='05d73a7974da8df92228160b96d91e7a006768f3',
                  previousUnclassified=4490,additionalFalsePositives=4,remainingUnclassified=4486,
                  binaryClosed=0,binaryTotal=22,actualSecretCount=None,productTestsExecuted=0,
                  scannerExecuted=False,targetsExecuted=False,valuesOrValueHashesWritten=False,
                  currentWholeG07Qualified=False,newAccepted=0)
    write(O/'manifest.json', result)
    print(json.dumps(dict(actualExit=0,classified=4,remaining=4486,manifestSha256=sha(O/'manifest.json'))))


if __name__ == '__main__':
    main()
