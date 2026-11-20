"""Authenticate the red/green A02 observations and the current unfiltered coverage."""

from collections import Counter
import gzip
from pathlib import Path
import re
import runpy
from xml.etree import ElementTree


HERE = Path(__file__).resolve()
T = runpy.run_path(str(HERE.with_name('5255_p020_search_empty_independent.py')))
P, R, E, read, save, ref = (T[key] for key in ('P', 'R', 'E', 'read', 'save', 'ref'))
COMPARATOR = 'dev/codex/schubert/characterization/ArtifactComparator'
EXPECTED_CASES = {'PT-CHR-CMP-A02-003': 'rejectsReportsThatBothOmitTheTwoRetainedSessionDestinations',
                  'PT-CHR-CMP-A02-004': 'rejectsReportsThatBothRedirectTheMiddleSessionDespiteActiveEvidence'}


def main():
    old_path = E/'PG40208-p020-a02-session-census-green208-v1'
    old_post = read(E/'PG40212-p020-a02-session-census-independent-v1'/'manifest.json')
    red, green, static, out = (next(E.glob(f'PG{run}-*')) if run != 40662
                               else E/'PG40662-p020-a02-redirect-independent-v1'
                               for run in (40656, 40658, 40660, 40662))
    red_unit, unit, analysis = (read(path/'manifest.json') for path in (red, green, static))
    assert red_unit['source'] != unit['source'] == analysis['source']
    assert unit['productionCore'] == red_unit['productionCore']
    assert red_unit['stages']['main']['actualExit'] == red_unit['stages']['test']['actualExit'] == 0
    assert red_unit['stages']['unit']['actualExit'] == 1
    tests = {(COMPARATOR.replace('/', '.') + 'Test', method + '()') for method in EXPECTED_CASES.values()}
    red_xml = ElementTree.parse(red/'xml/TEST-junit-jupiter.xml').getroot()
    assert all(node.find('failure').get('message') == 'expected: <false> but was: <true>'
               for node in red_xml.iter('testcase'))
    assert P['all_cases'](red) == dict.fromkeys(tests, 'failure')
    prior, now = P['all_cases'](old_path), P['all_cases'](green)
    assert len(prior) == 208 and tests.isdisjoint(prior)
    assert now == prior | dict.fromkeys(tests, 'PASS') and set(now.values()) == {'PASS'}
    assert len(now) == 210 and len({suite for suite, _ in now}) == 20
    assert len(unit['stages']) == 6 and all(stage['actualExit'] == 0 for stage in unit['stages'].values())
    assert re.findall(r'^Session "([^"]+)":', (green/'execinfo.log').read_text(), re.M) == [unit['session']]
    init_path = Path(unit['initLog']['path'])
    assert ref(init_path) == unit['initLog']
    init = init_path.read_bytes()
    assert not re.search(rb"Initializing '(?:com/microsoft/playwright|dev/codex/schubert/nk/|dev/codex/schubert/characterization/(?:Native|CurrentCharacterizationTest)|org/postgresql)", init)

    catalog = Path('program/characterization/baseline/current/artifacts/CHR-A02.json')
    current = ['/', '/', '/']
    nk = ['/login?session-expired', '/', '/']
    assert read(catalog)['sessionRedirectsOldestToNewest'] == current
    assert not R['git']('diff', '--name-only', '843de94', unit['source'], '--',
                        'program/characterization/baseline/current')
    ss = next(Path('documents/300_SS/350_運用・品質').glob('355_*'))
    assert 'A02のCurrent 3 session継続はDIF-016、NKは最古revoke' in ss.read_text()
    start = read(next(Path('documents/400_PGPT/470_PMO').glob('601_*/1027_P020*')))['values']
    assert not R['git']('diff', '--name-only', start['source'], unit['source'], '--', 'src')
    retained_test_only = set(R['git']('diff', '--name-only', unit['productionCore'], unit['source'],
                                     '--', 'src').decode().splitlines())
    assert len(retained_test_only) == 2 and all('/src/test/' in name for name in retained_test_only)
    assert {Path(name).name for name in retained_test_only} == {
        'AlertThresholdsTest.java', 'StorageFailureGraphTest.java'}
    ui = start['oracleReferences'][-1]['path']
    approved = R['git']('show', f'{start["canonicalDesignSource"]}:{ui}').decode()
    assert any('DIF-016' in line and '最古session' in line for line in approved.splitlines())

    pmd = T['decisions'](old_post, analysis, static)
    assert len(pmd) == 6 and all(row['disposition'] == 'NOT_APPLICABLE' for row in pmd)
    scope = Path(unit['classesDir'])
    assert R['physical'](scope) == unit['mainPhysical'] and analysis['allPhysicalUnchanged']
    out.mkdir()
    raw = P['unfiltered'](unit, green, scope, out, read(next(E.glob('PG37324*/manifest.json'))))
    assert all(row['className'].endswith('/GateCli') for row in raw['missedMethods'])
    totals = Counter()
    for line in (out/'raw.tsv').read_text().splitlines():
        fields = line.split('\t')
        if fields[0] != 'CLASS' or not fields[1].startswith(COMPARATOR):
            continue
        assert fields[3] == 'true'
        for name, missed, hit in (part.split(':') for part in fields[6:]):
            assert int(missed) == 0
            totals[name] += int(hit)
    assert totals['CLASS'] == 2 and totals['BRANCH'] > 0
    dispositions, init_log = out/'pmd-per-site.json', out/'class-init.log.gz'
    save(dispositions, pmd)
    init_log.write_bytes(gzip.compress(init, mtime=0))
    proof = out/'manifest.json'
    save(proof, dict(actualExit=0, source=unit['source'], productionCore=unit['productionCore'],
                     red=ref(red/'manifest.json'), green=ref(green/'manifest.json'),
                     static=ref(static/'manifest.json'), testIds=EXPECTED_CASES,
                     originalCases=208, fullOfflineCases=210, suites=20,
                     failed=0, errors=0, skipped=0, notRun=0, independentCurrent=current,
                     independentNk=nk, currentBaseline=ref(catalog), comparatorCounters=dict(totals),
                     retainedEarlierProductTestOnlyChanges=sorted(retained_test_only),
                     pmdDispositions=ref(dispositions), initialized=ref(init_log), raw=raw,
                     wholeOfflinePlusRealFileStoreSameRun=False, actualNkChr=0,
                     productTests=0, whole451=False, formalDelta=0, terminalAtUTC=R['utc']()))
    print(ref(proof), dict(totals), raw['rawTotals'])


if __name__ == '__main__':
    main()
