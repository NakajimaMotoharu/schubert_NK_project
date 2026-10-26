"""Independent raw enum-member grammar and source provenance, no Product execution."""
from collections import Counter
import json
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10522_constructor_carrier_post import matching_span
from pg10654_qualified_constructor_inputs_post import fixed_input_only

OUT = data.BASE/'PG10660-direct-enum-constructor-inputs-post-v1'
MEMBERS = {'Role':('ADMIN','USER'),'ResultCode':('AUTHENTICATION_FAILED','LOCKED'),
    'ArtemisQueuePressureClient.Pressure':('NORMAL','WARNING')}


def enum_input(expression,types):
    text = re.sub(r'"(?:\\.|[^"\\])*"','0',expression)
    text = re.sub(r"'(?:\\.|[^'\\])'",'0',text)
    text = re.sub(r'//[^\n]*|/\*.*?\*/','',text,flags=re.S)
    refs = []
    for qualifier,values in MEMBERS.items():
        prefix = r'\s*\.\s*'.join(map(re.escape,qualifier.split('.')))
        pattern = r'(?<![A-Za-z0-9_$])'+prefix+r'\s*\.\s*('+('|'.join(values))+r')\b'
        matches = list(re.finditer(pattern,text))
        refs.extend((qualifier,m.group(1)) for m in matches)
        text = re.sub(pattern,'0',text)
    return bool(refs) and fixed_input_only(text,types),refs


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    primary_path = data.BASE/'PG10658-direct-enum-constructor-inputs-v1/manifest.json'
    primary = data.read_checked(primary_path,'0405725d0079434a86a86976aee0b204fd429d52af72ec6ac5f472387997d1e6')
    rows = data.read_checked(primary_path.parent/'enum-input-reviews.json',primary['rowsSha256'])
    prior_path = data.BASE/'PG10652-qualified-constructor-inputs-v1/manifest.json'
    prior = data.read_checked(prior_path,'fbbf406acd3b6361fe5f27fb1636da77b16a817015e27cd9b43c807171ea9983')
    candidates = data.read_checked(prior_path.parent/'qualified-input-reviews.json',prior['qualifiedInputReviewsSha256'])
    original_path = data.BASE/'PG10646-constructor-literal-inputs-v1/manifest.json'
    original = data.read_checked(original_path,'a2f3823325d625a7d64ac2aad13cfe027a0497a7552ec9d23c61f32060710b55')
    entries = data.read_checked(original_path.parent/'input-reviews.json',original['inputReviewsSha256'])
    wanted = {i for i,r in enumerate(candidates) if r['status'] == 'NAMED_INPUT_ORIGIN_PENDING'}
    assert len(rows) == len(wanted) == 51 and {r['priorQualifiedIndex'] for r in rows} == wanted
    counts,refs = Counter(),Counter()
    consumers = set()
    for qualifier,definition in primary['enumDefinitions'].items():
        text = (data.ROOT/definition['path']).read_text()
        assert data.sha(text.encode()) == definition['sha256']
        assert re.search(r'\benum\s+'+qualifier.split('.')[-1]+r'\s*\{',text)
        assert all(re.search(r'^\s*'+value+r'\s*(?:,|\(|$)',text,re.M) for value in MEMBERS[qualifier])
    for result in rows:
        candidate = candidates[result['priorQualifiedIndex']]
        assert data.sha(json.dumps(candidate,sort_keys=True,ensure_ascii=False).encode()) == result['priorQualifiedSha256']
        row = entries[candidate['priorEntryIndex']]['original']
        assert result['key'] == candidate['key']
        text = (data.ROOT/row['path']).read_text()
        assert data.sha(text.encode()) == result['sourceSha256'] == row['sourceSha256']
        begin,end = matching_span(text,row)
        selected,used = enum_input(text[begin:end],row['expectedConstructorTypes'])
        expected = 'DIRECT_ENUM_AND_LITERAL_INPUTS_STATIC_REVIEWED' if selected else 'NAMED_INPUT_ORIGIN_PENDING'
        assert result['status'] == expected and result['productTestsExecuted'] == 0 and not result['wholeCaseFixtureQualified']
        assert Counter(map(tuple,result['directEnumReferences'])) == Counter(used)
        if selected:
            for qualifier,value in used:
                definition = primary['enumDefinitions'][qualifier]
                if qualifier in ('Role','ResultCode'):
                    assert 'import '+definition['qualifiedType']+';' in text
                else:
                    assert 'package dev.codex.schubert.nk.batch.mq;' in text
                refs[qualifier] += 1
                assert value in definition['selectedMembers']
            for contract in result['valuePreservingConstructorReferences']:
                assert '/src/main/java/' in contract['source']
                assert data.sha((data.ROOT/contract['source']).read_bytes()) == contract['sourceSha256']
            consumers.add(row['path'])
        counts[expected] += 1
    assert counts == primary['counts'] == {'DIRECT_ENUM_AND_LITERAL_INPUTS_STATIC_REVIEWED':13,'NAMED_INPUT_ORIGIN_PENDING':38}
    assert refs == {'Role':7,'ResultCode':3,'ArtemisQueuePressureClient.Pressure':3} and len(consumers) == 6
    vectors = [('new T(Role.ADMIN)',['T'],True),('new T(Role.MISSING)',['T'],False),
        ('new T(Role.ADMIN.wireValue())',['T'],False),('new T(Role)',['T'],False),
        ('new T("Role.ADMIN")',['T'],False),('new T(ArtemisQueuePressureClient.Pressure.WARNING)',['T'],True)]
    for text,types,wanted_result in vectors:
        assert enum_input(text,types)[0] is wanted_result
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=primary['source'],invocation=invocation,
        primaryManifestSha256=data.sha(primary_path.read_bytes()),priorCandidateRows=51,independentRawSpans=51,
        newDirectEnumInputSites=13,enumReferenceCounts=dict(refs),consumerSources=6,
        remainingNamedInputs=38,remainingMethodInputs=66,previous49AndTwoFixedNotRecounted=True,
        grammarMetadataVectors=6,productTestsExecuted=0,targetClassLoaded=False,targetCompilation=False,
        coverage=None,wholeOracleQualified=False,wireMappingQualified=False,externalActions=0,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
