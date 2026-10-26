"""Direct enum member inputs only; not wire mapping, fixture, auth or broker validation."""
from collections import Counter
import json
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10519_constructor_carrier_review_v2 import first_argument
from pg10652_qualified_constructor_inputs import unresolved_names

OUT = data.BASE/'PG10658-direct-enum-constructor-inputs-v1'
ENUMS = {
    'Role': ('dev.codex.schubert.nk.api.domain.Role',
        'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/domain/Role.java',('ADMIN','USER')),
    'ResultCode': ('dev.codex.schubert.nk.protocol.header.ResultCode',
        'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/header/ResultCode.java',('AUTHENTICATION_FAILED','LOCKED')),
    'ArtemisQueuePressureClient.Pressure': ('dev.codex.schubert.nk.batch.mq.ArtemisQueuePressureClient.Pressure',
        'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/mq/ArtemisQueuePressureClient.java',('NORMAL','WARNING')),
}


def references(expression):
    refs = []
    for qualifier,(_,_,members) in ENUMS.items():
        for member in members:
            tokens = []
            for i,part in enumerate((qualifier+'.'+member).split('.')):
                if i:
                    tokens.append('.')
                tokens.append(part)
            refs.append((tokens,qualifier,member))
    result,used = [],[]
    i = 0
    while i < len(expression):
        match = next(((tokens,q,m) for tokens,q,m in refs if [x[0] for x in expression[i:i+len(tokens)]] == tokens),None)
        if match is None:
            result.append(expression[i])
            i += 1
        else:
            tokens,q,m = match
            result.append(('true',expression[i][1],expression[i+len(tokens)-1][2]))
            used.append((q,m))
            i += len(tokens)
    return result,used


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    prior_path = data.BASE/'PG10652-qualified-constructor-inputs-v1/manifest.json'
    prior = data.read_checked(prior_path,'fbbf406acd3b6361fe5f27fb1636da77b16a817015e27cd9b43c807171ea9983')
    candidates = data.read_checked(prior_path.parent/'qualified-input-reviews.json',prior['qualifiedInputReviewsSha256'])
    first = data.read_checked(data.BASE/'PG10646-constructor-literal-inputs-v1/manifest.json',
        'a2f3823325d625a7d64ac2aad13cfe027a0497a7552ec9d23c61f32060710b55')
    originals = data.read_checked(data.BASE/'PG10646-constructor-literal-inputs-v1/input-reviews.json',first['inputReviewsSha256'])
    body_path = data.BASE/'PG10588-record-constructor-review-v1/manifest.json'
    body = data.read_checked(body_path,'7ac388609456e216a0f9be08e02855d2fa691ff8089a1a46eb745b0d38c9866f')
    bodies = {b['owner']:b for b in data.read_checked(body_path.parent/'constructor-reviews.json',body['reviewsSha256'])}
    normal = data.read_checked(data.BASE/'PG10632-query-semantic-constant-compile-v1/manifest.json',
        '8f29215a400d24a55ecabee90c74fb72a43525b740f129a12ae6053559701f87')
    definitions = {}
    for qualifier,(name,path,members) in ENUMS.items():
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == normal['begin']['inputHashes'][path]
        block = re.search(r'\benum\s+'+qualifier.split('.')[-1]+r'\s*\{([^}]*)\}',text,re.S)
        assert block and all(re.search(r'^\s*'+m+r'\s*(?:,|\(|$)',block[1],re.M) for m in members)
        definitions[qualifier] = dict(qualifiedType=name,path=path,sha256=data.sha(text.encode()),selectedMembers=list(members))
    rows,counts = [],Counter()
    for index,candidate in enumerate(candidates):
        if candidate['status'] != 'NAMED_INPUT_ORIGIN_PENDING':
            continue
        row = originals[candidate['priorEntryIndex']]['original']
        path = row['path']
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == row['sourceSha256'] == normal['begin']['inputHashes'][path]
        expression = first_argument(text,row)
        masked,used = references(expression)
        names,heads = unresolved_names(masked,row['expectedConstructorTypes'])
        selected = not names and bool(used)
        result = dict(priorQualifiedIndex=index,priorQualifiedSha256=data.sha(json.dumps(candidate,sort_keys=True,ensure_ascii=False).encode()),
            key=candidate['key'],sourceSha256=row['sourceSha256'],directEnumReferences=used,unresolvedInputNames=names,
            status='DIRECT_ENUM_AND_LITERAL_INPUTS_STATIC_REVIEWED' if selected else 'NAMED_INPUT_ORIGIN_PENDING',
            productTestsExecuted=0,wholeCaseFixtureQualified=False)
        if selected:
            for qualifier,_ in used:
                qualified,_,_ = ENUMS[qualifier]
                simple = qualifier.split('.')[0]
                assert not re.search(r'\b(?:class|record|interface|enum)\s+'+simple+r'\b',text)
                assert not re.search(r'\b(?:var|'+simple+r')\s+'+simple+r'\b',text)
                if qualifier in ('Role','ResultCode'):
                    assert 'import '+qualified+';' in text
                else:
                    assert 'package dev.codex.schubert.nk.batch.mq;' in text
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
    assert len(rows) == 51 and counts == {'DIRECT_ENUM_AND_LITERAL_INPUTS_STATIC_REVIEWED':13,'NAMED_INPUT_ORIGIN_PENDING':38}
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'enum-input-reviews.json',rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=normal['source'],invocation=invocation,
        priorManifestSha256=data.sha(prior_path.read_bytes()),enumDefinitions=definitions,selectedCandidates=51,
        counts=dict(counts),newEnumInputSites=13,previousFixedInputSitesNotNew=49,previousCorrectedSitesNotNew=2,
        remainingNamedInputs=38,remainingMethodInputs=66,rowsSha256=data.sha((OUT/'enum-input-reviews.json').read_bytes()),
        productTestsExecuted=0,targetClassLoaded=False,targetCompilation=False,coverage=None,
        wholeOracleQualified=False,wireMappingQualified=False,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
