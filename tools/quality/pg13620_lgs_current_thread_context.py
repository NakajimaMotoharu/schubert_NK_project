"""Current two standalone JUnit thread references, raw retained and global join still pending."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match

SOURCE = '17ab52b253282ce45016f0586c0167a22029fd8c'
OUT = data.BASE/'PG13620-lgs-current-thread-context-v1'
STATIC = ('PG13594-lgs-remaining-two-branches-v1', 'f1dc83806c95332d3095bf117d11b725998aa68ff9674371d1fd866eb1fadf12')
PT = ('PG13604-lgs-remaining-whole-eight-pt-v1', '435f90a3c03be3755a5f1886b979497d1aedc4dc64a454e1edc282929e4f9485')
REASON = ('The J2EE application-thread restriction does not apply to this isolated JavaSE JUnit fixture. '
          'Eight TWR-owned workers execute exactly64 finite own-memory callback exchanges; every Future is joined and pending0 is asserted. '
          'Future.get has no individual timeout; Product exchanges are bounded by the fixed2second wait and the selected JVM has180second timeout. '
          'Current whole8 and independent single-session CRC evidence cover these inputs/schedules only, not all schedules or service ownership. '
          'No broker, database, network, native, Root or actual authentication/credential operation is performed.')

def review():
    host = data.read_checked(data.BASE/PT[0]/'manifest.json', PT[1])
    assert host['source'] == SOURCE and host['actualExit'] == 0 and len(host['cases']) == 8
    sp = data.BASE/STATIC[0]
    static = data.read_checked(sp/'manifest.json', STATIC[1])
    raw = (sp/'pmd.xml').read_bytes()
    assert data.sha(raw) == static['reports']['pmd'] and static['rawStatic'] == 2 and static['rawStaticGateExit'] == 1
    actual = [(str(Path(f.get('name')).relative_to(data.ROOT)), n) for f in ET.fromstring(raw)
              if f.tag.rpartition('}')[2] == 'file' for n in f if n.tag.rpartition('}')[2] == 'violation']
    root = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
                            '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    rows = []
    for path, node in actual:
        identity = original_match(path, node, root, actual)
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == host['begin']['sourceHashes'][path] == static['candidateSourceHashes'][path]
        a = node.attrib
        assert a['rule'] == 'DoNotUseThreads'
        lines = text.splitlines(keepends=True)
        start = sum(map(len, lines[:int(a['beginline'])-1])) + int(a['begincolumn'])-1
        end = sum(map(len, lines[:int(a['endline'])-1])) + int(a['endcolumn'])
        ts = [(m.group(), m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//', '/*'))]
        i = next(i for i, (_, p) in enumerate(ts) if p == start)
        ma, mb, name = min((s for s in functions(ts) if s[0] <= i <= s[1]), key=lambda s:s[1]-s[0])
        compact = ''.join(t for t, _ in ts[ma:mb+1])
        assert name == 'web276ConcurrentRequests'
        assert all(value in compact for value in ['try(varpool=Executors.newFixedThreadPool(8))', 'i<64', 'pool.submit(', 'future.get()', 'assertEquals(64,observed.size())', 'assertEquals(0,wire.pendingCount())'])
        case, = [c for c in host['cases'] if c['name'] == name]
        assert case['classname'] == 'dev.codex.schubert.nk.web.messaging.LogSearchWireClientTest' and case['result'] == 'PASS'
        rows.append(dict(id=identity['id'], path=path, rule=a['rule'], attributes=dict(a), originalRowSha256=identity['rowSha256'],
            source=SOURCE, sourceSha256=data.sha(text.encode()), sourceSpanSha256=data.sha(text[start:end].encode()),
            method=name, methodTokenSha256=data.sha('\0'.join(t for t, _ in ts[ma:mb+1]).encode()),
            currentCase=case, kind='OWN_FINITE64_MEMORY_CALLBACK_TASKS', disposition='CONTEXT_NOT_APPLICABLE', reason=REASON,
            previousReferenceRetainedAsHistorical=True, newSourceReason=False, currentWholeJoinPending=True,
            productTestsExecutedByReview=0, oldRuntimeReassigned=False))
    assert len(rows) == 2 and {r['id'] for r in rows} == {'PMD-08082', 'PMD-08083'}
    return rows

if __name__ == '__main__':
    invocation = capture(__file__)
    assert not OUT.exists()
    rows = review()
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'review.json', dict(source=SOURCE, rows=rows))
    data.write(OUT/'manifest.json', dict(actualExit=0, source=SOURCE, invocation=invocation,
        reviewSha256=data.sha((OUT/'review.json').read_bytes()), sourceContexts=2, rawRetained=2,
        newSourceReasons=0, productTestsExecuted=0, oldRuntimeReassigned=False,
        globalJoinPendingUnchanged=2488, newAccepted=0, whole451Accepted=False, wholeF03Accepted=False, coverage=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
