"""Bind seven reviewed syntax candidates to original public sources/independent fixture files."""
import json
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG10122-oracle-same-selector-review-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    index = data.read_checked(data.BASE/'PG10120-protocol-storage-oracle-sites-v1/manifest.json',
        'f5dafc428c0e2367f79e0e59cd91b125639a88880f7be7bad72e879c0509527c')
    all_rows = data.read_checked(data.BASE/'PG10120-protocol-storage-oracle-sites-v1/sites.json',index['sitesJsonSha256'])
    selected = [r for r in all_rows if r['sharedDirectMethodSelectors']]
    assert len(selected) == 7 and index['actualExit'] == index['productTestsExecuted'] == 0
    fixtures = {
        'src/schubert-nk-protocol/src/test/resources/protocol/payload-golden-ui234-236.tsv':
            '49bb76ec610216042f8e53ed548f4d5e52707a8bbf930a9fc6c93300dfa24839',
        'src/schubert-nk-protocol/src/test/resources/protocol/named-types-ss323.tsv':
            '9529fce86672b27a435665331648110521be6f59c5fe3fe5ca516df5234c7a76'}
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in fixtures.items())
    expected = {('PayloadGoldenVectorTest.java',58):'INPUT_LAYOUT_ID_PLUS_FIXED_WIRE_HASH',
        ('PayloadGoldenVectorTest.java',75):'INPUT_LAYOUT_ID_PLUS_FIXED_WIRE_HASH',
        ('PayloadTypeCatalogTest.java',90):'REDACTION_PROPERTY_WITH_INDEPENDENT_NAMED_TYPE_FIXTURE',
        ('PayloadTypeCatalogTest.java',105):'REDACTION_PROPERTY_WITH_INDEPENDENT_NAMED_TYPE_FIXTURE',
        ('LinuxInodeSecurityTest.java',205):'ORACLE_FIX_REQUIRED_BUG1794',
        ('PrivateChildDirectoryTest.java',46):'JDK_PARENT_CHILD_UID_COMPARISON_NOT_PRODUCTION_GETTER',
        ('PrivateChildDirectoryTest.java',48):'JDK_PARENT_CHILD_DEVICE_COMPARISON_NOT_PRODUCTION_GETTER'}
    assert {(Path(r['path']).name,r['line']) for r in selected} == set(expected)
    review = []
    for row in selected:
        path = data.ROOT/row['path']
        assert data.sha(path.read_bytes()) == row['sourceSha256'] == index['sourceHashes'][row['path']]
        status = expected[(path.name,row['line'])]
        if path.name == 'PayloadGoldenVectorTest.java':
            assert row['expectedMethodSelectors'] == ['layout.id']
            assert '/protocol/payload-golden-ui234-236.tsv' in path.read_text()
        elif path.name == 'PayloadTypeCatalogTest.java':
            assert '/protocol/named-types-ss323.tsv' in path.read_text()
        elif path.name == 'LinuxInodeSecurityTest.java':
            assert row['expectedMethodSelectors'] == row['actualMethodSelectors'] == [
                'LinuxInodeSecurity.create','LinuxInodeSecurity.create().effectiveUid']
            assert 'LinuxInodeSecurity.create().effectiveUid(),' in path.read_text()
        else:
            assert row['expectedMethodSelectors'] == row['actualMethodSelectors'] == ['Files.getAttribute']
        review.append(dict(path=row['path'],line=row['line'],method=row['method'],
            sourceSha256=row['sourceSha256'],expectedExpressionSha256=row['expectedExpressionSha256'],status=status,
            scope='THIS_SITE_CONTEXT_ONLY_NOT_WHOLE_TEST_OR_PROGRAM_PASS'))
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'review.json',review)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=index['source'],invocation=invocation,
        indexManifestSha256='f5dafc428c0e2367f79e0e59cd91b125639a88880f7be7bad72e879c0509527c',
        reviewedDirectSameSelectorSites=7,nonTautologyForThisSiteWithFixtureContext=6,oracleFixRequired=1,
        issue='BUG-1794',horizontalIssue='YKT-1545',independentFixtureHashes=fixtures,
        remainingDirectExpectedCallSites=index['directExpectedCalls']-7,
        unresolvedIdentifierSites=index['expectedIdentifier'],countsOverlapNotCompletionRate=True,
        reviewSha256=data.sha((OUT/'review.json').read_bytes()),productTestsExecuted=0,
        runtimeOrIndependenceGatePassed=False,wholeG03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,reviewed=7,fixRequired=1,remainingDirect=209,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
