"""Independent XML/span/token/case binding and eight metadata negatives; no Product run."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match
import pg13620_lgs_current_thread_context as primary

OUT = data.BASE/'PG13622-lgs-current-thread-context-post-v1'
PIN = '4cc2f88c51a5c9823fe3d0d19902e8e4daf13eb886e0bbba3f565992d6304199'

def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    m = data.read_checked(primary.OUT/'manifest.json', PIN)
    review = data.read_checked(primary.OUT/'review.json', m['reviewSha256'])
    host = data.read_checked(data.BASE/primary.PT[0]/'manifest.json', primary.PT[1])
    sp = data.BASE/primary.STATIC[0]
    st = data.read_checked(sp/'manifest.json', primary.STATIC[1])
    raw = (sp/'pmd.xml').read_bytes()
    assert data.sha(raw) == st['reports']['pmd'] and st['rawStatic'] == 2
    actual = [(str(Path(f.get('name')).relative_to(data.ROOT)), n) for f in ET.fromstring(raw)
              if f.tag.rpartition('}')[2] == 'file' for n in f if n.tag.rpartition('}')[2] == 'violation']
    root = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
                            '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    mapped = {(p, tuple(sorted(n.attrib.items()))): original_match(p, n, root, actual) for p, n in actual}
    assert host['source'] == review['source'] == m['source'] == primary.SOURCE and host['actualExit'] == 0
    run = data.ROOT.parent/'pgpt-runs/PG379/pg13604-lgs-remaining-whole-eight-pt-v1'
    xml_cases = []
    for name, pin in host['xmlHashes'].items():
        path = run/'xml'/name
        assert data.sha(path.read_bytes()) == pin
        parsed = ET.parse(path).getroot()
        assert int(parsed.get('tests')) == 8 and all(int(parsed.get(k)) == 0 for k in ['failures', 'errors', 'skipped'])
        for case in parsed.findall('testcase'):
            assert not list(case)
            xml_cases.append((case.get('classname'), case.get('name')))
    assert len(xml_cases) == len(set(xml_cases)) == 8

    def validate(row):
        path = row['path']
        a = row['attributes']
        text = (data.ROOT/path).read_text()
        lines = text.splitlines(keepends=True)
        start = sum(map(len, lines[:int(a['beginline'])-1])) + int(a['begincolumn'])-1
        end = sum(map(len, lines[:int(a['endline'])-1])) + int(a['endcolumn'])
        ts = [(t.group(), t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//', '/*'))]
        i = next(i for i, (_, p) in enumerate(ts) if p == start)
        ma, mb, name = min((s for s in functions(ts) if s[0] <= i <= s[1]), key=lambda s:s[1]-s[0])
        compact = ''.join(t for t, _ in ts[ma:mb+1])
        case, = [c for c in host['cases'] if c['name'] == name]
        identity = mapped[(path, tuple(sorted(a.items())))]
        expected = dict(id=identity['id'], originalRowSha256=identity['rowSha256'], rule='DoNotUseThreads',
            source=primary.SOURCE, sourceSha256=host['begin']['sourceHashes'][path],
            sourceSpanSha256=data.sha(text[start:end].encode()), method=name,
            methodTokenSha256=data.sha('\0'.join(t for t, _ in ts[ma:mb+1]).encode()), currentCase=case,
            kind='OWN_FINITE64_MEMORY_CALLBACK_TASKS', disposition='CONTEXT_NOT_APPLICABLE', reason=primary.REASON,
            previousReferenceRetainedAsHistorical=True, newSourceReason=False, currentWholeJoinPending=True,
            productTestsExecutedByReview=0, oldRuntimeReassigned=False)
        if any(row.get(k) != v for k, v in expected.items()):
            raise ValueError('exact current source, diagnostic span, method and original case required')
        assert data.sha(text.encode()) == expected['sourceSha256'] == st['candidateSourceHashes'][path]
        assert name == 'web276ConcurrentRequests' and all(s in compact for s in ['try(varpool=Executors.newFixedThreadPool(8))', 'i<64', 'pool.submit(', 'future.get()', 'assertEquals(64,observed.size())', 'assertEquals(0,wire.pendingCount())'])
        assert (case['classname'], name) in xml_cases and case['result'] == 'PASS'

    rows = review['rows']
    assert len(rows) == len(mapped) == 2 and {r['id'] for r in rows} == {'PMD-08082', 'PMD-08083'}
    for row in rows:
        validate(row)
    labels = []
    for field, value in [('source', '0'*40), ('oldRuntimeReassigned', True), ('reason', ''),
                         ('sourceSpanSha256', '0'*64), ('method', 'foreign'), ('currentCase', {}),
                         ('disposition', 'SUPPRESSED'), ('currentWholeJoinPending', False)]:
        bad = copy.deepcopy(rows[0])
        bad[field] = value
        assert bad != rows[0]
        try:
            validate(bad)
        except ValueError:
            labels.append(field)
        else:
            raise AssertionError('invalid current source context accepted')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json', dict(actualExit=0, source=primary.SOURCE, invocation=invocation,
        reviewManifestSha256=PIN, sourceContexts=2, rawRetained=2, newSourceReasons=0,
        metadataNegativeVectors=len(labels), labels=labels, productTestsExecuted=0,
        globalJoinPendingUnchanged=2488, coverage=None, newAccepted=0, formalUpdated=False, whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
