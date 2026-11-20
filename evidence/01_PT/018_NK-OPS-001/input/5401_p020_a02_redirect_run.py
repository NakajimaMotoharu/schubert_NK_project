"""Use the retained offline roster for the ordered A02 destinations contract."""

from pathlib import Path
import runpy
import sys


HERE = Path(__file__).resolve()
P = runpy.run_path(str(HERE.with_name('5245_p020_login_title_whole.py')))
E, B, JDK, TC, ROOT, R = (P[key] for key in ('E', 'B', 'JDK', 'TC', 'ROOT', 'R'))
read, ref, save, step, git, physical = (P[key] for key in ('read', 'ref', 'save', 'step', 'git', 'physical'))
JAVA_DIR, TEST_PACKAGE = (P[key] for key in ('JAVA_DIR', 'TEST_PACKAGE'))
CASES = ['rejectsReportsThatBothOmitTheTwoRetainedSessionDestinations',
         'rejectsReportsThatBothRedirectTheMiddleSessionDespiteActiveEvidence']


def main(mode):
    red = mode == 'red'
    assert red or mode == 'green'
    plan = read(next(P['DOC'].glob('1027_P020*')))
    assert all(ref(Path(row['path'])) == row for row in plan['values']['oracleReferences'])
    previous_run = E / 'PG40208-p020-a02-session-census-green208-v1'
    previous = read(previous_run / 'begin.json')
    old = read(previous_run / 'manifest.json')
    assert old['source'] == previous['source'] and old['expected'] == previous['expected'] == 208
    assert old['stages']['unit']['actualExit'] == 0
    assert len(previous['exactScope']) == 20
    source = git('rev-parse', 'HEAD').decode().strip()
    changed = {str(B / 'tests/java' / JAVA_DIR / 'ArtifactComparatorTest.java')}
    if not red:
        changed |= {str(B / 'src/main/java' / JAVA_DIR / 'ArtifactComparator.java')}
    name = plan['values']['run'] if red else 'PG40658-p020-a02-redirect-green-v1'
    expected = 2 if red else 210
    out = E / name
    owned = ROOT.parent / 'pgpt-runs/PG379' / name.lower()
    out.mkdir()
    owned.mkdir(mode=0o700)
    snapshot = owned / 'snapshot'
    plan['values']['characterizationBase'] = old['source']
    inputs = P['frozen_source'](snapshot, source, previous, plan, changed)
    sdk = {key: Path(pin['path']) for key, pin in previous['tools'].items()}
    assert all(ref(path) == previous['tools'][key] for key, path in sdk.items())
    assert ref(JDK / 'java') == previous['jdk'] and ref(JDK / 'javac') == previous['javaC']
    cp = ':'.join(str(path) for name, path in sdk.items() if 'jacoco' not in name)
    classes = snapshot / B / 'target/classes'
    tests = owned / 'testclasses'
    temp = owned / 'tmp'
    logs = out / 'xml'
    for directory in (tests, temp, logs):
        directory.mkdir(mode=0o700)
    roster = previous['exactScope']
    selectors = [('--select-method', TEST_PACKAGE + 'ArtifactComparatorTest#' + n)
                 for n in CASES] if red else [('--select-class', TEST_PACKAGE+n) for n in roster]
    session = name.split('-')[0] + '-A02-DESTINATIONS-' + str(expected)
    exec_file = (out / 'jacoco.exec').resolve()
    agent = sdk['org.jacoco.agent-0.8.15-runtime.jar']
    init = owned / 'class-init.log'
    java = str(JDK / 'java')
    commands = {
        'main': [str(R['MAVEN']), '-o', '-B', '-ntp', '-N', f'-Dmaven.repo.local={TC}/m2/repository',
                 '-f', str(snapshot / B / 'pom.xml'), 'compile'],
        'test': [str(JDK / 'javac'), '-Xlint:all', '-Werror', '--release', '25',
                 '-cp', f'{classes}:{cp}', '-sourcepath', str(snapshot / B / 'tests/java'),
                 '-d', str(tests), *(str(snapshot / B / 'tests/java' / JAVA_DIR / (n+'.java'))
                                    for n in roster)],
        'unit': [java, '-Xmx1g', '-Djava.awt.headless=true', '-Duser.language=ja', '-Duser.country=JP',
                 '-Duser.timezone=Asia/Tokyo', '-Dchr.unitProjectRoot=' + str(snapshot),
                 '-Djava.io.tmpdir=' + str(temp), '-Xlog:class+init=info:file=' + str(init),
                 f'-javaagent:{agent}=destfile={exec_file},sessionid={session},append=false',
                 '-jar', str(sdk['junit-platform-console-standalone-1.13.4.jar']), 'execute',
                 '--disable-banner', '--details=summary', '--fail-if-no-tests', '--class-path',
                 f'{classes}:{tests}:{snapshot/B/"tests/resources"}:{cp}', '--reports-dir',
                 str(logs.resolve()), *(piece for pair in selectors for piece in pair),
                 '--config=junit.jupiter.execution.parallel.enabled=false']}
    save(out / 'begin.json', dict(source=source, productionCore=plan['values']['productionCoreMain'],
                                 groupStart=plan['eventId'], expected=expected, caseNames=CASES,
                                 original=ref(previous_run / 'manifest.json'), sourceChanges=sorted(changed),
                                 snapshot=str(snapshot), selectors=selectors, inputHashes=inputs,
                                 java=ref(JDK/'java'), javac=ref(JDK/'javac'), tools=previous['tools'],
                                 session=session, startedAtUTC=R['utc']()))
    stages = {}
    for label, command in commands.items():
        stages[label] = step(label, command, owned, out, 180)
        if stages[label]['actualExit']:
            break
    if stages.get('unit', {}).get('actualExit') == 0:
        tool = [java, '-jar', str(sdk['org.jacoco.cli-0.8.15-nodeps.jar'])]
        for label, command in {'coverage': [*tool, 'report', str(exec_file), '--classfiles', str(classes),
                                           '--xml', str((out/'coverage.xml').resolve())],
                               'execinfo': [*tool, 'execinfo', str(exec_file)],
                               'classinfo': [*tool, 'classinfo', str(classes)]}.items():
            stages[label] = step(label, command, owned, out)
    assert all(ref(snapshot / name)['sha256'] == digest for name, digest in inputs.items())
    manifest = out / 'manifest.json'
    save(manifest, dict(source=source, productionCore=plan['values']['productionCoreMain'],
                        expected=expected, stages=stages, run=name, session=session, classesDir=str(classes),
                        mainPhysical=physical(classes), initLog=ref(init) if init.is_file() else None,
                        xmlHashes={doc.name: ref(doc)['sha256'] for doc in logs.glob('*.xml')},
                        actualProductTests=0, actualNkChr=0, terminalAtUTC=R['utc']()))
    print(ref(manifest), {label: stage['actualExit'] for label, stage in stages.items()})
    return next((stage['actualExit'] for stage in stages.values() if stage['actualExit']), 0)


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1]))
