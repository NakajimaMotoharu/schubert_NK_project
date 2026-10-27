"""Corrected independent XML/span/current-case bindings and8 unequal negative metadata vectors."""
import copy
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match
SOURCE='977214e4409e70bcf7c38dfd34bbaa384fc14c9b'
OUT=data.BASE/'PG12085-media-wire-fixture-context-post-v2'
PIN='63dc90ee9d828ff192ca1214fe783fdcab704eae6d7abb3551870f05df532367'
def main():
    invocation=capture(__file__);assert not OUT.exists();p=data.BASE/'PG12081-media-wire-fixture-context-v1'
    m=data.read_checked(p/'manifest.json',PIN);rows=data.read_checked(p/'review.json',m['reviewSha256'])['rows']
    host=data.read_checked(data.BASE/'PG12076-media-wire-fixture-host-v1/manifest.json','1152f7f83f1bd58ef9cabdc8c804ad117241f7ecaa45662c9a17fe4698d3cc2a')
    sp=data.BASE/'PG12078-media-wire-fixture-static-v1';st=data.read_checked(sp/'manifest.json','9677642afbb43a6c36d4a5b8582343054217b99dcfaee948520bc51edbc13e9e');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    mapped={(p,tuple(sorted(n.attrib.items()))):original_match(p,n,original,actual) for p,n in actual}
    def validate(row):
        path=row['path'];a=row['attributes'];text=(data.ROOT/path).read_text();lines=text.splitlines(keepends=True)
        start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];i=next(i for i,(_,p) in enumerate(ts) if p==start)
        lo,hi,name=min((v for v in functions(ts) if v[0]<=i<=v[1]),key=lambda v:v[1]-v[0]);body=''.join(t for t,_ in ts[lo:hi+1]);ident=mapped[(path,tuple(sorted(a.items())))]
        case=next(c for c in host['begin']['cases'] if c['path']==path and c['method']==name)
        kinds={'web171TransportFailuresDoNotRetryOrLeakPending':'OWN_INTERRUPT_RESTORE_AND_SINGLE_CAPACITY_FIXTURE','web172ConcurrentQueriesKeepContextsAndRepliesSeparate':'OWN_SCENARIO100_FINITE_CALLBACK_WORKERS','web244ConcurrentRequests':'OWN_MEDIA64_CALLBACK_WORKERS_OUTER240','web260ConcurrentRequests':'OWN_MEDIA64_CALLBACK_WORKERS_OUTER240'}
        expected=dict(id=ident['id'],originalRowSha256=ident['rowSha256'],rule='DoNotUseThreads',source=SOURCE,sourceSha256=host['begin']['sourceInputHashes'][path],sourceSpanSha256=data.sha(text[start:end].encode()),method=name,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),currentCase=case,kind=kinds[name],disposition='CONTEXT_NOT_APPLICABLE',previousReferenceRetainedAsHistorical=True,newSourceReason=False,currentWholeJoinPending=True,productTestsExecutedByReview=0,oldRuntimeReassigned=False)
        if any(row.get(k)!=v for k,v in expected.items()) or not row.get('reason'):raise ValueError('current source/span/method/reason/case required')
        assert data.sha(text.encode())==row['sourceSha256'] and host['source']==SOURCE and host['actualExit']==0
        assert 'assertEquals(0,wire.pendingCount());' in body
        if name.startswith('web171'):
            assert 'Thread.currentThread().interrupt();' in body and 'finally{Thread.interrupted();}' in body and 'Executors.newSingleThreadExecutor()' in body
            assert all(s in body for s in ('release.await(5,TimeUnit.SECONDS)','entered.await(5,TimeUnit.SECONDS)','first.get(5,TimeUnit.SECONDS)'))
        elif name.startswith('web172'):
            assert 'n<100' in body and 'task.get(10,TimeUnit.SECONDS)' in body and 'finally{active.remove();}' in body
        else:
            assert 'i<64' in body and 'future.get();' in body and 'per-get deadline' in row['reason'] and 'owned launcher is limited to240 seconds' in row['reason']
        assert any(c['classname']==case['className'] and c['name']==name and not c['nonPass'] for c in host['cases'])
    assert len(rows)==len(mapped)==len({r['id'] for r in rows})==12 and Counter(r['rule'] for r in rows)==Counter(DoNotUseThreads=12)
    for row in rows:validate(row)
    negatives=0
    for field,value in [('source','0'*40),('oldRuntimeReassigned',True),('reason',''),('sourceSpanSha256','0'*64),('method','foreign'),('currentCase',{}),('disposition','SUPPRESSED'),('currentWholeJoinPending',False)]:
        bad=copy.deepcopy(rows[0]);bad[field]=value
        try:validate(bad)
        except ValueError:negatives+=1
        else:raise AssertionError('incorrect source/context accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewManifestSha256=PIN,sourceContexts=12,newSourceReasons=0,existingThreadReferencesReauthenticated=12,metadataNegativeVectors=negatives,productTestsExecuted=0,wholeF03Accepted=False,newAccepted=0,coverage=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
