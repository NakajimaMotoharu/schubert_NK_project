"""Relate two hand-written projection matrices to existing source/run-level metadata only."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

B = Path('evidence/01_PT/018_NK-OPS-001')
C = B / 'input/633_broker_projection_seventeen_method_scope.json'
O = B / 'evidence/PG24082-broker-projection-seventeen-method-review-v1'


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
        assert proof['actualExit'] == 0 and proof['tests'] == len(subject['oracles'])
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
        assert {v['runCase'] for v in subject['oracles']} == cases
        text = Path(subject['testPath']).read_text()
        for oracle in subject['oracles']:
            name = oracle['runCase'].split('#')[1].removesuffix('()')
            marker = 'void ' + name + '('
            assert text.count(marker) == 1
            start = text.index(marker)
            end = text.find('\n  @Test', start)
            if end < 0:
                end = text.index('\n  private static Map<', start)
            body = text[start:end]
            assert all(token in body for token in oracle['assertionTokens']), oracle['testId']
            assertion_reviews.append(dict(testId=oracle['testId'], caseRef=oracle['runCase'],
                                          declarationLine=text[:start].count('\n') + 1,
                                          snippets=len(oracle['assertionTokens']), independentExpected=oracle['expected']))
        # The provided session is an all-method rejecting memory interface, not a live connection.
        assert 'private static ClientSession unusedSession()' in text
        assert 'throw new AssertionError("borrowed session must remain untouched");' in text
        ids = {v['testId'] for v in subject['oracles']}
        for method in subject['methods']:
            assert set(method['testIds']) <= ids and set(method['runCases']) <= cases
            assert {v['runCase'] for v in subject['oracles'] if v['testId'] in method['testIds']} == set(method['runCases'])
            item = by_name[method['className']]
            result.append(dict(**method, sourcePath=subject['mainPath'], sourceSha256=item['sourceSha256'],
                               classSha256=item['classSha256'], canonicalOwner=subject['canonicalOwner'],
                               requirementIds=c['requirementIds'], uiRefs=c['ui'], ssRefs=c['designRefs'],
                               remaining=c['remaining'], exactAllMethodCasesOrOracleComplete=False,
                               reviewStatus='EXPLICIT_PROJECTION_METHOD_ORACLE_LINK_WITH_STATED_LIMITS',
                               actualBrokerOrManagementReaderQualified=False))
        limits.append(dict(sourcePath=subject['mainPath'], measuredMethodLinks=len(measured),
                           originalCompilerFilteredMethodsNotIndependentlyMeasured=filtered,
                           abstractReaderMethodsWithoutCode=abstract, defaultManagementReaderInvocationQualified=False))
    assert len(result) == 17 and len(assertion_reviews) == 9
    O.mkdir()
    target = O / 'method-oracle-relations.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    output = dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(), source=c['source'],
                  config={'path': str(C), 'sha256': sha(C)}, sourcePrograms=2, explicitlyRelatedMethods=17,
                  originalSuccessfulTestCases=9, assertionSnippetChecks=sum(v['snippets'] for v in assertion_reviews),
                  originalCompilerFilteredMethodsNotIndependentlyMeasured=7, abstractReaderMethodsWithoutCode=2,
                  subjectLimits=limits, assertionReviews=assertion_reviews, originalRunRepeated=False,
                  actualBrokerOrManagementReaderQualified=False, classInitFirstCaseKnown=False,
                  exactAllMethodCasesOrOracleComplete=False, productTestsExecuted=0, newUniqueTests=0,
                  compilerOrJvmExecuted=False, actualBackendActions=0, wholeG13Accepted=False,
                  whole451Accepted=False, newAcceptance=0, formalUpdated=False, effortRate=None,
                  files={target.name: sha(target)}, tool={'path': str(Path(__file__)), 'sha256': sha(Path(__file__))})
    (O / 'manifest.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(actualExit=0, explicitlyRelatedMethods=17, originalCases=9,
                         assertionSnippetChecks=output['assertionSnippetChecks'], manifestSha256=sha(O / 'manifest.json'))))


if __name__ == '__main__':
    main()
