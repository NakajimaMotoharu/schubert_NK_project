"""Relate existing measured XML to current class metadata, without execution or oracle inference."""
from pathlib import Path
import datetime
import hashlib
import json
import xml.etree.ElementTree as ET

R = Path.cwd()
B = Path('evidence/01_PT/018_NK-OPS-001')
C = B / 'input/605_pending12_method_coverage_scope.json'
O = B / 'evidence/PG23982-pending12-method-coverage-v1'
COUNTERS = ('INSTRUCTION', 'BRANCH', 'LINE', 'COMPLEXITY', 'METHOD', 'CLASS')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def counters(element):
    result = {}
    for c in element.findall('counter'):
        kind = c.attrib['type']
        assert kind in COUNTERS and kind not in result
        result[kind] = dict(covered=int(c.attrib['covered']), missed=int(c.attrib['missed']))
        assert min(result[kind].values()) >= 0
    return result


def filter_reason(name, method, config):
    for rule in config['compilerFilteredMethods']:
        if name.rsplit('/', 1)[-1] == rule['classSuffix'] and method['name'] in rule['names']:
            return rule['reason']
    return None


def main():
    assert not O.exists()
    cfg = load(C)
    for name, digest in cfg['inputs'].items():
        assert sha(R / name) == digest, name
    traces = load(Path(cfg['trace']))
    current = load(Path(cfg['currentMethodInventory']))
    assert len(traces) == 12 and len(current) == 1845
    by_source = {}
    for row in current:
        by_source.setdefault(row['sourcePath'], []).append(row)
    result = []
    for trace in traces:
        proof_path = Path(trace['proof']['path'])
        proof = load(proof_path)
        assert sha(proof_path) == trace['proof']['sha256']
        assert proof['actualExit'] == 0 and proof['productionCoreMain'] == cfg['source']
        assert proof['manualCoverageExclusions'] == [] and proof['oldExecCombined'] is False
        xml_path = proof_path.parent / 'original-coverage.xml'
        assert sha(xml_path) == proof['files'][xml_path.name]
        root = ET.fromstring(xml_path.read_bytes())
        classes = {x.attrib['name']: x for x in root.findall('./package/class')}
        source_rows = by_source[trace['mainPath']]
        module = trace['mainPath'].split('/')[1].removeprefix('schubert-nk-')
        expected = set(trace['completeSourceFilePhysicalClasses'])
        assert {x['physicalKey'].split(':', 1)[1].removesuffix('.class') for x in source_rows} == expected
        physical = []
        for row in sorted(source_rows, key=lambda x: x['physicalKey']):
            assert row['sourceSha256'] == trace['mainSha256'] and row['structure'] is not None
            key, entry = row['physicalKey'].split(':', 1)
            name = entry.removesuffix('.class')
            assert key == module and row['classSha256'] == trace['classHashes'][name]
            element = classes[name]
            assert element.attrib['sourcefilename'] == Path(trace['mainPath']).name
            # JaCoCo XML has name/sourcefilename, never the exec/classinfo class ID.
            assert trace['classIds'][name] == proof['classIds'][name]
            observed = {(x.attrib['name'], x.attrib['desc']): x for x in element.findall('method')}
            assert len(observed) == len(element.findall('method'))
            methods = []
            for method in row['structure']['methods']:
                identity = method['name'], method['descriptor']
                actual = observed.pop(identity, None)
                reason = filter_reason(name, method, cfg)
                if not method['hasCode']:
                    assert actual is None and reason is None
                    status = 'ABSTRACT_NO_CODE'
                elif actual is not None:
                    assert reason is None
                    status = 'MEASURED_IN_ORIGINAL_RUN'
                else:
                    assert reason is not None
                    status = 'ORIGINAL_STANDARD_COMPILER_FILTER_NOT_CLAIMED_EXECUTED'
                method_counters = counters(actual) if actual is not None else None
                if method_counters is not None:
                    assert method_counters['METHOD'] == dict(covered=1, missed=0)
                    assert all(v['missed'] == 0 for v in method_counters.values())
                methods.append(dict(name=method['name'], descriptor=method['descriptor'],
                                    hasCode=method['hasCode'], coverageStatus=status,
                                    counters=method_counters, originalFilterReason=reason,
                                    exactPerMethodOracle='NOT_VERIFIED'))
            assert not observed
            physical.append(dict(physicalKey=row['physicalKey'], classSha256=row['classSha256'],
                                 originalClassId=proof['classIds'][name],
                                 classIdProvenance='ORIGINAL_INDEPENDENT_POST_NOT_XML',
                                 counters=counters(element), methods=methods))
        total = {kind: dict(covered=sum(x['counters'].get(kind, {}).get('covered', 0) for x in physical),
                                 missed=sum(x['counters'].get(kind, {}).get('missed', 0) for x in physical))
                 for kind in COUNTERS}
        assert all(v['missed'] == 0 for v in total.values())
        assert total['LINE']['covered'] > 0 and total['METHOD']['covered'] > 0
        branch = total['BRANCH']['covered'] + total['BRANCH']['missed']
        result.append(dict(sourcePath=trace['mainPath'], sourceSha256=trace['mainSha256'],
                           canonicalOwner=trace['canonicalOwner'], originalProof=trace['proof'],
                           originalRunSource=trace['runSource'], currentProductionCoreMain=cfg['source'],
                           originalXml=dict(path=str(xml_path), sha256=sha(xml_path)), physical=physical,
                           perSourceCounters=total, branchStatus='MEASURED' if branch else 'NATURAL_ZERO_NOT_APPLICABLE',
                           branchRatio=1.0 if branch else None,
                           runCaseRefs=trace['executedCaseIds'], exactPerMethodOracle='NOT_VERIFIED',
                           wholeDependencyAccepted=False, whole451Accepted=False, newAcceptance=0))
    flat = [m for row in result for physical in row['physical'] for m in physical['methods']]
    summary = dict(sourcePrograms=len(result), physicalClasses=sum(len(x['physical']) for x in result),
                   knownMethodMetadata=len(flat), measuredCodeMethods=sum(x['coverageStatus'] == 'MEASURED_IN_ORIGINAL_RUN' for x in flat),
                   originalCompilerFilteredCodeMethods=sum(x['coverageStatus'].startswith('ORIGINAL_STANDARD') for x in flat),
                   abstractNoCodeMethods=sum(not x['hasCode'] for x in flat),
                   naturalZeroBranchSources=sum(x['branchRatio'] is None for x in result),
                   originalIndependentProofGroups=len({x['originalProof']['path'] for x in result}),
                   existingUniqueRunCaseIds=len({v for row in result for v in row['runCaseRefs']}))
    assert summary['physicalClasses'] == 17 and summary['originalCompilerFilteredCodeMethods'] == 8
    assert summary['existingUniqueRunCaseIds'] == 96
    O.mkdir()
    write(O / 'source-method-coverage.json', result)
    write(O / 'manifest.json', dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(),
          source=cfg['source'], config=dict(path=str(C), sha256=sha(C)), **summary,
          productTestsExecuted=0, newUniqueTests=0, compilerOrJvmExecuted=False, actualBackendActions=0,
          wholeMethodOracleTraceAccepted=False, wholeDependencyAccepted=False, registeredComponentDelta=None,
          oldExecCombined=False, manualCoverageExclusions=[], newAcceptance=0, formalUpdated=False, effortRate=None,
          files={'source-method-coverage.json': sha(O / 'source-method-coverage.json')},
          tool=dict(path=str(Path(__file__)), sha256=sha(Path(__file__)))))
    print(json.dumps(dict(actualExit=0, **summary, manifestSha256=sha(O / 'manifest.json'))))


if __name__ == '__main__':
    main()
