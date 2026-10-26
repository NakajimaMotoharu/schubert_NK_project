"""Independent SourceFile/current source/raw expected span metadata checks, no targets run."""
from pathlib import Path
import zipfile
from classfile_code_metadata import decode
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10522_constructor_carrier_post import matching_span

OUT = data.BASE/'PG10584-constructor-binding-post-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    prior = data.read_checked(data.BASE/'PG10580-remaining-constructor-bindings-v1/manifest.json',
        'a9e61e1889b9f51469f28112da46f5df80e47769a679b723f6739896c2bafc8c')
    original = data.read_checked(data.BASE/'PG10580-remaining-constructor-bindings-v1/constructor-bindings.json',prior['rowsSha256'])
    refined = data.read_checked(data.BASE/'PG10582-constructor-assertion-span-bindings-v1/manifest.json',
        '5d591abfbe83b4d81b5086ceb6081fa04cb4d2e6492225b0938c30b5e198eaa1')
    rows = data.read_checked(data.BASE/'PG10582-constructor-assertion-span-bindings-v1/constructor-bindings.json',refined['rowsSha256'])
    normal = data.read_checked(data.BASE/'PG10558-trace-context-final-compile-v1/manifest.json',
        'e4f64a5711e95d5b5a6362bcec7adb3fe641f878d2edb2809c7dcbc8770f5e49')
    assert len(rows) == len(original) == 168
    owners = {}
    for old,row in zip(original,rows):
        assert all(row[k] == value for k,value in old.items())
        text = (data.ROOT/row['path']).read_text()
        assert data.sha(text.encode()) == row['sourceSha256']
        matching_span(text,row)
        assert row['assertionStartLine'] <= row['line'] <= row['expectedFinalLine']
        for binding in row['assertionSpanConstructorBindings'].values():
            assert binding['status'] == 'EXACT_ASSERTION_TO_EXPECTED_END_UNIQUE_OWNER' and len(binding['owners']) == 1
            owner = binding['owners'][0]
            assert all(row['assertionStartLine'] <= c['line'] <= row['expectedFinalLine'] and c['owner'] == owner
                for c in binding['supportingInvocationMetadata'])
            owners[owner] = binding['mainSourceBinding']
    main_owners = {owner:value for owner,value in owners.items() if value is not None}
    assert len(owners) == 64 and len(main_owners) == 61
    for owner,value in main_owners.items():
        item = normal['jars'][value['module']]
        assert data.sha(Path(item['path']).read_bytes()) == item['sha256']
        with zipfile.ZipFile(item['path']) as jar:
            raw = jar.read(owner+'.class')
        model = decode(raw,owner+'.class')
        assert data.sha(raw) == value['physicalClassSha256']
        assert model['sourceFile'] == Path(value['source']).name
        assert data.sha((data.ROOT/value['source']).read_bytes()) == value['sourceSha256'] == normal['begin']['inputHashes'][value['source']]
    assert not refined['readerReexecuted'] and not refined['constructorSemanticsOrArgumentProvenanceQualified']
    record = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2086_残constructor168式の型・source位置束縛結果.md'
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=refined['source'],invocation=invocation,
        strictManifestSha256='a9e61e1889b9f51469f28112da46f5df80e47769a679b723f6739896c2bafc8c',
        refinedManifestSha256='5d591abfbe83b4d81b5086ceb6081fa04cb4d2e6492225b0938c30b5e198eaa1',
        originalRowFieldsRetained=168,independentRawExpectedSpansMatched=168,constructorTypeOccurrences=180,
        mainClassSourceFileHashBindings=61,uniqueMainSources=55,externalOrTestOwners=3,
        humanReviewSha256=data.sha(record.read_bytes()),readerReexecuted=False,
        targetCompilation=0,targetClassLoading=0,productTestsExecuted=0,externalActions=0,
        constructorSemanticsAndArgumentProvenanceQualified=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
