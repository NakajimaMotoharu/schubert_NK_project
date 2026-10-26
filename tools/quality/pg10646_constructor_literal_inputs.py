"""Literal-only inputs to value-preserving records; do not infer whole oracle or PT success."""
from collections import Counter
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10519_constructor_carrier_review_v2 import first_argument
from pg10588_record_constructor_review import record_review

OUT = data.BASE/'PG10646-constructor-literal-inputs-v1'
BODY_KINDS = {'VALIDATION_ONLY_NO_COMPONENT_REASSIGNMENT',
    'IMPLICIT_RECORD_CANONICAL_CONSTRUCTOR_NO_USER_TRANSFORMATION',
    'VALIDATION_PLUS_VALUE_PRESERVING_OWNERSHIP_COPY'}


def extra_names(expression,types):
    return sorted({v for v,_,_ in expression if re.fullmatch(r'[A-Za-z_$][A-Za-z0-9_$]*',v)}
        -set(types)-{'new','null','true','false','L','l'})


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    original_path = data.BASE/'PG10582-constructor-assertion-span-bindings-v1/manifest.json'
    original = data.read_checked(original_path,'5d591abfbe83b4d81b5086ceb6081fa04cb4d2e6492225b0938c30b5e198eaa1')
    rows = data.read_checked(original_path.parent/'constructor-bindings.json',original['rowsSha256'])
    body_path = data.BASE/'PG10588-record-constructor-review-v1/manifest.json'
    body = data.read_checked(body_path,'7ac388609456e216a0f9be08e02855d2fa691ff8089a1a46eb745b0d38c9866f')
    bodies = data.read_checked(body_path.parent/'constructor-reviews.json',body['reviewsSha256'])
    normal = data.read_checked(data.BASE/'PG10632-query-semantic-constant-compile-v1/manifest.json',
        '8f29215a400d24a55ecabee90c74fb72a43525b740f129a12ae6053559701f87')
    assert normal['source'] == '370fd74f6f170a18bc1bf959aa9fceced0def15a' and normal['actualExit'] == normal['testsExecuted'] == 0
    assert len(rows) == 168 and len(bodies) == 61
    by_owner = {b['owner']:b for b in bodies}
    for item in bodies:
        assert data.sha((data.ROOT/item['source']).read_bytes()) == item['sourceSha256'] == normal['begin']['inputHashes'][item['source']]
    results,counts = [],Counter()
    helper_reviews = {}
    for row in rows:
        path = row['path']
        assert path.startswith('src/') and '/src/test/java/' in path and path.endswith('.java')
        text = (data.ROOT/path).read_text()
        digest = data.sha(text.encode())
        assert digest == normal['begin']['inputHashes'][path]
        entry = dict(original=row,currentSourceSha256=digest)
        if digest != row['sourceSha256']:
            kind,actual = ('TemporaryInfrastructureException','error') if path.endswith('/LogQueryApplicationServiceTest.java') else ('BatchRepositoryException','e')
            message = 'request transaction is unavailable' if kind == 'TemporaryInfrastructureException' else 'batch repository operation failed'
            assert row['expectedConstructorTypes'] == [kind]
            assert row['method'] == ('deny' if actual == 'error' else 'redacted')
            assert f'assertEquals("{message}", {actual}.getMessage());' in text
            assert f'new {kind}().getMessage()' not in text
            entry.update(status='CURRENT_EXPECTED_REPLACED_BY_LITERAL_BUG1846_PREVIOUS_WORK',resolution='2089/10600 plus subsequent exact source-preservation chain',newFixCount=0)
        else:
            expression = first_argument(text,row)
            entry['rawExpectedExpressionSha256'] = data.sha(text[expression[0][1]:expression[-1][2]].encode())
            names = extra_names(expression,row['expectedConstructorTypes'])
            if row['expectedMethodSelectors']:
                entry.update(status='METHOD_INPUT_ORIGIN_PENDING',unreviewedSelectors=row['expectedMethodSelectors'])
            elif names:
                entry.update(status='NAMED_INPUT_ORIGIN_PENDING',unreviewedNames=names)
            else:
                contracts = []
                for name,binding in row['assertionSpanConstructorBindings'].items():
                    owner, = binding['owners']
                    source_binding = binding.get('mainSourceBinding')
                    if source_binding is not None:
                        assert isinstance(source_binding,dict) and '/src/main/java/' in source_binding['source']
                        item = by_owner[owner]
                        assert item['review']['kind'] in BODY_KINDS
                        assert item['sourceSha256'] == source_binding['sourceSha256']
                        contracts.append(dict(type=name,owner=owner,source=item['source'],sha256=item['sourceSha256'],review=item['review']))
                    else:
                        assert binding.get('mainSourceBinding') is None and '/src/test/java/' in path
                        assert name in ('Progress','Result') and owner.endswith('/'+Path(path).stem+'$'+name)
                        review = record_review(text,name)
                        assert review['kind'] == 'IMPLICIT_RECORD_CANONICAL_CONSTRUCTOR_NO_USER_TRANSFORMATION'
                        helper_reviews[(path,name)] = review
                        contracts.append(dict(type=name,owner=owner,testOnly=True,source=path,sha256=digest,review=review))
                assert contracts
                entry.update(status='LITERAL_INPUTS_AND_VALUE_PRESERVING_CONSTRUCTOR_STATIC_REVIEWED',constructorContracts=contracts,
                    inputExtraNames=[],wholeCaseFixtureQualified=False,dynamicQualification=False)
        counts[entry['status']] += 1
        results.append(entry)
    assert sorted(counts.values()) == [2,23,66,77] and len(helper_reviews) == 2
    assert extra_names([('new',0,3),('UserId',4,10),('(',10,11),('1',11,12),(')',12,13)],['UserId']) == []
    assert extra_names([('actual',0,6),('.',6,7),('get',7,10),('(',10,11),(')',11,12)],[]) == ['actual','get']
    assert extra_names([('count',0,5)],[]) == ['count']
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'input-reviews.json',results)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=normal['source'],invocation=invocation,
        originalBindingsManifestSha256=data.sha(original_path.read_bytes()),constructorReviewManifestSha256=data.sha(body_path.read_bytes()),
        originalRows=168,currentUnchangedRows=166,counts=dict(counts),testHelperRecordBodies=2,
        inputReviewsSha256=data.sha((OUT/'input-reviews.json').read_bytes()),classifierMetadataVectors=3,
        productTestsExecuted=0,targetClassLoaded=False,targetCompilation=False,coverage=None,
        wholeOracleQualified=False,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
