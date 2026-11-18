"""Bind existing Artemis value and characterization test records to source and design."""
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree
import json
import re
import runpy

A = runpy.run_path(str(Path(__file__).with_name('5215_g08_four_source_test_ids.py')))
D, E, REGISTRY = (A[key] for key in ('D', 'E', 'REGISTRY'))
read, sha, ref, git, checked = (A[key] for key in ('read', 'sha', 'ref', 'git', 'checked'))
START = next((D / '601_WBS66短期実行_20261117').glob('574_G08*.json'))
ROOT = Path('evidence/01_PT')
CHR = ROOT / '020_NK-CHR-001'
OPS = ROOT / '018_NK-OPS-001'
REPORT = E / 'PG40062-g08-artemis-chr-trace-v1'
PACKAGE = 'dev.codex.schubert.characterization'
SPECS = (
    ('PG39994', '042', 38, 42, 170, 'ArtifactComparatorTest', 'S04/DIF-008', 'BUG-3320'),
    ('PG40018', '044', 43, 48, 176, 'ArtifactComparatorTest', 'S02/DIF-013', 'BUG-3321'),
    ('PG40038', '046', 49, 54, 182, 'CorrelatedMenuActionContractTest', 'L01/QA-054', 'BUG-3323/3324'),
    ('PG40060', '048', 55, 59, 187, 'ArtifactComparatorTest', 'E01/DIF-005', 'BUG-3326/3327'),
)


def read_identity(path, source, expected=None):
    content = git('show', f'{source}:{path}')
    assert expected is None or sha(content) == expected, str(path)
    return content.decode(), dict(path=str(path), sha256=sha(content), source=source)


def bound_tests(xml, identities, classname, source_code, spec, total):
    cases = ElementTree.parse(xml).getroot().findall('testcase')
    indexed = {(case.get('classname'), case.get('name')) for case in cases}
    assert len(cases) == len(indexed) == total
    assert all(case.find(tag) is None for case in cases for tag in ('failure', 'error', 'skipped'))
    assert all(identity in spec for identity in identities), spec[:100]
    rows = []
    for identity, raw in identities.items():
        method = raw.removesuffix('()')
        assert (classname, method + '()') in indexed, (identity, method)
        assert re.search(r'\bvoid\s+' + re.escape(method) + r'\s*\(', source_code), method
        rows.append(dict(testId=identity, xmlClass=classname, xmlMethod=method + '()'))
    return rows


def design(prefixes, canonical):
    return [
        read_identity(next(Path('documents').rglob(f'{prefix}_*.md')), canonical)[1]
        for prefix in prefixes
    ]


def characterization(owners, canonical):
    rows = []
    for run, number, first, last, total, test_class, contract, issue in SPECS:
        proof = next(E.glob(run + '-*/manifest.json'))
        data = read(proof)
        assert data['actualExit'] == 0 and data['tests'] == total and not data['whole451Accepted']
        assert set(data['testIds']) == {f'PT-CHR-DEF{id_:03d}' for id_ in range(first, last + 1)}
        unit_path = checked(data['unit'])
        unit = read(unit_path)
        assert data['source'] == unit['source']
        xml = unit_path.parent / 'xml/TEST-junit-jupiter.xml'
        assert ref(xml)['sha256'] == unit['xmlHashes'][xml.name]
        base = Path('program/characterization')
        java = Path(*PACKAGE.split('.'))
        sources = [base / 'src/main/java' / java / 'ArtifactComparator.java']
        if contract.startswith('L01/'):
            sources.append(base / 'src/main/java' / java / 'CorrelatedLogEvidenceValidator.java')
        fixtures = {}
        tests = []
        spec = next(CHR.glob(number + '_*.md'))
        owner = owners[str(sources[0])]
        assert owner['owner'] == owner['costOwner'] == 'WBS-P020-01'
        for test_id, raw in data['testIds'].items():
            clazz, method = raw if isinstance(raw, list) else (test_class, raw)
            if clazz not in fixtures:
                test = base / 'tests/java' / java / (clazz + '.java')
                fixtures[clazz] = read_identity(test, unit['source'], unit['inputHashes'][str(test)])
            text, _ = fixtures[clazz]
            tests.extend(bound_tests(xml, {test_id: method}, PACKAGE + '.' + clazz, text,
                                     spec.read_text(), total))
        rows.append(dict(
            scope='OFFLINE_TOOL', contract=contract, localIssue=issue, owner=owner['owner'],
            main=[read_identity(p, unit['source'], unit['inputHashes'][str(p)])[1] for p in sources],
            fixtures=[item[1] for item in fixtures.values()], docs=design((264, 355), canonical),
            spec=ref(spec), wholeToolTests=total, tests=tests,
            run=unit['run'], xml=ref(xml), proof=ref(proof), realRuntimeProved=False,
        ))
    return rows


def artemis(owners, canonical, core, head):
    proof = next(E.glob('PG40008-*/independent.json'))
    independent = read(proof)
    primary = checked(independent['manifest'])
    data = read(primary)
    start = read(primary.with_name('begin.json'))
    assert independent['actualExit'] == data['actualExit'] == 0
    assert independent['sourceCore'] == data['sourceCore'] == core
    assert data['passed'] == 3 and all(data[key] == 0 for key in ('failed', 'errors', 'skipped', 'notRun'))
    target = data['target'].split('$', maxsplit=1)[0]
    module = Path('src/schubert-nk-batch/src')
    main = module / 'main/java' / (target + '.java')
    test_class = 'ArtemisStartupEvidenceValueTest'
    test = module / 'test/java' / target.rsplit('/', 1)[0] / (test_class + '.java')
    reference = owners[str(main)]
    assert reference['owner'] == reference['costOwner'] == 'WBS-P017-10'
    text, test_ref = read_identity(test, data['testSource'], start['testInput']['sha256'])
    assert read_identity(test, head)[1]['sha256'] == test_ref['sha256']
    _, main_ref = read_identity(main, core)
    assert read_identity(main, head)[1]['sha256'] == main_ref['sha256']
    spec = next(OPS.glob('4699_*.md'))
    xml = checked(data['testXml'])
    raw_class = data['sourceToPhysical'][data['target'] + '.class']
    return dict(
        scope='PRODUCT_VALUE_RECORD', owner=reference['owner'], consumer='WBS-P018-10.03',
        commonPriceChargedAgain=False, docs=design((231, 251, 253, 321, 342, 351), canonical),
        fixture=test_ref, main=[main_ref], spec=ref(spec), xml=ref(xml), proof=ref(proof),
        qualifiedPhysical=dict(sha256=raw_class['sha256'], crc64=independent['recordCrc64'],
                               counters=data['counters']),
        tests=bound_tests(xml, independent['testIds'], target.replace('/', '.').rsplit('.', 1)[0]
                          + '.' + test_class, text, spec.read_text(), 3),
        realRuntimeProved=False,
    )


def main():
    start = read(START)
    values = start['values']
    core, head = values['productionCoreMain'], values['source']
    assert git('rev-parse', 'HEAD').decode().strip() == head
    canonical = git('rev-parse', 'origin/main').decode().strip()
    owners = {entry['path']: entry for entry in read(REGISTRY)['artifacts']}
    rows = [artemis(owners, canonical, core, head), *characterization(owners, canonical)]
    ids = [test['testId'] for row in rows for test in row['tests']]
    assert len(ids) == len(set(ids)) == 25
    report = dict(actualExit=0, source=head, productionCoreMain=core, designCanonical=canonical,
                  ownerRegistryBefore=ref(REGISTRY), trace=rows, productCases=3, offlineToolCases=22,
                  newTestExecutions=0, initialMetadataGuard='PG40038 entries use explicit class/method pairs; the first read aborted before writing evidence.', priorRunsCombined=False, newMeasuredCoverage=0,
                  wholeG08Accepted=False, whole451Accepted=False, newAcceptance=0, effortRate=None,
                  terminalAtUTC=datetime.now(timezone.utc).isoformat(), verifier=ref(Path(__file__)))
    REPORT.mkdir()
    (REPORT / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
