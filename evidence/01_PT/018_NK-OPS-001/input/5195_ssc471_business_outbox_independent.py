"""Independently reconcile business Outbox original oracles, ABI and current physical coverage."""
from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import re
import subprocess
from xml.etree import ElementTree as ET

B = Path('evidence/01_PT/018_NK-OPS-001')
E = B / 'evidence'
J = Path('evidence/01_PT/006_NK-MSG-002/evidence')
OUT = E / 'PG39656-p00405-business-outbox-resource-independent-v1'
SPEC = spec_from_file_location('checks', B / 'input/5139_bug3272_context_independent_checks.py')
h = module_from_spec(SPEC)
SPEC.loader.exec_module(h)
ORIGINAL = '03eeef1a3d6cfb93000641bcb87f83507a1f3f4d'
PREVIOUS_CORE = '5e0b5575cf14416389a30be0175b52f7ec685983'
DESIGN = '907de7ce26b0cc2bfc1a7530fc75f8ae845e9161'
CLASS = 'dev/codex/schubert/nk/api/messaging/outbound/JdbcOutboxRepository'
EXTRA_CASES = {'requiredStatementNullStopsAllFourOperationsBeforeBinding',
               'requiredRowsNullClosesTheAlreadyAcquiredStatementExactlyOnce',
               'jdbcPrimarySuppressionAndJdkSelfFailureCloseRowsBeforeStatement'}


def check_main(config, candidate):
    path = config['mainSources'][0]
    old = h.git('show', f'{ORIGINAL}:{path}')
    current = h.git('show', f'{candidate}:{path}')
    assert current == Path(path).read_text()
    fixed = re.sub(r'\n  // SSC-471:.*?(?=  static OutboxEntry read)', '\n', current, flags=re.S)
    fixed = fixed.replace('import org.jspecify.annotations.Nullable;', '').replace('import javax.annotation.WillClose;', '')
    statements = r'@Nullable PreparedStatement acquiredStatement = connection\.prepareStatement\((sql|CLAIM_SQL)\);\s*@Nullable Throwable statementFailure = null;\s*try \{\s*PreparedStatement statement = requireValue\(acquiredStatement\);'
    fixed, n = re.subn(statements, r'try (PreparedStatement statement = connection.prepareStatement(\1)) {', fixed)
    assert n == 4
    result = r'@Nullable ResultSet acquiredRows = statement\.executeQuery\(\);\s*@Nullable Throwable resultFailure = null;\s*try \{\s*ResultSet result = requireValue\(acquiredRows\);'
    fixed, n = re.subn(result, 'try (ResultSet result = statement.executeQuery()) {', fixed)
    assert n == 2
    for failure, closer in [('statementFailure', 'closeStatement(acquiredStatement, statementFailure)'),
                            ('resultFailure', 'closeRows(acquiredRows, resultFailure)')]:
        derivative = (r'\} catch \(Throwable failure\) \{\s*' + failure
                      + r' = failure;\s*throw failure;\s*\} finally \{\s*' + re.escape(closer) + r';\s*\}')
        fixed, n = re.subn(derivative, '}', fixed)
        assert n == (4 if failure == 'statementFailure' else 2)
    assert h.TOKEN.findall(fixed) == h.TOKEN.findall(old)
    assert h.git('diff', '--name-only', PREVIOUS_CORE, config['productionCoreMain'], '--',
                 ':(glob)src/*/src/main/java/**/*.java').splitlines() == [path]


def check_fixtures(config, candidate):
    names = {}
    for item in config['testSources']:
        path = item['path']
        current = h.git('show', f'{candidate}:{path}')
        original = h.git('show', f'{ORIGINAL}:{path}')
        assert Path(path).read_text() == current
        name = Path(path).stem
        if name != 'JdbcOutboxPortTest':
            assert current == original
            continue
        prefix, new_blocks = current.split('\n  @FunctionalInterface\n  private interface RepositoryCall', 1)
        prefix += '\n}'
        constants = {'AUTO_COMMIT_POINT': 'connection.getAutoCommit', 'PREPARE_POINT': 'connection.prepareStatement',
                     'NEXT_POINT': 'result.next', 'ROWS_CLOSE_POINT': 'result.close',
                     'STATEMENT_CLOSE_POINT': 'statement.close'}
        for key, literal in constants.items():
            pattern = r'private static final String ' + key + r'\s*=\s*"' + re.escape(literal) + r'";'
            prefix, n = re.subn(pattern, '', prefix)
            assert n == 1
            prefix = prefix.replace(key, f'"{literal}"')
        prefix = prefix.replace('import org.jspecify.annotations.Nullable;', '')
        prefix = prefix.replace('private final Map<String, SQLException> additionalFaults = new HashMap<>();', '')
        prefix = prefix.replace('private boolean missingStatement;', '').replace('private boolean missingRows;', '')
        prefix = prefix.replace('@Nullable SQLException extra = additionalFaults.get(point);', '')
        prefix = prefix.replace('if (extra != null) throw extra;', '')
        prefix = prefix.replace('missingRows ? null : result()', 'result()').replace(
            'missingStatement ? null : statement()', 'statement()')
        prefix, n = re.subn(r'var pool = Executors.newFixedThreadPool\(2\);\s*try \{',
                            'try (var pool = Executors.newFixedThreadPool(2)) {', prefix)
        assert n == 1
        prefix, n = re.subn(r'\} finally \{\s*pool.shutdownNow\(\);\s*assertTrue\(pool.awaitTermination\(10, TimeUnit.SECONDS\)\);\s*\}', '}', prefix)
        assert n == 1
        assert h.TOKEN.findall(prefix) == h.TOKEN.findall(original)
        observed = set(re.findall(r'@Test\s+void (\w+)\(', new_blocks))
        assert observed == EXTRA_CASES
        assert '"22004"' in new_blocks and '"required database value is missing"' in new_blocks
        assert 'assertEquals(List.of(rowsFailure, statementFailure), List.of(failure.getSuppressed()))' in new_blocks
        assert 'assertSame(fixture.failure, failure.getCause())' in new_blocks
        names[name] = sorted(observed)
    return names


def measure(config, post, compiled):
    command = h.load(next(E.glob('PG39282*/raw-command.json')))[:5]
    command += [str(post.parent / 'jacoco.exec'), *[str(compiled / n) for n in config['physicalClasses']]]
    h.write(OUT / 'raw-command.json', command)
    raw = OUT / 'unfiltered.tsv'
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
    assert len(counters) == len(config['physicalClasses'])
    assert not any(row['type'] == CLASS for row in residual)
    target = counters[CLASS]
    assert all(v['missed'] == 0 for v in target.values())
    return raw, counters, residual


def main():
    config = h.load(B / 'input/5193_ssc471_business_outbox_profile.json')
    locations = {k: Path(v) / 'manifest.json' for k, v in config['slots'].items()}
    stages = {k: h.load(v) for k, v in locations.items()}
    assert all(v['actualExit'] == 0 for v in stages.values())
    unit, post = stages['unit'], stages['post']
    source = post['source']
    assert unit['begin']['source'] == source and unit['tests'] == post['tests'] == 12
    assert unit['failures'] == unit['errors'] == unit['skipped'] == 0
    assert not h.git('diff', '--name-only', source, 'HEAD', '--', 'src')
    assert not h.git('diff', '--name-only', config['productionCoreMain'], source, '--',
                     ':(glob)src/*/src/main/java/**/*.java')
    assert stages['preflight']['staticApplicable'] == 0 and post['completeSourceComponentFour100']
    assert not post['wholeScopeFour100'] and post['uncoveredFullSourceClasses']
    cases = ET.parse(locations['post'].parent / 'original-TEST-junit-jupiter.xml').getroot().findall('testcase')
    assert len(cases) == len({(r.get('classname'), r.get('name')) for r in cases}) == 12
    assert not any(r.findall('failure') or r.findall('error') or r.findall('skipped') for r in cases)
    check_main(config, source)
    witness = check_fixtures(config, source)
    previous = next(J.glob('PG21014*/manifest.json'))
    original = h.load(previous)
    prior = Path('../pgpt-runs/PG379/pg21014-outbox-null-oracle-nine-unit-v1/component').resolve() / (CLASS + '.class')
    assert h.ref(prior)['sha256'] == original['physicalHashes'][CLASS]
    compiled = (Path('../pgpt-runs/PG379') / config['privateDirs']['prepare'] / 'component').resolve()
    args = [str(Path('../toolchain/jdk-25.0.4/bin/javap').resolve()), '-public', '-s']
    assert subprocess.check_output(args + [str(prior)]) == subprocess.check_output(args + [str(compiled / (CLASS + '.class'))])
    assert subprocess.run(['git','merge-base','--is-ancestor',DESIGN,'origin/main']).returncode == 0
    most_recent = set(n.replace('()', '') for n in (row.get('name') for row in cases))
    original_names = {row[1] for row in original['selectedTestMethods']}
    assert original_names | EXTRA_CASES == most_recent and not (original_names & EXTRA_CASES)
    before_raw = E / 'PG39634-p00405-business-outbox-before-v1/manifest.json'
    assert h.load(before_raw)['originalRawCounters']['BRANCH'] == {'missed': 12, 'covered': 44}
    OUT.mkdir()
    raw, counters, residual = measure(config, locations['post'], compiled)
    h.write(OUT / 'retention.json', h.archive_streams(config))
    result = dict(actualExit=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(), source=source,
                  productionCoreMain=config['productionCoreMain'], tests=12, firstProductRunSuccess=True,
                  firstBaseIndependentSuccess=True, originalNineExactOracleAndBusinessControl=True,
                  newTestDefinitions=3, acceptedBoundaries={'nullStatements': 4, 'nullResultSets': 2, 'suppressionCases': 2},
                  failures=0, errors=0, skipped=0, notRun=0, witnessChanges=witness,
                  unchangedSqlUtcLeaseRetryAndPublicAbi=True, whole451Accepted=False, newAcceptance=0,
                  rawTarget=counters[CLASS], rawPerClass=counters, supportingDeficits=residual,
                  rawDigest=h.ref(raw), rawCommand=h.ref(OUT / 'raw-command.json'),
                  structuralCoverageExclusions=0, execCombined=False, designPullRequest=438, canonicalDesign=DESIGN,
                  positiveMainCrc=post['positiveMainCrc'], physicalClasses=post['physicalClasses'],
                  noneActualBackendNativeFsRootOrHeldClassActions=True,
                  technicalStaticApplicable=0, staticRawPmd=len(stages['static']['rawFindings']),
                  originalRawProof=h.ref(before_raw), earlierTestProof=h.ref(previous),
                  preparationMetadataFailures=['Ambiguous spec glob resolved to exact numbered spec.',
                                               'Sole package owners checked against 485 (two package-info owners).'],
                  proofs={k: h.ref(v) for k,v in locations.items()}, retention=h.ref(OUT / 'retention.json'),
                  verifier=h.ref(__file__))
    h.write(OUT / 'manifest.json', result)
    print(h.ref(OUT / 'manifest.json'), result['rawTarget'], len(residual))


if __name__ == '__main__':
    main()
