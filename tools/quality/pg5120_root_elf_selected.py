"""Frozen SSC306 RED/GREEN selected PT; actual XML/Main delta; no VM or full regression."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
BASE = 'a2ecc77ca312c383246c94ea692c4db7487112cd'
FULL = ROOT.parent / 'pgpt-runs/PG379/pg4970-ssc304-whole-qualified-v1/manifest.safe.json'
TC = ROOT.parent / 'toolchain'
CLASS = 'dev/codex/schubert/nk/batch/file/RootServiceExecutableAdmission'
SUITES = {
    'dev.codex.schubert.nk.storage.ServiceConfigFilesTest': 'storage',
    'dev.codex.schubert.nk.api.bootstrap.ApiNonSecretConfigTest': 'bootstrap',
    'dev.codex.schubert.nk.batch.file.RootServiceExecutableAdmissionTest': 'batch',
    'dev.codex.schubert.nk.batch.file.RootElfDigestPortTest': 'batch',
}
BUILT = ('storage', 'bootstrap', 'batch')
SIX = ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch')


def commands_for(base):
    return [base + ['-pl', ','.join('src/schubert-nk-' + m for m in SIX), 'spotless:check'],
            base + ['-pl', 'src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-batch', '-am',
                    '-Dtest=' + ','.join(SUITES), '-Dsurefire.failIfNoSpecifiedTests=false', 'test',
                    'org.jacoco:jacoco-maven-plugin:0.8.15:report',
                    'com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check']]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def main_delta(snapshot):
    reference = json.loads(FULL.read_bytes())
    q = reference['result']
    if not (reference['actualExit'] == 0 and q['productionSource'] == BASE
            and q['tests'] == 3791 and q['mainClasses'] == 1650
            and len(q['allPhysicalMainSha256']) == 1650
            and q['allSixFormatBeforeAnyPt'] is True and q['staticSixModules'] == 0
            and q['FESFlakyNotRun'] == 0):
        raise ValueError('original same-source qualification required')
    expected = {k: v for k, v in q['allPhysicalMainSha256'].items() if k.split(':', 1)[0] in BUILT}
    actual = {m + ':' + p.relative_to(snapshot / ('src/schubert-nk-' + m + '/target/classes')).as_posix(): sha(p)
              for m in BUILT for p in (snapshot / ('src/schubert-nk-' + m + '/target/classes')).rglob('*.class')}
    changed = sorted(k for k in actual.keys() & expected.keys() if actual[k] != expected[k])
    added = sorted(actual.keys() - expected.keys())
    removed = sorted(expected.keys() - actual.keys())
    if changed != ['batch:' + CLASS + '.class'] or added != ['batch:' + CLASS + '$DigestFactory.class'] or removed:
        raise ValueError('only Root ELF outer and one declared DigestFactory may differ')
    return {'referenceSource': BASE, 'originalPhysicalMain': 1650, 'selectedPhysicalMain': len(actual),
            'changed': changed, 'added': added, 'removed': removed, 'oldNativeImported': False,
            'physicalSha256': actual}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=('red', 'green'))
    args = parser.parse_args()
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed source required')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    version = 'v2' if args.phase == 'red' else 'v3'
    work = ROOT.parent / ('pgpt-runs/PG379/pg5120-root-elf-' + args.phase + '-' + version)
    os.umask(0o077)
    work.mkdir(mode=0o700)
    archive = work / 'source.tar'
    with archive.open('xb') as target:
        subprocess.run(['git', 'archive', head, 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization'],
                       cwd=ROOT, stdout=target, check=True)
        target.flush(); os.fsync(target.fileno())
    snapshot = work / 'source'; snapshot.mkdir(mode=0o700)
    with tarfile.open(archive) as saved:
        saved.extractall(snapshot, filter='data')
    inputs = {str(p.relative_to(snapshot)): sha(p) for p in snapshot.rglob('*') if p.is_file()}
    expected = {}
    for name, module in SUITES.items():
        text = (snapshot / ('src/schubert-nk-' + module + '/src/test/java/' + name.replace('.', '/') + '.java')).read_text()
        methods = re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(', text)
        if len(methods) != text.count('@Test') or len(set(methods)) != len(methods):
            raise ValueError('literal exact nonempty case inventory')
        expected[name] = sorted(methods)
    env = {k: v for k, v in os.environ.items() if k not in ('JAVA_TOOL_OPTIONS', 'JDK_JAVA_OPTIONS', '_JAVA_OPTIONS', 'CLASSPATH')}
    env.update(JAVA_HOME=str(TC / 'jdk-25.0.4'), PATH=str(TC / 'jdk-25.0.4/bin') + ':' + os.environ['PATH'],
               MAVEN_OPTS='-Xmx768m -Djava.io.tmpdir=' + str(work),
               SCHUBERT_PG_ROOT=str(ROOT.parent / 'characterization-tools/root/usr'))
    base = [str(TC / 'm2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'), '-B', '-o',
            '-Dmaven.repo.local=' + str(TC / 'm2/repository')]
    commands = commands_for(base)
    begin = {'sourceSnapshot': head, 'deployedSource': BASE, 'phase': args.phase, 'startUTC': utc(),
             'archiveSha256': sha(archive), 'inputs': inputs, 'expectedMethods': expected,
             'commands': commands, 'vmActions': 0, 'wholeRegression': False, 'formalAccepted': False}
    (work / 'begin.safe.json').write_text(json.dumps(begin, sort_keys=True))
    codes = []; logs = {}
    for index, command in enumerate(commands):
        path = work / ('phase-' + str(index) + '.private.log')
        with path.open('xb') as log:
            child = subprocess.Popen(command, cwd=snapshot, env=env, stdout=log, stderr=log)
            proc = Path('/proc') / str(child.pid)
            owner = {'pid': child.pid, 'ticks': int((proc / 'stat').read_text().rsplit(')', 1)[1].split()[19]),
                     'argvSha256': hashlib.sha256((proc / 'cmdline').read_bytes()).hexdigest(), 'phase': index}
            (work / ('owner-' + str(index) + '.safe.json')).write_text(json.dumps(owner))
            codes.append(child.wait()); log.flush(); os.fsync(log.fileno())
        logs[path.name] = sha(path)
        if codes[-1]: break
    actual = {}; xml = {}; reasons = []; static = {}; counters = {}
    for module in BUILT:
        target = snapshot / ('src/schubert-nk-' + module + '/target')
        for path in sorted((target / 'surefire-reports').glob('TEST-*.xml')):
            suite = ET.parse(path).getroot(); name = suite.get('name')
            if name in actual: reasons.append('duplicate suite')
            actual[name] = sorted(c.get('name') for c in suite.findall('testcase'))
            xml[name] = sha(path)
            for tag in ('failure', 'error', 'skipped', 'flakyFailure', 'flakyError', 'rerunFailure', 'rerunError'):
                if suite.findall('.//' + tag): reasons.append('non-success ' + tag)
            if any(suite.get(k) != '0' for k in ('failures', 'errors', 'skipped')): reasons.append('FES nonzero')
        static_path = target / 'spotbugsXml.xml'
        if static_path.is_file():
            static[module] = len(ET.parse(static_path).getroot().findall('.//BugInstance'))
        cov = target / 'site/jacoco/jacoco.xml'
        if cov.is_file() and module == 'batch':
            for c in ET.parse(cov).getroot().findall('package/class'):
                if c.get('name') == CLASS:
                    for method in c.findall('method'):
                        if method.get('name') == 'digest' or method.get('name', '').startswith('lambda$digest$'):
                            key = method.get('name') + method.get('desc')
                            counters[key] = {v.get('type'): {'missed': int(v.get('missed')), 'covered': int(v.get('covered'))}
                                             for v in method.findall('counter')}
    if actual != expected: reasons.append('exact selected case inventory incomplete')
    if not all(sha(snapshot / path) == digest for path, digest in inputs.items()): reasons.append('frozen input changed')
    if set(static) != set(BUILT) or any(static.values()): reasons.append('required three compiled-module fresh static incomplete/nonzero')
    if len(counters) != 3 or any(v['missed'] for counts in counters.values() for kind, v in counts.items()
                                   if kind in ('LINE', 'METHOD', 'BRANCH')):
        reasons.append('all digest overload/default-factory line/method/branch required')
    delta = None
    if codes == [0, 0]:
        try: delta = main_delta(snapshot)
        except ValueError as failure: reasons.append(str(failure))
    result = {**{k: v for k, v in begin.items() if k != 'inputs'}, 'endUTC': utc(), 'phaseExits': codes,
              'actualExit': 0 if codes == [0, 0] and not reasons else 1, 'tests': sum(map(len, actual.values())),
              'suites': len(actual), 'actualMethods': actual, 'xmlSha256': xml, 'logSha256': logs,
              'freshStatic': static, 'targetCoverage': counters, 'mainDelta': delta, 'reasons': reasons,
              'tdDRedIsNotAcceptance': args.phase == 'red'}
    (work / 'manifest.safe.json').write_text(json.dumps(result, sort_keys=True))
    print(json.dumps({k: result[k] for k in ('sourceSnapshot', 'phase', 'phaseExits', 'actualExit', 'tests', 'suites', 'reasons')}))
    return result['actualExit']


if __name__ == '__main__':
    raise SystemExit(main())
