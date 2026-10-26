"""Independent raw callee/literal grammar for66 existing source expressions; no target invocation."""
from collections import Counter
import json
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10522_constructor_carrier_post import matching_span
from pg10654_qualified_constructor_inputs_post import fixed_input_only

OUT = data.BASE/'PG10672-jdk-factory-constructor-inputs-post-v1'
IMPORTS = {'Optional':'java.util.Optional','List':'java.util.List','Instant':'java.time.Instant',
    'UUID':'java.util.UUID','Duration':'java.time.Duration','Path':'java.nio.file.Path'}
CALLEES = ('Optional.of','Optional.empty','List.of','Instant.parse','UUID.fromString','Duration.ofSeconds','Path.of')


def literal_jdk(expression,types):
    used = []
    text = expression
    for callee in CALLEES:
        pattern = r'\b'+r'\s*\.\s*'.join(map(re.escape,callee.split('.')))+r'(?=\s*\()'
        if re.search(pattern,text):
            used.append(callee)
        text = re.sub(pattern,'0',text)
    pattern = r'("(?:\\.|[^"\\])*")\s*\.\s*repeat(?=\s*\()'
    if re.search(pattern,text):
        used.append('LITERAL_STRING.repeat')
    text = re.sub(pattern,r'\1',text)
    return bool(used) and fixed_input_only(text,types),used


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    primary_path = data.BASE/'PG10670-jdk-factory-constructor-inputs-v1/manifest.json'
    primary = data.read_checked(primary_path,'8ff711165cb406394f9159d528b9764bac5b349566b756de38431c5b206ce247')
    rows = data.read_checked(primary_path.parent/'jdk-input-reviews.json',primary['rowsSha256'])
    prior_path = data.BASE/'PG10646-constructor-literal-inputs-v1/manifest.json'
    prior = data.read_checked(prior_path,'a2f3823325d625a7d64ac2aad13cfe027a0497a7552ec9d23c61f32060710b55')
    entries = data.read_checked(prior_path.parent/'input-reviews.json',prior['inputReviewsSha256'])
    wanted = {i for i,e in enumerate(entries) if e['status'] == 'METHOD_INPUT_ORIGIN_PENDING'}
    assert len(rows) == len(wanted) == 66 and {r['priorEntryIndex'] for r in rows} == wanted
    counts,consumers = Counter(),set()
    for result in rows:
        entry = entries[result['priorEntryIndex']]
        assert data.sha(json.dumps(entry,sort_keys=True,ensure_ascii=False).encode()) == result['priorEntrySha256']
        row = entry['original']
        assert result['key'] == {k:row[k] for k in ('path','method','line','expectedExpressionSha256')}
        path = row['path']
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == result['sourceSha256'] == row['sourceSha256']
        begin,end = matching_span(text,row)
        selected,used = literal_jdk(text[begin:end],row['expectedConstructorTypes'])
        expected = 'LITERAL_JDK_FACTORY_INPUTS_STATIC_REVIEWED' if selected else 'METHOD_OR_NAMED_INPUT_ORIGIN_PENDING'
        assert result['status'] == expected and not result['wholeCaseFixtureQualified'] and result['productTestsExecuted'] == 0
        if selected:
            assert set(result['jdkCallees']) == set(used)
            for callee in used:
                if callee == 'LITERAL_STRING.repeat':
                    continue
                simple = callee.split('.')[0]
                assert 'import '+IMPORTS[simple]+';' in text
                assert not re.search(r'\b(?:class|record|interface|enum)\s+'+simple+r'\b',text)
            for contract in result['valuePreservingConstructorReferences']:
                assert '/src/main/java/' in contract['source']
                assert data.sha((data.ROOT/contract['source']).read_bytes()) == contract['sourceSha256']
                assert any(b['owners'] == [contract['owner']] and b['mainSourceBinding'] is not None
                    and b['mainSourceBinding']['sourceSha256'] == contract['sourceSha256']
                    for b in row['assertionSpanConstructorBindings'].values())
            consumers.add(path)
        counts[expected] += 1
    assert counts == primary['counts'] == {'LITERAL_JDK_FACTORY_INPUTS_STATIC_REVIEWED':20,'METHOD_OR_NAMED_INPUT_ORIGIN_PENDING':46}
    assert len(consumers) == 12
    vectors = [('Optional.of(new T(1))',['T'],True),('Optional.of(new T(actual))',['T'],False),
        ('new T(MainFactory.value())',['T'],False),('new T(1).hashCode()',['T'],False),
        ('new T("2".repeat(32))',['T'],True),('new T(Path.of(path))',['T'],False)]
    for text,types,expected in vectors:
        assert literal_jdk(text,types)[0] is expected
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=primary['source'],invocation=invocation,
        primaryManifestSha256=data.sha(primary_path.read_bytes()),originalCandidateRows=66,independentRawSpans=66,
        fixedJdkInputSites=20,selectedConsumerSources=12,remainingMethodOrNamedInputs=46,
        callbackPropertyStillUnqualified=1,previous99AndTwoCorrectedNotRecounted=True,
        grammarMetadataVectors=6,productTestsExecuted=0,targetClassLoaded=False,targetCompilation=False,
        coverage=None,wholeOracleQualified=False,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
