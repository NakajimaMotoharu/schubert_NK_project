"""Independent SAX projection of pinned original XML, no Product or original test execution."""
from pathlib import Path
from xml.sax.handler import ContentHandler
import copy
import datetime
import hashlib
import io
import json
import xml.sax

B = Path('evidence/01_PT/018_NK-OPS-001')
C = B / 'input/605_pending12_method_coverage_scope.json'
P = B / 'evidence/PG23982-pending12-method-coverage-v1'
O = B / 'evidence/PG23984-pending12-method-coverage-independent-v1'
KINDS = ('INSTRUCTION', 'BRANCH', 'LINE', 'COMPLEXITY', 'METHOD', 'CLASS')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


class XmlClasses(ContentHandler):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.classes = {}
        self.current = None
        self.method = None

    def startElement(self, name, attributes):
        parent = self.stack[-1] if self.stack else None
        self.stack.append(name)
        if name == 'class' and parent == 'package':
            key = attributes['name']
            assert key not in self.classes
            self.current = dict(sourceFile=attributes['sourcefilename'], counters={}, methods={})
            self.classes[key] = self.current
            assert set(attributes.getNames()) == {'name', 'sourcefilename'}
        elif name == 'method' and parent == 'class':
            key = attributes['name'], attributes['desc']
            assert key not in self.current['methods']
            self.method = {}
            self.current['methods'][key] = self.method
        elif name == 'counter' and self.current is not None and parent in ('class', 'method'):
            target = self.method if parent == 'method' else self.current['counters']
            kind = attributes['type']
            assert kind in KINDS and kind not in target
            target[kind] = dict(covered=int(attributes['covered']), missed=int(attributes['missed']))

    def endElement(self, name):
        assert self.stack.pop() == name
        if name == 'method':
            self.method = None
        if name == 'class':
            self.current = None


def validate(rows, expected):
    assert type(rows) is list and rows == expected
    # Preserve null rather than treating natural-zero branch coverage as an observed 100%.
    for row in rows:
        assert row['branchRatio'] is None or type(row['branchRatio']) is float
        assert type(row['newAcceptance']) is int and row['newAcceptance'] == 0


class OriginalCases(ContentHandler):
    def __init__(self):
        super().__init__()
        self.cases = set()

    def startElement(self, name, attributes):
        assert name not in ('failure', 'error', 'skipped', 'aborted')
        if name == 'testsuite':
            assert all(int(attributes.get(k, '0')) == 0 for k in ('failures', 'errors', 'skipped'))
        if name == 'testcase':
            key = attributes['classname'] + '#' + attributes['name'].removesuffix('()')
            assert key not in self.cases
            self.cases.add(key)


def main():
    assert not O.exists()
    config = load(C)
    for name, digest in config['inputs'].items():
        assert sha(Path(name)) == digest
    supplement_path = B / 'input/610_pending12_original_junit_supplement.json'
    supplement = load(supplement_path)
    for name, digest in supplement['inputs'].items():
        assert sha(Path(name)) == digest
    manifest = load(P / 'manifest.json')
    matrix = load(P / 'source-method-coverage.json')
    assert sha(P / 'source-method-coverage.json') == manifest['files']['source-method-coverage.json']
    traces = load(Path(config['trace']))
    current = load(Path(config['currentMethodInventory']))
    # Explicit independent list: seven javac record methods and one synthetic switch initializer.
    record = 'dev/codex/schubert/nk/batch/mq/ArtemisAddressSettingsReadinessClient$Capacity'
    filtered = {(record, 'toString', '()Ljava/lang/String;'), (record, 'hashCode', '()I'),
                (record, 'equals', '(Ljava/lang/Object;)Z')}
    filtered |= {(record, n, '()J') for n in ('memoryMib', 'memoryMessages', 'pageMib', 'pageMessages')}
    filtered.add(('dev/codex/schubert/nk/api/bootstrap/ServiceDatabaseAdmission$1', '<clinit>', '()V'))
    expected = []
    all_cases = set()
    for trace in traces:
        proof_path = Path(trace['proof']['path'])
        proof = load(proof_path)
        assert sha(proof_path) == trace['proof']['sha256'] and proof['actualExit'] == 0
        assert proof['productionCoreMain'] == config['source']
        xml_path = proof_path.parent / 'original-coverage.xml'
        assert sha(xml_path) == proof['files']['original-coverage.xml']
        reader = xml.sax.make_parser()
        reader.setFeature(xml.sax.handler.feature_external_ges, False)
        reader.setFeature(xml.sax.handler.feature_external_pes, False)
        data = XmlClasses()
        reader.setContentHandler(data)
        reader.parse(io.BytesIO(xml_path.read_bytes()))
        members = [v for v in current if v['sourcePath'] == trace['mainPath']]
        names = {v['physicalKey'].split(':')[1][:-6] for v in members}
        assert names == set(trace['completeSourceFilePhysicalClasses'])
        junit_path = proof_path.parent / 'original-TEST-junit-jupiter.xml'
        assert sha(junit_path) == proof['files'][junit_path.name] == supplement['inputs'][str(junit_path)]
        case_reader = xml.sax.make_parser()
        case_reader.setFeature(xml.sax.handler.feature_external_ges, False)
        case_reader.setFeature(xml.sax.handler.feature_external_pes, False)
        case_handler = OriginalCases()
        case_reader.setContentHandler(case_handler)
        case_reader.parse(io.BytesIO(junit_path.read_bytes()))
        case_ids = case_handler.cases
        assert set(trace['executedCaseIds']) == case_ids
        all_cases.update(case_ids)
        physical = []
        for member in sorted(members, key=lambda v: v['physicalKey']):
            name = member['physicalKey'].split(':')[1][:-6]
            assert member['sourceSha256'] == trace['mainSha256']
            assert member['classSha256'] == proof['physical'][name] == trace['classHashes'][name]
            assert proof['classIds'][name] == trace['classIds'][name]
            source = data.classes[name]
            assert source['sourceFile'] == Path(trace['mainPath']).name
            normal = member['structure']['methods']
            report_methods = set(source['methods'])
            methods = []
            for method in normal:
                key = method['name'], method['descriptor']
                if method['hasCode'] is False:
                    assert key not in report_methods
                    status, counters, reason = 'ABSTRACT_NO_CODE', None, None
                elif (name, *key) in filtered:
                    assert key not in report_methods
                    status, counters = 'ORIGINAL_STANDARD_COMPILER_FILTER_NOT_CLAIMED_EXECUTED', None
                    reason = ('Original23238 standard record filter, original bytes retained' if name == record else
                              'Original23656 compiler synthetic switch table filter, original bytes retained')
                    assert ('7 generated methods' in proof.get('standardCompilerFilters', '') if name == record else
                            proof['automaticCompilerGeneratedFiltering'][0]['physicalClassRetained'] is True)
                else:
                    assert key in report_methods
                    status, counters, reason = 'MEASURED_IN_ORIGINAL_RUN', source['methods'][key], None
                    assert counters['METHOD'] == {'covered': 1, 'missed': 0}
                    assert all(v['missed'] == 0 for v in counters.values())
                methods.append(dict(name=key[0], descriptor=key[1], hasCode=method['hasCode'], coverageStatus=status,
                                    counters=counters, originalFilterReason=reason, exactPerMethodOracle='NOT_VERIFIED'))
            assert report_methods == {(v['name'], v['descriptor']) for v in methods if v['counters'] is not None}
            physical.append(dict(physicalKey=member['physicalKey'], classSha256=member['classSha256'],
                                 originalClassId=proof['classIds'][name], classIdProvenance='ORIGINAL_INDEPENDENT_POST_NOT_XML',
                                 counters=source['counters'], methods=methods))
        total = {kind: {'covered': 0, 'missed': 0} for kind in KINDS}
        for child in physical:
            for kind, numbers in child['counters'].items():
                for k in ('covered', 'missed'):
                    total[kind][k] += numbers[k]
        nonzero_branch = sum(total['BRANCH'].values()) != 0
        expected.append(dict(sourcePath=trace['mainPath'], sourceSha256=trace['mainSha256'], canonicalOwner=trace['canonicalOwner'],
                             originalProof=trace['proof'], originalRunSource=trace['runSource'], currentProductionCoreMain=config['source'],
                             originalXml={'path': str(xml_path), 'sha256': sha(xml_path)}, physical=physical, perSourceCounters=total,
                             branchStatus='MEASURED' if nonzero_branch else 'NATURAL_ZERO_NOT_APPLICABLE',
                             branchRatio=1.0 if nonzero_branch else None, runCaseRefs=trace['executedCaseIds'],
                             exactPerMethodOracle='NOT_VERIFIED', wholeDependencyAccepted=False, whole451Accepted=False, newAcceptance=0))
    validate(matrix, expected)
    assert len(all_cases) == 96
    mutations = []
    for label, fn in [
        ('missing-source', lambda r: r.pop()), ('duplicate-source', lambda r: r.append(copy.deepcopy(r[0]))),
        ('wrong-source-sha', lambda r: r[0].update(sourceSha256='0' * 64)),
        ('wrong-class-sha', lambda r: r[0]['physical'][0].update(classSha256='0' * 64)),
        ('wrong-class-id', lambda r: r[0]['physical'][0].update(originalClassId='0' * 16)),
        ('xml-id-provenance', lambda r: r[0]['physical'][0].update(classIdProvenance='XML_ID')),
        ('missing-method', lambda r: r[0]['physical'][0]['methods'].pop()),
        ('wrong-descriptor', lambda r: r[0]['physical'][0]['methods'][0].update(descriptor='()Vbad')),
        ('missed-line', lambda r: r[0]['perSourceCounters']['LINE'].update(missed=1)),
        ('group-counter-as-source', lambda r: r[2]['perSourceCounters']['METHOD'].update(covered=4)),
        ('zero-branch-false100', lambda r: r[2].update(branchRatio=1.0)),
        ('method-oracle-inferred', lambda r: r[0]['physical'][0]['methods'][0].update(exactPerMethodOracle='VERIFIED')),
        ('dependency-inferred', lambda r: r[0].update(wholeDependencyAccepted=True)),
        ('acceptance-inferred', lambda r: r[0].update(newAcceptance=1)),
        ('missing-run-case', lambda r: r[0]['runCaseRefs'].pop()),
    ]:
        value = copy.deepcopy(matrix)
        fn(value)
        try:
            validate(value, expected)
        except AssertionError:
            mutations.append(label)
        else:
            raise AssertionError('mutation accepted: ' + label)
    O.mkdir()
    totals = {k: manifest[k] for k in ('sourcePrograms', 'physicalClasses', 'knownMethodMetadata', 'measuredCodeMethods',
                                    'originalCompilerFilteredCodeMethods', 'abstractNoCodeMethods', 'naturalZeroBranchSources',
                                    'originalIndependentProofGroups', 'existingUniqueRunCaseIds')}
    result = dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(), source=config['source'], **totals,
                  producerManifest={'path': str(P / 'manifest.json'), 'sha256': sha(P / 'manifest.json')},
                  independentParser='SAX_NO_EXTERNAL_ENTITIES', metadataNegativeChecks=mutations,
                  productTestsExecuted=0, newUniqueTests=0, compilerOrJvmExecuted=False, actualBackendActions=0,
                  xmlIdFieldAssumed=False, wholeMethodOracleTraceAccepted=False, wholeDependencyAccepted=False,
                  registeredComponentDelta=None, newAcceptance=0, formalUpdated=False, effortRate=None,
                  bugs=['BUG-2514', 'BUG-2515'], ykts=['YKT-2252', 'YKT-2253'],
                  junitSupplement={'path': str(supplement_path), 'sha256': sha(supplement_path)},
                  verifier={'path': str(Path(__file__)), 'sha256': sha(Path(__file__))})
    (O / 'manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(actualExit=0, **totals, negatives=len(mutations), manifestSha256=sha(O / 'manifest.json'))))


if __name__ == '__main__':
    main()
