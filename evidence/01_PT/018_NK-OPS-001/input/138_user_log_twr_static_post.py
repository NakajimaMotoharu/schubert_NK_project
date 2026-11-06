"""JDK metadata disassembly only, never loads or invokes a Product class."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import pg9666_pagination_static as c

r = Path.cwd()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
oldp = r / 'evidence/01_PT/018_NK-OPS-001/evidence/PG21754-user-log-sql-error-static-review-v1/manifest.json'
assert sha(oldp) == '9f73753258328cd8da4abfb009e208a9ca12f3690a0c35b423541dc62937c4b0'
old = json.loads(oldp.read_text())
assert old['actualExit'] == 0 and old['productTests'] == 0 and old['dynamicHoldMaintained']
for n, h in old['inputHashes'].items():
    assert sha(r / n) == h
    assert hashlib.sha256(subprocess.check_output(['git', 'show', old['source'] + ':' + n])).hexdigest() == h
for ref in old['existingStatic']:
    assert sha(r / ref['path']) == ref['sha256']
normalp = Path(old['normalManifest']['path'])
assert sha(normalp) == old['normalManifest']['sha256']
normal = json.loads(normalp.read_text())
jar = normal['jars']['api']
assert sha(Path(jar['path'])) == jar['sha256']
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
spec = r / old['specification']['path']
original_spec = subprocess.check_output(['git', 'show', old['source'] + ':' + old['specification']['path']])
assert hashlib.sha256(original_spec).hexdigest() == old['specification']['sha256']
assert b'return' in original_spec and sha(spec) != old['specification']['sha256']
for p in [Path(__file__), spec]:
    assert hashlib.sha256(subprocess.check_output(['git', 'show', head + ':' + str(p.relative_to(r))])).hexdigest() == sha(p)
jdk = r.parent / 'toolchain/jdk-25.0.4'
javap = jdk / 'bin/javap'
slot = r.parent / 'pgpt-runs/PG379/pg21756-user-log-twr-static-post-v1'
assert not slot.exists()
slot.mkdir()
c.SLOT = slot
stages = {}
checks = []
for simple, methods in [('UserQueryRepository', ['search', 'detail']), ('LogQueryRepository', ['search'])]:
    cls = 'dev.codex.schubert.nk.api.persistence.' + simple
    init = slot / (simple + '.class-init.stdout')
    cmd = [str(javap), '-J-Xlog:class+init=info:file=' + str(init), '-classpath', jar['path'], '-c', '-p', cls]
    stage = c.step(simple, cmd, r, timeout=30)
    assert stage['actualExit'] == 0 and not stage['timedOut']
    assert (slot / (simple + '.stderr')).read_bytes() == b''
    text = (slot / (simple + '.stdout')).read_text()
    blocks = re.split(r'(?=^  (?:public|private|protected|static) )', text, flags=re.M)
    for method in methods:
        found = [x for x in blocks if re.search(r'^  public .*\b' + method + r'\(', x)]
        assert len(found) == 1
        block = found[0]
        lines = block.splitlines()
        returns = [i for i, l in enumerate(lines) if re.search(r'\b\d+: areturn\b', l)]
        assert len(returns) == 1
        before = lines[:returns[0]]
        rs = [i for i, l in enumerate(before) if 'java/sql/ResultSet.close:()V' in l]
        ps = [i for i, l in enumerate(before) if 'java/sql/PreparedStatement.close:()V' in l]
        assert rs and ps and max(rs) < max(ps)
        assert 'Exception table:' in block and 'java/lang/Throwable.addSuppressed' in block
        assert 'TemporaryInfrastructureException.preserveFatal' in block
        checks.append(dict(className=simple, method=method, normalReturnSites=1,
            resultSetCloseBeforePreparedStatementCloseBeforeReturn=True,
            exceptionTableAndSuppressionPresent=True, preMappingFatalCallPresent=True,
            dynamicBehaviorProven=False))
    initialized = set(re.findall(r"Initializing '([^']+)", init.read_text()))
    assert not any(n.startswith('dev/codex/schubert/nk/') for n in initialized)
    stages[simple] = stage
assert len(checks) == 3
other_docs = []
for name in ['2759_UserLogSQL原joint34_単体テスト仕様.md', '2760_UserLogSQL原joint34_実行結果.md', '2036_SQL前境界の依存判定.md']:
    p = r / 'evidence/01_PT/018_NK-OPS-001' / name
    text = p.read_text()
    assert 'returnをTWR外' not in text and 'TWRの外に置' not in text
    other_docs.append(dict(path=str(p.relative_to(r)), sha256=sha(p), requiresLexicalReturnPlacement=False))
for n, h in old['inputHashes'].items():
    assert sha(r / n) == h
out = r / 'evidence/01_PT/018_NK-OPS-001/evidence/PG21756-user-log-twr-static-post-v1'
assert not out.exists()
out.mkdir()
files = {}
for p in slot.iterdir():
    if p.is_file():
        shutil.copyfile(p, out / p.name)
        files[p.name] = sha(out / p.name)
m = dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(), checkerSource=head,
    checkerSha256=sha(Path(__file__)), source=old['source'], productionMainSource=old['productionMainSource'],
    original=dict(path=str(oldp.relative_to(r)), sha256=sha(oldp)), inputHashes=old['inputHashes'],
    originalSpecification=old['specification'], correctedSpecification=dict(path=str(spec.relative_to(r)), sha256=sha(spec)),
    javaTool=dict(path=str(javap), sha256=sha(javap), releaseSha256=sha(jdk / 'release')),
    jar=jar, stages=stages, files=files, staticReturnChecks=checks,
    unchangedRelatedSpecifications=other_docs, productInitializations=0, productInvocations=0,
    productTests=0, newMethods=0, newSourceProofs=0, newAcceptance=0,
    coverage=None, ptExemptionGranted=False, refusalScopeUnresolved=True,
    dynamicHoldMaintained=True, relatedBug='BUG-2401', relatedHorizontal='YKT-2146', effortRate=None)
(out / 'manifest.json').write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(actualExit=0, staticEntries=3, productTests=0, manifestSha256=sha(out / 'manifest.json'))))
