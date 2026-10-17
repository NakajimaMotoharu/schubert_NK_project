"""Recover saved PMD; issue only the missing Checkstyle once. BUG1391/YKT1157."""
import ast
import hashlib
import inspect
import json
import os
import subprocess
from lan_server import copy, run
from pg4844_ssc301_302_full import ROOT, W, SOURCE

SLOT = 'pg4856-static-completion-v1'


def require(value, why):
    if not value:
        raise ValueError(why)


def original_input(raw):
    tree = ast.parse(raw)
    calls = [n.value for n in tree.body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
             and isinstance(n.value.func, ast.Name) and n.value.func.id == 'server']
    require(len(calls) == 1 and len(calls[0].args) == 1, 'one frozen literal invocation')
    value = ast.literal_eval(calls[0].args[0])
    require(value['source'] == SOURCE and value['staticJob'] == 'PG4850-ssc301-302-static-v1'
            and value['includeCheckstyle'] is True, 'original failed phase, never new PMD')
    return value


def server(data):
    import datetime
    import hashlib
    import json
    from collections import Counter
    from pathlib import Path
    import shutil
    import subprocess
    import xml.etree.ElementTree as E
    b = Path('/home/mini/schubert-nk-pgpt')
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    old_root = b / 'runs/PG4850-ssc301-302-static-v1'
    frozen = b / 'transfer/PG4850-ssc301-302-static-v1/static.private.py'
    require(sha(frozen) == data['originalPayloadSha256'], 'exact failed original payload')
    begin = json.loads((old_root / 'begin.safe.json').read_bytes())
    require(begin['productionCandidateSource'] == data['source'], 'original actual PMD begin')
    candidate = b / ('runs/' + data['candidateJob'] + '/candidate')
    source = b / 'source-full-PG4844'
    for root in (source, candidate):
        require({str(p.relative_to(root)): sha(p) for p in root.glob('src/*/src/main/java/**/*.java')}
                == data['sourceSha256'] and len(data['sourceSha256']) == 849, 'all immutable Main inputs')
    old = json.loads((b / 'runs/PG3422-candidate-static-v1/manifest.safe.json').read_bytes())
    require(sha(b / 'runs/PG3422-candidate-static-v1/manifest.safe.json') == data['originalStaticManifestSha256'], 'original pinned tool receipt')
    # Exact command already ran. Every third-party auxiliary and all six current
    # project Jars must still match; no analyzer invocation is reconstructed here.
    aux = json.loads(data['auxJson'])
    require(all(sha(Path(p)) == h for p, h in aux.items()), 'all exact typed auxiliaries')
    require((old_root / 'aux-classpath.txt').read_text().splitlines() == list(aux), 'original auxiliary order')
    rules = b / 'runs/PG3382-static-gate-v1/result/source/tools/quality/static'
    require(all(sha(rules / n) == h for n, h in old['ruleSha256'].items()), 'all original analyzer rules')
    jar = b / 'runs/PG3382-static-gate-v1/checkstyle-14.3.0-all.jar'
    require(sha(jar) == old['pinnedToolSha256']['checkstyle-14.3.0-all.jar'], 'fixed Checkstyle tool')
    root = E.parse(old_root / 'pmd.xml').getroot()
    findings = root.findall('.//{*}violation'); errors = root.findall('.//{*}error')
    require(not errors and findings and not (old_root / 'checkstyle.xml').exists(), 'saved complete PMD, missing-only Checkstyle')
    require(sorted(f.get('name') for f in root.findall('{*}file')) == sorted(set(f.get('name') for f in root.findall('{*}file'))), 'unique PMD paths')
    require(all(Path(f.get('name')).is_relative_to(candidate) for f in root.findall('{*}file')), 'original candidate report paths')
    require((old_root / 'all-java.txt').read_text().splitlines() == [str(p) for p in sorted(candidate.glob('src/*/src/main/java/**/*.java'))], 'original all-file listing')
    counts = dict(Counter(v.get('rule') for v in findings))
    out = b / 'runs/PG4856-static-completion-v1'; out.mkdir(mode=0o700)
    for name in ('pmd.xml', 'pmd.private.log', 'begin.safe.json', 'all-java.txt', 'aux-classpath.txt'):
        shutil.copy2(old_root / name, out / name)
        require(sha(out / name) == sha(old_root / name), 'immutable original evidence copied')
    fixed = json.loads((b / 'runs/PG3382-static-gate-v1/result/manifest.safe.json').read_bytes())
    argv = list(fixed['checkstyle']['argv'])
    argv[argv.index('-c') + 1] = str(rules / 'checkstyle.xml')
    argv[argv.index('-o') + 1] = str(out / 'checkstyle.xml'); argv[-1] = '@' + str(out / 'all-java.txt')
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (out / 'checkstyle-begin.safe.json').write_text(json.dumps({'command': argv, 'startUTC': start, 'source': data['source']}))
    checked = subprocess.run(argv, capture_output=True, timeout=90)
    (out / 'checkstyle.private.log').write_bytes(checked.stdout + checked.stderr)
    cs = E.parse(out / 'checkstyle.xml').getroot().findall('.//error')
    require(checked.returncode == len(cs) % 256, 'fresh actual Checkstyle exit agrees with XML')
    require(all(sha(Path(p)) == h for p, h in aux.items()), 'aux unchanged after missing phase')
    for folder in (candidate, source):
        require({str(p.relative_to(folder)): sha(p) for p in folder.glob('src/*/src/main/java/**/*.java')} == data['sourceSha256'], 'all inputs unchanged after analyzers')
    prior = json.loads((b / 'runs/PG4700-ssc299-static-v1/manifest.safe.json').read_bytes())['pmd']['ruleCounts']
    value = {'actualExit': 0, 'mainGitSource': data['source'], 'sameCurrentSixJarAbi': True,
             'allMainSha256': data['sourceSha256'], 'auxJarSha256': aux, 'rulesSuppressed': False,
             'ruleSha256': old['ruleSha256'], 'pinnedToolSha256': old['pinnedToolSha256'],
             'pmd': {'actualExit': None, 'exitMissingReason': 'Original child numeric exit was checked in frozen control flow but not separately persisted before KeyError; no numeric observation fabricated.', 'originalPhaseReachedAfterExitAndStableInputChecks': True, 'rawFindings': len(findings), 'processingErrors': 0, 'ruleCounts': counts, 'reportSha256': sha(out / 'pmd.xml'), 'logSha256': sha(out / 'pmd.private.log')},
             'checkstyle': {'actualExit': checked.returncode, 'findings': len(cs), 'reportSha256': sha(out / 'checkstyle.xml')},
             'actualRuleCountDeltaFromOld825e': {k: counts.get(k, 0)-prior.get(k, 0) for k in set(counts)|set(prior) if counts.get(k, 0) != prior.get(k, 0)},
             'recoveredOriginalFailure': data['originalFailure'], 'pmdReissued': False, 'vmActions': 0,
             'F03Accepted': False, 'formalAccepted': False, 'startUTC': start,
             'endUTC': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True)); value['serverManifestSha256'] = sha(out / 'manifest.safe.json')
    print(json.dumps(value))


def main():
    old = W / 'pg4850-ssc301-302-static-v1'
    failed = json.loads((old / 'manifest.safe.json').read_bytes()); raw = (old / 'static.private.py').read_text()
    require(failed['actualExit'] == 1 and hashlib.sha256(raw.encode()).hexdigest() == failed['payloadSha256'], 'original actual failed invocation')
    observer = (old / 'observer.private.log').read_text()
    require("KeyError: 'actualExit'" in observer and "proof['renamedPrivateSymbols']" in observer, 'original exact post-PMD failure')
    data = original_input(raw)
    from pg4850_ssc301_302_static import current_auxiliary
    original = json.loads((W / 'pg4700-ssc299-static-v1/manifest.safe.json').read_bytes())['result']
    data.update(auxJson=json.dumps(current_auxiliary(original['auxJarSha256'], data['qualifiedJars'])), originalPayloadSha256=failed['payloadSha256'], originalFailure={'actualExit': 1, 'manifestSha256': hashlib.sha256((old / 'manifest.safe.json').read_bytes()).hexdigest(), 'observerSha256': hashlib.sha256(observer.encode()).hexdigest()})
    require(not subprocess.check_output(['git', 'diff', SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw'], cwd=ROOT), 'fixed qualified source')
    payload = '\n'.join(inspect.getsource(f) for f in (require, server)) + '\nDATA=' + repr(data) + '\nserver(DATA)\n'
    from pyflakes.api import check
    require(check(payload, '<missing-only static continuation>') == 0, 'complete emitted static0')
    os.umask(0o077); out = W / SLOT; out.mkdir(mode=0o700); script = out / 'complete.private.py'; script.write_text(payload)
    remote = '/home/mini/schubert-nk-pgpt/transfer/PG4856-static-completion-v1'
    rc, _ = run('test ! -e /home/mini/schubert-nk-pgpt/runs/PG4856-static-completion-v1 && mkdir -m700 ' + remote, timeout=30); require(rc == 0, 'new-only completion')
    rc, _ = copy(script, remote + '/', timeout=60); require(rc == 0, 'frozen continuation transferred')
    rc, output = run('python3 -B ' + remote + '/complete.private.py', timeout=150); (out / 'observer.private.log').write_text(output)
    value = {'actualExit': rc, 'productionSource': SOURCE, 'payloadSha256': hashlib.sha256(payload.encode()).hexdigest(), 'pmdReissued': False}
    if rc == 0: value['result'] = json.loads(next(x for x in reversed(output.splitlines()) if x.startswith('{')))
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True)); print(json.dumps({k: v for k, v in value.items() if k != 'result'})); return rc


if __name__ == '__main__':
    raise SystemExit(main())
