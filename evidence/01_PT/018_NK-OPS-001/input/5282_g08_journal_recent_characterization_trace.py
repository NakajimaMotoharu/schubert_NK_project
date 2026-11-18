"""Trace two current product value tests and the last three offline comparison cases."""
from datetime import datetime, timezone
from pathlib import Path
import json
import runpy

BASE = runpy.run_path(str(Path(__file__).with_name('5266_g08_artemis_characterization_trace.py')))
D, E, REGISTRY, OPS = (BASE[key] for key in ('D', 'E', 'REGISTRY', 'OPS'))
read, sha, ref, git, checked = (BASE[key] for key in ('read', 'sha', 'ref', 'git', 'checked'))
main_source, logged_tests = BASE['read_identity'], BASE['bound_tests']
lookup_design = BASE['design']
SPECS = (
    ('PG40078', '050', 60, 64, 192, 'ArtifactComparatorTest', 'O01/DIF-014', 'BUG-3330'),
    ('PG40092', '052', 65, 70, 198, 'ArtifactComparatorTest', 'S08/DIF-009', 'BUG-3333/3334'),
    ('PG40108', '054', 71, 76, 204, 'ArtifactComparatorTest', 'U01/DIF-003', 'BUG-3335/3336/3337'),
)


def journal(owners, independent, canonical, core, head):
    note = read(independent)
    report = checked(note['manifest'])
    primary = read(report)
    start = read(report.parent / 'begin.json')
    assert note['actualExit'] == primary['actualExit'] == 0
    assert note['sourceCore'] == primary['sourceCore'] == core
    assert note['absentOuterParserInitialization'] and note['runtimeOperationCount'] == 0
    assert set(note['testIds']) == {'PT-P01810-CATALOG-065A', 'PT-P01810-CATALOG-065B'}
    name = 'dev/codex/schubert/nk/batch/platform/'
    clazz = 'BrokerJournalEvidence'
    fixture_class = 'BrokerJournalValueContractTest'
    module = Path('src/schubert-nk-batch/src')
    source = module / 'main/java' / (name + clazz + '.java')
    fixture = module / 'test/java' / (name + fixture_class + '.java')
    assert owners[str(source)]['owner'] == owners[str(source)]['costOwner'] == 'WBS-P017-10'
    _, src = main_source(source, core)
    assert main_source(source, head)[1]['sha256'] == src['sha256']
    text, test = main_source(fixture, note['testSource'], start['testInput']['sha256'])
    assert main_source(fixture, head)[1]['sha256'] == test['sha256']
    spec = next(OPS.glob('4703_*.md'))
    xml = checked(primary['testXml'])
    targets = []
    for test_id, tag in zip(('PT-P01810-CATALOG-065A', 'PT-P01810-CATALOG-065B'),
                            ('Summary', 'Anchor'), strict=True):
        binary = name + clazz + '$' + tag
        counters = note['counters'][binary]
        assert all(counter['missed'] == 0 for counter in counters.values())
        item = primary['physical'][binary + '.class']['origin']
        targets.append(dict(testId=test_id, classFileSha256=item['sha256'],
                            crc64=note['crc64'][binary], rawCounters=counters))
    return dict(scope='PRODUCT_JOURNAL_VALUE_RECORDS', sharedOwner='WBS-P017-10', consumer='WBS-P018-10.03',
                costReapplied=False, main=src, fixture=test, docs=lookup_design((251, 343, 351), canonical),
                xml=ref(xml), proof=ref(independent), spec=ref(spec), physical=targets,
                tests=logged_tests(xml, note['testIds'], name.replace('/', '.') + fixture_class,
                                   text, spec.read_text(), 2),
                realJournalOrBroker=False)


def main():
    start = read(next((D / '601_WBS66短期実行_20261117').glob('607_G08*.json')))
    values = start['values']
    core, head = values['productionCoreMain'], values['source']
    assert git('rev-parse', 'HEAD').decode().strip() == head
    assert all(ref(Path(item['path'])) == item for item in values['oracleReferences'])
    canonical = git('rev-parse', 'origin/main').decode().strip()
    owners = {entry['path']: entry for entry in read(REGISTRY)['artifacts']}
    check_chr = BASE['characterization']
    check_chr.__globals__['SPECS'] = SPECS
    tool = check_chr(owners, canonical)
    product = journal(owners, checked(values['oracleReferences'][-1]), canonical, core, head)
    ids = {case['testId'] for case in product['tests']}
    for item in tool:
        assert not ids.intersection(case['testId'] for case in item['tests'])
        ids.update(case['testId'] for case in item['tests'])
    assert len(ids) == 19
    result = dict(actualExit=0, head=head, productionCoreMain=core, canonicalDesign=canonical,
                  scopeRegistryBefore=ref(REGISTRY), product=product, tool=tool, productCases=2,
                  offlineToolCases=17, priorRunsCombined=False, newTestsExecuted=0,
                  initialSetupExits=[1, 1], initialSetupCause='Legacy reference helper requires Path',
                  newCoverageMeasured=0, wholeG08Accepted=False, whole451Accepted=False,
                  formalIntake=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(), verifier=ref(Path(__file__)))
    out = E / values['run']
    out.mkdir()
    path = out / 'manifest.json'
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(ref(path))


if __name__ == '__main__':
    main()
