"""Current memory-channel100 worker source/span/case metadata only; no target execution."""
import copy
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match
SOURCE='7368ba9d4a38677f5eade903771832e612aa42b5'
OUT=data.BASE/'PG12295-api-value-context-post-v1'
PIN='4d3f6cf82d1bb4d5a0a5a3a50afcfe3accea90fa446dd9fe634daf1e6f87abb1'
def main():
    invocation=capture(__file__);assert not OUT.exists();p=data.BASE/'PG12293-api-value-context-v1'
    m=data.read_checked(p/'manifest.json',PIN);rows=data.read_checked(p/'review.json',m['reviewSha256'])['rows']
    host=data.read_checked(data.BASE/'PG12288-api-value-host-v1/manifest.json','c0478ed0d574dce6353c8de4643f28c44f094f26d91b61f32db0d93eb69848b0')
    sp=data.BASE/'PG12290-api-value-static-v1';st=data.read_checked(sp/'manifest.json','3d593e24fabfd7a5ec0323f9b308c47c1b2106dfa66dc16210c6a5f80e89954c');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation' and n.get('rule') in ('DoNotUseThreads','AvoidSynchronizedStatement')]
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    mapped={(p,tuple(sorted(n.attrib.items()))):original_match(p,n,original,actual) for p,n in actual}
    def validate(row):
        path=row['path'];a=row['attributes'];text=(data.ROOT/path).read_text();lines=text.splitlines(keepends=True)
        start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];i=next(i for i,(_,p) in enumerate(ts) if p==start)
        lo,hi,name=min((v for v in functions(ts) if v[0]<=i<=v[1]),key=lambda v:v[1]-v[0]);body=''.join(t for t,_ in ts[lo:hi+1]);ident=mapped[(path,tuple(sorted(a.items())))]
        case=next(c for c in host['begin']['cases'] if c['path']==path and c['method']==name)
        thread=a['rule']=='DoNotUseThreads';assert thread
        expected=dict(id=ident['id'],originalRowSha256=ident['rowSha256'],rule=a['rule'],source=SOURCE,sourceSha256=host['begin']['sourceInputHashes'][path],sourceSpanSha256=data.sha(text[start:end].encode()),method=name,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),currentCase=case,kind='OWN_STUB64_SYNTHETICCLOCK_PUBLICTRACE',disposition='CONTEXT_NOT_APPLICABLE',previousReferenceRetainedAsHistorical=thread,newSourceReason=not thread,currentWholeJoinPending=True,productTestsExecutedByReview=0,oldRuntimeReassigned=False)
        if any(row.get(k)!=v for k,v in expected.items()) or not row.get('reason'):raise ValueError('current source/span/method/reason/case required')
        assert data.sha(text.encode())==row['sourceSha256'] and host['source']==SOURCE and host['actualExit']==0
        assert name=='concurrentCallsAndEvidence' and all(w in body for w in ('Executors.newFixedThreadPool(8)','i<64','executor.invokeAll(tasks,5,TimeUnit.SECONDS)','future.get()','assertEquals(expected,actual)'))
        assert any(c['classname']==case['className'] and c['name']==name and not c['nonPass'] for c in host['cases'])
    assert len(rows)==len(mapped)==len({r['id'] for r in rows})==2 and Counter(r['rule'] for r in rows)==Counter(DoNotUseThreads=2)
    for row in rows:validate(row)
    negatives=0
    for field,value in [('source','0'*40),('oldRuntimeReassigned',True),('reason',''),('sourceSpanSha256','0'*64),('method','foreign'),('currentCase',{}),('disposition','SUPPRESSED'),('currentWholeJoinPending',False)]:
        bad=copy.deepcopy(rows[0]);bad[field]=value
        try:validate(bad)
        except ValueError:negatives+=1
        else:raise AssertionError('incorrect source/context accepted')
    def count_contract(value):
        total=len(mapped)
        if value.get('rawRetained')!=total or value.get('sourceContexts')!=total or value.get('wholeStaticScopeRaw')!=total or value.get('rawRetainedMeaning')!='COUNT_UNIQUE_SELECTED_REVIEWED_RETAINED_FINDING_IDS':
            raise ValueError('all auxiliary counts and selected scope must equal independently mapped XML IDs')
    count_contract(m)
    for field,value in [('rawRetained',3),('sourceContexts',3),('wholeStaticScopeRaw',3),('rawRetainedMeaning','WHOLE_GLOBAL_RAW')]:
        bad=dict(m);bad[field]=value
        try:count_contract(bad)
        except ValueError:negatives+=1
        else:raise AssertionError('incorrect cardinality accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewManifestSha256=PIN,sourceContexts=len(mapped),rawRetained=len(mapped),newSourceReasons=0,existingThreadReferencesReauthenticated=2,metadataNegativeVectors=negatives,productTestsExecuted=0,wholeF03Accepted=False,newAccepted=0,coverage=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
