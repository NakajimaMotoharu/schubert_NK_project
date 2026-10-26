"""Independent raw AST-span and exact owner/source-kind post, no Product execution."""
from collections import Counter
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10522_constructor_carrier_post import matching_span
from public_java_digest_provenance import LEX

OUT = data.BASE/'PG10648-constructor-literal-inputs-post-v1'


def literal_only(expression,types):
    names = {m.group() for m in LEX.finditer(expression) if re.fullmatch(r'[A-Za-z_$][A-Za-z0-9_$]*',m.group())}
    if names-set(types)-{'new','null','true','false'}:
        raise ValueError('only selected exact literal inputs; no unknown identifier or generic L/l exemption')


def source_kind(binding,path,name):
    owner, = binding['owners']
    item = binding.get('mainSourceBinding')
    if item is not None:
        if not isinstance(item,dict) or '/src/main/java/' not in item['source']:
            raise ValueError('real Main source path required')
        return 'MAIN'
    if name not in ('Progress','Result') or '/src/test/java/' not in path or not owner.endswith('/'+Path(path).stem+'$'+name):
        raise ValueError('exact two Test helper owners only')
    return 'TEST_HELPER'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    primary_path = data.BASE/'PG10646-constructor-literal-inputs-v1/manifest.json'
    primary = data.read_checked(primary_path,'a2f3823325d625a7d64ac2aad13cfe027a0497a7552ec9d23c61f32060710b55')
    rows = data.read_checked(primary_path.parent/'input-reviews.json',primary['inputReviewsSha256'])
    original_path = data.BASE/'PG10582-constructor-assertion-span-bindings-v1/manifest.json'
    original = data.read_checked(original_path,'5d591abfbe83b4d81b5086ceb6081fa04cb4d2e6492225b0938c30b5e198eaa1')
    originals = data.read_checked(original_path.parent/'constructor-bindings.json',original['rowsSha256'])
    assert len(rows) == len(originals) == 168
    literal_count,raw_count,main_count,test_count = 0,0,0,0
    consumers = set()
    for row,old in zip(rows,originals):
        assert row['original'] == old
        path = old['path']
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == row['currentSourceSha256']
        if row['status'] == 'CURRENT_EXPECTED_REPLACED_BY_LITERAL_BUG1846_PREVIOUS_WORK':
            assert row['newFixCount'] == 0 and old['method'] in ('deny','redacted')
            assert data.sha(text.encode()) != old['sourceSha256']
            continue
        assert data.sha(text.encode()) == old['sourceSha256']
        begin,end = matching_span(text,old)
        assert data.sha(text[begin:end].encode()) == row['rawExpectedExpressionSha256']
        raw_count += 1
        if row['status'] != 'LITERAL_INPUTS_AND_VALUE_PRESERVING_CONSTRUCTOR_STATIC_REVIEWED':
            continue
        literal_only(text[begin:end],old['expectedConstructorTypes'])
        assert not old['expectedMethodSelectors'] and not row['dynamicQualification'] and not row['wholeCaseFixtureQualified']
        literal_count += 1
        consumers.add(path)
        for contract in row['constructorContracts']:
            kind = source_kind(old['assertionSpanConstructorBindings'][contract['type']],path,contract['type'])
            assert data.sha((data.ROOT/contract['source']).read_bytes()) == contract['sha256']
            if kind == 'MAIN':
                assert '/src/main/java/' in contract['source']
                main_count += 1
            else:
                assert contract['testOnly'] and contract['source'] == path
                assert contract['review']['kind'] == 'IMPLICIT_RECORD_CANONICAL_CONSTRUCTOR_NO_USER_TRANSFORMATION'
                test_count += 1
    assert raw_count == 166 and literal_count == 23 and main_count == 14 and test_count == 9
    rejected = []
    for text,types in [('new UserId(actual.value())',['UserId']),('new UserId(L)',['UserId'])]:
        try:
            literal_only(text,types)
        except ValueError:
            rejected.append('nonliteral-input')
        else:
            raise AssertionError('unqualified input source accepted')
    fake = dict(owners=['p/T$Unknown'],mainSourceBinding=None)
    try:
        source_kind(fake,'src/m/src/test/java/p/T.java','Unknown')
    except ValueError:
        rejected.append('unknown-Test-owner')
    else:
        raise AssertionError('unknown Test helper accepted')
    fake = dict(owners=['p/T'],mainSourceBinding=dict(source='src/m/src/test/java/p/T.java'))
    try:
        source_kind(fake,'src/m/src/test/java/p/T.java','T')
    except ValueError:
        rejected.append('false-Main-source')
    else:
        raise AssertionError('Main label spoof accepted')
    assert Counter(row['status'] for row in rows) == primary['counts']
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=primary['source'],invocation=invocation,
        primaryManifestSha256=data.sha(primary_path.read_bytes()),originalRowsAllFieldsPreserved=168,
        independentlyMatchedRawSpans=166,literalInputSites=23,mainValueConstructorOccurrences=14,
        testHelperConstructorOccurrences=9,selectedConsumerSources=len(consumers),previouslyFixedNotNew=2,
        methodInputsPending=66,namedInputsPending=77,metadataNegativeVectors=rejected,
        productTestsExecuted=0,targetClassLoaded=False,targetCompilation=False,coverage=None,
        wholeOracleQualified=False,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
