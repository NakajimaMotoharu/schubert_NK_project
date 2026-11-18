"""Independently bind the S08 comparison to real saved Current and hand-derived NK counts."""
from collections import Counter
from pathlib import Path
import gzip
import re
import runpy

HERE = Path(__file__).resolve()
S = runpy.run_path(str(HERE.with_name('5255_p020_search_empty_independent.py')))
C, P, R, E = (S[key] for key in ('C', 'P', 'R', 'E'))
read, save, ref = (S[key] for key in ('read', 'save', 'ref'))
PREVIOUS = E / 'PG40075-p020-o01-restart192-v2'
PRIOR = E / 'PG40078-p020-o01-restart-independent-v1'
HISTORY = E / 'PG40018-p020-game-onchange-independent-v1'
FIRST = E / 'PG40088-p020-s08-voice198-v1'
FIRST_STATIC = E / 'PG40090-p020-s08-voice-static-v1'
UNIT = E / 'PG40089-p020-s08-voice198-v2'
STATIC = E / 'PG40091-p020-s08-voice-static-v2'
OUT = E / 'PG40092-p020-s08-voice-independent-v1'
IDS = {
    'PT-CHR-DEF065': 'comparesMultipleVoicesWithoutConvertingTheNormalScenarioProjection',
    'PT-CHR-DEF066': 'requiresBothMultipleVoiceSidesAndTheNamedApproval',
    'PT-CHR-DEF067': 'rejectsDuplicatedRowsOrBodiesWithTheCorrectPlayerCount',
    'PT-CHR-DEF068': 'rejectsLostPlayersLostLinksAndStringCounts',
    'PT-CHR-DEF069': 'rejectsWrongCurrentGroupingEvenWithCorrectNkGrouping',
    'PT-CHR-DEF070': 'rejectsUsingTheVoiceApprovalToConsumeAnOrdinaryArtifactDrift',
}


def main():
    prior, first, first_static, unit, analysis = (
        read(path / 'manifest.json') for path in (PRIOR, FIRST, FIRST_STATIC, UNIT, STATIC))
    assert first['source'] == first_static['source'] != unit['source'] == analysis['source']
    assert first_static['stageExits'] == dict(spotbugs=1, format=0, checkstyle=0, pmd=4)
    assert first_static['reports']['pmd']['findings'] == 8
    assert first_static['reports']['spotbugs']['findings'] == 1
    assert all(len(row['stages']) == 6 and all(s['actualExit'] == 0 for s in row['stages'].values())
               and row['actualBackendActions'] == 0 for row in (first, unit))
    assert analysis['allPhysicalUnchanged'] and first['mainPhysical'] != unit['mainPhysical']
    assert not R['git']('diff', '--name-only', '843de94', unit['source'], '--', str(R['B'] / 'baseline/current'))
    start = read(next(Path('documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117').glob('592_P020*.json')))
    supplemental = Path(start['values']['oracleReferences'][-1]['path'])
    assert ref(supplemental) == start['values']['oracleReferences'][-1]
    assert supplemental.read_bytes() == R['git']('show', f"{start['values']['source']}:{supplemental}")
    saved = read(supplemental)['checks']['CHR-S08']['multiple-voice-fixture']
    assert saved['status'] == 'PASS'
    expectation = dict(linkedVoiceCount=2, renderedEntryRows=2, renderedBodies=2, renderedAudioPlayers=2)
    assert {key: saved['evidence'][key] for key in expectation} == expectation
    nk = expectation | dict(renderedEntryRows=1, renderedBodies=1)
    ui = next(Path('documents/200_UI').rglob('223_*.md'))
    approved = R['git']('show', f'origin/main:{ui}').decode()
    assert any('全playerを表示' in line and '本文を重複表示しない' in line for line in approved.splitlines())
    assert any('DIF-009' in line and '現行1 link dataでは差なし' in line
               for line in R['git']('show', 'origin/main:' + S['UI']).decode().splitlines())

    before = P['all_cases'](PREVIOUS)
    cases = P['all_cases'](UNIT)
    new = {(C['NAME'], method + '()') for method in IDS.values()}
    assert len(before) == 192 and not new & before.keys()
    assert cases == P['all_cases'](FIRST) == before | dict.fromkeys(new, 'PASS')
    assert set(cases.values()) == {'PASS'}
    assert len(cases) == 198 and len({group for group, _ in cases}) == 20
    scope = Path(unit['classesDir'])
    assert R['physical'](scope) == unit['mainPhysical'] and len(unit['mainPhysical']) == 17
    init = Path(unit['initLog']['path'])
    assert ref(init) == unit['initLog']
    raw_init = init.read_bytes()
    assert not re.search(rb"Initializing '(?:com/microsoft/playwright|dev/codex/schubert/nk/|dev/codex/schubert/characterization/(?:Native|CurrentCharacterizationTest)|org/postgresql)", raw_init)
    session = (UNIT / 'execinfo.log').read_text()
    assert session.count('Session "') == 1 and unit['session'] in session
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
        actualExit=0, source=unit['source'], unit=ref(UNIT / 'manifest.json'), static=ref(STATIC / 'manifest.json'),
        firstUnit=ref(FIRST / 'manifest.json'), firstStaticFailure=ref(FIRST_STATIC / 'manifest.json'),
        firstSuccess=198, tests=198, suites=20, originalTests=192, newDefinitions=6,
        failed=0, errors=0, skipped=0, notRun=0, testIds=IDS, comparatorCounters=dict(per),
        currentSupplemental=ref(supplemental), independentExpected=dict(current=expectation, nk=nk),
        raw=raw, pmdReviews=ref(review), pmdRaw=6, pmdApplicable=0, pmdUnclassified=0,
        actualNkChr=False, actualBackendActions=0, originalBaselineUnchanged=True, classInit=ref(compressed),
        productTests=0, newAcceptance=0, formalUpdated=False, whole451Accepted=False,
        terminalAtUTC=R['utc'](), verifier=ref(HERE))
    save(OUT / 'manifest.json', report)
    print(ref(OUT / 'manifest.json'), dict(per))


if __name__ == '__main__':
    main()
