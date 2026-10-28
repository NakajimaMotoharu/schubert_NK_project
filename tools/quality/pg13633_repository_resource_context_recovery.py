"""Exact same-byte Main TWR ownership context, not an execution or old runtime transfer."""
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from f03_literal_batch_sources import tokens
from pg11370_source_constructor_owner_audit import functions, close
from public_java_digest_provenance import LEX
from pg11054_api_request_context import original_match
from trace_owner_join import canonical

SOURCE = '17ab52b253282ce45016f0586c0167a22029fd8c'
OUT = data.BASE/'PG13633-repository-resource-context-recovery-v2'
NORMAL = ('PG13596-lgs-remaining-two-branches-v1', '1f1ff5bbdec9107bc7ce9f4a91ab202a1ddeb65b22b0d978c9c3eaf388ad1a12')
MEASURED = ('PG13253-current-all-java-static-v2', '751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
BASE = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/persistence/'
PATHS = {BASE+'AsyncJobCountRepository.java': 'e337ab556b1e6b7033626ab57740c11f4b13e35ae446a582f20f41f344f66b76',
         BASE+'OutboxObservationRepository.java': '90b0d76c02ba974dc22034fe8a13003fb93298105b5f3b3e53f1f90d99544f16'}
REASON = ('The acquired PS and RS aliases have exact null rejection followed immediately by nested Java9 try(variable) ownership. '
          'TWR closes every nonnull acquisition on normal, checked, unchecked and fatal exit, with RS before PS and language-defined suppression. '
          'Null return has no acquired object; borrowed Connection is neither configured nor closed. '
          'No resource leak is evidenced by these four declarations. PMD raw findings remain visible; internal analyzer cause is not established. '
          'This is exact-source static ownership reasoning, not live DB/role qualification or current-source runtime/coverage.')

def ownership(text):
    ts = [(m.group(), m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//', '/*'))]
    scope, = [s for s in functions(ts) if s[2] == 'read']
    a, b, _ = scope
    body = [t for t, _ in ts[a:b+1]]
    compact = ''.join(body)
    assert 'connection.prepareStatement(SQL)' in compact and compact.count('connection.prepareStatement(') == 1
    assert compact.count('statement.executeQuery()') == 1
    assert not any(s in compact for s in ['connection.close(', 'connection.commit(', 'connection.rollback(', 'connection.set', 'DriverManager', 'getConnection('])
    patterns = [tokens('@Nullable PreparedStatement statement = connection.prepareStatement(SQL); if (statement == null) throw new SQLException(INVALID); try (statement) {'),
                tokens('@Nullable ResultSet rows = statement.executeQuery(); if (rows == null) throw new SQLException(INVALID); try (rows) {')]
    spans = []
    for pattern in patterns:
        at, = [i for i in range(len(body)) if body[i:i+len(pattern)] == pattern]
        opening = a+at+len(pattern)-1
        end = close(ts, opening, '{', '}')
        spans.append((opening, end))
    assert spans[0][0] < spans[1][0] < spans[1][1] < spans[0][1]
    assert all(t != 'return' for t, _ in ts[spans[0][0]:spans[0][1]+1])
    return dict(method='read', methodTokenSha256=data.sha('\0'.join(body).encode()),
                nestedOwnerTokenSpans=spans, acquisitionAndGuardOrderVerified=True,
                borrowedConnectionNotModified=True, returnAfterResources=True)

def review():
    n = data.read_checked(data.BASE/NORMAL[0]/'manifest.json', NORMAL[1])
    measured = data.read_checked(data.BASE/MEASURED[0]/'manifest.json', MEASURED[1])
    all_rows = data.read_checked(data.BASE/MEASURED[0]/'findings.json', measured['findingsSha256'])
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json', '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    assert n['source'] == SOURCE and n['actualExit'] == n['testsExecuted'] == 0
    assert measured['actualExit'] == 0 and measured['analysisComplete'] and not measured['processingErrors']
    logical = {r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    actual = []
    for item in all_rows:
        if item['path'] in PATHS:
            assert item['rule'] == 'CloseResource' and item['sourceSha256'] == PATHS[item['path']]
            node = ET.Element('violation', item['attributes'])
            node.text = item['message']
            actual.append((item['path'], node))
    assert len(actual) == 4
    rows = []
    for path, node in actual:
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == PATHS[path] == n['begin']['inputHashes'][path]
        identity = original_match(path, node, original, actual)
        owner = canonical(path, logical)
        assert owner['canonicalOwner'] == owner['canonicalCostOwner'] == 'WBS-P018-09'
        attrs = node.attrib
        lines = text.splitlines(keepends=True)
        start = sum(map(len, lines[:int(attrs['beginline'])-1])) + int(attrs['begincolumn'])-1
        end = sum(map(len, lines[:int(attrs['endline'])-1])) + int(attrs['endcolumn'])-1
        assert text[start:end] == attrs['variable'] and attrs['variable'] in ['statement', 'rows']
        rows.append(dict(id=identity['id'], path=path, source=SOURCE, sourceSha256=PATHS[path], attributes=dict(attrs),
            originalRowSha256=identity['rowSha256'], sourceSpanSha256=data.sha(text[start:end].encode()), spanConvention='PMD_1_ORIGIN_EXCLUSIVE_END_TO_PYTHON_HALF_OPEN', spanStartOffset=start, spanEndOffsetExclusive=end,
            ownership=ownership(text), **owner, disposition='CONTEXT_NOT_APPLICABLE', reason=REASON,
            rawRetained=True, currentWholeJoinPending=True, productTestsExecuted=0,
            historicalRuntimeTransferred=False, currentRuntimeQualification=False))
    assert {r['id'] for r in rows} == {'PMD-00386', 'PMD-00387', 'PMD-00388', 'PMD-00389'}
    return rows

if __name__ == '__main__':
    invocation = capture(__file__)
    assert not OUT.exists()
    rows = review()
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'review.json', dict(source=SOURCE, rows=rows))
    data.write(OUT/'manifest.json', dict(actualExit=0, source=SOURCE, invocation=invocation,
        reviewSha256=data.sha((OUT/'review.json').read_bytes()), sourceContexts=4, newSourceReasons=4,
        rawRetained=4, normalManifestSha256=NORMAL[1], measuredBaselineManifestSha256=MEASURED[1],
        productTestsExecuted=0, coverage=None, sourceChanged=False, newAccepted=0, formalUpdated=False, whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))
