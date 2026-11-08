"""Relate three hand-written pool/metric matrices to existing source/run-level metadata only."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

B = Path('evidence/01_PT/018_NK-OPS-001')
C = B / 'input/637_pool_webmetric_ten_method_scope.json'
O = B / 'evidence/PG24102-pool-webmetric-ten-method-review-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def main():
    assert not O.exists()
    c = load(C)
    for path, pin in c['inputs'].items():
        assert sha(Path(path)) == pin
    for ref in c['designRefs']:
        raw = subprocess.check_output(['git', 'show', ref['source'] + ':' + ref['path']])
        assert hashlib.sha256(raw).hexdigest() == ref['sha256']
    current = load(Path(c['methodInventory']))
    coverage = load(Path(c['perSourceCoverage']))
    traces = load(Path(c['sourceTrace']))
    result, assertion_reviews, limits = [], [], []
    for subject in c['subjects']:
        proof = load(Path(subject['originalIndependentPost']))
        trace = next(v for v in traces if v['mainPath'] == subject['mainPath'])
        source_coverage = next(v for v in coverage if v['sourcePath'] == subject['mainPath'])
        assert proof['actualExit'] == 0 and proof['tests'] == subject['originalRunCaseCount']
        assert proof['productionCoreMain'] == c['source'] and proof['whole451Accepted'] is False
        assert trace['canonicalOwner'] == subject['canonicalOwner']
        assert sha(Path(subject['testPath'])) == proof['inputHashes'][subject['testPath']]
        physical = [v for v in current if v['sourcePath'] == subject['mainPath']]
        by_name = {v['physicalKey'].split(':')[1].removesuffix('.class'): v for v in physical}
        assert set(by_name) == set(trace['completeSourceFilePhysicalClasses'])
        for name, item in by_name.items():
            assert item['sourceSha256'] == sha(Path(subject['mainPath'])) == trace['mainSha256']
            assert item['classSha256'] == proof['physical'][name] == trace['classHashes'][name]
        measured = set()
        filtered = abstract = 0
        for record in source_coverage['physical']:
            name = record['physicalKey'].split(':')[1].removesuffix('.class')
            for method in record['methods']:
                status = method['coverageStatus']
                if status == 'MEASURED_IN_ORIGINAL_RUN':
                    measured.add((name, method['name'], method['descriptor']))
                elif status == 'ABSTRACT_NO_CODE':
                    abstract += 1
                else:
                    assert status == 'ORIGINAL_STANDARD_COMPILER_FILTER_NOT_CLAIMED_EXECUTED'
                    filtered += 1
        assert len(measured) == len(subject['methods']) == subject['measuredMethods']
        assert filtered == subject['filteredMethods'] and abstract == subject['abstractNoCodeMethods']
        assert {(v['className'], v['method'], v['descriptor']) for v in subject['methods']} == measured
        cases = set(trace['executedCaseIds'])
        assert {v['runCase'] for v in subject['oracles']} <= cases
        assert len(cases) == subject['originalRunCaseCount']
        text = Path(subject['testPath']).read_text()
        for oracle in subject['oracles']:
            name = oracle['runCase'].split('#')[1].removesuffix('()')
            marker = 'void ' + name + '('
            assert text.count(marker) == 1
            start = text.index(marker)
            end = text.find('\n  @Test', start)
            if end < 0:
                end = text.index(subject['finalCaseBoundary'], start) if subject['finalCaseBoundary'] is not None else len(text)
            body = text[start:end]
            assert all(token in body for token in oracle['assertionTokens']), oracle['testId']
            assertion_reviews.append(dict(testId=oracle['testId'], caseRef=oracle['runCase'],
                                          declarationLine=text[:start].count('\n') + 1,
                                          snippets=len(oracle['assertionTokens']), independentExpected=oracle['expected']))
        if 'WebServiceMetricBinding.java' in subject['mainPath']:
            assert subject['notRunTestIds'] == ['WEBSERVICE009']
            assert not any('webservice009' in x for x in cases)
            assert proof['wholeOriginal22Accepted'] is False
            assert len(subject['testInputPaths']) == 2
        ids = {v['testId'] for v in subject['oracles']}
        for method in subject['methods']:
            assert set(method['testIds']) <= ids and set(method['runCases']) <= cases
            assert {v['runCase'] for v in subject['oracles'] if v['testId'] in method['testIds']} == set(method['runCases'])
            item = by_name[method['className']]
            result.append(dict(**method, sourcePath=subject['mainPath'], sourceSha256=item['sourceSha256'],
                               classSha256=item['classSha256'], canonicalOwner=subject['canonicalOwner'],
                               requirementIds=c['requirementIds'], uiRefs=c['ui'], ssRefs=c['designRefs'],
                               remaining=c['remaining'], exactAllMethodCasesOrOracleComplete=False,
                               reviewStatus='EXPLICIT_POOL_OR_METRIC_METHOD_ORACLE_LINK_WITH_STATED_LIMITS',
                               actualDatabaseOrLiveHttpQualified=False))
        limits.append(dict(sourcePath=subject['mainPath'], measuredMethodLinks=len(measured),
                           originalCompilerFilteredMethodsNotIndependentlyMeasured=filtered,
                           abstractReaderMethodsWithoutCode=abstract, actualDatabaseOrLiveHttpQualified=False))
    assert len(result) == 10 and len(assertion_reviews) == 23
    O.mkdir()
    target = O / 'method-oracle-relations.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    output = dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(), source=c['source'],
                  config={'path': str(C), 'sha256': sha(C)}, sourcePrograms=3, explicitlyRelatedMethods=10,
                  originalSuccessfulTestCases=23, assertionSnippetChecks=sum(v['snippets'] for v in assertion_reviews),
                  originalCompilerFilteredMethodsNotIndependentlyMeasured=0, abstractReaderMethodsWithoutCode=0,
                  subjectLimits=limits, assertionReviews=assertion_reviews, originalRunRepeated=False,
                  actualDatabaseOrLiveHttpQualified=False, caseSpecificCoverageMeasured=False,
                  exactAllMethodCasesOrOracleComplete=False, productTestsExecuted=0, newUniqueTests=0,
                  compilerOrJvmExecuted=False, actualBackendActions=0, wholeG13Accepted=False,
                  whole451Accepted=False, newAcceptance=0, formalUpdated=False, effortRate=None,
                  files={target.name: sha(target)}, tool={'path': str(Path(__file__)), 'sha256': sha(Path(__file__))})
    (O / 'manifest.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(actualExit=0, explicitlyRelatedMethods=10, originalCases=23,
                         assertionSnippetChecks=output['assertionSnippetChecks'], manifestSha256=sha(O / 'manifest.json'))))


if __name__ == '__main__':
    main()
