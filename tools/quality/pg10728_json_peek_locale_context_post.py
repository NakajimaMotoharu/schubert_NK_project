"""Independent exact-coordinate/fixed dependency/contract source audit; no parser or Product run."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG10728-json-peek-locale-context-post-v1'
GSON_SHA = '2cbd119bf1961c28788310963dc80ba65f58cdeec1dd139c8bdb1240faa2c36f'
TESTS = {
    'RequestLogDetails.java':('RequestLogDetailsTest.java','"{} {}"'),
    'BrokerJournalEvidence.java':('BrokerJournalEvidenceTest.java','"{} {}\\n"'),
    'ReleaseInventory.java':('ReleaseInventoryTest.java','refused(golden() + " {}");'),
    'SessionAttributeCodec.java':('SessionAttributeCodecTest.java','ANONYMOUS + "{}"'),
}


def contract_eligible(jar_sha,strictness,root_closed,validation_kept):
    return jar_sha == GSON_SHA and strictness == 'STRICT' and root_closed and validation_kept


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    primary_path = data.BASE/'PG10726-json-peek-locale-context-v1/manifest.json'
    primary = data.read_checked(primary_path,'412995d03337a68d8e8b2ab5f1462bfb429e4bb362d2e11c73444b8438bb6726')
    rows = data.read_checked(primary_path.parent/'contexts.json',primary['rowsSha256'])
    reference = data.read_checked(primary_path.parent/'historical-library-contract-reference.json',primary['libraryReferenceSha256'])
    normal = data.read_checked(data.BASE/'PG10714-graph-constants-six-compile-v1/manifest.json',
        'b24ac5ef1f85b9ed935e0772ef04040acbd12b78f573a88aa4d9420ae4995676')
    assert primary['source'] == normal['source']
    assert reference['gsonJarSha256'] == data.sha(Path(reference['gsonJar']).read_bytes()) == GSON_SHA
    assert reference['oldLibraryVectorsNotReexecuted'] and reference['oldProductionResultsNotReassigned']
    decisions = (data.ROOT/reference['decisionPath']).read_text()
    assert reference['sectionText'] in decisions and data.sha(reference['sectionText'].encode()) == reference['sectionSha256']
    assert '479～521' in reference['sectionText'] and 'EOFなら17/END_DOCUMENT' in reference['sectionText']
    assert data.sha((data.ROOT/reference['studySource']).read_bytes()) == reference['studySourceSha256']
    assert len(rows) == 5 and {r['originalFinding']['id'] for r in rows} == {'PMD-00135','PMD-03056','PMD-06189','PMD-06882','PMD-07451'}
    test_references = []
    for row in rows:
        original = row['originalFinding']
        path = original['path']
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == row['sourceSha256'] == original['inputSha256'] == normal['begin']['inputHashes'][path]
        if original['rule'] == 'UnusedReturnValue':
            lines = text.splitlines()
            assert lines[original['line']-1].strip().split('//')[0].strip() == 'reader.peek();'
            prefix = '\n'.join(lines[:original['line']])
            assert prefix.rfind('reader.endObject();') > prefix.rfind('reader.beginObject();') >= 0
            assert prefix.rfind('reader.setStrictness(Strictness.STRICT);') > prefix.rfind('new JsonReader(') >= 0
            assert text.count('reader.setStrictness(') == 1
            assert contract_eligible(reference['gsonJarSha256'],'STRICT',True,True)
            assert row['status'] == 'NOT_APPLICABLE_PURE_UNUSED_RESULT_RULE_TO_REQUIRED_STRICT_VALIDATION_EFFECT'
            filename,fixture = TESTS[Path(path).name]
            test, = [p for p in normal['begin']['inputHashes'] if '/src/test/java/' in p and p.endswith('/'+filename)]
            content = (data.ROOT/test).read_text()
            assert data.sha(content.encode()) == normal['begin']['inputHashes'][test] and fixture in content
            test_references.append(dict(path=test,sha256=data.sha(content.encode()),existingTrailingDataFixture=fixture,
                executionStatus='NOT_EXECUTED_OR_REASSIGNED_BY_THIS_REVIEW'))
        else:
            assert original['rule'] == 'UseLocaleWithCaseConversions' and path.endswith('/SemanticFieldValueTest.java')
            assert 'UUID_TEXT.toUpperCase()' in text and '"123e4567-e89b-12d3-a456-426614174000"' in text
            assert row['status'] == 'APPLICABLE_TEST_FIXTURE_STYLE_PG_PENDING'
            assert row['review']['observedLocaleFailure'] is False
        assert row['productTestsExecuted'] == 0 and row['dynamicQualification'] is False
    assert not contract_eligible(GSON_SHA,'LENIENT',True,True)
    assert not contract_eligible('0'*64,'STRICT',True,True)
    assert not contract_eligible(GSON_SHA,'STRICT',False,True)
    assert not contract_eligible(GSON_SHA,'STRICT',True,False)
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'existing-source-test-references.json',test_references)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=primary['source'],invocation=invocation,
        primaryManifestSha256=data.sha(primary_path.read_bytes()),exactRawFindingSites=5,
        fixedGsonValidationEffectContextSites=4,localeFixtureStylePending=1,negativeMetadataVectors=4,
        existingTestSourceReferences=4,testReferencesSha256=data.sha((OUT/'existing-source-test-references.json').read_bytes()),
        productTestsExecuted=0,targetProductCodeExecuted=False,libraryContractReexecuted=False,coverage=None,
        rawFindingsNotSuppressed=True,externalActions=0,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
