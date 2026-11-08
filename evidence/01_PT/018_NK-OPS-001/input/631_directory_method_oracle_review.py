"""Validate frozen manual unsupported-default policy links, using public source and existing success only."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

B = Path('evidence/01_PT/018_NK-OPS-001')
C = B / 'input/629_directory_three_method_oracle_scope.json'
O = B / 'evidence/PG24062-directory-three-method-oracle-review-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def main_no_fallback(path):
    text = Path(path).read_text()
    return text.count('throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);') == 3


def main():
    assert not O.exists()
    c = load(C)
    for path, pin in c['inputs'].items():
        assert sha(Path(path)) == pin
    for ref in c['designRefs']:
        raw = subprocess.check_output(['git', 'show', ref['source'] + ':' + ref['path']])
        assert hashlib.sha256(raw).hexdigest() == ref['sha256']
    source = next(v for v in load(Path(c['methodInventory'])) if v['sourcePath'] == c['mainPath'])
    proof = load(Path(c['originalIndependentPost']))
    trace = next(v for v in load(Path(c['sourceTrace'])) if v['mainPath'] == c['mainPath'])
    assert source['sourceSha256'] == sha(Path(c['mainPath'])) == trace['mainSha256']
    name = source['physicalKey'].split(':')[1].removesuffix('.class')
    assert source['classSha256'] == proof['physical'][name] == trace['classHashes'][name]
    assert proof['actualExit'] == 0 and proof['tests'] == 4
    assert proof['productionCoreMain'] == c['source'] and proof['wholeDependencyQualified'] is False
    assert sha(Path(c['testPath'])) == proof['inputHashes'][c['testPath']]
    expected = {(v['name'], v['descriptor']) for v in source['structure']['methods'] if v['hasCode']}
    assert len(expected) == len(c['methods']) == 3
    assert {(v['method'], v['descriptor']) for v in c['methods']} == expected
    assert sum(v['hasCode'] for v in source['structure']['methods']) == 3
    assert sum(not v['hasCode'] for v in source['structure']['methods']) == 9
    text = Path(c['testPath']).read_text()
    case_refs = set(trace['executedCaseIds'])
    assert len(case_refs) == len(c['oracles']) == 4
    assert {v['runCase'] for v in c['oracles']} == case_refs
    assertions = []
    for row in c['oracles']:
        method = row['runCase'].split('#')[1].removesuffix('()')
        marker = 'void ' + method + '('
        assert text.count(marker) == 1
        start = text.index(marker)
        end = text.find('\n  @Test', start)
        body = text[start:end] if end >= 0 else text[start:text.index('\n  private static void assertFailure(')]
        assert all(token in body for token in row['assertionTokens']), row['testId']
        assertions.append(dict(testId=row['testId'], caseRef=row['runCase'],
                               declarationLine=text[:start].count('\n') + 1,
                               snippets=len(row['assertionTokens']), independentExpected=row['expected']))
    ids = {v['testId'] for v in c['oracles']}
    rows = []
    for row in c['methods']:
        assert set(row['testIds']) <= ids and set(row['runCases']) <= case_refs
        assert {v['runCase'] for v in c['oracles'] if v['testId'] in row['testIds']} == set(row['runCases'])
        rows.append(dict(**row, sourcePath=c['mainPath'], sourceSha256=source['sourceSha256'],
                         classSha256=source['classSha256'], requirementIds=c['requirementIds'],
                         uiRefs=c['ui'], ssRefs=c['designRefs'], remaining=c['remaining'],
                         reviewStatus='EXPLICIT_DEFAULT_METHOD_ORACLE_LINK_WITH_STATED_LIMITS',
                         exactAllMethodCasesOrOracleComplete=False, wholeDependencyAccepted=False))
    helper_start = text.index('  private static void assertFailure(')
    helper_end = text.index('\n  /**', helper_start)
    helper = text[helper_start:helper_end]
    for token in ['StorageIoException.Reason.UNAVAILABLE', 'FIXED_MESSAGE, failure.getMessage()', 'assertNull(failure.getCause())', 'assertEquals(0, failure.getSuppressed().length)', 'StorageIoException.class, failure.getClass()']:
        assert token in helper
    assert main_no_fallback(c['mainPath'])
    O.mkdir()
    target = O / 'method-oracle-relations.json'
    target.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    result = dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(), source=c['source'],
                  config={'path': str(C), 'sha256': sha(C)}, sourcePrograms=1, explicitlyRelatedMethods=3,
                  originalSuccessfulTestCases=4, assertionSnippetChecks=sum(v['snippets'] for v in assertions),
                  assertionReviews=assertions, unsupportedDefaultsDoNotFallback=True,
                  actualNativeQualified=False, abstractNoCodeMethodsQualified=False,
                  exactAllMethodCasesOrOracleComplete=False, originalRunRepeated=False, productTestsExecuted=0,
                  newUniqueTests=0, compilerOrJvmExecuted=False, actualBackendActions=0,
                  wholeDependencyAccepted=False, wholeG13Accepted=False, whole451Accepted=False,
                  newAcceptance=0, formalUpdated=False, effortRate=None,
                  files={target.name: sha(target)}, tool={'path': str(Path(__file__)), 'sha256': sha(Path(__file__))})
    (O / 'manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(actualExit=0, explicitlyRelatedMethods=3, assertionSnippetChecks=result['assertionSnippetChecks'],
                         unsupportedDefaultsDoNotFallback=True, manifestSha256=sha(O / 'manifest.json'))))


if __name__ == '__main__':
    main()
