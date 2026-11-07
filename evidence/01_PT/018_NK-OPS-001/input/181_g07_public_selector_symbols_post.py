"""Independent exact-position/public-declaration proof; never imports producer or targets."""
from collections import Counter
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
O = B/'PG22172-g07-four-selector-symbols-independent-v1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_bytes())
key = lambda row: tuple(row[k] for k in ('path','ruleId','startLine','endLine','inputSha256'))


def main():
    assert not O.exists()
    producer = B/'PG22170-g07-four-selector-symbols-v1'
    assert sha(producer/'manifest.json') == '1f1870d8e118e72d84c7b9bbbb938dbc135fffb6a0dc56a78a1cd39307007e3c'
    p = load(producer/'manifest.json')
    assert p['actualExit'] == 0 and sha(producer/'updates.json') == p['updatesSha256']
    updates = load(producer/'updates.json')
    origin = B/'provisional/PG9888-g07-capture-shape-v1'
    assert sha(origin/'manifest.json') == '6043b800e9bd89d1fff646dbb7dda064a78ec028a4730e6903cba9c7380871eb'
    assert sha(origin/'residual-metadata-shapes.json') == load(origin/'manifest.json')['residualMetadataSha256']
    pending = load(origin/'residual-metadata-shapes.json')
    prior = load(B/'PG22160-g07-three-public-test-symbols-v1/updates.json')
    assert sha(B/'PG22160-g07-three-public-test-symbols-v1/updates.json') == load(B/'PG22160-g07-three-public-test-symbols-v1/manifest.json')['updatesSha256']
    old = Counter(key(v) for v in prior)
    fresh = Counter(key(v) for v in updates)
    all_keys = Counter(key(v) for v in pending)
    assert len(updates) == len(fresh) == 4 and not old.keys() & fresh.keys()
    assert all(n == 1 and all_keys[k] == 1 for k,n in fresh.items())
    expected = {
      ('tools/quality/022_collect_inspector_launch_evidence.py',123): 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiNonSecretConfigTest.java',
      ('tools/quality/022_collect_inspector_launch_evidence.py',239): 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/ReleaseApprovalTest.java',
      ('tools/quality/022_collect_inspector_launch_evidence.py',241): 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/ReleaseSignatureVerifierTest.java',
      ('tools/quality/pg6582_api_jdbc_domain_selected.py',28): 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/persistence/BorrowedJdbcFatal329Test.java',
    }
    assert {(x['path'],x['startLine']) for x in updates} == set(expected)
    rule = B/'provisional/PG8979-gitleaks-rule-provenance-v1/manifest.json'
    assert sha(rule) == '97b57201394a789a6871fa2f73b6521d71e48e5452ff2b426a6e23e4ca580c8a'
    regex = re.compile(load(rule)['rules']['generic-api-key']['regex'],re.ASCII)
    for item in updates:
        path,line = item['path'],item['startLine']
        assert line == item['endLine'] and sha(R/path) == item['inputSha256'] == p['sourceHashes'][path]
        source = (R/path).read_text()
        # Positions are independently calculated from the complete fixed source.
        captures = {m.group(1) for m in regex.finditer(source)
                    if source.count('\n',0,m.start(1))+1 == line
                    == source.count('\n',0,m.end(1))+1}
        assert len(captures) == 1
        java_path = expected[(path,line)]
        assert java_path == item['declarationPath'] and sha(R/java_path) == item['declarationSourceSha256'] == p['sourceHashes'][java_path]
        assert not any(x in java_path for x in ('RootFailedStart','SnapshotKeyCloseWitness','pg9892','private'))
        java_lines = (R/java_path).read_text().splitlines()
        if path.startswith('tools/quality/022_'):
            tree = ast.parse(source)
            constants = [n for n in ast.walk(tree) if isinstance(n,ast.Constant) and isinstance(n.value,str)
                         and n.lineno <= line <= n.end_lineno and n.value in captures]
            assert len(constants) == 1
            symbol = constants[0].value
            enclosing = [n for n in ast.walk(tree) if isinstance(n,ast.Tuple)
                         and n.lineno <= line <= n.end_lineno and len(n.elts) == 3
                         and isinstance(n.elts[0],ast.Constant) and isinstance(n.elts[0].value,str)
                         and n.elts[0].value.startswith('dev.')]
            assert len(enclosing) == 1
            cls = enclosing[0].elts[0].value
            assert java_path.endswith('/'+cls.replace('.','/')+'.java')
            witnessed = [i+1 for i,text in enumerate(java_lines)
                         if re.fullmatch(r'\s*void\s+'+re.escape(symbol)+r'\(\)\s*\{\s*',text)
                         and java_lines[i-1].strip() == '@Test']
        else:
            tree = ast.parse(source)
            selectors = next(n.value for n in tree.body if isinstance(n,ast.Assign)
                             and any(isinstance(t,ast.Name) and t.id == 'API' for t in n.targets))
            assert isinstance(selectors,ast.Set)
            strings = [n.value for n in selectors.elts if isinstance(n,ast.Constant) and isinstance(n.value,str)]
            matches = [v for v in strings if all(v == c or v.endswith('.'+c) for c in captures)]
            assert len(matches) == 1
            cls = 'dev.codex.schubert.nk.'+matches[0]
            package,simple = cls.rsplit('.',1)
            assert 'package '+package+';' in java_lines
            witnessed = [i+1 for i,text in enumerate(java_lines)
                         if re.fullmatch(r'(?:(?:public|final)\s+)*class\s+'+re.escape(simple)+r'\s*\{',text)]
        assert len(witnessed) == 1 and witnessed == item['declarationLines']
        assert item['fullExactCaptureClosure'] is True and item['capturesProven'] == 1
    assert sum((all_keys-old-fresh).values()) == 4486
    O.mkdir()
    result = dict(atJST=datetime.datetime.now().astimezone().isoformat(),actualExit=0,
                  command=[sys.executable,'-B',str(Path(__file__).relative_to(R))],
                  os=platform.platform(),python=platform.python_version(),scriptSha256=sha(Path(__file__)),
                  producerSha256=sha(producer/'manifest.json'),previousUpdatesSha256=sha(B/'PG22160-g07-three-public-test-symbols-v1/updates.json'),
                  originalMetadataSha256=sha(origin/'residual-metadata-shapes.json'),
                  previousUnclassified=4490,additionalFalsePositives=4,remainingUnclassified=4486,
                  originalMultiplicityPreserved=True,overlapWithPrevious=False,
                  methodDeclarations=3,classDeclarations=1,scannerExecuted=False,targetsExecuted=False,
                  productTestsExecuted=0,newAccepted=0,actualSecretCount=None,binaryClosed=0,binaryTotal=22,
                  valuesOrValueHashesWritten=False)
    (O/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(actualExit=0,classified=4,remaining=4486,manifestSha256=sha(O/'manifest.json'))))


if __name__ == '__main__':
    main()
