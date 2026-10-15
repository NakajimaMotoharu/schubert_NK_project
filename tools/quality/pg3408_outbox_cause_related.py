"""One fixed-candidate related60/11 run; new API class is never given old native credit."""
import hashlib
import inspect
import json
import os
from pathlib import Path
import shlex
import subprocess

from lan_server import copy, run
from pg3348_related_boundary_group import classify, require

ROOT = Path(__file__).resolve().parents[2]
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
BASE = '/home/mini/schubert-nk-pgpt'
DEPLOYED = 'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25'
MAIN = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxJmsSender.java'
CHANGED = {MAIN,
           'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxDispatcherTest.java',
           'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/AuthenticationFailureGraphTest.java',
           'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/SessionFailureGraphTest.java'}
CLASSES = {
    'protocol': {'dev.codex.schubert.nk.protocol.file.LargeResultRecordCodecTest': 7},
    'storage': {'dev.codex.schubert.nk.storage.LinuxProcessExecTest': 8},
    'bootstrap': {'dev.codex.schubert.nk.bootstrap.FixedNativeCoverageProfileTest': 5},
    'api': {'dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatcherTest': 19,
            'dev.codex.schubert.nk.api.security.AuthenticationFailureGraphTest': 1},
    'web': {'dev.codex.schubert.nk.web.logging.WebLogMessageSenderTest': 5,
            'dev.codex.schubert.nk.web.session.SessionFailureGraphTest': 1,
            'dev.codex.schubert.nk.web.revocation.RevocationRetryCoordinatorTest': 8},
    'batch': {'dev.codex.schubert.nk.batch.file.MorningStartupRetainOwnerTest': 1,
              'dev.codex.schubert.nk.batch.file.MorningStartupLaunchOwnerTest': 3,
              'dev.codex.schubert.nk.batch.file.MorningStartupLaunchOwnerAdmissionTest': 2}}


def server(data):
    import datetime
    import hashlib
    import json
    import os
    from pathlib import Path
    import shutil
    import subprocess
    import tarfile
    import xml.etree.ElementTree as E
    import zipfile

    os.umask(0o077)
    b = Path('/home/mini/schubert-nk-pgpt')
    out = b / 'runs/PG3408-related-v1'; source = b / 'source-PG3408-related-v1'
    require(shutil.disk_usage(b).free > 12 * 1024 ** 3, 'capacity before new selected build')
    out.mkdir(); source.mkdir(); (out / 'tmp').mkdir()
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    archive = b / 'transfer/PG3408-related-v1/source.tar'
    require(sha(archive) == data['archiveSha256'], 'fixed archive')
    with tarfile.open(archive) as image:
        image.extractall(source, filter='data')
    inputs = {str(p.relative_to(source)): sha(p) for p in source.rglob('*') if p.is_file()}
    env = {k: v for k, v in os.environ.items() if k not in ['JAVA_TOOL_OPTIONS', 'JDK_JAVA_OPTIONS', '_JAVA_OPTIONS']}
    env.update(JAVA_HOME=str(b / 'tools/jdk-25.0.4'),
               PATH=str(b / 'tools/jdk-25.0.4/bin') + ':' + env['PATH'],
               SCHUBERT_PG_ROOT=str(b / 'tools/postgresql18/usr'),
               SCHUBERT_SHELLCHECK=str(b / 'tools/shellcheck-0.11.0'),
               MAVEN_OPTS='-Xmx768m -Djava.io.tmpdir=' + str(out / 'tmp'))
    require((Path(env['SCHUBERT_PG_ROOT']) / 'lib/postgresql/18/bin/initdb').is_file(), 'actual PG18 root')
    argv = [str(b / 'tools/maven/bin/mvn'), '-o', '--no-transfer-progress', '-Dstyle.color=never',
            '-Djansi.force=false', '-Dmaven.repo.local=' + str(b / 'm2/repository'),
            '-Dnk.pt.node=' + str(b / 'tools/node-v24.19.0/bin/node'), '-Dnk.pt.repository=' + str(source),
            '-Dtest=' + ','.join(c for names in data['classes'].values() for c in names),
            '-pl', ','.join('src/schubert-nk-' + m for m in data['classes']),
            'clean', 'spotless:check', 'test-compile', 'jar:test-jar', 'test', 'spotbugs:check', 'jacoco:report', 'jar:jar']
    start = datetime.datetime.now(datetime.timezone.utc)
    begin = {'run': 'PG3408-related-v1', 'startUTC': start.isoformat(), 'pid': os.getpid(),
             'ticks': int(Path('/proc/self/stat').read_text().rsplit(')', 1)[1].split()[19]),
             'candidateSource': data['candidateSource'], 'sourceSnapshot': data['head'],
             'archiveSha256': data['archiveSha256'], 'expectedTests': 60, 'expectedSuites': 11,
             'command': argv}
    (out / 'begin.safe.json').write_text(json.dumps(begin))
    print(json.dumps({'started': {k: v for k, v in begin.items() if k != 'command'}}), flush=True)
    with (out / 'maven.private.log').open('xb') as log:
        actual = subprocess.run(argv, cwd=source, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=900, umask=0o027)
    (out / 'maven-exit.safe.json').write_text(json.dumps({'mavenExit': actual.returncode, 'head': data['head']}))
    require(actual.returncode == 0, 'real selected Maven0 required')
    modules = {}; cases = set(); total_main = 0
    changed_class = 'dev/codex/schubert/nk/api/messaging/outbound/OutboxJmsSender.class'
    for module, expected in data['classes'].items():
        target = source / ('src/schubert-nk-' + module + '/target')
        xmls = sorted((target / 'surefire-reports').glob('TEST-*.xml'))
        actual_cases = classify([E.parse(p).getroot() for p in xmls], expected); cases.update(actual_cases)
        static = target / 'spotbugsXml.xml'
        require(not E.parse(static).findall('.//BugInstance'), 'SpotBugs0')
        jar = target / ('schubert-nk-' + module + '-0.1.0-SNAPSHOT.jar')
        old = b / 'runs/PG3398-six-v1' / module / jar.name
        require(sha(old) == data['priorJarHashes'][module], 'actual whole3707 old jar')
        images = []
        for p in [old, jar]:
            with zipfile.ZipFile(p) as z:
                require(len(z.namelist()) == len(set(z.namelist())), 'unique jar members')
                images.append({n: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()})
        require(images[0].keys() == images[1].keys(), 'same complete physical members')
        differences = sorted(n for n in images[0] if images[0][n] != images[1][n])
        require(differences == ([changed_class] if module == 'api' else []), 'exactly registered one Main class changes; no old native credit')
        physical = sum(n.endswith('.class') for n in images[1]); total_main += physical
        coverage = target / 'site/jacoco/jacoco.xml'; cov = E.parse(coverage).getroot()
        modules[module] = {'tests': len(actual_cases), 'suites': len(xmls), 'mainClasses': physical,
                           'jarSha256': sha(jar), 'changedMembers': differences,
                           'xmlHashes': {p.name: sha(p) for p in xmls}, 'staticSha256': sha(static),
                           'coverageXmlSha256': sha(coverage)}
        if module == 'api':
            cls = next(c for pkg in cov.findall('package') for c in pkg.findall('class') if c.get('name') + '.class' == changed_class)
            method = next(m for m in cls.findall('method') if m.get('name') == 'isDuplicateConfirmation')
            counters = {c.get('type'): {'missed': int(c.get('missed')), 'covered': int(c.get('covered'))} for c in method.findall('counter')}
            require(all(counters[k]['missed'] == 0 for k in ['LINE', 'METHOD', 'BRANCH']), 'entire changed graph method covered')
            modules[module]['changedMethodCounters'] = counters
    require(len(cases) == 60 and sum(m['suites'] for m in modules.values()) == 11 and total_main == 1643, 'genuine60/11/1643')
    require(all(sha(source / p) == h for p, h in inputs.items()), 'all frozen inputs unchanged')
    result = {'actualExit': 0, 'mavenExit': 0, 'run': 'PG3408-related-v1', 'candidateSource': data['candidateSource'],
              'deployedProductionSource': data['deployedSource'], 'sourceSnapshot': data['head'],
              'archiveSha256': data['archiveSha256'], 'tests': 60, 'suites': 11, 'mainClasses': total_main,
              'FESFlakyNotRun': 0, 'existingStaticSixModules': 0, 'modules': modules,
              'oldNativeImported': False, 'fullRegressionPending': True, 'nativePending': True,
              'formalUpdated': False, 'vmActions': 0, 'startUTC': start.isoformat(),
              'endUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'logSha256': sha(out / 'maven.private.log')}
    (out / 'manifest.safe.json').write_text(json.dumps(result, sort_keys=True))
    result['serverManifestSha256'] = sha(out / 'manifest.safe.json')
    print(json.dumps(result))


def main():
    require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT), 'clean fixed source')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    candidate = subprocess.check_output(['git', 'log', '-1', '--format=%H', '--', MAIN], cwd=ROOT, text=True).strip()
    old = json.loads((W / 'pg3400-oracle-boundary-full-qualified-v1/manifest.safe.json').read_bytes())
    require(old['actualExit'] == 0 and old['result']['tests'] == 3707, 'qualified original3707')
    changed = set(subprocess.check_output(['git', 'diff', '--name-only', old['result']['sourceSnapshot'], head,
                                         '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'program/characterization'], cwd=ROOT, text=True).splitlines())
    require(changed == CHANGED and candidate != DEPLOYED, 'only registered one Main and three Test files')
    require(sum(sum(v.values()) for v in CLASSES.values()) == 60, 'independent selected60')
    os.umask(0o077); out = W / 'pg3408-outbox-cause-related-v1'; out.mkdir()
    archive = out / 'source.tar'
    archive.write_bytes(subprocess.check_output(['git', 'archive', '--format=tar', head, 'pom.xml', 'mvnw', '.mvn', 'src', 'program/characterization', 'documents/100_RD', 'documents/200_UI', 'documents/300_SS'], cwd=ROOT))
    data = {'head': head, 'candidateSource': candidate, 'deployedSource': DEPLOYED,
            'archiveSha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'classes': CLASSES,
            'priorJarHashes': old['result']['jarHashes']}
    payload = inspect.getsource(require) + '\n' + inspect.getsource(classify) + '\n' + inspect.getsource(server) + '\nserver(' + repr(data) + ')\n'
    compile(payload, '<related60 exact candidate>', 'exec')
    script = out / 'related.private.py'; script.write_text(payload)
    rc, _ = run('test ! -e ' + BASE + '/runs/PG3408-related-v1 && test ! -e ' + BASE + '/source-PG3408-related-v1 && mkdir -m700 ' + BASE + '/transfer/PG3408-related-v1', timeout=30)
    require(rc == 0, 'new-only related60 slot')
    for path in [archive, script]:
        rc, _ = copy(path, BASE + '/transfer/PG3408-related-v1/', timeout=60); require(rc == 0, 'fixed source transfer')
    rc, output = run('python3 -B ' + shlex.quote(BASE + '/transfer/PG3408-related-v1/related.private.py'), timeout=960)
    (out / 'observer.private.log').write_text(output)
    receipt = {'actualExit': rc, 'payloadSha256': hashlib.sha256(payload.encode()).hexdigest(), 'formalUpdated': False}
    if rc == 0:
        receipt['result'] = json.loads(next(line for line in reversed(output.splitlines()) if line.startswith('{')))
    (out / 'manifest.safe.json').write_text(json.dumps(receipt, sort_keys=True))
    print(json.dumps({k: v for k, v in receipt.items() if k != 'result'}))
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
