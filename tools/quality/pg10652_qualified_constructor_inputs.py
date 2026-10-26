"""Remove only exact constructor-head identifiers, not same-named input variables."""
import json
from collections import Counter
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10519_constructor_carrier_review_v2 import first_argument

OUT = data.BASE/'PG10652-qualified-constructor-inputs-v1'


def unresolved_names(expression,types):
    skip,heads = set(),[]
    identifier = lambda s: re.fullmatch(r'[A-Za-z_$][A-Za-z0-9_$]*',s) is not None
    for i,(value,_,_) in enumerate(expression):
        if value != 'new':
            continue
        j = i+1
        while j < len(expression) and (identifier(expression[j][0]) or expression[j][0] == '.'):
            j += 1
        name = ''.join(t[0] for t in expression[i+1:j])
        if name not in types or j >= len(expression) or expression[j][0] != '(':
            raise ValueError('exact original bound constructor head required')
        skip.update(range(i+1,j))
        heads.append(name)
    for i,(value,start,_) in enumerate(expression):
        if value in ('L','l') and i and expression[i-1][2] == start and expression[i-1][0].isdigit():
            skip.add(i)
    names = {value for i,(value,_,_) in enumerate(expression) if i not in skip and identifier(value)}-{'new','null','true','false'}
    return sorted(names),heads


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    prior_path = data.BASE/'PG10646-constructor-literal-inputs-v1/manifest.json'
    prior = data.read_checked(prior_path,'a2f3823325d625a7d64ac2aad13cfe027a0497a7552ec9d23c61f32060710b55')
    entries = data.read_checked(prior_path.parent/'input-reviews.json',prior['inputReviewsSha256'])
    body_path = data.BASE/'PG10588-record-constructor-review-v1/manifest.json'
    body = data.read_checked(body_path,'7ac388609456e216a0f9be08e02855d2fa691ff8089a1a46eb745b0d38c9866f')
    bodies = data.read_checked(body_path.parent/'constructor-reviews.json',body['reviewsSha256'])
    by_owner = {b['owner']:b for b in bodies}
    normal = data.read_checked(data.BASE/'PG10632-query-semantic-constant-compile-v1/manifest.json',
        '8f29215a400d24a55ecabee90c74fb72a43525b740f129a12ae6053559701f87')
    assert normal['source'] == prior['source'] == '370fd74f6f170a18bc1bf959aa9fceced0def15a'
    results,counts = [],Counter()
    for index,entry in enumerate(entries):
        if entry['status'] != 'NAMED_INPUT_ORIGIN_PENDING':
            continue
        row = entry['original']
        text = (data.ROOT/row['path']).read_text()
        assert data.sha(text.encode()) == row['sourceSha256'] == normal['begin']['inputHashes'][row['path']]
        expression = first_argument(text,row)
        names,heads = unresolved_names(expression,row['expectedConstructorTypes'])
        assert heads and not row['expectedMethodSelectors']
        result = dict(priorEntryIndex=index,priorEntrySha256=data.sha(json.dumps(entry,sort_keys=True,ensure_ascii=False).encode()),
            key={k:row[k] for k in ('path','method','line','expectedExpressionSha256')},sourceSha256=row['sourceSha256'],
            actualConstructorHeads=heads,unresolvedInputNames=names,
            status='NAMED_INPUT_ORIGIN_PENDING' if names else 'QUALIFIED_CONSTRUCTOR_LITERAL_INPUTS_STATIC_REVIEWED',
            productTestsExecuted=0,wholeCaseFixtureQualified=False)
        if not names:
            contracts = []
            for name in heads:
                binding = row['assertionSpanConstructorBindings'][name]
                owner, = binding['owners']
                item = by_owner[owner]
                assert binding['mainSourceBinding'] is not None and '/src/main/java/' in item['source']
                assert item['review']['kind'] != 'NONRECORD_EXCEPTION_REVIEWED_SEPARATELY_NOT_VALUE_ORACLE'
                assert data.sha((data.ROOT/item['source']).read_bytes()) == item['sourceSha256'] == normal['begin']['inputHashes'][item['source']]
                contracts.append(item)
            result['valuePreservingConstructorReferences'] = contracts
        counts[result['status']] += 1
        results.append(result)
    assert len(results) == 77 and counts == {'QUALIFIED_CONSTRUCTOR_LITERAL_INPUTS_STATIC_REVIEWED':26,'NAMED_INPUT_ORIGIN_PENDING':51}
    assert unresolved_names([('new',0,3),('T',4,5),('(',5,6),('T',6,7),(')',7,8)],['T'])[0] == ['T']
    assert unresolved_names([('new',0,3),('T',4,5),('(',5,6),('L',6,7),(')',7,8)],['T'])[0] == ['L']
    assert unresolved_names([('new',0,3),('T',4,5),('(',5,6),('1',6,7),('L',7,8),(')',8,9)],['T'])[0] == []
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'qualified-input-reviews.json',results)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=normal['source'],invocation=invocation,
        priorReviewManifestSha256=data.sha(prior_path.read_bytes()),priorInputReviewsSha256=prior['inputReviewsSha256'],
        priorEntries=168,selectedNamedCandidates=77,counts=dict(counts),newLiteralInputSites=26,
        previouslyReviewedLiteralSitesNotNew=23,previouslyFixedSitesNotNew=2,
        remainingNamedInputs=51,remainingMethodInputs=66,
        qualifiedInputReviewsSha256=data.sha((OUT/'qualified-input-reviews.json').read_bytes()),
        classifierMetadataVectors=3,productTestsExecuted=0,targetClassLoaded=False,targetCompilation=False,
        coverage=None,wholeOracleQualified=False,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
