"""Two finite mock-worker references and one deliberate public-monitor independence oracle."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match
SOURCE='ee82637a750105243ddeac665c61d27a781e5cf1'
OUT=data.BASE/'PG12111-authz-fixture-context-v1'
def review():
    host=data.read_checked(data.BASE/'PG12107-authz-fixture-host-v2/manifest.json','4f764569dc6164b941b9b1e211578d47f6384cd2c0509862c0b6dba45ef0fefc')
    assert host['source']==SOURCE and host['actualExit']==0 and host['observedTestExecutions']==4 and host['typeOnlyReferenceGuardVectors']==dict(positive=1,negative=4)
    sp=data.BASE/'PG12109-authz-fixture-static-v2';m=data.read_checked(sp/'manifest.json','debf7b4ce804a32e6b5c797e4fc5b1a2c129bf7caa065a1891487e50fa31ff6b');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==m['reports']['pmd']['sha256'] and m['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation'];original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');rows=[]
    for path,node in actual:
        ident=original_match(path,node,original,actual);text=(data.ROOT/path).read_text();assert data.sha(text.encode())==host['begin']['sourceInputHashes'][path]
        assert len(re.findall(r'@AfterEach\s+void clear\(\)\s*\{\s*SecurityContextHolder\.clearContext\(\);\s*\}',text))==1
        a=dict(node.attrib);lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];i=next(i for i,(_,p) in enumerate(ts) if p==start);lo,hi,name=min((v for v in functions(ts) if v[0]<=i<=v[1]),key=lambda v:v[1]-v[0]);body=''.join(t for t,_ in ts[lo:hi+1])
        assert name=='web124ConcurrentPoliciesHaveNoCrossRequestIdentity' and all(s in body for s in ('Executors.newFixedThreadPool(8)','i<100','pool.invokeAll(jobs)','future.get(30,TimeUnit.SECONDS)','synchronized(filter)','finally{SecurityContextHolder.clearContext();}'))
        thread=a['rule']=='DoNotUseThreads';assert thread or a['rule']=='AvoidSynchronizedStatement'
        reason=('A dedicated standalone JavaSE JUnit owns eight TWR workers and exactly100 in-memory MockServlet policy checks, checks identity separation, and clears SecurityContext in finally and the original AfterEach. Future gets have30-second bounds; invokeAll itself is unbounded and the outer owned JVM has240-second timeout with actual normal terminal. There is no external HTTP, authentication, DB, JMS or application-managed thread.' if thread else 'The test thread deliberately holds the public filter monitor while other workers invoke the same filter. Their successful bounded completion is the independent oracle that production does not synchronize on this externally accessible monitor. Replacing it with another lock would remove the required test. The monitor covers finite test orchestration, not production shared-state synchronization; actual100 checks and the dedicated outer terminal are verified.')
        case=next(c for c in host['begin']['cases'] if c['path']==path and c['method']==name);assert any(c['classname']==case['className'] and c['name']==name and not c['nonPass'] for c in host['cases'])
        rows.append(dict(id=ident['id'],path=path,rule=a['rule'],attributes=a,originalRowSha256=ident['rowSha256'],source=SOURCE,sourceSha256=data.sha(text.encode()),sourceSpanSha256=data.sha(text[start:end].encode()),method=name,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),currentCase=case,kind='OWN_MOCK100_JAVASE_WORKERS' if thread else 'PUBLIC_FILTER_MONITOR_INDEPENDENCE_ORACLE',disposition='CONTEXT_NOT_APPLICABLE' if thread else 'REQUIRED_CONTRACT',reason=reason,previousReferenceRetainedAsHistorical=thread,newSourceReason=not thread,currentWholeJoinPending=True,productTestsExecutedByReview=0,oldRuntimeReassigned=False))
    assert len(rows)==len({r['id'] for r in rows})==3 and sum(r['newSourceReason'] for r in rows)==1;return rows
def main():
    invocation=capture(__file__);assert not OUT.exists();rows=review();verify(invocation);OUT.mkdir();data.write(OUT/'review.json',dict(source=SOURCE,rows=rows));data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=3,existingThreadReferencesReauthenticated=2,newSourceReasons=1,rawRetained=3,productTestsExecuted=0,wholeF03Accepted=False,newAccepted=0,coverage=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
