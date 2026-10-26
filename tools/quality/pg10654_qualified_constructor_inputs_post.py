"""Independent raw-expression grammar verifies77 prior candidates without target execution."""
from collections import Counter
import json
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10522_constructor_carrier_post import matching_span

OUT = data.BASE/'PG10654-qualified-constructor-inputs-post-v1'


def fixed_input_only(expression,types):
    text = re.sub(r'"(?:\\.|[^"\\])*"', '0', expression)
    text = re.sub(r"'(?:\\.|[^'\\])'", '0', text)
    for name in sorted(types,key=len,reverse=True):
        pattern = r'\bnew\s+'+r'\s*\.\s*'.join(re.escape(part) for part in name.split('.'))+r'(?=\s*\()'
        text = re.sub(pattern,'0',text)
    text = re.sub(r'\b(?:true|false|null)\b','0',text)
    text = re.sub(r'(?<![A-Za-z0-9_$])\d+[Ll]?(?![A-Za-z0-9_$])','0',text)
    return re.search(r'[A-Za-z_$]',text) is None


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    primary_path = data.BASE/'PG10652-qualified-constructor-inputs-v1/manifest.json'
    primary = data.read_checked(primary_path,'fbbf406acd3b6361fe5f27fb1636da77b16a817015e27cd9b43c807171ea9983')
    rows = data.read_checked(primary_path.parent/'qualified-input-reviews.json',primary['qualifiedInputReviewsSha256'])
    prior_path = data.BASE/'PG10646-constructor-literal-inputs-v1/manifest.json'
    prior = data.read_checked(prior_path,'a2f3823325d625a7d64ac2aad13cfe027a0497a7552ec9d23c61f32060710b55')
    entries = data.read_checked(prior_path.parent/'input-reviews.json',prior['inputReviewsSha256'])
    wanted = {i for i,e in enumerate(entries) if e['status'] == 'NAMED_INPUT_ORIGIN_PENDING'}
    assert len(rows) == len(wanted) == 77 and {r['priorEntryIndex'] for r in rows} == wanted
    counts = Counter()
    for result in rows:
        entry = entries[result['priorEntryIndex']]
        assert data.sha(json.dumps(entry,sort_keys=True,ensure_ascii=False).encode()) == result['priorEntrySha256']
        row = entry['original']
        assert result['key'] == {k:row[k] for k in ('path','method','line','expectedExpressionSha256')}
        text = (data.ROOT/row['path']).read_text()
        assert data.sha(text.encode()) == result['sourceSha256'] == row['sourceSha256']
        begin,end = matching_span(text,row)
        literal = fixed_input_only(text[begin:end],row['expectedConstructorTypes'])
        expected = 'QUALIFIED_CONSTRUCTOR_LITERAL_INPUTS_STATIC_REVIEWED' if literal else 'NAMED_INPUT_ORIGIN_PENDING'
        assert result['status'] == expected and not result['wholeCaseFixtureQualified'] and result['productTestsExecuted'] == 0
        counts[expected] += 1
        if literal:
            assert not result['unresolvedInputNames'] and result['valuePreservingConstructorReferences']
            for contract in result['valuePreservingConstructorReferences']:
                assert '/src/main/java/' in contract['source']
                assert data.sha((data.ROOT/contract['source']).read_bytes()) == contract['sourceSha256']
                bindings = row['assertionSpanConstructorBindings'].values()
                assert any(b['owners'] == [contract['owner']] and b['mainSourceBinding'] is not None
                    and b['mainSourceBinding']['source'] == contract['source']
                    and b['mainSourceBinding']['sourceSha256'] == contract['sourceSha256'] for b in bindings)
    assert counts == primary['counts'] == {'QUALIFIED_CONSTRUCTOR_LITERAL_INPUTS_STATIC_REVIEWED':26,'NAMED_INPUT_ORIGIN_PENDING':51}
    vectors = [('new T(T)',['T'],False),('new T(L)',['T'],False),
        ('new T(1L)',['T'],True),('new O.T(1)',['O.T'],True),('new O.T(O)',['O.T'],False)]
    for text,types,expected in vectors:
        assert fixed_input_only(text,types) is expected
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=primary['source'],invocation=invocation,
        primaryManifestSha256=data.sha(primary_path.read_bytes()),originalCandidateRows=77,
        originalRowReferencesPreserved=77,independentRawSpans=77,newFixedInputSites=26,remainingNamedInputs=51,
        remainingMethodInputs=66,previous23AndTwoFixedNotRecounted=True,grammarMetadataVectors=5,
        productTestsExecuted=0,targetClassLoaded=False,targetCompilation=False,coverage=None,
        wholeOracleQualified=False,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
