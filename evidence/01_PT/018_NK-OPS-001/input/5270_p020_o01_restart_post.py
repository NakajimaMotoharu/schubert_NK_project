"""Verify restart outcome projections, exact local tests, and original Current bytes."""
from collections import Counter
from pathlib import Path
import gzip
import re
import runpy

HERE = Path(__file__).resolve()
S = runpy.run_path(str(HERE.with_name('5255_p020_search_empty_independent.py')))
C, P, R, E = (S[key] for key in ('C', 'P', 'R', 'E'))
read, save, ref = (S[key] for key in ('read', 'save', 'ref'))
PREVIOUS = E / 'PG40057-p020-error-disclosure187-v2'
PRIOR = E / 'PG40060-p020-error-disclosure-independent-v1'
HISTORY = E / 'PG40018-p020-game-onchange-independent-v1'
FIRST = E / 'PG40074-p020-o01-restart192-v1'
UNIT = E / 'PG40075-p020-o01-restart192-v2'
STATIC = E / 'PG40076-p020-o01-restart-static-v1'
OUT = E / 'PG40078-p020-o01-restart-independent-v1'
IDS = {
    'PT-CHR-DEF060': 'acceptsTheApprovedRestartSessionOutcomeAndInvalidationEvidence',
    'PT-CHR-DEF061': 'requiresTheRestartInvalidationObservationSeparatelyFromOutcome',
    'PT-CHR-DEF062': 'rejectsASelfReportedNewLoginAfterRestart',
    'PT-CHR-DEF063': 'rejectsTextualAndNullInvalidationValuesEvenWhenSelfReported',
    'PT-CHR-DEF064': 'rejectsRestartDifferenceClaimsAgainstAnUnrelatedField',
}


def main():
    prior, first, unit, analysis = (read(path / 'manifest.json') for path in (PRIOR, FIRST, UNIT, STATIC))
    assert first['source'] != unit['source'] == analysis['source']
    assert list(first['stages']) == ['main', 'test']
    assert first['stages']['main']['actualExit'] == 0 and first['stages']['test']['actualExit'] == 1
    first_log = Path(first['stages']['test']['log']['path'])
    assert ref(first_log) == first['stages']['test']['log']
    assert 'cannot find symbol' in first_log.read_text() and 'JsonNode cannot be converted to String' in first_log.read_text()
    assert len(unit['stages']) == 6 and all(row['actualExit'] == 0 for row in unit['stages'].values())
    assert unit['actualBackendActions'] == 0 and analysis['allPhysicalUnchanged']
    assert not R['git']('diff', '--name-only', '843de94', unit['source'], '--', str(R['B'] / 'baseline/current'))

    baseline = R['B'] / 'baseline/current/artifacts/CHR-O01.json'
    legacy = read(baseline)
    assert legacy['sessionAfterRestart'] == 'redirect-login' and legacy['sessionInvalidated'] is True
    assert baseline.read_bytes() == R['git']('show', f'843de94:{baseline}')
    ui = R['git']('show', 'origin/main:' + S['UI']).decode()
    assert any('DIF-014' in line and '再起動継続' in line for line in ui.splitlines())
    package = Path(str(R['B'])) / 'tests/java/dev/codex/schubert/characterization/ArtifactComparatorTest.java'
    fixture = R['git']('show', f"{unit['source']}:{package}").decode()
    assert 'FIXTURE_RESTART_NK = "authenticated"' in fixture
    before = P['all_cases'](PREVIOUS)
    cases = P['all_cases'](UNIT)
    new = {(C['NAME'], method + '()') for method in IDS.values()}
    assert len(before) == 187 and not new & before.keys()
    assert cases == before | dict.fromkeys(new, 'PASS')
    assert set(cases.values()) == {'PASS'}
    assert len(cases) == 192 and len({group for group, _ in cases}) == 20
    scope = Path(unit['classesDir'])
    assert R['physical'](scope) == unit['mainPhysical'] and len(unit['mainPhysical']) == 17
    init = Path(unit['initLog']['path'])
    assert ref(init) == unit['initLog']
    raw_init = init.read_bytes()
    assert not re.search(rb"Initializing '(?:com/microsoft/playwright|dev/codex/schubert/nk/|dev/codex/schubert/characterization/(?:Native|CurrentCharacterizationTest)|org/postgresql)", raw_init)
    session = (UNIT / 'execinfo.log').read_text()
    assert session.count('Session "') == 1 and unit['session'] in session
    assert analysis['stageExits'] == dict(spotbugs=0, format=0, checkstyle=0, pmd=4)
    pmd = S['decisions'](read(HISTORY / 'manifest.json'), analysis, STATIC)
    assert len(pmd) == 6 and all(row['disposition'] == 'NOT_APPLICABLE' for row in pmd)
    OUT.mkdir()
    raw = P['unfiltered'](unit, UNIT, scope, OUT, read(next(E.glob('PG37324*/manifest.json'))))
    assert raw['missedMethods'] == prior['raw']['missedMethods']
    per = Counter()
    for line in (OUT / 'raw.tsv').read_text().splitlines():
        row = line.split('\t')
        if row[0] == 'CLASS' and row[1].startswith(S['PKG'] + 'ArtifactComparator'):
            assert row[3] == 'true'
            for key, miss, hit in (part.split(':') for part in row[6:]):
                assert int(miss) == 0
                per[key] += int(hit)
    assert per['CLASS'] == 2
    review = OUT / 'pmd-per-site.json'
    save(review, pmd)
    compressed = OUT / 'class-init.log.gz'
    compressed.write_bytes(gzip.compress(raw_init, mtime=0))
    report = dict(
        actualExit=0, source=unit['source'], unit=ref(UNIT / 'manifest.json'),
        static=ref(STATIC / 'manifest.json'), firstCompileFailure=ref(FIRST / 'manifest.json'),
        firstIndependentSetupExit=1, firstIndependentSetupCause='File digest helper was called with bytes',
        firstPreparationUnitTestsExecuted=0, firstDynamicCompleted=192, tests=192, suites=20,
        originalTests=187, newDefinitions=5, failed=0, errors=0, skipped=0, notRun=0, testIds=IDS,
        comparatorCounters=dict(per), raw=raw, pmdReviews=ref(review), pmdRaw=6,
        pmdApplicable=0, pmdUnclassified=0, baseline=ref(baseline), originalBaselineUnchanged=True,
        currentExpected=dict(sessionAfterRestart='redirect-login', sessionInvalidated=True),
        nkProjectionExpected=dict(sessionAfterRestart='authenticated', sessionInvalidated=False),
        nkRealSameSessionWitness=False, actualNkChr=False, actualBackendActions=0,
        classInit=ref(compressed), productTests=0, newAcceptance=0, formalUpdated=False,
        whole451Accepted=False, terminalAtUTC=R['utc'](), verifier=ref(HERE),
    )
    save(OUT / 'manifest.json', report)
    print(ref(OUT / 'manifest.json'), dict(per))


if __name__ == '__main__':
    main()
