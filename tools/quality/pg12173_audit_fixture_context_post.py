"""Independent MockServlet XML/span/current-case/clear hook bindings and8 unequal negative metadata vectors."""
import copy
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match
SOURCE='92c80a593717465426a33bdf581bc7e94b1235f1'
OUT=data.BASE/'PG12173-audit-fixture-context-post-v1'
PIN='6c4c5b7032d4c2bd6e103900648521ee961a816a184d89215ed46d50d5ab036e'
def main():
    invocation=capture(__file__);assert not OUT.exists();p=data.BASE/'PG12175-audit-fixture-context-v2'
    m=data.read_checked(p/'manifest.json',PIN);rows=data.read_checked(p/'review.json',m['reviewSha256'])['rows']
    host=data.read_checked(data.BASE/'PG12166-audit-fixture-host-v1/manifest.json','bdbd9713e98261dc6928af9962c3e9743d91be68683cb6e015e8eb509ce236c1')
    sp=data.BASE/'PG12168-audit-fixture-static-v1';st=data.read_checked(sp/'manifest.json','7782fd394e8f7972e0dfc878264791ce2f6540da31574f8a0eb7dfbdc0840845');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation' and n.get('rule') in ('DoNotUseThreads','AvoidSynchronizedStatement')]
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    mapped={(p,tuple(sorted(n.attrib.items()))):original_match(p,n,original,actual) for p,n in actual}
    def validate(row):
        path=row['path'];a=row['attributes'];text=(data.ROOT/path).read_text();lines=text.splitlines(keepends=True)
        start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];i=next(i for i,(_,p) in enumerate(ts) if p==start)
        lo,hi,name=min((v for v in functions(ts) if v[0]<=i<=v[1]),key=lambda v:v[1]-v[0]);body=''.join(t for t,_ in ts[lo:hi+1]);ident=mapped[(path,tuple(sorted(a.items())))]
        case=next(c for c in host['begin']['cases'] if c['path']==path and c['method']==name)
        thread=a['rule']=='DoNotUseThreads';assert thread or a['rule']=='AvoidSynchronizedStatement'
        expected=dict(id=ident['id'],originalRowSha256=ident['rowSha256'],rule=a['rule'],source=SOURCE,sourceSha256=host['begin']['sourceInputHashes'][path],sourceSpanSha256=data.sha(text[start:end].encode()),method=name,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),currentCase=case,kind='OWN_AUDIT100_JAVASE_WORKERS' if thread else 'PUBLIC_AUDIT_MONITOR_INDEPENDENCE_ORACLE',disposition='CONTEXT_NOT_APPLICABLE' if thread else 'REQUIRED_CONTRACT',previousReferenceRetainedAsHistorical=thread,newSourceReason=not thread,currentWholeJoinPending=True,productTestsExecutedByReview=0,oldRuntimeReassigned=False)
        if any(row.get(k)!=v for k,v in expected.items()) or not row.get('reason'):raise ValueError('current source/span/method/reason/case required')
        assert data.sha(text.encode())==row['sourceSha256'] and host['source']==SOURCE and host['actualExit']==0
        assert name=='web100ConcurrentAuditEventsStayIndependent'
        assert all(v in body for v in ('Executors.newFixedThreadPool(8)','i<100','synchronized(audit){for(varjob:pool.invokeAll(jobs))job.get(10,TimeUnit.SECONDS);}'))
        assert any(c['classname']==case['className'] and c['name']==name and not c['nonPass'] for c in host['cases'])
    assert len(rows)==len(mapped)==len({r['id'] for r in rows})==3 and Counter(r['rule'] for r in rows)==Counter(DoNotUseThreads=2,AvoidSynchronizedStatement=1)
    for row in rows:validate(row)
    negatives=0
    for field,value in [('source','0'*40),('oldRuntimeReassigned',True),('reason',''),('sourceSpanSha256','0'*64),('method','foreign'),('currentCase',{}),('disposition','SUPPRESSED'),('currentWholeJoinPending',False)]:
        bad=copy.deepcopy(rows[0]);bad[field]=value
        try:validate(bad)
        except ValueError:negatives+=1
        else:raise AssertionError('incorrect source/context accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewManifestSha256=PIN,sourceContexts=3,newSourceReasons=1,existingThreadReferencesReauthenticated=2,metadataNegativeVectors=negatives,productTestsExecuted=0,wholeF03Accepted=False,newAccepted=0,coverage=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
