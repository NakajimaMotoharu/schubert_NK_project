"""SSC308 primitive FD factories and dual inherited ownership; new fixed source, no VM action."""
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
PENDING = 'dev/codex/schubert/nk/batch/file/RootStartupPending'
PENDING_SUITES = {
    'dev.codex.schubert.nk.batch.file.RootPendingWaitTest': 'batch',
    'dev.codex.schubert.nk.batch.file.RootStartupPendingTest': 'batch',
    'dev.codex.schubert.nk.batch.file.StartupLaunchFilesTest': 'batch',
}
FACTORY_REFERENCE = 'e8ecff1bec1d7ddd51cdfbf803acda07c2f6cdb9'
FACTORY_FULL = ROOT.parent / 'pgpt-runs/PG379/pg5130-root-whole-qualified-v1/manifest.safe.json'
SCOPE = 'dev/codex/schubert/nk/storage/ResourceScope'
DIRECTORY = 'dev/codex/schubert/nk/storage/OwnedTransferDirectory'
TEST_UMASK = 0o027


def storage_suites():
    folder = ROOT / 'src/schubert-nk-storage/src/test/java'
    result = {}
    for path in sorted(folder.rglob('*Test.java')):
        if path.is_symlink(): raise ValueError('physical test source only')
        if '@Test' in path.read_text():
            result[path.relative_to(folder).with_suffix('').as_posix().replace('/', '.')] = 'storage'
    if len(result) != 25: raise ValueError('actual all25 storage suites required')
    return result


def commands_for(base, suites=SUITES):
    return [base + ['-pl', ','.join('src/schubert-nk-' + m for m in SIX), 'spotless:check'],
            base + ['-pl', 'src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-batch', '-am',
                    '-Dtest=' + ','.join(suites), '-Dsurefire.failIfNoSpecifiedTests=false', 'test',
                    'org.jacoco:jacoco-maven-plugin:0.8.15:report',
                    'com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check']]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def main_delta(snapshot, group='elf'):
    reference = json.loads((FACTORY_FULL if group == 'factory' else FULL).read_bytes())
    q = reference['result']
    source = FACTORY_REFERENCE if group == 'factory' else BASE
    tests, classes = (3814, 1654) if group == 'factory' else (3791, 1650)
    if not (type(reference['actualExit']) is int and reference['actualExit'] == 0 and q['productionSource'] == source
            and q['tests'] == tests and q['mainClasses'] == classes
            and len(q['allPhysicalMainSha256']) == classes
            and q['allSixFormatBeforeAnyPt'] is True and q['staticSixModules'] == 0
            and q['FESFlakyNotRun'] == 0):
        raise ValueError('original same-source qualification required')
    expected = {k: v for k, v in q['allPhysicalMainSha256'].items() if k.split(':', 1)[0] in BUILT}
    actual = {m + ':' + p.relative_to(snapshot / ('src/schubert-nk-' + m + '/target/classes')).as_posix(): sha(p)
              for m in BUILT for p in (snapshot / ('src/schubert-nk-' + m + '/target/classes')).rglob('*.class')}
    changed = sorted(k for k in actual.keys() & expected.keys() if actual[k] != expected[k])
    added = sorted(actual.keys() - expected.keys())
    removed = sorted(expected.keys() - actual.keys())
    allowed_changed = {'batch:' + CLASS + '.class'}
    allowed_added = {'batch:' + CLASS + '$DigestFactory.class'}
    if group == 'pending':
        allowed_changed.add('batch:' + PENDING + '.class')
        allowed_added |= {'batch:' + PENDING + suffix + '.class' for suffix in ('$WaitIo', '$LaunchRead', '$1')}
    if group == 'factory':
        allowed_changed = {'batch:' + CLASS + '.class', 'batch:' + PENDING + '.class',
                           'batch:' + PENDING + '$1.class', 'storage:' + SCOPE + '.class',
                           'storage:' + DIRECTORY + '.class', 'storage:' + DIRECTORY + '$EntryHandle.class'}
        allowed_added = {'storage:' + SCOPE + suffix + '.class' for suffix in ('$Acquire', '$Release', '$OwnedAction')}
        allowed_added |= {'storage:' + DIRECTORY + '$EntryOpen.class', 'batch:' + CLASS + '$RootDescriptor.class'}
        allowed_changed |= {'storage:dev/codex/schubert/nk/storage/' + name + '.class'
                            for name in ('StorageRootInspection', 'ExistingFileAccess', 'ServiceConfigFiles', 'LinuxFilesystemClassifier')}
    if group == 'factory':
        native = 'storage:dev/codex/schubert/nk/storage/'
        native_names = ('LinuxFileLock','LinuxSealedProof','LinuxStartupAdmission')
        allowed_changed |= {native+n+'.class' for n in native_names} | {native+'LinuxFileLock$OwnedDescriptor.class'}
        allowed_added |= {native+'LinuxSealedProof$Descriptor.class',native+'LinuxStartupAdmission$FdOwners.class'}
        optional_debug = {key for key in expected if any(key.startswith(native+n+'$') for n in native_names)} - allowed_changed
    else:
        optional_debug = set()
    if not allowed_changed <= set(changed) or not set(changed) <= allowed_changed | optional_debug or set(added) != allowed_added or removed:
        raise ValueError('declared semantic changes plus explicitly bounded nested debug candidates only')
    return {'referenceSource': source, 'originalPhysicalMain': classes, 'selectedPhysicalMain': len(actual),
            'changed': changed, 'added': added, 'removed': removed, 'oldNativeImported': False,
            'physicalSha256': actual}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=('red', 'green'))
    parser.add_argument('--group', choices=('elf', 'pending', 'guards', 'factory'), default='elf')
    args = parser.parse_args()
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed source required')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    version = 'v2' if args.phase == 'red' else 'v3'
    stem = {'elf': 'pg5120-root-elf', 'pending': 'pg5124-root-pending', 'guards': 'pg5126-root-guards',
            'factory': 'pg5136-factory-io'}[args.group]
    if args.group != 'elf': version = 'v1'
    if args.group == 'factory': version = 'v2'
    if args.group != 'factory' or args.phase != 'green': raise ValueError('this new run accepts factory green only')
    stem = 'pg5148-native-fd'
    work = ROOT.parent / ('pgpt-runs/PG379/' + stem + '-' + args.phase + '-' + version)
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
    suites = SUITES if args.group == 'elf' else {**SUITES, **PENDING_SUITES}
    if args.group in ('guards', 'factory'): suites = {**suites, 'dev.codex.schubert.nk.batch.file.RootEntryRejectionTest': 'batch'}
    if args.group == 'factory': suites = {**suites, **storage_suites()}
    for name, module in suites.items():
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
    commands = commands_for(base, suites)
    begin = {'sourceSnapshot': head, 'deployedSource': BASE, 'phase': args.phase, 'group': args.group, 'startUTC': utc(),
             'archiveSha256': sha(archive), 'inputs': inputs, 'expectedMethods': expected,
             'commands': commands, 'parentUmask': '0077', 'childMavenUmask': '0027',
             'vmActions': 0, 'wholeRegression': False, 'formalAccepted': False}
    (work / 'begin.safe.json').write_text(json.dumps(begin, sort_keys=True))
    codes = []; logs = {}
    for index, command in enumerate(commands):
        path = work / ('phase-' + str(index) + '.private.log')
        with path.open('xb') as log:
            child = subprocess.Popen(command, cwd=snapshot, env=env, stdout=log, stderr=log, umask=TEST_UMASK)
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
        if cov.is_file() and (module == 'batch' or args.group == 'factory' and module == 'storage'):
            for c in ET.parse(cov).getroot().findall('package/class'):
                required = {CLASS, PENDING} if args.group != 'elf' else {CLASS}
                if args.group == 'factory': required |= {SCOPE, DIRECTORY, CLASS + '$RootDescriptor'}
                if c.get('name') in required:
                    for method in c.findall('method'):
                        digest_target = c.get('name') == CLASS and (method.get('name') == 'digest' or method.get('name', '').startswith('lambda$digest$'))
                        pending_target = c.get('name') == PENDING and (method.get('name') == 'readLaunch' or (method.get('name') == 'awaitLaunch' and '$WaitIo;' in method.get('desc', '')))
                        factory_target = args.group == 'factory' and (
                            c.get('name') == SCOPE and method.get('name') in ('acquire', 'use')
                            or c.get('name') == DIRECTORY and method.get('name') == 'openRoot'
                            or c.get('name') == CLASS + '$RootDescriptor' and method.get('name') in ('<init>', 'close'))
                        if digest_target or pending_target or factory_target:
                            key = method.get('name') + method.get('desc')
                            counters[key] = {v.get('type'): {'missed': int(v.get('missed')), 'covered': int(v.get('covered'))}
                                             for v in method.findall('counter')}
    if actual != expected: reasons.append('exact selected case inventory incomplete')
    if not all(sha(snapshot / path) == digest for path, digest in inputs.items()): reasons.append('frozen input changed')
    if set(static) != set(BUILT) or any(static.values()): reasons.append('required three compiled-module fresh static incomplete/nonzero')
    if len(counters) != (10 if args.group == 'factory' else 5 if args.group != 'elf' else 3) or any(v['missed'] for counts in counters.values() for kind, v in counts.items()
                                   if kind in ('LINE', 'METHOD', 'BRANCH')):
        reasons.append('all digest overload/default-factory line/method/branch required')
    delta = None
    if codes == [0, 0]:
        try: delta = main_delta(snapshot, args.group if args.group in ('elf', 'factory') else 'pending')
        except ValueError as failure: reasons.append(str(failure))
    storage_report = ET.parse(snapshot / 'src/schubert-nk-storage/target/site/jacoco/jacoco.xml').getroot() if (snapshot / 'src/schubert-nk-storage/target/site/jacoco/jacoco.xml').is_file() else None
    storage_four = {v.get('type'): {'missed':int(v.get('missed')), 'covered':int(v.get('covered'))}
                    for v in storage_report.findall('counter') if v.get('type') in ('LINE','METHOD','CLASS','BRANCH')} if storage_report is not None else {}
    if set(storage_four) != {'LINE','METHOD','CLASS','BRANCH'} or any(v['missed'] for v in storage_four.values()):
        reasons.append('all storage four counters must be complete; no exclusions')
    result = {'storageFourCounters':storage_four, **{k: v for k, v in begin.items() if k != 'inputs'}, 'endUTC': utc(), 'phaseExits': codes,
              'actualExit': 0 if codes == [0, 0] and not reasons else 1, 'tests': sum(map(len, actual.values())),
              'suites': len(actual), 'actualMethods': actual, 'xmlSha256': xml, 'logSha256': logs,
              'freshStatic': static, 'targetCoverage': counters, 'mainDelta': delta, 'reasons': reasons,
              'tdDRedIsNotAcceptance': args.phase == 'red'}
    (work / 'manifest.safe.json').write_text(json.dumps(result, sort_keys=True))
    print(json.dumps({k: result[k] for k in ('sourceSnapshot', 'phase', 'phaseExits', 'actualExit', 'tests', 'suites', 'reasons')}))
    return result['actualExit']


if __name__ == '__main__':
    raise SystemExit(main())
