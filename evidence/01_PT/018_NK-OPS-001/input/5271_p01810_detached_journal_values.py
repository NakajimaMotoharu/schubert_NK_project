"""Qualify the two existing journal value records with a closed local JUnit classpath."""
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree
import gzip
import re
import runpy

HERE = Path(__file__).resolve()
A = runpy.run_path(str(HERE.with_name('5256_p01810_broker_evidence_value_run.py')))
E, D, ROOT, TC, JDK, MOD, SC = (A[key] for key in ('E', 'D', 'ROOT', 'TC', 'JDK', 'MOD', 'SC'))
git, ref, read, save, step = (A[key] for key in ('git', 'ref', 'read', 'save', 'step'))
OUT = E / 'PG40080-p01810-detached-journal-values-v1'
PKG = Path('dev/codex/schubert/nk/batch/platform')
FILE = 'BrokerJournalEvidence'
TEST_NAME = 'BrokerJournalValueContractTest'
TEST = MOD / 'src/test/java' / PKG / (TEST_NAME + '.java')
TYPE = str(PKG).replace('/', '.') + '.' + TEST_NAME
MAIN = MOD / 'src/main/java' / PKG / (FILE + '.java')
TARGETS = [str(PKG / (FILE + '$' + inner)) for inner in ('Summary', 'Anchor')]
IDS = {
    'PT-P01810-CATALOG-065A': 'summaryPreservesIndependentValuesWithoutRenderingThem',
    'PT-P01810-CATALOG-065B': 'anchorPreservesAllWitnessValuesWithoutRenderingThem',
}
SESSION = 'PG40080-JOURNAL-VALUE-RECORDS'


def run():
    start = read(next(D.glob('584_P01810*.json')))['values']
    pins = start['oracleReferences']
    assert all(ref(Path(pin['path'])) == pin for pin in pins)
    catalog, build, static, toolchain, previous = (read(pin['path']) for pin in pins)
    core = build['sourceCore']
    assert core == start['productionCoreMain']
    source = git('rev-parse', 'HEAD').decode().strip()
    assert git('diff', '--name-only', start['source'], source, '--', 'src').decode().splitlines() == [str(TEST)]
    assert git('show', f'{source}:{MAIN}') == git('show', f'{core}:{MAIN}') == MAIN.read_bytes()
    assert ref(MAIN)['sha256'] == build['sourceInputs'][str(MAIN)]
    assert previous['executable'][TARGETS[1]]['counters']['CLASS'] == dict(covered=0, missed=1)
    spec, = [row for row in catalog if row['plannedCaseId'] == 'PT-P01810-CATALOG-065']
    assert spec['owners'] == ['WBS-P017-10']

    work = ROOT.parent / 'pgpt-runs/PG379' / OUT.name.lower()
    work.mkdir(mode=0o700)
    OUT.mkdir()
    product = work / 'product'
    classes = work / 'testclasses'
    directory = work / 'tmp'
    xml = OUT / 'xml'
    for p in (classes, directory, xml):
        p.mkdir()
    physical = {}
    for stem in (str(PKG / FILE), *TARGETS):
        key = stem + '.class'
        origin = Path(build['cwd']) / MOD / 'target/classes' / key
        assert ref(origin)['sha256'] == build['physicalClassHashes']['batch'][key]
        output = product / key
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(origin.read_bytes())
        physical[key] = dict(origin=ref(origin), snapshot=ref(output))
    wanted = ('junit-platform-console-standalone-1.13.4.jar', 'org.jacoco.cli-0.8.15-nodeps.jar',
              'org.jacoco.agent-0.8.15-runtime.jar', 'jspecify-1.0.1.jar')
    jars = [Path(toolchain['tools'][name]['path']) for name in wanted]
    assert all(ref(path) == toolchain['tools'][path.name] for path in jars)
    junit, cli, agent, jspecify = jars
    assert ref(JDK / 'java') == toolchain['jdk'] and ref(JDK / 'javac') == toolchain['javaC']
    test = work / TEST
    test.parent.mkdir(parents=True)
    test.write_bytes(git('show', f'{source}:{TEST}'))
    save(OUT / 'begin.json', dict(sourceCore=core, unitSource=source, product=physical,
         toolchain=[ref(item) for item in jars], testInput=ref(test), references=pins, session=SESSION,
         onlyThreePhysicalClasses=True, mainUnchanged=True, productOperationsPermitted=0,
         startedAtUTC=datetime.now(timezone.utc).isoformat()))

    cp = f'{product}:{junit}:{jspecify}'
    stages = {}

    def run_stage(name, command, expected=(0,)):
        stages[name] = step(name, command, work, OUT, 65)
        assert stages[name]['actualExit'] in expected, name

    run_stage('testcompile', [str(JDK / 'javac'), '-Xlint:all', '-Werror', '--release', '25',
                   '-cp', cp, '-d', str(classes), str(test)])
    execfile = (OUT / 'jacoco.exec').resolve()
    run_stage('unit', [str(JDK / 'java'), '-Djava.io.tmpdir=' + str(directory),
                       '-Xlog:class+init=info:file=' + str(work / 'class-init.log'),
                       f'-javaagent:{agent}=destfile={execfile},sessionid={SESSION},append=false',
                       '-jar', str(junit), 'execute', '--disable-banner', '--disable-ansi-colors',
                       '--fail-if-no-tests', '--details=summary', '--class-path',
                       f'{classes}:{product}:{jspecify}', '--select-class', TYPE, '--reports-dir', str(xml.resolve()),
                       '--config=junit.jupiter.execution.parallel.enabled=false'])
    run_stage('execinfo', [str(JDK / 'java'), '-jar', str(cli), 'execinfo', str(execfile)])
    target_files = [str(product / (name + '.class')) for name in TARGETS]
    run_stage('classinfo', [str(JDK / 'java'), '-jar', str(cli), 'classinfo', *target_files])
    recipe = read(E / 'PG40060-p020-error-disclosure-independent-v1' / 'manifest.json')['raw']['command']
    assert recipe[4] == '--line-deficits'
    run_stage('raw', [*recipe[:5], str(execfile), *target_files])
    raw = Path(stages['raw']['log']['path']).read_bytes()
    (OUT / 'raw.tsv').write_bytes(raw)

    listing = (OUT / 'sources.txt').resolve()
    listing.write_text(str(test) + '\n')
    pmd = list(static['command'])
    for option, new in (('--file-list', str(listing)), ('--report-file', str((OUT / 'pmd.xml').resolve())),
                        ('--aux-classpath', f'{JDK.parent}/lib/jrt-fs.jar:{cp}')):
        pmd[pmd.index(option)+1] = new
    git_style = TC / 'google-java-format-1.36.1-all-deps.jar'
    checkstyle = SC['TOOL'] / 'static-gates-20261015/checkstyle-14.3.0-all.jar'
    run_stage('pmd', pmd, (0, 4))
    run_stage('checkstyle', [str(JDK / 'java'), '-jar', str(checkstyle), '-c',
                str(ROOT / 'tools/quality/static/checkstyle.xml'), '-f', 'xml', '-o',
                str((OUT / 'checkstyle.xml').resolve()), '@' + str(listing)])
    run_stage('format', [str(JDK / 'java'), '-jar', str(git_style), '--skip-reflowing-long-strings',
                         '--dry-run', '--set-exit-if-changed', str(test)])

    test_report = xml / 'TEST-junit-jupiter.xml'
    tree = ElementTree.parse(test_report)
    cases = {(n.get('classname'), n.get('name')) for n in tree.iter('testcase')}
    assert cases == {(TYPE, method + '()') for method in IDS.values()}
    assert sum(1 for _ in tree.iter('testcase')) == 2
    assert not any(n.tag in ('failure', 'error', 'skipped') for n in tree.iter())
    init = (work / 'class-init.log').read_bytes()
    assert all((f"Initializing '{name}'").encode() in init for name in TARGETS)
    assert not re.search(rb"Initializing '(?:dev/codex/schubert/nk/batch/platform/BrokerJournalEvidence'|org/apache/activemq/|org/postgresql/|com/fasterxml/jackson/)", init)
    archive = OUT / 'class-init.log.gz'
    archive.write_bytes(gzip.compress(init, mtime=0))
    rows = [line.split('\t') for line in raw.decode().splitlines() if line.startswith('CLASS\t')]
    assert {row[1] for row in rows} == set(TARGETS)
    assert all(row[3] == 'true' for row in rows)
    counters = {row[1]: {key: dict(missed=int(miss), covered=int(hit)) for key, miss, hit in
                         (part.split(':') for part in row[6:])} for row in rows}
    assert all(n['missed'] == 0 for record in counters.values() for n in record.values())
    assert all(record['BRANCH'] == dict(missed=0, covered=0) for record in counters.values())
    pmd_tree = ElementTree.parse(OUT / 'pmd.xml')
    violations = [dict(rule=n.get('rule'), line=n.get('beginline')) for n in pmd_tree.findall('.//{*}violation')]
    assert not pmd_tree.findall('.//{*}error') and not pmd_tree.findall('.//{*}configerror')
    assert not ElementTree.parse(OUT / 'checkstyle.xml').findall('.//{*}error')
    save(OUT / 'manifest.json', dict(
        actualExit=0, sourceCore=core, testSource=source, tests=2, fails=0, errors=0, skips=0, notRun=0,
        stageResults=stages, testIds=IDS, testXml=ref(test_report), raw=ref(OUT / 'raw.tsv'),
        exec=ref(execfile), init=ref(archive), session=SESSION, counters=counters, pmd=violations,
        physical=physical, noWhole451=False, acceptedNew=0, actualJournalOrBrokerActions=0,
        terminalAtUTC=datetime.now(timezone.utc).isoformat(), runner=ref(HERE)))
    print(ref(OUT / 'manifest.json'), counters, violations)


if __name__ == '__main__':
    run()
