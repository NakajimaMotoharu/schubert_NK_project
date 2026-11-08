"""Check a hand-reviewed six-method contract matrix against pinned public evidence only."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

B = Path('evidence/01_PT/018_NK-OPS-001')
C = B / 'input/617_listener_six_method_oracle_scope.json'
O = B / 'evidence/PG24022-listener-six-method-oracle-review-v1'


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
        content = subprocess.check_output(['git', 'show', ref['source'] + ':' + ref['path']])
        assert hashlib.sha256(content).hexdigest() == ref['sha256']
    inventory = load(Path(c['methodInventory']))
    proof = load(Path(c['originalIndependentPost']))
    assert proof['actualExit'] == 0 and proof['tests'] == 6
    assert proof['productionCoreMain'] == c['source'] and proof['wholeDelegateQualified'] is False
    assert proof['branchStatus'] == 'NATURAL_ZERO_NOT_APPLICABLE_RATIO_NULL'
    assert proof['branchRatio'] is None
    cases = {v['className'] + '#' + v['name'] for v in proof['caseTimings']}
    text = Path(c['testPath']).read_text()
    assert len(c['oracles']) == len(c['methods']) == 6
    assertions = []
    for row in c['oracles']:
        assert row['runCase'] in cases
        method_name = row['runCase'].split('#')[1].removesuffix('()')
        marker = 'void ' + method_name + '('
        assert text.count(marker) == 1
        start = text.index(marker)
        end = text.find('\n  @Test', start)
        body = text[start:end] if end >= 0 else text[start:text.index('\n  private static void assertEvent')]
        for token in row['assertionTokens']:
            assert token in body, (row['testId'], token)
        assertions.append(dict(testId=row['testId'], caseRef=row['runCase'],
                               declarationLine=text[:start].count('\n') + 1,
                               explicitlyCheckedAssertionSnippets=len(row['assertionTokens']),
                               independentExpected=row['expected']))
    result = []
    ids = {v['testId'] for v in c['oracles']}
    for path in sorted({v['sourcePath'] for v in c['methods']}):
        current = [v for v in inventory if v['sourcePath'] == path]
        assert len(current) == 1 and current[0]['structure'] is not None
        class_name = current[0]['physicalKey'].split(':')[1].removesuffix('.class')
        expected = {(v['name'], v['descriptor']) for v in current[0]['structure']['methods']}
        selected = [v for v in c['methods'] if v['sourcePath'] == path]
        assert len(expected) == len(selected) == 3
        assert {(v['method'], v['descriptor']) for v in selected} == expected
        assert current[0]['classSha256'] == proof['physical'][class_name]
        main = Path(path).read_text()
        assert main.count('delegate.onMessage(context, message);') == 1
        assert main.count('delegate.onMessage(context, message, attempted, confirmed);') == 1
        route = 'ASYNC_WORK' if 'QuestionWorkListener' in path else 'WEB_LOG'
        detected_by = 'API_WORK' if route == 'ASYNC_WORK' else 'API_WEB_LOG'
        assert 'BrokerTopology.' + route in main and 'FatalDlqMetadata.DetectedBy.' + detected_by in main
        for row in selected:
            assert row['className'] == class_name and set(row['testIds']) <= ids
            assert set(row['runCases']) <= cases and row['unverified']
            result.append(dict(**row, sourceSha256=current[0]['sourceSha256'], classSha256=current[0]['classSha256'],
                               requirementIds=c['requirementIds'], uiRefs=c['ui'], ssRefs=c['designRefs'],
                               exactAllMethodCasesOrOracleComplete=False, methodLinkAcceptedAsFullPT=False))
    O.mkdir()
    matrix = O / 'method-oracle-relations.json'
    matrix.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    output = dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(), source=c['source'],
                  config={'path': str(C), 'sha256': sha(C)}, sourcePrograms=2, explicitlyRelatedMethods=6,
                  originalSuccessfulTestCases=6, assertionSnippetChecks=sum(v['explicitlyCheckedAssertionSnippets'] for v in assertions),
                  assertionReviews=assertions, methodOracleObservationScope='WRAPPER_CONTRACT_ONLY_WITH_STATED_LIMITS',
                  exactAllMethodCasesOrOracleComplete=False, originalBranchRatio=None,
                  originalRunRepeated=False, productTestsExecuted=0, newUniqueTests=0, compilerOrJvmExecuted=False,
                  actualBackendActions=0, wholeDelegateAccepted=False, wholeG13Accepted=False, whole451Accepted=False,
                  newAcceptance=0, formalUpdated=False, effortRate=None,
                  files={matrix.name: sha(matrix)}, tool={'path': str(Path(__file__)), 'sha256': sha(Path(__file__))})
    (O / 'manifest.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(actualExit=0, sourcePrograms=2, explicitlyRelatedMethods=6,
                         assertionSnippetChecks=output['assertionSnippetChecks'], manifestSha256=sha(O / 'manifest.json'))))


if __name__ == '__main__':
    main()
