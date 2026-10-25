"""Current source/class/annotation/owner and corrected static-input post; no product PT replay."""
import datetime as dt
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import class_reference_metadata as classfile
import g07_host_class_provenance_inputs as data
import pg9346_direct_companion_jdk_post as steps
from host_tool_invocation import capture, verify

ROOT = data.ROOT
OPS = data.BASE
BASE = ROOT / 'evidence/01_PT/002_NK-PRO-002/evidence/provisional'
WORK = ROOT.parent / 'pgpt-runs/PG379'
SOURCE = '3154be39380de4771111f859ffb8315420274b0a'
NORMAL = WORK / 'pg9660-pagination-six-compile-v1/snapshot'
SLOT = WORK / 'pg9668-pagination-trace-quality-post-v1'
OUT = BASE / 'PG9668-pagination-trace-quality-post-v1'
TYPE = 'dev.codex.schubert.nk.protocol.layout.PayloadPaginationBoundaryTest'
TEST = 'src/schubert-nk-protocol/src/test/java/' + TYPE.replace('.', '/') + '.java'
MAIN = 'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/PayloadSemanticValidator.java'
SPEC = ROOT / 'evidence/01_PT/002_NK-PRO-002/006_Page境界_単体テスト仕様書.md'
IDS = {
    'page001SecondPageHasIndependentExpectedBounds': 'PT-PRO-002-PAGE001',
    'page002MaximumEffectivePageKeepsExactNineDigitArithmetic': 'PT-PRO-002-PAGE002',
    'page003RejectsIndependentRangeAndOneFieldArithmeticChanges': 'PT-PRO-002-PAGE003'}


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    assert data.sha(SPEC.read_bytes()) == '86eb7c04246aa2c6a452b77538a068eb91c435fc92ddd94b877b40dfd7fc4878'
    normal = data.read_checked(OPS / 'PG9660-pagination-six-compile-v1/manifest.json',
        'f2ae182bb3a88eff78542ce0c18f3a497263aaabb7ed7fdbea5237a9ab467c2c')
    post = data.read_checked(BASE / 'PG9664-pagination-boundary-post-v1/manifest.json',
        'd12d686512ce45599f7a9eaa89d03560a7c579aaa8c3e5036b9de2a641510959')
    fixed = data.read_checked(BASE / 'PG9666-pagination-static-v2/manifest.json',
        '41807eb5d29a989424939246359f8eb7f9162bd03c7fbc4d1f2bd8932546de08')
    failed = data.read_checked(BASE / 'PG9666-pagination-static-v1/manifest.json',
        '8d84b114236c23040c081547441776cc038835f85ca60398da499a0b4b4df6d4')
    assert all(r['actualExit'] == 0 and r['source'] == SOURCE for r in (normal, post, fixed))
    assert failed['actualExit'] == 1 and failed['source'] == SOURCE
    assert post['actualTests'] == post['newTestIds'] == 3 and set(post['cases']) == set(IDS)
    assert post['allMainBytesUnchangedFromPriorCompile'] and post['allMainClassCount'] == 1843
    hashes = normal['begin']['inputHashes']
    prior = data.read_checked(OPS / data.PINS['normal'][0] / 'manifest.json', data.PINS['normal'][1])
    previous = prior['begin']['inputHashes']
    assert set(hashes) - set(previous) == {TEST} and not set(previous) - set(hashes)
    assert all(hashes[p] == h for p, h in previous.items())
    assert all(data.sha((ROOT / p).read_bytes()) == data.sha((NORMAL / p).read_bytes()) == h for p, h in hashes.items())
    graph = data.read_checked(OPS / data.PINS['graph'][0] / 'manifest.json', data.PINS['graph'][1])
    metadata = data.read_checked(OPS / data.PINS['graph'][0] / 'test-class-metadata.json', graph['testMetadataSha256'])
    existing = set()
    for row in metadata:
        path = NORMAL / ('src/schubert-nk-' + row['module']) / 'target/test-classes' / row['entry']
        assert data.sha(path.read_bytes()) == row['sha256']
        existing.add((row['module'], row['entry']))
    observed = set()
    for module in normal['jars']:
        base = NORMAL / ('src/schubert-nk-' + module) / 'target/test-classes'
        observed.update((module, p.relative_to(base).as_posix()) for p in base.rglob('*.class'))
    entry = TYPE.replace('.', '/') + '.class'
    assert len(existing) == 1910 and observed - existing == {('protocol', entry)} and not existing - observed
    owners = data.read_checked(OPS / 'PG9546-shared-fixture7-source-join-v1/manifest.json',
        '4d82743eb894ccd448a2ef88b40f566bc0fb08a8ee4b5128a925e49c08b7dd61')
    subject = [r for r in owners['sourceRows'] if r['path'] == MAIN]
    assert len(subject) == 1 and subject[0]['canonicalOwner'] == subject[0]['canonicalCostOwner'] == 'WBS-P002-02'
    assert subject[0]['sha256'] == hashes[MAIN]
    new_class = NORMAL / 'src/schubert-nk-protocol/target/test-classes' / entry
    info = classfile.read(new_class.read_bytes())
    assert info['className'] == TYPE.replace('.', '/') and info['sourceFile'] == Path(TEST).name
    main_map = data.read_checked(OPS / data.PINS['graph'][0] / 'main-class-sources.json', graph['mainMapSha256'])
    references = {name: main_map[name] for name in info['references'] if name in main_map}
    assert 'dev/codex/schubert/nk/protocol/layout/PayloadSemanticValidator' in references
    static_counts = {}
    input_classes = {}
    for module, result in fixed['results'].items():
        assert result['receipt']['actualExit'] == 0 and not result['receipt']['timedOut']
        assert result['findings'] == result['processingErrors'] == 0
        report = BASE / 'PG9666-pagination-static-v2' / ('current-v2-spotbugs-' + module + '.xml')
        old_report = report.with_name('original-v1-spotbugs-' + module + '.xml')
        assert data.sha(report.read_bytes()) == result['reportSha256']
        assert data.sha(old_report.read_bytes()) == failed['reports']['spotbugs-' + module]['sha256']
        root = ET.parse(report).getroot()
        aux = {n.text for n in root.findall('Project/AuxClasspathEntry')}
        assert aux == set(result['dependencyHashes']) and not any('/m2/repository/dev/codex/schubert/' in p for p in aux)
        assert not root.findall('.//BugInstance') and not root.findall('.//MissingClass') and not root.findall('.//Error')
        assert all(data.sha(Path(p).read_bytes()) == h for p, h in result['dependencyHashes'].items())
        with zipfile.ZipFile(normal['jars'][module]['path']) as archive:
            actual = {p: data.sha(archive.read(p)) for p in archive.namelist() if p.endswith('.class')}
        assert actual == result['physicalClasses']
        assert not (set(actual) & set(input_classes))
        input_classes.update(actual)
        static_counts[module] = len(actual)
    assert len(input_classes) == 1843
    assert sum(len(ET.parse(BASE / 'PG9666-pagination-static-v2' / ('original-v1-spotbugs-' + m + '.xml')).getroot().findall('.//MissingClass')) for m in normal['jars']) == 18
    for name in ('pmd-test', 'checkstyle-test'):
        assert failed['stages'][name]['actualExit'] == 0 and failed['reports'][name]['findings'] == failed['reports'][name]['processingErrors'] == 0
        filename = 'pmd.xml' if name == 'pmd-test' else 'checkstyle.xml'
        assert data.sha((WORK / 'pg9666-pagination-static-v1' / filename).read_bytes()) == failed['reports'][name]['sha256']
    os.umask(0o077)
    SLOT.mkdir()
    reader = SLOT / 'reader'
    reader.mkdir()
    ast = ROOT / 'tools/quality/architecture/ExistingTestMethodJdkAudit.java'
    annotations = ROOT / 'tools/quality/architecture/PublicTestMethodMetadataAudit.java'
    helpers = {str(p.relative_to(ROOT)): data.sha(p.read_bytes()) for p in (ast, annotations)}
    catalog = SLOT / 'new-test-source.txt'
    with catalog.open('x') as stream:
        stream.write(TEST + '\n')
    classes = SLOT / 'new-test-class.tsv'
    with classes.open('x') as stream:
        stream.write('protocol\t' + str(new_class) + '\n')
    tc = ROOT.parent / 'toolchain'
    steps.SLOT = SLOT
    stages = [steps.step('compile-readers', [str(tc / 'jdk-25.0.4/bin/javac'), '--release', '25', '-proc:none', '-Xlint:all', '-Werror', '-d', str(reader), str(ast), str(annotations)])]
    assert stages[0]['actualExit'] == 0 and not stages[0]['timedOut']
    for label, helper, root, inputs in [('parse-new-source', ast, ROOT, catalog), ('read-new-class', annotations, NORMAL, classes)]:
        stages.append(steps.step(label, [str(tc / 'jdk-25.0.4/bin/java'), '-cp', str(reader), helper.stem, str(root), str(inputs)]))
        assert stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut']
    source_lines = (SLOT / 'parse-new-source.stdout').read_text().splitlines()
    class_lines = (SLOT / 'read-new-class.stdout').read_text().splitlines()
    assert source_lines[0] == 'SELFTEST\t7' and class_lines[0] == 'SELFTEST\t6'
    source_rows = {}
    for line in source_lines[1:]:
        path, owner, name, params, start, end = line.split('\t')
        assert path == TEST and owner == TYPE and params == '0' and name in IDS and name not in source_rows
        assert 1 <= int(start) <= int(end) <= len((ROOT / TEST).read_text().splitlines())
        source_rows[name] = dict(startLine=int(start), endLine=int(end), descriptor='()V', testId=IDS[name])
    byte_methods = set()
    for line in class_lines[1:]:
        values = line.split('\t')
        if values[0] == 'CLASS':
            assert values == ['CLASS', 'protocol', TYPE.replace('.', '/'), Path(TEST).name, data.sha(new_class.read_bytes())]
        else:
            assert len(values) == 7 and values[:3] == ['TEST', 'protocol', TYPE.replace('.', '/')]
            assert values[4:] == ['()V', '0', 'org.junit.jupiter.api.Test']
            byte_methods.add(values[3])
    assert set(source_rows) == byte_methods == set(IDS)
    assert all(data.sha((ROOT / p).read_bytes()) == h for p, h in helpers.items())
    verify(invocation)
    OUT.mkdir()
    value = dict(actualExit=0, source=SOURCE, timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(), invocation=invocation,
        normalManifestSha256='f2ae182bb3a88eff78542ce0c18f3a497263aaabb7ed7fdbea5237a9ab467c2c',
        hostPostManifestSha256='d12d686512ce45599f7a9eaa89d03560a7c579aaa8c3e5036b9de2a641510959',
        staticV2ManifestSha256='41807eb5d29a989424939246359f8eb7f9162bd03c7fbc4d1f2bd8932546de08',
        helpers=helpers, readerStages=stages, methods=source_rows, staticInputClassCounts=static_counts,
        staticInputClasses=1843, oldStaticMissingClasses=18, newStaticMissingClasses=0,
        existingTestClassesSameBytes=1910, currentTestClasses=1911, currentMainSourceFiles=965,
        currentTestSourceFiles=825, currentJavaSourceFiles=1790, addedOrdinaryTestDeclarations=3,
        currentOrdinaryTestDeclarationCount=5625, declarationCountNotPassCount=True,
        newTestSourceSha256=hashes[TEST], normalTestClassSha256=data.sha(new_class.read_bytes()),
        declaredMainMethodUnderTest='PayloadSemanticValidator.validate', originalMainOwnerProof=subject[0],
        sourceOwnerCandidate=dict(path=TEST, canonicalOwner='WBS-P002-02', canonicalCostOwner='WBS-P002-02',
            basis='EXPLICIT_PROGRAM_SPEC_AND_ORIGINAL_MAIN_METHOD_SUBJECT_NOT_NAMESPACE_OR_REFERENCE_MAJORITY', masterRegistered=False),
        relatedMainReferences=references, reflectiveOrDynamicLookup=info['reflectiveOrDynamicLookup'],
        v1FailurePreserved=True, oldM2ArtifactsModified=False, rulesOrSuppressionChanged=False,
        actualTestsInOriginalRun=3, productTestsExecutedByThisPost=0, newTestIds=3, newMain=0,
        formalUpdated=False, newAccepted=0, coverageUnion=False, programPtComplete=False, whole451Accepted=False,
        effortPercent=None, currentWholeWbsAuditExecuted=False)
    data.write(OUT / 'manifest.json', value)
    print(json.dumps(dict(actualExit=0, newDeclaredMethods=3, currentTestClasses=1911, staticMainClasses=1843, missingClasses=0)))
    print('manifestSha256=' + data.sha((OUT / 'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
