"""Current12 raw Thread references: exact finite same-JVM fixture contracts, not suppression."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match
SOURCE='977214e4409e70bcf7c38dfd34bbaa384fc14c9b'
OUT=data.BASE/'PG12081-media-wire-fixture-context-v1'
def review():
    host=data.read_checked(data.BASE/'PG12076-media-wire-fixture-host-v1/manifest.json','1152f7f83f1bd58ef9cabdc8c804ad117241f7ecaa45662c9a17fe4698d3cc2a')
    assert host['source']==SOURCE and host['actualExit']==0 and host['observedTestExecutions']==24
    assert host['stages'][-1]['actualExit']==0 and not host['stages'][-1]['timedOut']
    sp=data.BASE/'PG12078-media-wire-fixture-static-v1';m=data.read_checked(sp/'manifest.json','9677642afbb43a6c36d4a5b8582343054217b99dcfaee948520bc51edbc13e9e')
    raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==m['reports']['pmd']['sha256'] and m['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');rows=[]
    for path,node in actual:
        ident=original_match(path,node,original,actual);text=(data.ROOT/path).read_text();assert data.sha(text.encode())==host['begin']['sourceInputHashes'][path]
        a=dict(node.attrib);assert a['rule']=='DoNotUseThreads';lines=text.splitlines(keepends=True)
        start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];i=next(i for i,(_,p) in enumerate(ts) if p==start)
        lo,hi,name=min((v for v in functions(ts) if v[0]<=i<=v[1]),key=lambda v:v[1]-v[0]);compact=''.join(t for t,_ in ts[lo:hi+1])
        if name=='web171TransportFailuresDoNotRetryOrLeakPending':
            assert all(s in compact for s in ('Thread.currentThread().interrupt();','Thread.interrupted();','Executors.newSingleThreadExecutor()','release.await(5,TimeUnit.SECONDS)','first.get(5,TimeUnit.SECONDS)','assertEquals(1,sends.get());','assertEquals(0,wire.pendingCount());'))
            kind='OWN_INTERRUPT_RESTORE_AND_SINGLE_CAPACITY_FIXTURE';reason='A dedicated JVM intentionally interrupts its current test thread, proves propagation, and clears it in finally. A TWR single worker with five-second latch/get bounds proves one-send capacity and pending0; it is an owned JavaSE fixture, not application-managed threading.'
        elif name=='web172ConcurrentQueriesKeepContextsAndRepliesSeparate':
            assert all(s in compact for s in ('Executors.newFixedThreadPool(8)','n<100','task.get(10,TimeUnit.SECONDS)','active.remove();','assertEquals(100,seen.size());','assertEquals(0,wire.pendingCount());'))
            kind='OWN_SCENARIO100_FINITE_CALLBACK_WORKERS';reason='Eight owned TWR JavaSE workers issue exactly100 in-memory callback exchanges with ten-second gets; per-worker context is removed in finally, IDs and response separation, erased requests and pending0 are asserted. No broker, DB, file, HTTP or service is called.'
        else:
            assert name in ('web244ConcurrentRequests','web260ConcurrentRequests') and all(s in compact for s in ('Executors.newFixedThreadPool(8)','i<64','future.get();','assertEquals(64,observed.size());','assertEquals(0,wire.pendingCount());'))
            kind='OWN_MEDIA64_CALLBACK_WORKERS_OUTER240';reason='Eight owned TWR JavaSE workers issue exactly64 in-memory callback exchanges and assert distinct IDs, success and pending0. Original future.get has no per-get deadline; it is preserved, not described as bounded locally. The owned launcher is limited to240 seconds and its actual successful terminal is verified. This does not qualify production scheduling or external JMS.'
        case=next(c for c in host['begin']['cases'] if c['path']==path and c['method']==name)
        assert any(c['classname']==case['className'] and c['name']==name and not c['nonPass'] for c in host['cases'])
        rows.append(dict(id=ident['id'],path=path,rule=a['rule'],attributes=a,originalRowSha256=ident['rowSha256'],source=SOURCE,sourceSha256=data.sha(text.encode()),sourceSpanSha256=data.sha(text[start:end].encode()),method=name,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),currentCase=case,kind=kind,disposition='CONTEXT_NOT_APPLICABLE',reason=reason,previousReferenceRetainedAsHistorical=True,newSourceReason=False,currentWholeJoinPending=True,productTestsExecutedByReview=0,oldRuntimeReassigned=False))
    assert len(rows)==len({r['id'] for r in rows})==12;return rows
def main():
    invocation=capture(__file__);assert not OUT.exists();rows=review();verify(invocation);OUT.mkdir()
    data.write(OUT/'review.json',dict(source=SOURCE,rows=rows));data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=12,existingThreadReferencesReauthenticated=12,newSourceReasons=0,rawRetained=12,productTestsExecuted=0,wholeF03Accepted=False,newAccepted=0,coverage=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
