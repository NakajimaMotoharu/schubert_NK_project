"""Independent exact Main nullable-state and immutable factory references; no dynamic owner verification."""
import copy
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical

SOURCE = 'f24d1649e170e46aafb59a37b9750c602206364c'
OUT = data.BASE/'PG10924-main-null-owner-route-post-v1'
IDS = {'PMD-00346','PMD-02960','PMD-06145','PMD-06201','PMD-07371'}


def contract(rows,original,hashes):
    if len(rows) != 5 or {r['id'] for r in rows} != IDS:
        raise ValueError('exact five original findings')
    for row in rows:
        old = original[row['id']]
        if row['source'] != SOURCE or row['path'] != old['path'] or row['sourceSha256'] != hashes.get(row['path']) or row['sourceSha256'] != old['inputSha256']:
            raise ValueError('exact whole current input')
        if row['attributes'] != old['attributes'] or row['rule'] != old['rule'] or row['originalRowSha256'] != old['rowSha256']:
            raise ValueError('original raw coordinates/rule')
        if row['status'] != 'SOURCE_REBOUND_CURRENT_WHOLE_PENDING' or row['currentWholeCaseRefs'] != [] or row['priorRuntimeReassigned'] is not False:
            raise ValueError('old source runtime not current qualification')
        if row['newProductExecutions'] != 0 or row['newCoverage'] is not None or row['scopeGeneralized'] is not False or row['rawWarningRetained'] is not True or not row['reason']:
            raise ValueError('only exact explicit review, no execution/suppression')
        expected_mode = 'CHANGED_SOURCE_STATEMENT_REAUTHENTICATION' if row['id'] in ('PMD-06145','PMD-06201') else 'EXACT_WHOLE_SOURCE_REUSE'
        if row['sourceRebindMode'] != expected_mode:
            raise ValueError('changed source and exact source are different')


def one(tokens,fragment):
    needle = canonical(fragment)
    return sum(tokens[i:i+len(needle)] == needle for i in range(len(tokens)-len(needle)+1)) == 1


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    path = data.BASE/'PG10922-main-null-owner-route-context-v1/manifest.json'
    primary = data.read_checked(path,'9360be53ed58a1cf468f0968ca1b91b51fe288a4e217b6576fd342e6c1a88480')
    rows = data.read_checked(path.parent/'contexts.json',primary['contextsSha256'])
    raw = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
        '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    original = {r['id']:r for r in raw}
    normal = data.read_checked(data.BASE/'PG10892-web-boundary-line-six-compile-v1/manifest.json',
        '345e989275ba9dd52da2356d303c7c1a818feeaf4a41244b6ba05b8e26bf2de9')
    hashes = normal['begin']['inputHashes']
    assert primary['actualExit'] == 0 and primary['source'] == normal['source'] == SOURCE
    contract(rows,original,hashes)
    evidence_pins = {
        'PG9095-api-ro-attempt-union-context-v1':'64157d793d00ab8222dd3380262e2cff6ceb2f32ef216565ca0ebb39f6ab7918',
        'PG7058-monitoring-window-post-v1':'c36ed65e7fc8789a1306137c1bf44d13e44a325436541fc0f64ea474b7ce5e46',
        'PG7096-web-http-metric-post-v1':'cbcb5c9821ccbcf05d9f73701e252c2a8a833773d6d3ca2614620a33f8c3d01a',
        'PG5426-static-findings-v1':'41ddbd7c37b2bbcbc7ee69ef911c4743f59b29523559068581622c24efdb42bc'}
    proofs = {name:data.read_checked(data.BASE/name/'manifest.json',digest) for name,digest in evidence_pins.items()}
    line_fragments = {
        'PMD-00346':'retained = null;',
        'PMD-02960':'violationStart = null;',
        'PMD-06145':'decoded = null;',
        'PMD-06201':'pending = null;',
        'PMD-07371':'private static final Map<String, Route> INDEX = index();'}
    for row in rows:
        after = (data.ROOT/row['path']).read_text()
        assert data.sha(after.encode()) == row['sourceSha256']
        line = after.splitlines()[int(row['attributes']['beginline'])-1]
        assert one(canonical(line),line_fragments[row['id']])
        before = subprocess.check_output(['git','show',row['priorSource']+':'+row['path']],cwd=data.ROOT)
        if row['sourceRebindMode'] == 'EXACT_WHOLE_SOURCE_REUSE':
            assert data.sha(before) == row['sourceSha256'] and row['statementBinding'] is None
        else:
            binding = row['statementBinding']
            assert data.sha(before) == binding['priorWholeSourceSha256'] != binding['currentWholeSourceSha256'] == row['sourceSha256']
            fragment = ('var result = new InspectorAesCredential(version, decoded); decoded = null; return result;'
                if row['id'] == 'PMD-06145' else 'Session current = pending; if (current != null && current.closed()) pending = null;')
            assert one(canonical(before.decode()),fragment) and one(canonical(after),fragment)
            assert data.sha('\n'.join(canonical(fragment)).encode()) == binding['statementTokenSha256']
            if row['id'] == 'PMD-06145':
                # Verify the single same-value numeric alias independently of source generator.
                assert one(canonical(after),'private static final int AES_KEY_BYTES = 32;')
                old_method = before.decode().split('public static InspectorAesCredential consume(',1)[1].split('private static IllegalArgumentException invalid(',1)[0]
                new_method = after.split('public static InspectorAesCredential consume(',1)[1].split('private static IllegalArgumentException invalid(',1)[0]
                values = canonical(new_method)
                sites = [i for i,v in enumerate(values) if v == 'AES_KEY_BYTES']
                assert len(sites) == 1
                i = sites[0]
                values[i:i+1] = canonical('32')
                assert values == canonical(old_method)
                assert data.sha('\n'.join(values).encode()) == binding['consumeWholeMethodTokenSha256']
                assert one(canonical(after),'if (decoded != null) Arrays.fill(decoded, (byte) 0);')
            else:
                assert binding['consumeWholeMethodTokenSha256'] is None
                assert 'private @Nullable Session pending;' in after and '|| pending != null' in after
    assert all(p['actualExit'] == 0 for p in proofs.values())
    previous = data.read_checked(data.BASE/'PG10916-main-null-crypto-resource-context-v1/manifest.json',primary['priorLayerManifestSha256'])
    assert primary['referencedRows'] == previous['referencedRowsAfter']+5 == 2696
    assert primary['currentWholePending'] == previous['currentWholePendingAfter']+5 == 16
    assert primary['noCurrentReference'] == previous['noCurrentReferenceAfter']-5 == 6552
    bads = [rows[:-1],rows+[rows[0]]]
    for field,value in [('sourceSha256','0'*64),('source','old'),('status','PASS'),('currentWholeCaseRefs',['old-case']),
                        ('priorRuntimeReassigned',True),('newCoverage',100),('sourceRebindMode','EXACT_WHOLE_SOURCE_REUSE')]:
        bad = copy.deepcopy(rows)
        target = next(r for r in bad if r['id'] == 'PMD-06145')
        target[field] = value
        try: contract(bad,original,hashes)
        except ValueError: bads.append(bad)
        else: raise AssertionError('forged/source-transfer metadata accepted')
    for bad in bads[:2]:
        try: contract(bad,original,hashes)
        except ValueError: pass
        else: raise AssertionError('missing/duplicate finding accepted')
    assert len(bads) == 9
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        primaryManifestSha256=data.sha(path.read_bytes()),contextsSha256=primary['contextsSha256'],originalEvidencePins=evidence_pins,
        findings=5,exactWholeSourceReuse=3,changedSourceStatementReauthentication=2,metadataNegativeVectors=9,
        sourceDerivedRaw=9248,referencedRows=2696,currentWholePending=16,noCurrentReference=6552,
        wholeF03Accepted=False,productTestsExecuted=0,coverage=None,newAccepted=0,formalUpdated=False,effortPercent=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
