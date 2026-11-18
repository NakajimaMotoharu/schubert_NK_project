"""Verify the U01 array against independent saved Current and approved menu order."""
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree
import gzip
import re
import runpy

HERE = Path(__file__).resolve()
S = runpy.run_path(str(HERE.with_name('5255_p020_search_empty_independent.py')))
C, P, R, E = (S[key] for key in ('C', 'P', 'R', 'E'))
read, save, ref = (S[key] for key in ('read', 'save', 'ref'))
PREVIOUS = E / 'PG40089-p020-s08-voice198-v2'
PRIOR = E / 'PG40092-p020-s08-voice-independent-v1'
HISTORY = E / 'PG40018-p020-game-onchange-independent-v1'
FIRST = E / 'PG40104-p020-u01-menu204-v1'
INTERMEDIATE = E / 'PG40105-p020-u01-menu204-v2'
FIRST_STATIC = E / 'PG40106-p020-u01-menu-static-v1'
UNIT = E / 'PG40107-p020-u01-menu204-v3'
STATIC = E / 'PG40109-p020-u01-menu-static-v2'
OUT = E / 'PG40108-p020-u01-menu-independent-v1'
IDS = {
    'PT-CHR-DEF071': 'acceptsTheFiveLegacyAndNineApprovedAdministratorCardsInOrder',
    'PT-CHR-DEF072': 'requiresTheMenuCardArrayObservationOnU01',
    'PT-CHR-DEF073': 'rejectsRenamingACurrentFunctionEvenIfTheClaimMatches',
    'PT-CHR-DEF074': 'rejectsReorderingLegacyFunctionsWithinTheAdministratorMenu',
    'PT-CHR-DEF075': 'rejectsAUserMenuOrAnUnrelatedPointerAsTheAdministratorObservation',
    'PT-CHR-DEF076': 'aSeparateN01ClaimCannotSatisfyTheU01MenuContract',
}


def main():
    previous, first, unit, analysis = (read(path / 'manifest.json') for path in (PRIOR, FIRST, UNIT, STATIC))
    mid = read(INTERMEDIATE / 'manifest.json')
    first_static = read(FIRST_STATIC / 'manifest.json')
    assert first['source'] != mid['source'] == first_static['source'] != unit['source'] == analysis['source']
    assert all(stage['actualExit'] == 0 for stage in mid['stages'].values())
    assert first_static['stageExits'] == dict(spotbugs=0, format=0, checkstyle=0, pmd=4)
    assert first_static['reports']['pmd']['findings'] == 8
    assert first['stages']['unit']['actualExit'] == 1
    first_xml = FIRST / 'xml/TEST-junit-jupiter.xml'
    failure = ElementTree.parse(first_xml).getroot()
    assert {key: failure.get(key) for key in ('tests', 'failures', 'errors', 'skipped')} == dict(
        tests='204', failures='51', errors='1', skipped='0')
    assert len(unit['stages']) == 6 and all(stage['actualExit'] == 0 for stage in unit['stages'].values())
    assert analysis['allPhysicalUnchanged'] and unit['actualBackendActions'] == 0
    assert not R['git']('diff', '--name-only', '843de94', unit['source'], '--', str(R['B'] / 'baseline/current'))
    baseline = R['B'] / 'baseline/current/artifacts/CHR-U01.json'
    legacy = read(baseline)['cards']
    assert legacy == ['シナリオ閲覧', '検索', 'アニメ視聴', '音楽', 'ログ照会']
    ui = next(Path('documents/200_UI').rglob('223_*.md'))
    doc = R['git']('show', f'origin/main:{ui}').decode()
    assert 'USERは7項目、ADMINはこれにLog照会とUser管理を加える' in doc
    assert re.findall(r'^[5-7]\. (.+)$', doc, re.M)[:3] == ['質問する', '通知', '質問回答']
    nk = legacy[:4] + ['質問する', '通知', '質問回答', legacy[-1], 'User管理']
    assert len(nk) == 9

    before = P['all_cases'](PREVIOUS)
    cases = P['all_cases'](UNIT)
    new = {(C['NAME'], method + '()') for method in IDS.values()}
    assert len(before) == 198 and not new & before.keys()
    assert cases == P['all_cases'](INTERMEDIATE) == before | dict.fromkeys(new, 'PASS')
    assert set(cases.values()) == {'PASS'}
    assert len(cases) == 204 and len({group for group, _ in cases}) == 20
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
    assert raw['missedMethods'] == previous['raw']['missedMethods']
    per = Counter()
    for line in (OUT / 'raw.tsv').read_text().splitlines():
        row = line.split('\t')
        if row[0] == 'CLASS' and row[1].startswith(S['PKG'] + 'ArtifactComparator'):
            assert row[3] == 'true'
            for key, miss, hit in (part.split(':') for part in row[6:]):
                assert int(miss) == 0
                per[key] += int(hit)
    assert per['CLASS'] == 2

    read_step = unit['stages']['execinfo']['command']
    first_exec = (FIRST / 'jacoco.exec').resolve()
    assert read_step[-2] == 'execinfo'
    read_only = R['step']('failed-probe-read', [*read_step[:-1], str(first_exec)], Path.cwd(), OUT)
    assert read_only['actualExit'] == 0
    failed_output = Path(read_only['log']['path']).read_text()
    assert failed_output.count('Session "') == 1 and first['session'] in failed_output
    assert not re.search(r'(com/microsoft/playwright/|org/postgresql/|dev/codex/schubert/nk/)', failed_output)
    decoded = OUT / 'failed-probe-types.tsv'
    decoded.write_text(failed_output)

    review = OUT / 'pmd-per-site.json'
    save(review, pmd)
    compressed = OUT / 'class-init.log.gz'
    compressed.write_bytes(gzip.compress(raw_init, mtime=0))
    result = dict(
        actualExit=0, source=unit['source'], unit=ref(UNIT / 'manifest.json'),
        static=ref(STATIC / 'manifest.json'), firstUnit=ref(INTERMEDIATE / 'manifest.json'),
        firstStaticFailure=ref(FIRST_STATIC / 'manifest.json'), firstRejectedUnit=ref(FIRST / 'manifest.json'),
        firstRejectedXml=ref(first_xml), firstRejectedExec=ref(first_exec), failedReadOnly=read_only,
        failedProbeFile=ref(decoded), initialFES=dict(passed=152, failures=51, errors=1, skipped=0, notRun=0),
        firstSuccess=152, tests=204, suites=20, originalTests=198, newDefinitions=6,
        failed=0, errors=0, skipped=0, notRun=0, testIds=IDS, comparatorCounters=dict(per),
        currentBaseline=ref(baseline), independentExpected=dict(current=legacy, nkComparableAdmin=nk),
        raw=raw, pmdReviews=ref(review), pmdRaw=6, pmdApplicable=0, pmdUnclassified=0,
        actualNkChr=False, actualBackendActions=0, originalBaselineUnchanged=True, classInit=ref(compressed),
        productTests=0, newAcceptance=0, formalUpdated=False, whole451Accepted=False,
        terminalAtUTC=R['utc'](), verifier=ref(HERE))
    save(OUT / 'manifest.json', result)
    print(ref(OUT / 'manifest.json'), dict(per))


if __name__ == '__main__':
    main()
