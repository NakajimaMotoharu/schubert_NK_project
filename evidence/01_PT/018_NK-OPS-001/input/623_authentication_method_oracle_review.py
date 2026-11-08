"""Validate frozen manual consumer-policy links, using public source and existing success only."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

B = Path('evidence/01_PT/018_NK-OPS-001')
C = B / 'input/621_authentication_five_method_oracle_scope.json'
O = B / 'evidence/PG24032-authentication-five-method-oracle-review-v1'


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
    source = next(v for v in load(Path(c['methodInventory'])) if v['sourcePath'] == c['mainPath'])
    proof = load(Path(c['originalIndependentPost']))
    trace = next(v for v in load(Path(c['sourceTrace'])) if v['mainPath'] == c['mainPath'])
    assert source['sourceSha256'] == sha(Path(c['mainPath'])) == trace['mainSha256']
    name = source['physicalKey'].split(':')[1].removesuffix('.class')
    assert source['classSha256'] == proof['physical'][name] == trace['classHashes'][name]
    assert proof['actualExit'] == 0 and proof['tests'] == 16
    assert proof['productionCoreMain'] == c['source'] and proof['wholeDependencyQualified'] is False
    assert sha(Path(c['testPath'])) == proof['inputHashes'][c['testPath']]
    expected = {(v['name'], v['descriptor']) for v in source['structure']['methods']}
    assert len(expected) == len(c['methods']) == 5
    assert {(v['method'], v['descriptor']) for v in c['methods']} == expected
    assert all(v['hasCode'] for v in source['structure']['methods'])
    text = Path(c['testPath']).read_text()
    case_refs = set(trace['executedCaseIds'])
    assert len(case_refs) == len(c['oracles']) == 16
    assert {v['runCase'] for v in c['oracles']} == case_refs
    assertions = []
    for row in c['oracles']:
        method = row['runCase'].split('#')[1].removesuffix('()')
        marker = 'void ' + method + '('
        assert text.count(marker) == 1
        start = text.index(marker)
        end = text.find('\n  @Test', start)
        body = text[start:end] if end >= 0 else text[start:text.index('\n  private static void expectStorageFailure')]
        assert all(token in body for token in row['assertionTokens']), row['testId']
        assert 'verifyReleasedAndConsumed();' in body
        assertions.append(dict(testId=row['testId'], caseRef=row['runCase'],
                               declarationLine=text[:start].count('\n') + 1,
                               snippets=len(row['assertionTokens']), independentExpected=row['expected']))
    helper_start = text.index('    void verifyReleasedAndConsumed()')
    helper = text[helper_start:text.index('\n    @Override', helper_start)]
    assert 'assertArrayEquals(new char[16], password);' in helper
    assert 'assertEquals(1, statement.closed);' in helper and 'assertEquals(1, cursor.closed);' in helper
    assert 'codec.close()' not in helper and 'Arrays.fill' not in helper
    # The assertions observe consumption before Fixture.close() performs its own cleanup.
    main_source = Path(c['mainPath']).read_text()
    assert "Arrays.fill(password, '\\0');" in main_source
    assert main_source.index('Objects.requireNonNull(password, "password");') < main_source.index('    try {')
    assert main_source.index('    } finally {') < main_source.index("Arrays.fill(password, '\\0');")
    ids = {v['testId'] for v in c['oracles']}
    rows = []
    for row in c['methods']:
        assert set(row['testIds']) <= ids and set(row['runCases']) <= case_refs
        assert {v['runCase'] for v in c['oracles'] if v['testId'] in row['testIds']} == set(row['runCases'])
        rows.append(dict(**row, sourcePath=c['mainPath'], sourceSha256=source['sourceSha256'],
                         classSha256=source['classSha256'], requirementIds=c['requirementIds'],
                         uiRefs=c['ui'], ssRefs=c['designRefs'], remaining=c['remaining'],
                         reviewStatus='EXPLICIT_CONSUMER_METHOD_ORACLE_LINK_WITH_STATED_LIMITS',
                         exactAllMethodCasesOrOracleComplete=False, wholeDependencyAccepted=False))
    O.mkdir()
    target = O / 'method-oracle-relations.json'
    target.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    result = dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(), source=c['source'],
                  config={'path': str(C), 'sha256': sha(C)}, sourcePrograms=1, explicitlyRelatedMethods=5,
                  originalSuccessfulTestCases=16, assertionSnippetChecks=sum(v['snippets'] for v in assertions),
                  assertionReviews=assertions, consumptionObservedBeforeFixtureCleanup=True,
                  publicDefaultMatcherActualMatchingQualified=False, sameRowDatabaseConcurrencyQualified=False,
                  exactAllMethodCasesOrOracleComplete=False, originalRunRepeated=False, productTestsExecuted=0,
                  newUniqueTests=0, compilerOrJvmExecuted=False, actualBackendActions=0,
                  wholeDependencyAccepted=False, wholeG13Accepted=False, whole451Accepted=False,
                  newAcceptance=0, formalUpdated=False, effortRate=None,
                  files={target.name: sha(target)}, tool={'path': str(Path(__file__)), 'sha256': sha(Path(__file__))})
    (O / 'manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(actualExit=0, explicitlyRelatedMethods=5, assertionSnippetChecks=result['assertionSnippetChecks'],
                         consumptionObservedBeforeFixtureCleanup=True, manifestSha256=sha(O / 'manifest.json'))))


if __name__ == '__main__':
    main()
