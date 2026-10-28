"""Correct current LGS diagnostic span sidecars; preserve old extended-window witnesses and all PT."""
import copy
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pmd_source_span_ascii import span, selftest

SOURCE = '17ab52b253282ce45016f0586c0167a22029fd8c'
OUT = data.BASE/'PG13652-lgs-canonical-spans-v1'
LEGACY = ('PG13620-lgs-current-thread-context-v1', '4cc2f88c51a5c9823fe3d0d19902e8e4daf13eb886e0bbba3f565992d6304199')
LEGACY_POST = ('PG13622-lgs-current-thread-context-post-v1', 'b5f14c84a2ec006155445d089d5682742ae8ea45ecf63da42ad652297a576ac6')

def corrected_rows():
    m = data.read_checked(data.BASE/LEGACY[0]/'manifest.json', LEGACY[1])
    p = data.read_checked(data.BASE/LEGACY_POST[0]/'manifest.json', LEGACY_POST[1])
    legacy = data.read_checked(data.BASE/LEGACY[0]/'review.json', m['reviewSha256'])
    static = data.read_checked(data.BASE/'PG13594-lgs-remaining-two-branches-v1/manifest.json', 'f1dc83806c95332d3095bf117d11b725998aa68ff9674371d1fd866eb1fadf12')
    host = data.read_checked(data.BASE/'PG13604-lgs-remaining-whole-eight-pt-v1/manifest.json', '435f90a3c03be3755a5f1886b979497d1aedc4dc64a454e1edc282929e4f9485')
    assert host['source'] == m['source'] == p['source'] == legacy['source'] == SOURCE
    assert host['actualExit'] == m['actualExit'] == p['actualExit'] == 0 and p['reviewManifestSha256'] == LEGACY[1]
    rows = []
    for row in legacy['rows']:
        path = row['path']
        text = (data.ROOT/path).read_bytes().decode('utf-8')
        assert data.sha(text.encode()) == row['sourceSha256'] == static['candidateSourceHashes'][path] == host['begin']['sourceHashes'][path]
        start, end, value = span(text, row['attributes'])
        assert end < len(text) and row['sourceSpanSha256'] == data.sha(text[start:end+1].encode())
        assert data.sha(value.encode()) != row['sourceSpanSha256']
        assert row['currentCase'] in host['cases'] and row['currentCase']['result'] == 'PASS'
        preserved = copy.deepcopy(row)
        preserved['sourceSpanSha256'] = data.sha(value.encode())
        rows.append(dict(id=row['id'], path=path, source=SOURCE, sourceSha256=row['sourceSha256'],
            legacyReviewManifestSha256=LEGACY[1], legacyExtendedWindowSha256=row['sourceSpanSha256'],
            legacyWindowStartOffset=start, legacyWindowEndOffsetExclusive=end+1,
            canonicalSpanStartOffset=start, canonicalSpanEndOffsetExclusive=end,
            canonicalSpanSha256=data.sha(value.encode()), convention='PMD_1_ORIGIN_EXCLUSIVE_END_TO_PYTHON_HALF_OPEN',
            correctedContextWitness=preserved, dispositionReasonAndCaseUnchanged=True,
            rawRetained=True, currentWholeJoinPending=True, productTestsExecuted=0,
            oldResultsModified=False, oldRuntimeTransferred=False))
    assert len(rows) == 2 and {r['id'] for r in rows} == {'PMD-08082', 'PMD-08083'}
    return rows

if __name__ == '__main__':
    invocation = capture(__file__)
    assert not OUT.exists()
    vectors = selftest()
    rows = corrected_rows()
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'corrections.json', dict(source=SOURCE, rows=rows))
    data.write(OUT/'manifest.json', dict(actualExit=0, source=SOURCE, invocation=invocation,
        correctionsSha256=data.sha((OUT/'corrections.json').read_bytes()), correctedCurrentRows=2,
        legacyReviewManifestSha256=LEGACY[1], legacyPostManifestSha256=LEGACY_POST[1],
        spanToolVectors=vectors, rawRetained=2, productTestsExecuted=0, coverage=None,
        oldResultsModified=False, globalHorizontalExpansionComplete=False,
        joinedContextWarningsUnchanged=3353, currentWholeJoinPendingUnchanged=2492,
        newSourceReasons=0, newAccepted=0, formalUpdated=False, whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))
