"""Requalify the intact six pure Music Track view tests on the pinned current Protocol artifact."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
from tempfile import mkdtemp
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

from jacoco_readonly_exec_subset import decode

ROOT = Path.cwd()
OPS = Path('evidence/01_PT/018_NK-OPS-001/evidence')
PLAN = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
TOOLS = ROOT.parent / 'toolchain'
JAVA = TOOLS / 'jdk-25.0.4/bin/java'
JAVAC = JAVA.with_name('javac')
RUN = 'PG41500-scr013-track-current-six-v1'
OWNER = 'dev/codex/schubert/nk/web/view/MusicTrackViewModel'
TEST = 'dev.codex.schubert.nk.web.view.MusicTrackPublicContractTest'


def read(path):
    return json.loads(path.read_bytes())


def pin(path):
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def write(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def now():
    return datetime.now(timezone.utc).isoformat()


def git(*argv):
    return subprocess.check_output(['git', *argv], timeout=30)


def evidence(number):
    return next(OPS.glob(f'PG{number}-*/manifest.json'))


def cases(path):
    return sorted(
        (node.attrib['name'], node.attrib['classname'],
         next((kind for kind in ('failure', 'error', 'skipped') if node.find(kind) is not None), 'pass'))
        for node in ET.parse(path).getroot().findall('testcase')
    )


def main():
    event = read(next(PLAN.glob('1898_*')))
    scope = event['values']
    head, core = scope['source'], scope['productionCoreMain']
    assert git('rev-parse', 'HEAD').decode().strip() == head
    q = read(next(PLAN.glob('1899_*')))['quota']
    assert q['ordinaryUsageAllowed'] and q['primary']['remainingPercent'] > 10
    assert q['secondary'] is None or q['secondary']['remainingPercent'] > 10
    age = datetime.now(timezone.utc) - datetime.fromisoformat(q['observedAtUTC'])
    assert 0 <= age.total_seconds() <= 120
    old_path = evidence('27782')
    old = read(old_path)
    old_xml = old_path.parent / 'original-TEST-junit-jupiter.xml'
    assert pin(old_xml)['sha256'] == old['files'][old_xml.name]
    expected = cases(old_xml)
    assert len(expected) == 6 and all(row[1:] == (TEST, 'pass') for row in expected)

    main = [
        Path('src/schubert-nk-web/src/main/java') / (name + '.java')
        for name in (OWNER, 'dev/codex/schubert/nk/web/view/TopBarViewModel',
                     'dev/codex/schubert/nk/web/session/SessionPrincipal')
    ]
    fixture = Path('src/schubert-nk-web/src/test/java') / (TEST.replace('.', '/') + '.java')
    source_inputs = [*main, fixture]
    for item in source_inputs:
        assert item.read_bytes() == git('show', f'{head}:{item}')
        assert pin(item)['sha256'] == old['inputHashes'][str(item)]

    current = read(evidence('41322'))['packagingProof']['artifacts']['protocol']
    protocol = Path(current['artifact']['path'])
    assert pin(protocol)['sha256'] == current['artifact']['sha256']
    assert not git('diff', '--name-only', current['archiveSource'], head, '--', 'pom.xml', 'src/schubert-nk-protocol')
    sdk = []
    for name, digest in old['dependencies'].items():
        path = Path(name)
        if path.is_relative_to(TOOLS):
            assert pin(path)['sha256'] == digest
            sdk.append(path)
    assert len(sdk) == 4
    classpath = os.pathsep.join(map(str, [protocol, *sdk]))
    agent = next((TOOLS / 'm2/repository/org/jacoco/org.jacoco.agent/0.8.15').glob('*-runtime.jar'))
    assert pin(agent)['sha256'] == read(evidence('38002'))['measurementAgentSha256']
    analyzer = Path('tools/quality/jacoco/UnfilteredCodeMeasurement.java')
    assert analyzer.read_bytes() == git('show', f'{head}:{analyzer}')
    analysis_deps = read(evidence('41304'))['tools'][0]['argv'][5]
    for dependency in analysis_deps.split(os.pathsep):
        assert Path(dependency).is_relative_to(TOOLS)
        assert Path(dependency).is_file()

    home = ROOT.parent / 'pgpt-runs/PG379' / RUN
    home.mkdir(mode=0o700)
    scratch = Path(mkdtemp(prefix='pgpt-scr013-', dir='/dev/shm'))
    classes, analyzer_classes = scratch / 'classes', scratch / 'analyzer-classes'
    classes.mkdir()
    analyzer_classes.mkdir()
    stages = []

    def run(name, argv):
        started = now()
        p = subprocess.run(list(map(str, argv)), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        for tag, log in (('stdout', p.stdout), ('stderr', p.stderr)):
            (home / f'{name}.{tag}').write_bytes(log)
        data = dict(step=name, command=list(map(str, argv)), beganAtUTC=started, terminalAtUTC=now(),
                    exit=p.returncode, stdout=pin(home / f'{name}.stdout'), stderr=pin(home / f'{name}.stderr'))
        write(home / f'{name}.terminal.json', data)
        stages.append(data)
        return p

    start = dict(run=RUN, source=head, productionCore=core, sourceInputs=list(map(pin, source_inputs)),
                 expectation=expected, currentProtocol=pin(protocol), dependencies=list(map(pin, sdk)),
                 observedQuota=q, originalProof=pin(old_path), workDirectory=str(scratch), startedAtUTC=now())
    write(home / 'begin.json', start)
    flags = ['--release', '25', '-encoding', 'UTF-8', '-Xlint:all', '-Werror', '-proc:none', '-implicit:none']
    assert run('compile', [JAVAC, *flags, '-cp', classpath, '-d', classes, *source_inputs]).returncode == 0
    assert run('analyzer-compile', [JAVAC, '--release', '25', '-cp', analysis_deps, '-d', analyzer_classes,
                                    analyzer]).returncode == 0
    exec_file, reports = home / 'unit.exec', home / 'xml'
    result = run('junit', [JAVA, '-Duser.timezone=Asia/Tokyo', f'-javaagent:{agent}=destfile={exec_file},append=false,sessionid={RUN}',
                           '-cp', str(classes) + os.pathsep + classpath, 'org.junit.platform.console.ConsoleLauncher',
                           'execute', '--disable-banner', '--disable-ansi-colors', '--details', 'summary',
                           '--fail-if-no-tests', '--include-engine', 'junit-jupiter', '--select-class', TEST,
                           '--reports-dir', reports])
    report = reports / 'TEST-junit-jupiter.xml'
    assert result.returncode == 0 and cases(report) == expected
    physical = [classes / item.relative_to('src/schubert-nk-web/src/main/java').with_suffix('.class') for item in main]
    measurement = run('raw', [JAVA, '-cp', str(analyzer_classes) + os.pathsep + analysis_deps,
                              'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement',
                              '--strict-original-exec', '--line-deficits', exec_file, *physical])
    assert measurement.returncode == 0
    names = {p.relative_to(classes).as_posix().removesuffix('.class') for p in physical}
    exec_info = decode(exec_file.read_bytes(), names, strict_class_names=True)
    assert len(exec_info['sessions']) == 1 and exec_info['sessions'][0]['labelBytesHex'] == RUN.encode().hex()
    counters = {}
    for line in measurement.stdout.decode().splitlines():
        parts = line.split('\t')
        if parts[0] != 'CLASS':
            continue
        name, crc, present = parts[1:4]
        assert present == 'true' and int(crc, 16) == int(exec_info['classes'][name]['crc64'], 16)
        counters[name] = {key: dict(missed=int(miss), covered=int(hit)) for
                          key, miss, hit in (part.split(':') for part in parts[6:])}
    assert set(counters) == names
    out = OPS / RUN
    out.mkdir()
    raw = out / 'unfiltered.tsv'
    raw.write_bytes(measurement.stdout)
    write(out / 'manifest.json', dict(run=RUN, source=head, productionCore=core, exitCode=0, tested=6,
          priorProof=pin(old_path), actualCases=expected, skipped=0, notRun=0, failures=0, errors=0,
          newDefinitions=0, sameFixtureAndIndependentLiteralOracle=True, singleExec=True, scopePhysical=3,
          rawCounters=counters, ownedTargetFull=all(counters[OWNER][k]['missed'] == 0 for k in
                 ('LINE', 'METHOD', 'CLASS', 'BRANCH')),
          verifiedSourceInputs=start['sourceInputs'], currentProtocol=start['currentProtocol'],
          terminalReceipts=stages, actualExec=pin(exec_file), actualXml=pin(report), rawTSV=pin(raw),
          knownHeldOperations=0, whole451=False, newFormalAcceptance=0, terminalAtUTC=now()))
    print('cases', len(expected), 'owned-target', counters[OWNER])


if __name__ == '__main__':
    main()

