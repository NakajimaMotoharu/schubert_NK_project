"""Join two exact fixed-diagnostic contracts to independent completed evidence."""
from datetime import datetime, timezone
from pathlib import Path
import re
import runpy
import subprocess
from xml.etree import ElementTree as ET

ENTRY = Path(__file__).resolve()
h = runpy.run_path(str(ENTRY.with_name('5189_wbs66_four_module_delta_handoff.py')))
E = h['E']
D = h['D']
OUT = E / 'PG39628-p01810-inbox-inspection-diagnostic-lineage-v1'
CONTRACTS = (
    ('012', 'PG35842', 21, 'InboxRequestValueContractTest',
     'requestValue002OrderedValueComponentsAndFixedRedactionRetainBorrowedCanonical',
     'InboxRequest[message/correlation/owner/token/request/time=<redacted>]', 'value'),
    ('045', 'PG29434', 8, 'InspectionAttemptTest', 'redactionAndValueOwnership',
     'InspectionAttempt[observation=<redacted>]', 'first'),
)


def anchored_method(text, name):
    pattern = r'^  (?:public String|void) ' + re.escape(name) + r'\([^\n]*\)\s*\{.*?^  }$'
    matches = re.findall(pattern, text, re.M | re.S)
    [method] = matches
    return method


def observe(case, rows, values):
    tag, run, cases, test_name, method, marker, test_value = case
    catalog_id = f'PT-P01810-CATALOG-{tag}'
    [record] = [row for row in rows if row['catalog'] == catalog_id]
    assert record['shape'] == 'FIXED_REDACTED_LITERAL'
    main = record['path']
    expected_source_class = main.partition('/src/main/java/')[2].removesuffix('.java')
    postfile = h['matching_path'](run + '*/manifest.json')
    post = h['load'](postfile)
    cast = post['inputHashes']
    [test_path] = [p for p in cast if p.endswith('/' + test_name + '.java')]
    main_text = h['git']('show', f'{values["productionCoreMain"]}:{main}')
    assert main_text == h['git']('show', f'{values["source"]}:{main}')
    assert h['sha'](main_text) == cast[main] == record['sha256']
    test_text = h['git']('show', f'{values["source"]}:{test_path}')
    assert h['sha'](test_text) == cast[test_path]
    assert test_text == h['git']('show', f'{post["source"]}:{test_path}')
    assert main_text == h['git']('show', f'{post["source"]}:{main}')
    actual_body = anchored_method(main_text.decode(), 'toString')
    assert re.fullmatch(r'  public String toString\(\)\s*\{\s*return "'
                        + re.escape(marker) + r'";\s*}', actual_body)
    test_body = anchored_method(test_text.decode(), method)
    assert re.search(r'assertEquals\(\s*"' + re.escape(marker) + r'",\s*' + test_value
                     + r'\.toString\(\)\s*\);', test_body)
    assert post['actualExit'] == 0 and post['tests'] == cases and post['oldExecCombined'] is False
    f = postfile.parent
    for name in ('original-TEST-junit-jupiter.xml', 'original-coverage.xml', 'jacoco.exec'):
        assert h['ref'](f / name)['sha256'] == post['files'][name]
    xml = ET.parse(f / 'original-TEST-junit-jupiter.xml')
    qualified_cases = xml.getroot().findall('testcase')
    assert len(qualified_cases) == cases
    assert not any(n.findall('failure') or n.findall('error') or n.findall('skipped') for n in qualified_cases)
    [witness] = [n for n in qualified_cases if n.get('classname').endswith('.' + test_name)
                 and n.get('name') == method + '()']
    assert witness.get('classname').replace('.', '/') == test_path.partition('/src/test/java/')[2].removesuffix('.java')
    coverage = ET.parse(f / 'original-coverage.xml')
    [member] = [n for c in coverage.iter('class') if c.get('name') == expected_source_class
                for n in c.findall('method') if n.get('name') == 'toString']
    assert member.get('desc') == '()Ljava/lang/String;'
    counters = {r.get('type'): {'missed': int(r.get('missed')), 'covered': int(r.get('covered'))}
                for r in member.findall('counter')}
    for name, count in (('INSTRUCTION', 2), ('LINE', 1), ('METHOD', 1)):
        assert counters[name] == {'missed': 0, 'covered': count}
    assert 'BRANCH' not in counters
    if tag == '012':
        raw_file = h['matching_path']('PG35844*/manifest.json')
        raw = h['load'](raw_file)
        joined_file = h['matching_path']('PG35843*/manifest.json')
        joined = h['load'](joined_file)
        assert joined['source'] == post['source'] and joined['run'] == post['run']
        assert joined['originalGenericPost'] == h['ref'](postfile)
        copied = joined_file.parent / 'jacoco.exec'
        assert raw['originalSingleExec'] == h['ref'](copied)
        assert h['ref'](copied)['sha256'] == post['files']['jacoco.exec']
        assert raw['actualUnitSource'] == post['source']
        assert raw['actualExit'] == 0
    else:
        raw_file = h['matching_path']('PG29438*/manifest.json')
        assert h['load'](raw_file)['post'] == h['ref'](postfile)
    return dict(catalogId=catalog_id, mainPath=main, mainSha256=cast[main],
                testPath=test_path, testSha256=cast[test_path], witnessClass=witness.get('classname'),
                witnessMethod=method, expectedLiteral=marker, staticMethodIndependentOfInstanceState=True,
                historicalSource=post['source'], historicalCore=post['productionCoreMain'],
                historicalClassCrc=post['classIds'][expected_source_class],
                actualRelevantOriginalCases=1, originalWholeCases=cases, originalMethodCounters=counters,
                naturalNoBranch=True, originalFiles=[h['ref'](f / name) for name in
                    ('original-TEST-junit-jupiter.xml', 'original-coverage.xml', 'jacoco.exec')],
                originalProof=h['ref'](postfile), supplementalProof=h['ref'](raw_file),
                currentCandidateClaim='IDENTICAL_FOCUSED_MAIN_AND_TEST_ONLY')


def main():
    start = h['load'](next(D.glob('472_*')))
    values = start['values']
    assert subprocess.run(['git', 'merge-base', '--is-ancestor', values['source'], 'HEAD']).returncode == 0
    assert not h['git']('diff', '--name-only', values['source'], 'HEAD', '--', 'src')
    assert h['git']('rev-parse', 'origin/dev-foundation').decode().strip() == values['source']
    assert all(h['ref'](Path(v['path'])) == v for v in values['oracleReferences'])
    cat = h['matching_path']('PG38818*/attempt-02/catalog-evidence.json')
    rows = h['load'](cat)
    items = [observe(row, rows, values) for row in CONTRACTS]
    result = dict(actualExit=0, startEvent=start['eventId'], productionCore=values['productionCoreMain'],
                  source=values['source'], terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                  catalogReference=h['ref'](cat), matchedIndependentDiagnosticContracts=2,
                  items=items, productTestsRerun=0, firstCandidateStaticWitness=2, reusedOriginalExecUnion=0,
                  wholeCurrentCoverageCredited=0, actualProducerSinksProved=False, newAcceptance=0,
                  initialAttempt=h['ref'](OUT / 'first-verifier-failure.json'),
                  originalRowPriceAddedPp=0, QAOrHoldChanged=0, verifier=h['ref'](ENTRY.relative_to(Path.cwd())))
    output = OUT / 'manifest.json'
    h['write'](output, result)
    print(h['ref'](output))


if __name__ == '__main__':
    main()
