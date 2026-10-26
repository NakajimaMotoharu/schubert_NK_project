"""Literal arguments behind exact imported JDK callees only; no Product execution."""
from collections import Counter
import json
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10519_constructor_carrier_review_v2 import first_argument
from pg10652_qualified_constructor_inputs import unresolved_names

OUT = data.BASE/'PG10670-jdk-factory-constructor-inputs-v1'
IMPORTS = {'Optional':'java.util.Optional','List':'java.util.List','Instant':'java.time.Instant',
    'UUID':'java.util.UUID','Duration':'java.time.Duration','Path':'java.nio.file.Path'}
METHODS = {'Optional.of','Optional.empty','List.of','Instant.parse','UUID.fromString','Duration.ofSeconds','Path.of'}


def mask_jdk(expression):
    result,used = [],[]
    i = 0
    while i < len(expression):
        values = [v for v,_,_ in expression[i:i+3]]
        joined = ''.join(values)
        if len(values) == 3 and joined in METHODS and i+3 < len(expression) and expression[i+3][0] == '(':
            result.append(('true',expression[i][1],expression[i+2][2]))
            used.append(joined)
            i += 3
        elif len(values) == 3 and values[0].startswith('"') and values[1:] == ['.','repeat'] and i+3 < len(expression) and expression[i+3][0] == '(':
            result.append((values[0],expression[i][1],expression[i+2][2]))
            used.append('LITERAL_STRING.repeat')
            i += 3
        else:
            result.append(expression[i])
            i += 1
    return result,used


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    prior_path = data.BASE/'PG10646-constructor-literal-inputs-v1/manifest.json'
    prior = data.read_checked(prior_path,'a2f3823325d625a7d64ac2aad13cfe027a0497a7552ec9d23c61f32060710b55')
    entries = data.read_checked(prior_path.parent/'input-reviews.json',prior['inputReviewsSha256'])
    body_path = data.BASE/'PG10588-record-constructor-review-v1/manifest.json'
    body = data.read_checked(body_path,'7ac388609456e216a0f9be08e02855d2fa691ff8089a1a46eb745b0d38c9866f')
    bodies = {b['owner']:b for b in data.read_checked(body_path.parent/'constructor-reviews.json',body['reviewsSha256'])}
    normal = data.read_checked(data.BASE/'PG10632-query-semantic-constant-compile-v1/manifest.json',
        '8f29215a400d24a55ecabee90c74fb72a43525b740f129a12ae6053559701f87')
    rows,counts = [],Counter()
    for index,entry in enumerate(entries):
        if entry['status'] != 'METHOD_INPUT_ORIGIN_PENDING':
            continue
        row = entry['original']
        path = row['path']
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == row['sourceSha256'] == normal['begin']['inputHashes'][path]
        expression = first_argument(text,row)
        masked,used = mask_jdk(expression)
        names,heads = unresolved_names(masked,row['expectedConstructorTypes'])
        selected = not names and bool(used)
        result = dict(priorEntryIndex=index,priorEntrySha256=data.sha(json.dumps(entry,sort_keys=True,ensure_ascii=False).encode()),
            key={k:row[k] for k in ('path','method','line','expectedExpressionSha256')},sourceSha256=row['sourceSha256'],
            jdkCallees=used,unresolvedInputNames=names,
            status='LITERAL_JDK_FACTORY_INPUTS_STATIC_REVIEWED' if selected else 'METHOD_OR_NAMED_INPUT_ORIGIN_PENDING',
            productTestsExecuted=0,wholeCaseFixtureQualified=False)
        if selected:
            for callee in set(used):
                if callee == 'LITERAL_STRING.repeat':
                    continue
                simple = callee.split('.')[0]
                assert 'import '+IMPORTS[simple]+';' in text
                assert not re.search(r'\b(?:class|record|interface|enum)\s+'+simple+r'\b',text)
                assert not re.search(r'\b(?:var|'+simple+r')\s+'+simple+r'\b',text)
            contracts = []
            for head in heads:
                binding = row['assertionSpanConstructorBindings'][head]
                owner, = binding['owners']
                item = bodies[owner]
                assert binding['mainSourceBinding'] is not None and '/src/main/java/' in item['source']
                assert item['review']['kind'] != 'NONRECORD_EXCEPTION_REVIEWED_SEPARATELY_NOT_VALUE_ORACLE'
                assert data.sha((data.ROOT/item['source']).read_bytes()) == item['sourceSha256'] == normal['begin']['inputHashes'][item['source']]
                contracts.append(item)
            result['valuePreservingConstructorReferences'] = contracts
        counts[result['status']] += 1
        rows.append(result)
    assert len(rows) == 66 and counts == {'LITERAL_JDK_FACTORY_INPUTS_STATIC_REVIEWED':20,'METHOD_OR_NAMED_INPUT_ORIGIN_PENDING':46}
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'jdk-input-reviews.json',rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=normal['source'],invocation=invocation,
        priorManifestSha256=data.sha(prior_path.read_bytes()),candidateRows=66,counts=dict(counts),newFixedJdkInputSites=20,
        previous99AndTwoCorrectedNotRecounted=True,remainingMethodOrNamedInputs=46,callbackPropertyStillUnqualified=1,
        rowsSha256=data.sha((OUT/'jdk-input-reviews.json').read_bytes()),productTestsExecuted=0,
        targetClassLoaded=False,targetCompilation=False,coverage=None,wholeOracleQualified=False,
        externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
