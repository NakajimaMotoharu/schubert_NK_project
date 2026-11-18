"""Verify frozen WebLog JDBC expectations, exact borrowed boundary and physical raw counters."""
from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import re
import subprocess
from xml.etree import ElementTree as ET

B = Path('evidence/01_PT/018_NK-OPS-001')
E = B / 'evidence'
J = Path('evidence/01_PT/015_NK-WEB-001/evidence')
OUT = E / 'PG39690-p00405-weblog-outbox-resource-independent-v1'
SPEC = spec_from_file_location('existing_oracle_tools', B / 'input/5139_bug3272_context_independent_checks.py')
h = module_from_spec(SPEC)
SPEC.loader.exec_module(h)
ORIGINAL = '411d97d6c98def68b064924b5f5dba3d0c459f7f'
BASE_CORE = '15ee95822be0f4387e1e127cf43d43a08945c3c6'
DESIGN = '5aafdc4bff5e8a4c15db9a8000ddf3f1fd17f774'
CLASS = 'dev/codex/schubert/nk/web/logging/WebLogOutboxRepository'
NEW = {
    'port021AllFourMissingStatementsAreRejectedBeforeBind',
    'port022MissingRowsCloseOnlyTheAcquiredStatementOnce',
    'port023AliasedRowsFailureKeepsPrimaryCauseAndStatementSuppression',
}


def exact_main(path, source, core):
    previous = h.git('show', f'{ORIGINAL}:{path}')
    current = h.git('show', f'{source}:{path}')
    assert current == Path(path).read_text()
    inverse = re.sub(r'\n  // SSC-472:.*?(?=  static ClaimedWebLog read)', '\n', current, flags=re.S)
    inverse = inverse.replace('import javax.annotation.WillClose;', '').replace('import java.sql.PreparedStatement;', '')
    opener = (r'@Nullable PreparedStatement acquiredStatement =\s*(connection\.prepareStatement\(.*?\));\s*'
              r'@Nullable Throwable statementFailure = null;\s*try \{\s*'
              r'PreparedStatement statement = required\(acquiredStatement\);')
    inverse, n = re.subn(opener, r'try (var statement = \1) {', inverse, flags=re.S)
    assert n == 4
    rows = (r'@Nullable ResultSet acquiredRows = statement\.executeQuery\(\);\s*'
            r'@Nullable Throwable rowFailure = null;\s*try \{\s*ResultSet result = required\(acquiredRows\);')
    inverse, n = re.subn(rows, 'try (ResultSet result = statement.executeQuery()) {', inverse)
    assert n == 1
    for failure, closer, expected in [('statementFailure', 'closeStatement(acquiredStatement, statementFailure)', 4),
                                       ('rowFailure', 'closeRows(acquiredRows, rowFailure)', 1)]:
        bound = (r'\} catch \(Throwable failure\) \{\s*' + failure
                 + r' = failure;\s*throw failure;\s*\} finally \{\s*' + re.escape(closer) + r';\s*\}')
        inverse, n = re.subn(bound, '}', inverse)
        assert n == expected
    assert h.TOKEN.findall(previous) == h.TOKEN.findall(inverse)
    assert h.git('diff', '--name-only', BASE_CORE, core, '--',
                 ':(glob)src/*/src/main/java/**/*.java').splitlines() == [path]


def exact_tests(path, source):
    previous = h.git('show', f'{ORIGINAL}:{path}')
    current = h.git('show', f'{source}:{path}')
    assert current == Path(path).read_text()
    begin = current.index('\n  @Test\n  void port021')
    end = current.index('\n  private static ClaimedWebLog readWorker', begin)
    added = current[begin:end]
    inverse = current[:begin] + current[end:]
    inverse = inverse.replace('boolean missingStatement;', '').replace('boolean missingRows;', '')
    inverse = inverse.replace('return missingStatement ? null : statement();', 'return statement();')
    inverse = inverse.replace('return missingRows ? null : result();', 'return result();')
    inverse, n = re.subn(r'var workers = Executors.newFixedThreadPool\(2\);\s*try \{',
                         'try (var workers = Executors.newFixedThreadPool(2)) {', inverse)
    assert n == 1
    inverse, n = re.subn(r'} finally \{\s*workers.shutdownNow\(\);\s*'
                         r'assertTrue\(workers.awaitTermination\(10, TimeUnit.SECONDS\)\);\s*\}', '}', inverse)
    assert n == 1
    assert h.TOKEN.findall(previous) == h.TOKEN.findall(inverse)
    cases = set(re.findall(r'@Test\s+void\s+(\w+)\(', added))
    assert cases == NEW
    for item in ('List.of(AUTO, PREPARE)', 'List.of(AUTO, PREPARE, QUERY, PS_CLOSE)',
                 'List.of(AUTO, PREPARE, QUERY, NEXT, RS_CLOSE, PS_CLOSE)',
                 'assertSame(same, observed.getCause())', 'List.of(observed.getSuppressed())'):
        assert item in added
    assert added.count('assertEquals("22004", failure.getSQLState());') == 2


def main():
    c = h.load(B / 'input/5200_ssc472_weblog_outbox_profile.json')
    paths = {k: Path(v) / 'manifest.json' for k, v in c['slots'].items()}
    audits = {k: h.load(p) for k, p in paths.items()}
    assert all(m['actualExit'] == 0 for m in audits.values())
    unit, post = audits['unit'], audits['post']
    source = post['source']
    assert unit['begin']['source'] == source and unit['tests'] == post['tests'] == 23
    assert unit['failures'] == unit['errors'] == unit['skipped'] == 0
    assert post['completeSourceComponentFour100'] and not post['wholeScopeFour100']
    assert audits['preflight']['staticApplicable'] == 0
    assert not h.git('diff', '--name-only', source, 'HEAD', '--', 'src')
    assert not h.git('diff', '--name-only', c['productionCoreMain'], source, '--', ':(glob)src/*/src/main/java/**/*.java')
    exact_main(c['mainSources'][0], source, c['productionCoreMain'])
    exact_tests(c['testSources'][0]['path'], source)
    [original_path] = list(J.glob('PG19638*/manifest.json'))
    original = h.load(original_path)
    assert original['tests'] == 20 and original['source'] == ORIGINAL
    prior = Path('../pgpt-runs/PG379/pg19638-web-outbox-jdbc-twenty-unit-v1/component').resolve() / (CLASS + '.class')
    assert h.ref(prior)['sha256'] == original['physicalHashes'][CLASS]
    compiled = (Path('../pgpt-runs/PG379') / c['privateDirs']['prepare'] / 'component').resolve()
    args = [str(Path('../toolchain/jdk-25.0.4/bin/javap').resolve()), '-public', '-s']
    assert subprocess.check_output(args + [str(prior)]) == subprocess.check_output(args + [str(compiled / (CLASS + '.class'))])
    assert subprocess.run(['git', 'merge-base', '--is-ancestor', DESIGN, 'origin/main']).returncode == 0
    xml = ET.parse(paths['post'].parent / 'original-TEST-junit-jupiter.xml')
    cases = xml.getroot().findall('testcase')
    assert len(cases) == len({(case.get('classname'), case.get('name')) for case in cases}) == 23
    assert not any(case.findall('failure') or case.findall('error') or case.findall('skipped') for case in cases)
    witnessed = {case.get('name').removesuffix('()') for case in cases}
    assert witnessed == {test[1] for test in original['selectedTestMethods']} | NEW and len(witnessed) == 23
    before = E / 'PG39668-p00405-weblog-outbox-before-v1/manifest.json'
    assert h.load(before)['originalRawCounters']['BRANCH'] == {'missed': 10, 'covered': 41}
    OUT.mkdir()
    command = h.load(next(E.glob('PG39282*/raw-command.json')))[:5]
    command += [str(paths['post'].parent / 'jacoco.exec'), *[str(compiled / p) for p in c['physicalClasses']]]
    h.write(OUT / 'raw-command.json', command)
    raw = OUT / 'unfiltered.tsv'
    with raw.open('xb') as stream:
        subprocess.run(command, stdout=stream, check=True, timeout=60)
    counters, missing = {}, []
    for line in raw.read_text().splitlines():
        fields = line.split('\t')
        if fields[0] == 'CLASS':
            counters[fields[1]] = {key: {'missed': int(m), 'covered': int(n)}
                                  for key, m, n in [x.split(':') for x in fields[6:]]}
        if fields[0] == 'DEFICIT':
            missing.append(dict(type=fields[1], method=fields[2], line=int(fields[4]), counters=fields[5:]))
    assert len(counters) == len(c['physicalClasses']) == post['physicalClasses']
    assert all(v['missed'] == 0 for v in counters[CLASS].values())
    assert not any(row['type'] == CLASS for row in missing)
    h.write(OUT / 'retention.json', h.archive_streams(c))
    result = dict(actualExit=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(), source=source,
                  productionCoreMain=c['productionCoreMain'], tests=23, newTestDefinitions=3,
                  failures=0, errors=0, skipped=0, notRun=0,
                  firstProductRunSuccess=True, firstIndependentPostSuccess=True,
                  originalTwentyFixtureTokenOracleRetained=True, privateOwnershipContractRechecked=True,
                  actualNullStatementCases=4, actualNullRowsCases=1, actualSelfSuppressionCases=1,
                  temporaryWorkerFiniteCleanup=True, actualQualityApplicable=0,
                  staticRawPmd=len(audits['static']['rawFindings']), publicAbiFrozen=True,
                  allOriginalSqlUtcLeaseRetryBindingsRetained=True, qa050LogoutMayNotBeReusedForWebLog=True,
                  targetRaw=counters[CLASS], classCounters=counters, supportingRawDeficits=missing,
                  positiveMainCrc=post['positiveMainCrc'], actualPhysical=post['physicalClasses'],
                  noCoverageExclusions=True, oldExecCombined=False,
                  formalUpdated=False, newAcceptance=0, whole451Accepted=False,
                  designPullRequest=439, canonicalDesign=DESIGN, before=h.ref(before),
                  rawCommand=h.ref(OUT/'raw-command.json'), rawData=h.ref(raw),
                  proofs={k:h.ref(v) for k,v in paths.items()}, retention=h.ref(OUT/'retention.json'),
                  verifier=h.ref(__file__))
    h.write(OUT / 'manifest.json', result)
    print(h.ref(OUT / 'manifest.json'), counters[CLASS], len(missing))


if __name__ == '__main__':
    main()
