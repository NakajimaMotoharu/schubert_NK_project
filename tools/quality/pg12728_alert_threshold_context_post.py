"""Independent current fixture contexts: original XML nodes, method/class scopes, explicit controls and counts."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg12248_main_local_maps_post import enclosing_method
from pg11054_api_request_context import original_match

SOURCE='af3f0f86d295ed721f5c1b41670ef224eb1d49e3'
PIN='f6359bf01da291c5f348e690f1f0ebe2ba99e7fbfa1d0ed89fa6836396e33b47'
OUT=data.BASE/'PG12728-alert-threshold-context-post-v1'
CONTROLS={'threshold014ConcurrentStatelessEvaluations':['try(varexecutor=Executors.newFixedThreadPool(4))','index<64','executor.invokeAll(tasks,10,TimeUnit.SECONDS)','future.get()','executor.shutdownNow()','assertTrue(executor.awaitTermination(10,TimeUnit.SECONDS))','assertEquals(expected,future.get())']}
KINDS={'DoNotUseThreads':'FINITE_OWNED_PURE_ALERT_THRESHOLD_WORKERS'}

def main():
    invocation=capture(__file__);assert not OUT.exists();p=data.BASE/'PG12726-alert-threshold-context-v1';m=data.read_checked(p/'manifest.json',PIN);rows=data.read_checked(p/'review.json',m['reviewSha256'])['rows']
    host=data.read_checked(data.BASE/'PG12720-alert-threshold-host-v1/manifest.json','ccb4a097f17f8e40779ca3f01f3ab79a876f0c33eccb94d27c31f54661562513')
    sp=data.BASE/'PG12722-alert-threshold-static-v1';st=data.read_checked(sp/'manifest.json','2cd61dcada2767e9c62b6e580d0e5e2215758471408d6e69833e9d6452996707');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    mapped={original_match(path,n,original,actual)['id']:(path,n) for path,n in actual};assert len(mapped)==len(rows)==len({r['id'] for r in rows})==4 and set(mapped)=={r['id'] for r in rows}
    def validate(row):
        if row.get('id') not in mapped:raise ValueError('known current original ID required')
        path,node=mapped[row['id']];a=dict(node.attrib);rule=a['rule'];method=a.get('method');text=(data.ROOT/path).read_text();sha=data.sha(text.encode());assert sha==host['begin']['sourceInputHashes'][path]
        lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];point=next(i for i,(_,p) in enumerate(ts) if p==start)
        holder=method;lo,hi=enclosing_method(ts,method,point)
        controls=CONTROLS[holder];assert all(c in ''.join(t for t,_ in ts[lo:hi+1]) for c in controls)
        cases=[c for c in host['begin']['cases'] if c['path']==path and c['method']==method];assert cases and all(any(a['classname']==c['className'] and a['name']==c['method'] and not a['nonPass'] for a in host['cases']) for c in cases)
        identity=original_match(path,node,original,actual)
        expected=dict(path=path,rule=rule,attributes=a,originalRowSha256=identity['rowSha256'],source=SOURCE,sourceSha256=sha,sourceSpanSha256=data.sha(text[start:end].encode()),scopeName=holder,scopeKind='OWNER_CLASS' if method is None else 'METHOD',scopeTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),controls=controls,currentCases=cases,kind=KINDS[rule],disposition='CONTEXT_NOT_APPLICABLE',currentWholeJoinPending=True,oldRuntimeReassigned=False,productTestsExecutedByReview=0,newAccepted=0)
        if any(row.get(k)!=v for k,v in expected.items()) or not row.get('reason'):raise ValueError('exact source/owner-scope/controls/cases and no product credit required')
    for row in rows:validate(row)
    labels=[]
    for field,value in [('id','foreign'),('source','0'*40),('sourceSha256','0'*64),('sourceSpanSha256','0'*64),('scopeName','foreign'),('scopeKind','UNKNOWN'),('scopeTokenSha256','0'*64),('controls',[]),('currentCases',[]),('kind','EXEMPT'),('disposition','SUPPRESSED'),('reason',''),('currentWholeJoinPending',False),('oldRuntimeReassigned',True),('productTestsExecutedByReview',1),('newAccepted',1)]:
        bad=copy.deepcopy(rows[0]);assert bad.get(field)!=value;bad[field]=value
        try:validate(bad)
        except ValueError:labels.append(field)
        else:raise AssertionError('wrong current source/context accepted')
    def counts(v):
        if v.get('sourceContexts')!=len(mapped) or v.get('rawRetained')!=len(mapped) or v.get('wholeStaticScopeRaw')!=len(mapped) or v.get('rawRetainedMeaning')!='COUNT_UNIQUE_SELECTED_REVIEWED_RETAINED_FINDING_IDS' or v.get('sourceCorrections')!=0 or v.get('newAccepted')!=0:raise ValueError('selected scope count and no product/static correction credit required')
    counts(m)
    for field,value in [('sourceContexts',23),('rawRetained',3),('wholeStaticScopeRaw',0),('rawRetainedMeaning','WHOLE_GLOBAL_RAW'),('sourceCorrections',24),('newAccepted',1)]:
        bad=dict(m);assert bad.get(field)!=value;bad[field]=value
        try:counts(bad)
        except ValueError:labels.append('manifest.'+field)
        else:raise AssertionError('wrong context scope cardinality accepted')
    assert len(labels)==22 and host['source']==SOURCE and host['actualExit']==0 and host['observedTestExecutions']==14
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewManifestSha256=PIN,sourceContexts=len(mapped),rawRetained=len(mapped),metadataNegativeVectors=len(labels),metadataNegativeLabels=labels,productTestsExecuted=0,sourceCorrections=0,coverage=None,newAccepted=0,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
