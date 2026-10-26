"""Five Main owner-null/window/immutable-index contexts, exact source or explicit statement reauthentication."""
from collections import Counter
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical

SOURCE = 'f24d1649e170e46aafb59a37b9750c602206364c'
OUT = data.BASE/'PG10922-main-null-owner-route-context-v1'
IDS = {'PMD-00346','PMD-02960','PMD-06145','PMD-06201','PMD-07371'}


def includes_once(text,fragment):
    values,needle = canonical(text),canonical(fragment)
    if sum(values[i:i+len(needle)] == needle for i in range(len(values)-len(needle)+1)) != 1:
        raise ValueError('one exact reviewed statement')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG10892-web-boundary-line-six-compile-v1/manifest.json',
        '345e989275ba9dd52da2356d303c7c1a818feeaf4a41244b6ba05b8e26bf2de9')
    hashes = normal['begin']['inputHashes']
    assert normal['source'] == SOURCE and normal['actualExit'] == 0
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
        '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    targets = [r for r in original if r['id'] in IDS]
    assert len(targets) == 5
    api = data.read_checked(data.BASE/'PG9095-api-ro-attempt-union-context-v1/manifest.json',
        '64157d793d00ab8222dd3380262e2cff6ceb2f32ef216565ca0ebb39f6ab7918')
    window = data.read_checked(data.BASE/'PG7058-monitoring-window-post-v1/manifest.json',
        'c36ed65e7fc8789a1306137c1bf44d13e44a325436541fc0f64ea474b7ce5e46')
    route = data.read_checked(data.BASE/'PG7096-web-http-metric-post-v1/manifest.json',
        'cbcb5c9821ccbcf05d9f73701e252c2a8a833773d6d3ca2614620a33f8c3d01a')
    legacy = data.read_checked(data.BASE/'PG5426-static-findings-v1/manifest.json',
        '41ddbd7c37b2bbcbc7ee69ef911c4743f59b29523559068581622c24efdb42bc')
    assert all(p['actualExit'] == 0 for p in (api,window,route,legacy))
    result = []
    for row in targets:
        path = row['path']
        after = (data.ROOT/path).read_text()
        assert data.sha(after.encode()) == hashes[path] == row['inputSha256']
        changed,statement = False,None
        if row['id'] == 'PMD-00346':
            prior_source = api['source']
            hits = [r for r in api['staticDispositions'] if r['sourcePath'] == path and r['raw']['rule'] == row['rule']]
            assert len(hits) == 1 and hits[0]['sourceSha256'] == hashes[path]
            assert {k:v for k,v in hits[0]['raw'].items() if k != 'message'} == row['attributes']
            before = subprocess.check_output(['git','show',prior_source+':'+path],cwd=data.ROOT)
            assert data.sha(before) == hashes[path]
            reason = hits[0]['reason']
            includes_once(after,'owned.close(); retained = null;')
            assert 'private @Nullable Connection retained;' in after and 'if (owned == null) return;' in after
            assert 'unconfirmed.set(true);' in after and 'throw close;' in after
            prior_proof = 'PG9095'
        elif row['id'] in ('PMD-02960','PMD-07371'):
            prior = window if row['id'] == 'PMD-02960' else route
            prior_source = prior['source']
            assert prior['sourceFiles'][path] == hashes[path]
            raw_hits = [r for r in prior['staticRaw']['pmd']['findings'] if r['rule'] == row['rule'] and
                {k:v for k,v in r.items() if k != 'message'} == row['attributes']]
            assert len(raw_hits) == 1
            if row['id'] == 'PMD-02960':
                assert 'private @Nullable Duration violationStart;' in after
                includes_once(after,'if (state != State.VIOLATING) { violationStart = null; return state == State.NORMAL ? Optional.of(Duration.ZERO) : Optional.empty(); }')
                reason = 'Private annotated nullable violation origin resets on NORMAL/UNKNOWN, Optional result never null; existing1562 exact contract.'
                prior_proof = 'PG7058/1562'
            else:
                includes_once(after,'private static final Map<String, Route> INDEX = index();')
                includes_once(after,'for (var route : values()) values.put(route.retainedTemplate, route); return Map.copyOf(values);')
                reason = 'Private static immutable INDEX built once by index factory from closed enum; existing1571 exact context, not mutable accessor.'
                prior_proof = 'PG7096/1571'
        else:
            changed = True
            hits = [r for r in legacy['findings'] if r['sourcePath'] == path and r['rule'] == 'NullAssignment']
            assert len(hits) == 1 and hits[0]['status'] == 'REQUIRED_CONTRACT'
            old = hits[0]
            prior_source = legacy['source']
            before = subprocess.check_output(['git','show',prior_source+':'+path],cwd=data.ROOT).decode()
            assert data.sha(before.encode()) == old['sourceSha256'] != hashes[path]
            if row['id'] == 'PMD-06145':
                fragment = 'var result = new InspectorAesCredential(version, decoded); decoded = null; return result;'
                for text in (before,after):
                    includes_once(text,fragment)
                    assert 'byte @Nullable [] decoded = null;' in text
                    includes_once(text,'if (decoded != null) Arrays.fill(decoded, (byte) 0);')
                before_body = before.split('public static InspectorAesCredential consume(',1)[1].split('private static IllegalArgumentException invalid(',1)[0]
                after_body = after.split('public static InspectorAesCredential consume(',1)[1].split('private static IllegalArgumentException invalid(',1)[0]
                includes_once(after,'private static final int AES_KEY_BYTES = 32;')
                after_tokens = canonical(after_body)
                assert after_tokens.count('AES_KEY_BYTES') == 1
                expanded = []
                for token in after_tokens:
                    expanded.extend(canonical('32') if token == 'AES_KEY_BYTES' else [token])
                assert canonical(before_body) == expanded
                body_hash = data.sha('\n'.join(expanded).encode())
            else:
                fragment = 'Session current = pending; if (current != null && current.closed()) pending = null;'
                for text in (before,after):
                    includes_once(text,fragment)
                    assert 'private @Nullable Session pending;' in text
                assert '|| pending != null' in after and 'pending = session;' in after
                body_hash = None
            statement = dict(priorWholeSourceSha256=old['sourceSha256'],currentWholeSourceSha256=hashes[path],
                statementTokenSha256=data.sha('\n'.join(canonical(fragment)).encode()),consumeWholeMethodTokenSha256=body_hash,
                priorCoordinates={k:old[k] for k in ('beginline','endline','begincolumn','endcolumn')},
                oldFindingId=old['findingId'],priorTechnicalDisposition=old['status'])
            reason = old['reason']
            prior_proof = 'PG5426/1108'
        result.append(dict(id=row['id'],source=SOURCE,path=path,sourceSha256=hashes[path],rule=row['rule'],
            attributes=row['attributes'],originalRowSha256=row['rowSha256'],reason=reason,priorSource=prior_source,
            priorProof=prior_proof,sourceRebindMode='CHANGED_SOURCE_STATEMENT_REAUTHENTICATION' if changed else 'EXACT_WHOLE_SOURCE_REUSE',
            statementBinding=statement,technicalDisposition='EXPLICIT_NECESSARY_SOURCE_CONTRACT',
            status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',currentWholeCaseRefs=[],priorRuntimeReassigned=False,
            newProductExecutions=0,newCoverage=None,scopeGeneralized=False,rawWarningRetained=True))
    assert Counter(r['sourceRebindMode'] for r in result) == Counter(EXACT_WHOLE_SOURCE_REUSE=3,CHANGED_SOURCE_STATEMENT_REAUTHENTICATION=2)
    decision = data.ROOT/'documents/400_PGPT/440_判断/441_実装判断記録.md'
    assert '## PG-D687' in decision.read_text()
    previous = data.read_checked(data.BASE/'PG10916-main-null-crypto-resource-context-v1/manifest.json',
        'd41f3747340987cf0a408a71e2224b07b9ec5f08664b79f687b75b240f19492d')
    old_contexts = data.read_checked(data.BASE/'PG10916-main-null-crypto-resource-context-v1/contexts.json',previous['contextsSha256'])
    assert not IDS & {r['id'] for r in old_contexts}
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'contexts.json',result)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        contextsSha256=data.sha((OUT/'contexts.json').read_bytes()),priorLayerManifestSha256='d41f3747340987cf0a408a71e2224b07b9ec5f08664b79f687b75b240f19492d',
        findings=5,wholeSourceExactReuse=3,changedSourceStatementReauthentication=2,
        judgement='PG-D687',judgementDocumentSha256=data.sha(decision.read_bytes()),
        sourceDerivedRaw=9248,referencedRows=2696,currentWholePending=16,noCurrentReference=6552,
        rawWarningsRemoved=0,newMainOrTestChanges=0,productTestsExecuted=0,coverage=None,wholeF03Accepted=False,
        externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
