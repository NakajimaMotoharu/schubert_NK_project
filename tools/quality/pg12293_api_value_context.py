"""Current memory-channel100 worker source/span/case metadata only; no target execution."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match
SOURCE='7368ba9d4a38677f5eade903771832e612aa42b5'
OUT=data.BASE/'PG12293-api-value-context-v1'
def review():
    host=data.read_checked(data.BASE/'PG12288-api-value-host-v1/manifest.json','c0478ed0d574dce6353c8de4643f28c44f094f26d91b61f32db0d93eb69848b0')
    assert host['source']==SOURCE and host['actualExit']==0 and host['observedTestExecutions']==18
    sp=data.BASE/'PG12290-api-value-static-v1';m=data.read_checked(sp/'manifest.json','3d593e24fabfd7a5ec0323f9b308c47c1b2106dfa66dc16210c6a5f80e89954c');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==m['reports']['pmd']['sha256'] and m['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation' and n.get('rule') in ('DoNotUseThreads','AvoidSynchronizedStatement')];original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');rows=[]
    for path,node in actual:
        ident=original_match(path,node,original,actual);text=(data.ROOT/path).read_text();assert data.sha(text.encode())==host['begin']['sourceInputHashes'][path]
        a=dict(node.attrib);lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];i=next(i for i,(_,p) in enumerate(ts) if p==start);lo,hi,name=min((v for v in functions(ts) if v[0]<=i<=v[1]),key=lambda v:v[1]-v[0]);body=''.join(t for t,_ in ts[lo:hi+1])
        assert name=='concurrentCallsAndEvidence' and all(w in body for w in ('Executors.newFixedThreadPool(8)','i<64','executor.invokeAll(tasks,5,TimeUnit.SECONDS)','future.get()','assertEquals(expected,actual)'))
        thread=a['rule']=='DoNotUseThreads';assert thread
        reason='Dedicated JavaSE JUnit owns eight TWR workers and64 synthetic-clock calls; invokeAll has5second timeout, actual resultset equals64 independent fixed Instants. Only one fixed public trace is written inside fresh owned CWD and independently hashed. No EJB/application-managed thread or external filesystem data/DB/JMS/network/VM/Root; raw retained and whole-source applicability pending.'
        case=next(c for c in host['begin']['cases'] if c['path']==path and c['method']==name);assert any(c['classname']==case['className'] and c['name']==name and not c['nonPass'] for c in host['cases'])
        rows.append(dict(id=ident['id'],path=path,rule=a['rule'],attributes=a,originalRowSha256=ident['rowSha256'],source=SOURCE,sourceSha256=data.sha(text.encode()),sourceSpanSha256=data.sha(text[start:end].encode()),method=name,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),currentCase=case,kind='OWN_STUB64_SYNTHETICCLOCK_PUBLICTRACE',disposition='CONTEXT_NOT_APPLICABLE',reason=reason,previousReferenceRetainedAsHistorical=thread,newSourceReason=not thread,currentWholeJoinPending=True,productTestsExecutedByReview=0,oldRuntimeReassigned=False))
    assert len(rows)==len({r['id'] for r in rows})==2 and sum(r['newSourceReason'] for r in rows)==0;return rows
def main():
    invocation=capture(__file__);assert not OUT.exists();rows=review();verify(invocation);OUT.mkdir();data.write(OUT/'review.json',dict(source=SOURCE,rows=rows));data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=len(rows),existingThreadReferencesReauthenticated=len(rows),newSourceReasons=0,rawRetained=len({r['id'] for r in rows}),rawRetainedMeaning='COUNT_UNIQUE_SELECTED_REVIEWED_RETAINED_FINDING_IDS',wholeStaticScopeRaw=len(rows),productTestsExecuted=0,wholeF03Accepted=False,newAccepted=0,coverage=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
