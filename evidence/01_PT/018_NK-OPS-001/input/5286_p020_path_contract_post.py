"""Inspect the independent red and green offline DIF-015 evidence without rerunning tests."""
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET
import gzip
import re
import runpy

HERE = Path(__file__).resolve()
S = runpy.run_path(str(HERE.with_name('5255_p020_search_empty_independent.py')))
P, R, E = (S[name] for name in ('P', 'R', 'E'))
read, save, ref = (S[name] for name in ('read', 'save', 'ref'))
OLD = E / 'PG40107-p020-u01-menu204-v3'
OLD_POST = E / 'PG40108-p020-u01-menu-independent-v1'
RED = E / 'PG40122-p020-path-contract-red206-v1'
FIRST_GREEN = E / 'PG40124-p020-path-contract-green206-v1'
FIRST_STATIC = E / 'PG40126-p020-path-contract-static-v1'
UNIT = E / 'PG40128-p020-path-contract-green206-v2'
STATIC = E / 'PG40130-p020-path-contract-static-v2'
OUT = E / 'PG40132-p020-path-contract-independent-v1'
IDS = {
    'PT-CHR-DEF077': ('GateContractValidatorNegativeTest', 'rejectsOtherValidMetadataValuesForTheLegacyPathContract'),
    'PT-CHR-DEF078': ('ArtifactComparatorTest', 'rejectsALegacyPathDifferenceWhenTheLoadedRuleClaimsItIsPermitted'),
}
UI = 'documents/200_UI/260_引継ぎ・監査/264_現行互換性Characterization Test仕様.md'
PREFIX = 'dev.codex.schubert.characterization.'
ALLOWED = 'program/characterization/tests/resources/cases/dif-allowlist.json'


def main():
    red, green, current, old_static, static = (read(folder / 'manifest.json') for folder in
                                              (RED, FIRST_GREEN, UNIT, FIRST_STATIC, STATIC))
    assert red['stages']['unit']['actualExit'] == 1
    assert len({red['source'], green['source'], current['source']}) == 3
    assert green['source'] == old_static['source'] and current['source'] == static['source']
    assert green['mainPhysical'] == current['mainPhysical'] and static['allPhysicalUnchanged']
    assert all(r['actualExit'] == 0 for stage in (green, current) for r in stage['stages'].values())
    before = P['all_cases'](OLD)
    cases = P['all_cases'](UNIT)
    assert len(before) == 204 and len(cases) == 206 and len({suite for suite, _ in cases}) == 20
    new_tests = {(PREFIX + name, method + '()') for name, method in IDS.values()}
    assert not new_tests & before.keys()
    assert cases == before | dict.fromkeys(new_tests, 'PASS') == P['all_cases'](FIRST_GREEN)
    first_xml = RED / 'xml/TEST-junit-jupiter.xml'
    xml = ET.parse(first_xml).getroot()
    assert {k: xml.get(k) for k in ('tests', 'failures', 'errors', 'skipped')} == {
        'tests': '206', 'failures': '2', 'errors': '0', 'skipped': '0'}
    assert {(r.get('classname'), r.get('name')) for r in xml.iter('testcase')
            if r.find('failure') is not None} == new_tests
    assert old_static['reports']['pmd']['findings'] == 11
    assert old_static['stageExits'] == static['stageExits'] == dict(spotbugs=0, format=0, checkstyle=0, pmd=4)
    assert static['priorExactMainTyped']['actualArchivedExit'] == 0
    assert static['priorExactMainTyped']['executedInCurrentScope'] is False
    assert static['reports']['spotbugs']['physical'] == 17 and static['reports']['spotbugs']['exactPhysical']
    catalog = read(ALLOWED)
    rule, = [row for row in catalog['differences'] if row['id'] == 'DIF-015']
    assert (rule['mode'], rule['field'], rule['selectorType'], rule['selectors']) == (
        'contract', 'http.path', 'semantic', ['http.path'])
    assert len(rule['cases']) == 24
    ui = R['git']('show', f'origin/main:{UI}').decode()
    line, = [line for line in ui.splitlines() if line.startswith('| DIF-015 |')]
    assert '初期releaseで変更なし' in line and 'TST-005' in line
    assert not R['git']('diff', '--name-only', '843de94', current['source'], '--', str(R['B'] / 'baseline/current'))
    assert green['actualBackendActions'] == current['actualBackendActions'] == 0
    pmd = S['decisions'](read(OLD_POST / 'manifest.json'), static, STATIC)
    assert len(pmd) == 7
    owner_local, = [r for r in pmd if r['disposition'] == 'UNCLASSIFIED']
    assert owner_local['owner'] == 'GateContractValidator.java'
    assert owner_local['rule'] == 'UseConcurrentHashMap'
    assert owner_local['anchor'] == 'Map<String, Object> metrics = new LinkedHashMap<>();'
    lines = Path(owner_local['file']['path']).read_text().splitlines()
    local = '\n'.join(lines[owner_local['line'] - 1:]).split('\n  }', 1)[0]
    assert 'return Map.copyOf(metrics);' in local
    assert all(text.startswith(('    Map<String, Object> metrics', '    return Map.copyOf(metrics)',
                                '      metrics.put(', '    metrics.put('))
               for text in local.splitlines() if 'metrics' in text)
    owner_local.update(disposition='NOT_APPLICABLE',
                       reason='Each invocation creates its own local map and returns an immutable copy.')
    assert all(r['disposition'] == 'NOT_APPLICABLE' for r in pmd)
    init = Path(current['initLog']['path'])
    assert ref(init) == current['initLog']
    raw_init = init.read_bytes()
    assert not re.search(rb"Initializing '(?:com/microsoft/playwright|dev/codex/schubert/nk/|org/postgresql)", raw_init)
    ev = (UNIT / 'execinfo.log').read_text()
    assert re.findall(r'^Session "([^"]+)":', ev, re.M) == [current['session']]
    OUT.mkdir()
    scope = Path(current['classesDir'])
    assert R['physical'](scope) == current['mainPhysical'] and len(current['mainPhysical']) == 17
    raw = P['unfiltered'](current, UNIT, scope, OUT, read(next(E.glob('PG37324*/manifest.json'))))
    previous = read(OLD_POST / 'manifest.json')
    assert raw['missedMethods'] == previous['raw']['missedMethods']
    counters = Counter()
    for line in (OUT / 'raw.tsv').read_text().splitlines():
        row = line.split('\t')
        if row[0] == 'CLASS' and row[1].startswith(
              tuple(S['PKG'] + name for name in ('ArtifactComparator', 'GateContractValidator'))):
            assert row[3] == 'true'
            for key, miss, hit in (part.split(':') for part in row[6:]):
                assert int(miss) == 0
                counters[key] += int(hit)
    assert counters['CLASS'] == 4
    exec_read = current['stages']['execinfo']['command']
    rejected_exec = (RED / 'jacoco.exec').resolve()
    rejected = R['step']('rejected-execinfo', [*exec_read[:-1], str(rejected_exec)], Path.cwd(), OUT)
    assert rejected['actualExit'] == 0
    rejected_text = Path(rejected['log']['path']).read_text()
    assert re.findall(r'^Session "([^"]+)":', rejected_text, re.M) == [red['session']]
    archive = OUT / 'class-init.log.gz'
    archive.write_bytes(gzip.compress(raw_init, mtime=0))
    review = OUT / 'pmd-per-site.json'
    save(review, pmd)
    result = dict(
        actualExit=0, source=current['source'], unit=ref(UNIT / 'manifest.json'), static=ref(STATIC / 'manifest.json'),
        firstUnit=ref(FIRST_GREEN / 'manifest.json'), firstStaticFailure=ref(FIRST_STATIC / 'manifest.json'),
        firstRejectedUnit=ref(RED / 'manifest.json'), firstRejectedXml=ref(first_xml), firstRejectedExec=ref(rejected_exec),
        failedReadOnly=rejected, initialFES=dict(passed=204, failures=2, errors=0, skipped=0, notRun=0),
        tests=206, suites=20, failed=0, errors=0, skipped=0, notRun=0, newDefinitions=2, testIds=IDS,
        independentExpected=dict(designRow=line, mode='contract', field='http.path', selector='http.path', cases=24),
        approvedRevision=R['git']('rev-parse', 'origin/main').decode().strip(),
        raw=raw, changedToolCounters=dict(counters), pmdReviews=ref(review), pmdRaw=7, pmdApplicable=0,
        baselineUnchanged=True, classInit=ref(archive), actualNkChr=False, productTests=0, newAcceptance=0,
        whole451Accepted=False, terminalAtUTC=R['utc'](), verifier=ref(HERE))
    save(OUT / 'manifest.json', result)
    print(ref(OUT / 'manifest.json'), counters, raw['missedMethods'])


if __name__ == '__main__':
    main()
