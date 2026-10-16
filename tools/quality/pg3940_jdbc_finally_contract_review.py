"""Source/type/design/Test-bound assessment of required JDBC failure precedence; raw warnings retained."""
import hashlib
import inspect
import json
import os
import subprocess
from lan_server import run, copy
from pg3928_current_boundary_full_six import ROOT, W, SOURCE, require
from source_jdbc_close_precedence_inventory_test import facts

SPECS = {
    'BatchRunRepository': 'interruptionAndRuntime',
    'BackupStepRepository': 'nullAndUnknownFailures',
    'CleanupRepository': 'jdbcFailuresRemainRedacted',
    'CleanupStepRepository': 'interruptRuntimeAndResourceOwnership',
    'CleanupTerminalRepository': 'cterm008SqlBodyMustNotHideFatalOwnedClose',
    'InspectionSummaryRepository': 'interruptAndRuntime',
    'RunReferenceRepository': 'interruptionAndRuntime'}
DOC = 'documents/300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md'
TOOL = 'tools/quality/SourceJdbcClosePrecedenceInventory.java'


def server(data):
    import datetime
    import hashlib
    import json
    import os
    from pathlib import Path
    import subprocess
    import xml.etree.ElementTree as E
    from collections import Counter
    os.umask(0o077); b = Path('/home/mini/schubert-nk-pgpt'); out = b / 'runs/PG3940-jdbc-finally-review-v1'; out.mkdir(); (out / 'classes').mkdir()
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    source = b / 'source-full-PG3734'; prior = b / 'runs/PG3864-suppression-identity-review-v1'
    require(sha(prior / 'manifest.safe.json') == data['priorManifestSha256'], 'immutable current1840/278 source report')
    before = json.loads((prior / 'manifest.safe.json').read_bytes()); require(sha(prior / 'all1840-dispositions.safe.json') == before['dispositionsSha256'], 'original warning bytes')
    rows = json.loads((prior / 'all1840-dispositions.safe.json').read_bytes()); require(len(rows) == 1840 and before['technicalDispositions'] == 278, 'no missing/recounted warning')
    require({str(p.relative_to(source)): sha(p) for p in source.glob('src/*/src/main/java/**/*.java')} == data['sourceSha256'], 'all current849 exact Main')
    whole = b / 'runs/PG3738-hygiene-whole-qualified-v1/manifest.safe.json'; require(sha(whole) == data['qualificationSha256'], 'genuine original3714 identity')
    q = json.loads(whole.read_bytes()); require(q['actualExit'] == 0 and q['productionSource'] == data['source'] and q['tests'] == 3714, 'original current-source qualification')
    helper = source / 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/JdbcResourceFailures.java'
    require(sha(helper) == data['helperSha256'], 'actual approved priority helper unchanged')
    cpmeta = b / 'runs/PG3690-import-candidate-v1/manifest.safe.json'; require(sha(cpmeta) == data['classpathAuthoritySha256'], 'actual immutable compiler classpath')
    item = json.loads(cpmeta.read_bytes())['modules']['batch']; cp = item['phases']['after']['command'][-1]
    def cp_hash():
        values = {}
        for p in map(Path, cp.split(':')):
            require(p.is_absolute() and p.exists(), 'fixed real type dependency')
            values[str(p)] = {str(x.relative_to(p)): sha(x) for x in p.rglob('*') if x.is_file() and x.suffix in {'.java', '.class'}} if p.is_dir() else sha(p)
        return hashlib.sha256(json.dumps(values, sort_keys=True).encode()).hexdigest()
    require(cp_hash() == item['classpathInputsSha256'], 'all exact type inputs')
    tool = b / 'transfer/PG3940-jdbc-finally-review-v1/SourceJdbcClosePrecedenceInventory.java'; require(sha(tool) == data['toolSha256'], 'fixed independent typed extractor')
    jdk = b / 'tools/jdk-25.0.4/bin'
    compiled = subprocess.run([str(jdk / 'javac'), '-Xlint:all', '-Werror', '-d', str(out / 'classes'), str(tool)], capture_output=True, timeout=30)
    (out / 'compile.private.log').write_bytes(compiled.stdout + compiled.stderr); require(compiled.returncode == 0 and not compiled.stderr, 'inventory compiler lint0')
    result = subprocess.run([str(jdk / 'java'), '-Xmx1536m', '-cp', str(out / 'classes'), 'SourceJdbcClosePrecedenceInventory', str(source / 'src/schubert-nk-batch/src/main/java'), cp], capture_output=True, text=True, timeout=180)
    (out / 'facts.safe.tsv').write_text(result.stdout); (out / 'facts.private.log').write_text(result.stderr); require(result.returncode == 0, 'all typed source symbols resolve')
    resolved = facts(result.stdout); suite_hashes = {}; assessed = []
    for row in rows:
        if row['rule'] != 'DoNotThrowExceptionInFinally': continue
        name = Path(row['path']).stem
        if name not in data['specs']: continue
        require(row['disposition'] == 'UNCLASSIFIED' and row['sourceSha256'] == sha(source / row['path']), 'only exact unresolved coordinates')
        relative = str(Path(row['path']).relative_to('src/schubert-nk-batch/src/main/java'))
        matching = [f for f in resolved if f['path'] == relative and int(f['firstLine']) == row['coordinates']['beginline']]
        require(len(matching) == 1, 'exact finally start and required same-symbol capture/close/priority/rethrow shape')
        cls = 'dev.codex.schubert.nk.batch.repository.' + name + 'Test'; method = data['specs'][name]
        xml = b / 'runs/PG3734-six-v1/batch/surefire-reports' / ('TEST-' + cls + '.xml')
        require(sha(xml) == q['modules']['batch']['xmlHashes'][xml.name], 'actual original owning XML')
        tree = E.parse(xml).getroot(); require(any(c.get('name') == method for c in tree.findall('testcase')) and not any(n.tag in {'failure', 'error', 'skipped', 'flakyFailure', 'rerunFailure'} for n in tree.iter()), 'actual independent owning compound-failure Test success')
        test = source / ('src/schubert-nk-batch/src/test/java/' + cls.replace('.', '/') + '.java'); require(sha(test) == data['testSha256'][name], 'actual unchanged independent Test source')
        suite_hashes[cls] = sha(xml)
        row.update(disposition='REQUIRED_APPROVED_JDBC_FAILURE_PRECEDENCE', basis='SS332/SSC063199 explicitly requires direct finally close once, unknown identity preserved, SQL plus unknown cleanup prioritizes cleanup, and only fixed redacted suppression. Typed capture preserves original parameter identity; close catches the same three types, helper controls only the same secondary rethrow. Independent real-DB 68-vector owning Tests prove precedence/resource ownership. Blanket removal would violate the approved contract.',
                   scope='EXACT_APPROVED_CONTRACT_TECHNICAL_ASSESSMENT_NOT_GATE', qualityGatePass=False, rawWarningRemoved=False,
                   typedFact=matching[0], owningTestId=cls + '#' + method, owningXmlSha256=sha(xml), design=data['design'], helperSha256=data['helperSha256'])
        assessed.append(row)
    require(len(assessed) == 28, 'exact manually reviewed seven repository/28scope partition, other24 finally warnings unresolved')
    require(cp_hash() == item['classpathInputsSha256'] and {str(p.relative_to(source)): sha(p) for p in source.glob('src/*/src/main/java/**/*.java')} == data['sourceSha256'], 'all Main/type inputs unchanged')
    (out / 'all1840-dispositions.safe.json').write_text(json.dumps(rows, sort_keys=True)); (out / 'assessed28.safe.json').write_text(json.dumps(assessed, sort_keys=True))
    value = {'actualExit': 0, 'productionSource': data['source'], 'rawFindings': 1840, 'newTechnicalAssessments': 28, 'technicalDispositions': 306, 'unclassified': 1534, 'applicableViolationCount': None,
             'dispositions': dict(Counter(r['disposition'] for r in rows)), 'assessedSha256': sha(out / 'assessed28.safe.json'), 'allDispositionsSha256': sha(out / 'all1840-dispositions.safe.json'),
             'typedFactsSha256': sha(out / 'facts.safe.tsv'), 'owningSuiteHashes': suite_hashes, 'MainChanged': False, 'pmdReissued': False, 'regressionReissued': False, 'vmActions': 0,
             'suppressionAdded': False, 'ruleChanged': False, 'F03Accepted': False, 'formalAccepted': False, 'recordedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True)); value['serverManifestSha256'] = sha(out / 'manifest.safe.json'); print(json.dumps(value))


def main():
    require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT), 'clean fixed reader')
    old = json.loads((W / 'pg3738-hygiene-whole-qualified-v1/manifest.safe.json').read_bytes())
    prior = json.loads((W / 'pg3864-suppression-identity-review-v1/manifest.safe.json').read_bytes())
    cp = json.loads((W / 'pg3690-import-candidate-stage-v1/manifest.safe.json').read_bytes())
    require(not subprocess.check_output(['git', 'diff', 'origin/main', 'HEAD', '--', DOC], cwd=ROOT), 'approved design equals origin/main')
    tests = {n: 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/' + n + 'Test.java' for n in SPECS}
    shared = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/JdbcResourceCases.java'
    require(not subprocess.check_output(['git', 'diff', old['result']['sourceSnapshot'], 'HEAD', '--', *tests.values(), shared], cwd=ROOT), 'same independent68-vector oracle and owning Tests, not new expected values')
    helper = 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/JdbcResourceFailures.java'
    data = {'source': SOURCE, 'specs': SPECS, 'testSha256': {n: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for n, p in tests.items()},
            'sourceSha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('src/*/src/main/java/**/*.java')},
            'priorManifestSha256': prior['result']['serverManifestSha256'], 'qualificationSha256': old['result']['qualificationManifestSha256'],
            'classpathAuthoritySha256': cp['result']['serverManifestSha256'], 'toolSha256': hashlib.sha256((ROOT / TOOL).read_bytes()).hexdigest(),
            'helperSha256': hashlib.sha256((ROOT / helper).read_bytes()).hexdigest(), 'design': {'path': DOC, 'sha256': hashlib.sha256((ROOT / DOC).read_bytes()).hexdigest(), 'basis': 'SSC063/SSC199'},
            'independent68VectorOracleSha256': hashlib.sha256((ROOT / shared).read_bytes()).hexdigest()}
    os.umask(0o077); out = W / 'pg3940-jdbc-finally-review-v1'; out.mkdir()
    script = out / 'review.private.py'; script.write_text('\n'.join(inspect.getsource(f) for f in [require, facts, server]) + '\nserver(' + repr(data) + ')\n')
    compile(script.read_text(), '<read-only JDBC finally assessment>', 'exec')
    destination = '/home/mini/schubert-nk-pgpt/transfer/PG3940-jdbc-finally-review-v1'
    status, _ = run('test ! -e /home/mini/schubert-nk-pgpt/runs/PG3940-jdbc-finally-review-v1 && mkdir -m700 ' + destination, timeout=30); require(status == 0, 'new-only host assessment')
    for p in [script, ROOT / TOOL]:
        status, _ = copy(p, destination + '/', timeout=60); require(status == 0, 'fixed tool and proof inputs')
    status, output = run('python3 -B ' + destination + '/review.private.py', timeout=240); (out / 'observer.private.log').write_text(output)
    value = {'actualExit': status, 'productionSource': SOURCE, 'payloadSha256': hashlib.sha256(script.read_bytes()).hexdigest(), 'F03Accepted': False}
    if status == 0: value['result'] = json.loads(next(line for line in reversed(output.splitlines()) if line.startswith('{')))
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True)); print(json.dumps(value)); return status


if __name__ == '__main__':
    raise SystemExit(main())
