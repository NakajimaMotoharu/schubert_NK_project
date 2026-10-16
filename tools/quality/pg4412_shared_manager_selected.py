"""Frozen-source isolated Maven selection, compiler NullAway and fresh JaCoCo; no VM action."""
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
WORK = ROOT.parent / 'pgpt-runs/PG379/pg4412-shared-manager-selected-v1'
SOURCE = '964e96e45'
TOOLCHAIN = ROOT.parent / 'toolchain'
BOOT = 'dev.codex.schubert.nk.bootstrap.'
TESTS = [BOOT + n for n in ['SystemManagerObservationTest', 'LinuxSystemdSessionTest',
    'ChildStartupContextTest', 'ChildMaintenanceParentTest', 'ChildMaintenanceInspectorTest',
    'ChildBrokerTest', 'ChildCaddyTest', 'MaintenanceParentGuardTest', 'MaintenanceOwnerFrameTest']]
TESTS += ['dev.codex.schubert.nk.batch.platform.RootStartupContextTest']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    os.umask(0o077)
    head = subprocess.check_output(['git', 'rev-parse', SOURCE], cwd=ROOT, text=True).strip()
    WORK.mkdir(mode=0o700)
    archive = WORK / 'source.tar'
    with archive.open('xb') as target:
        subprocess.run(['git', 'archive', head, 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization'],
                       cwd=ROOT, stdout=target, check=True)
        target.flush(); os.fsync(target.fileno())
    snapshot = WORK / 'source'; snapshot.mkdir(mode=0o700)
    with tarfile.open(archive) as saved:
        saved.extractall(snapshot, filter='data')
    files = {str(p.relative_to(snapshot)): sha(p) for p in snapshot.rglob('*') if p.is_file()}
    expected = {}
    for name in TESTS:
        module = 'batch' if '.batch.' in name else 'bootstrap'
        text = (snapshot / ('src/schubert-nk-' + module + '/src/test/java/' + name.replace('.', '/') + '.java')).read_text()
        methods = re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(', text)
        if len(methods) != text.count('@Test') or len(set(methods)) != len(methods):
            raise ValueError('independent exact real method inventory required')
        expected[name] = sorted(methods)
    env = {k: v for k, v in os.environ.items() if k not in ['JAVA_TOOL_OPTIONS', 'JDK_JAVA_OPTIONS', '_JAVA_OPTIONS', 'CLASSPATH']}
    env.update(JAVA_HOME=str(TOOLCHAIN / 'jdk-25.0.4'),
               PATH=str(TOOLCHAIN / 'jdk-25.0.4/bin') + ':' + os.environ['PATH'],
               MAVEN_OPTS='-Xmx768m -Djava.io.tmpdir=' + str(WORK),
               SCHUBERT_PG_ROOT=str(TOOLCHAIN / 'postgresql18/usr'))
    command = [str(TOOLCHAIN / 'm2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),
               '-B', '-o', '-Dmaven.repo.local=' + str(TOOLCHAIN / 'm2/repository'),
               '-pl', 'src/schubert-nk-batch', '-am', '-Dtest=' + ','.join(TESTS),
               '-Dsurefire.failIfNoSpecifiedTests=false', 'test',
               'org.jacoco:jacoco-maven-plugin:0.8.15:report']
    began = datetime.datetime.now(datetime.timezone.utc).isoformat()
    begin = {'sourceSnapshot': head, 'archiveSha256': sha(archive), 'inputs': files,
             'expectedMethods': expected, 'command': command, 'startUTC': began,
             'sourceRole': 'unaccepted candidate; deployed source remains7bb', 'replayAllowed': False}
    (WORK / 'begin.safe.json').write_text(json.dumps(begin, sort_keys=True))
    with (WORK / 'maven.private.log').open('xb') as log:
        child = subprocess.Popen(command, cwd=snapshot, env=env, stdout=log, stderr=log)
        proc = Path('/proc') / str(child.pid)
        owner = {'pid': child.pid, 'ticks': int((proc / 'stat').read_text().rsplit(')', 1)[1].split()[19]),
                 'argvSha256': hashlib.sha256((proc / 'cmdline').read_bytes()).hexdigest()}
        (WORK / 'owner.safe.json').write_text(json.dumps(owner))
        code = child.wait(); log.flush(); os.fsync(log.fileno())
    actual = {}; xmls = {}; counters = {}; reasons = []
    for module in ['protocol', 'storage', 'bootstrap', 'api', 'web', 'batch']:
        target = snapshot / ('src/schubert-nk-' + module + '/target')
        for path in sorted((target / 'surefire-reports').glob('TEST-*.xml')):
            report = ET.parse(path).getroot(); name = report.get('name')
            methods = [case.get('name') for case in report.findall('testcase')]
            if name in actual: reasons.append('duplicate suite')
            actual[name] = sorted(methods); xmls[name] = sha(path)
            if any(report.get(k) != '0' for k in ['failures', 'errors', 'skipped']): reasons.append('FES nonzero')
            if report.findall('.//failure') or report.findall('.//error') or report.findall('.//skipped'): reasons.append('non-success case')
        cov = target / 'site/jacoco/jacoco.xml'
        if cov.exists():
            tree = ET.parse(cov).getroot()
            for entry in tree.findall('package/class'):
                if entry.get('name') in ['dev/codex/schubert/nk/bootstrap/SystemManagerObservation',
                                         'dev/codex/schubert/nk/bootstrap/SystemManagerObservation$Service',
                                         'dev/codex/schubert/nk/bootstrap/LinuxSystemdSession',
                                         'dev/codex/schubert/nk/bootstrap/LinuxSystemdSession$Native',
                                         'dev/codex/schubert/nk/bootstrap/LinuxSystemdSession$Factory']:
                    counters[entry.get('name')] = {c.get('type'): {'missed': int(c.get('missed')), 'covered': int(c.get('covered'))}
                                                   for c in entry.findall('counter')}
    if actual != expected: reasons.append('selected identity inventory differs')
    if not all(sha(snapshot / p) == value for p, value in files.items()): reasons.append('fixed input changed')
    value = {'actualMavenExit': code, 'actualExit': 0 if code == 0 and not reasons else 1,
             'sourceSnapshot': head, 'startUTC': began, 'endUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'tests': sum(len(v) for v in actual.values()), 'suites': len(actual), 'xmlSha256': xmls,
             'reasons': reasons, 'coverage': counters, 'wholeRegression': False, 'formalAccepted': False,
             'vmActions': 0, 'mavenLogSha256': sha(WORK / 'maven.private.log'), 'command': command}
    (WORK / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True))
    print(json.dumps(value)); return value['actualExit']


if __name__ == '__main__':
    raise SystemExit(main())
