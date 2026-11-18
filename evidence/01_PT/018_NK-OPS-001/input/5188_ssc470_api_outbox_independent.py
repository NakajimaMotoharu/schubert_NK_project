"""Verify exact original proxies, public signatures and current raw API Outbox counters."""
from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import re
import subprocess
from xml.etree import ElementTree

B = Path('evidence/01_PT/018_NK-OPS-001')
E = B / 'evidence'
OUT = E / 'PG39606-p00405-api-outbox-typed-close-independent-v1'
ORIGINAL = '103ae01acff5f25b4d25c48c932e520892856811'
BASE_CORE = 'f8b668a320e091ce8ebb6c8835aac47366d8ca70'
DESIGN = 'ed689fd1e6e5eec3fd1509795789dc7e4085e788'
PROOF = spec_from_file_location('fixture_proof', B / 'input/5139_bug3272_context_independent_checks.py')
h = module_from_spec(PROOF)
PROOF.loader.exec_module(h)
REPOSITORY = 'dev/codex/schubert/nk/api/monitoring/persistence/OutboxObservationRepository'


def verify_fixtures(config, source):
    targets = {'COUNT_READ_POINT': 'count', 'ROWS_CLOSE_POINT': 'RSclose', 'STATEMENT_CLOSE_POINT': 'PSclose'}
    method = re.compile(r'^  void\s+(outboxDb\d{3})\b', re.M)
    for row in config['testSources']:
        path = row['path']
        current = h.git('show', f'{source}:{path}')
        old = h.git('show', f'{ORIGINAL}:{path}')
        assert current == Path(path).read_text()
        if not path.endswith('OutboxObservationRepositoryTest.java'):
            assert current == old
            continue
        assert method.findall(old) == [f'outboxDb{i:03}' for i in range(1, 11)]
        assert method.findall(current) == [*method.findall(old), 'outboxDb011']
        prefix, extra = current.split('\n  @Test\n  void outboxDb011', 1)
        for name, literal in targets.items():
            declaration = f'  private static final String {name} = "{literal}";'
            assert prefix.count(declaration) == 1
            prefix = prefix.replace(declaration, '').replace(name, f'"{literal}"')
        assert h.TOKEN.findall(prefix + '\n}') == h.TOKEN.findall(old)
        tokens = h.TOKEN.findall(extra)
        for expression in [
            'rows.faults.put(COUNT_READ_POINT, rowFailure)',
            'rows.faults.put(ROWS_CLOSE_POINT, rowFailure)',
            'rows.faults.put(STATEMENT_CLOSE_POINT, statementSecondary)',
            'assertSame(rowFailure, failedRows.getCause())',
            'assertEquals(List.of(statementSecondary), List.of(failedRows.getSuppressed()))',
            'assertEquals(List.of(), List.of(rowFailure.getSuppressed()))',
            'rows.complete()',
            'statement.faults.put("timeout", statementFailure)',
            'statement.faults.put(STATEMENT_CLOSE_POINT, statementFailure)',
            'assertSame(statementFailure, failedStatement.getCause())',
            'assertEquals(List.of(), List.of(failedStatement.getSuppressed()))',
            'assertEquals(List.of(), List.of(statementFailure.getSuppressed()))',
            'assertEquals(1, statement.prepared)',
            'assertEquals(0, statement.executed)',
            'assertEquals(1, statement.timeout)',
            'assertEquals(List.of("PS"), statement.closes)',
        ]:
            seq = h.TOKEN.findall(expression)
            assert any(tokens[i:i + len(seq)] == seq for i in range(len(tokens) - len(seq) + 1)), expression
        assert tokens.count('IllegalArgumentException') == 2


def verify_abi(config, prepared, compiled):
    pre = h.load(next(E.glob('PG25448*preflight*/manifest.json')))
    old = Path('../pgpt-runs/PG379/pg25450-api-outbox-jdbc-original-whole18-v1/component')
    compiler = Path('../toolchain/jdk-25.0.4/bin/javap').resolve()
    current = prepared['physicalClassHashes']
    for name, expected in pre['targetClassHashes'].items():
        previous = old / Path(name).name
        assert h.ref(previous)['sha256'] == expected
        assert h.ref(compiled / name)['sha256'] == current[name]
        assert (current[name] != expected) == (name == REPOSITORY + '.class')
        args = [str(compiler), '-public', '-s']
        assert subprocess.check_output(args + [str(previous)], timeout=15) == subprocess.check_output(
            args + [str(compiled / name)], timeout=15)
    helper = h.load(next(E.glob('PG39268*/manifest.json')))['physicalClassHashes']
    helpers = set(current) - set(pre['targetClassHashes'])
    assert len(helpers) == 6 and all(current[k] == helper[k] for k in helpers)
    assert h.git('diff', '--name-only', BASE_CORE, config['productionCoreMain'],
                 '--', ':(glob)src/*/src/main/java/**/*.java').splitlines() == [config['mainSources'][3]]
    assert subprocess.run(['git', 'merge-base', '--is-ancestor', DESIGN, 'origin/main']).returncode == 0


def main():
    config = h.load(B / 'input/5186_ssc470_api_outbox_typed_close_profile.json')
    all_paths = {k: Path(v) / 'manifest.json' for k, v in config['slots'].items()}
    data = {k: h.load(p) for k, p in all_paths.items()}
    assert all(m['actualExit'] == 0 for m in data.values())
    unit, post = data['unit'], data['post']
    source = post['source']
    assert unit['source'] == source and unit['tests'] == post['tests'] == 19
    assert all(unit[k] == 0 for k in ('failures', 'errors', 'skipped'))
    assert data['preflight']['staticApplicable'] == 0 and post['wholeScopeFour100']
    assert not h.git('diff', '--name-only', config['productionCoreMain'], source,
                     '--', ':(glob)src/*/src/main/java/**/*.java')
    assert not h.git('diff', '--name-only', source, 'HEAD', '--', 'src')
    xml = all_paths['post'].parent / 'original-TEST-junit-jupiter.xml'
    cases = ElementTree.parse(xml).getroot().findall('testcase')
    assert len(cases) == len({(x.get('classname'), x.get('name')) for x in cases}) == 19
    assert not any(case.findall('failure') or case.findall('error') or case.findall('skipped') for case in cases)
    verify_fixtures(config, source)
    compiled = (Path('../pgpt-runs/PG379') / config['privateDirs']['prepare'] / 'component').resolve()
    verify_abi(config, data['prepare'], compiled)
    before = E / 'PG39582-p00405-api-outbox-raw-before-v1/manifest.json'
    assert h.load(before)['rawBranches'] == {'missed': 4, 'covered': 28}
    initial = E / 'PG39586-bug3292-api-outbox-prestyle-v1/manifest.json'
    assert h.load(initial)['actualExit'] == 1
    OUT.mkdir()
    raw = OUT / 'unfiltered.tsv'
    command = h.load(next(E.glob('PG39282*/raw-command.json')))[:5] + [
        str(all_paths['post'].parent / 'jacoco.exec'), *[str(compiled / n) for n in config['physicalClasses']]]
    h.write(OUT / 'raw-command.json', command)
    with raw.open('xb') as out:
        subprocess.run(command, check=True, stdout=out, timeout=80)
    counters, residual = {}, []
    for line in raw.read_text().splitlines():
        fields = line.split('\t')
        if fields[0] == 'CLASS':
            counters[fields[1]] = {k: {'missed': int(m), 'covered': int(c)}
                                   for k, m, c in [v.split(':') for v in fields[6:]]}
        if fields[0] == 'DEFICIT':
            residual.append(dict(type=fields[1], member=fields[2], line=int(fields[4]), counters=fields[5:]))
    assert len(counters) == post['physicalClasses'] == 9
    targets = {name: counters[name] for name in config['targetClasses']}
    assert not any(v['missed'] for row in targets.values() for v in row.values())
    assert all(row['type'] not in targets for row in residual)
    total = {k: {state: sum(v[k][state] for v in targets.values()) for state in ('missed', 'covered')}
             for k in ('LINE', 'METHOD', 'CLASS', 'BRANCH', 'INSTRUCTION', 'COMPLEXITY')}
    h.write(OUT / 'retention.json', h.archive_streams(config))
    result = dict(actualExit=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                  source=source, productionCoreMain=config['productionCoreMain'], tests=19,
                  failures=0, errors=0, skipped=0, notRun=0, newTestDefinitions=1,
                  firstProductRunSuccess=True, firstIndependentPostSuccess=True,
                  portableClosedScope=True, original18FullFixturesPreserved=True,
                  twoIndependentSelfSuppressionCases=True, oneChangedPhysicalClassWithPublicAbiStable=True,
                  unchangedFileAndClassOrderProof=True, rawTargets=total, rawPerClass=counters,
                  supportDeficits=residual, rawCoverageExclusions=0, oldExecCombined=False,
                  standardTargets=post['coverage'], standardSupportingClassesComplete=post['completeSourceComponentFour100'],
                  actualPhysicalClasses=post['physicalClasses'], positiveMainCrc=post['positiveMainCrc'],
                  staticApplicable=0, staticRawPmd=len(data['static']['rawFindings']),
                  initialBeforeCorrectionPmd=h.ref(initial), previousRawCoverage=h.ref(before),
                  prepMetadataIssues=['Qualification profile requires F03 as sole certification cost owner; fixed separately from multi-leaf WBS relevance.',
                                      'Git design-only patch context includes a development completion note; used exact standalone SSC-470 sections on main.'],
                  canonicalDesign=DESIGN, designPullRequest=437,
                  formalUpdated=False, newAcceptance=0, whole451Accepted=False,
                  raw=h.ref(raw), rawCommand=h.ref(OUT / 'raw-command.json'),
                  retention=h.ref(OUT / 'retention.json'), proofs={k: h.ref(v) for k, v in all_paths.items()},
                  verifier=h.ref(__file__))
    h.write(OUT / 'manifest.json', result)
    print(h.ref(OUT / 'manifest.json'), total, len(residual))


if __name__ == '__main__':
    main()
