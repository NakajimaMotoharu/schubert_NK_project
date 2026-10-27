"""Two finite mock-worker references and one deliberate public-monitor independence oracle."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match
SOURCE='4b5f6faa078be348132a6ece9140b0c1a31d7907'
OUT=data.BASE/'PG12201-audit-metric-context-v1'
def review():
    host=data.read_checked(data.BASE/'PG12196-audit-metric-host-v1/manifest.json','5611da6fac4d7f4959d97882e2a0c297d5d9681fa7b29e3a8721f15373d75fc8')
    assert host['source']==SOURCE and host['actualExit']==0 and host['observedTestExecutions']==19
    sp=data.BASE/'PG12198-audit-metric-static-v1';m=data.read_checked(sp/'manifest.json','a10133ca7dedd88083f8f39c8b96b0af1cde5ffc161655dc8feb3591b10d8255');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==m['reports']['pmd']['sha256'] and m['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation' and n.get('rule') in ('DoNotUseThreads','AvoidSynchronizedStatement')];original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');rows=[]
    for path,node in actual:
        ident=original_match(path,node,original,actual);text=(data.ROOT/path).read_text();assert data.sha(text.encode())==host['begin']['sourceInputHashes'][path]
        a=dict(node.attrib);lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];i=next(i for i,(_,p) in enumerate(ts) if p==start);lo,hi,name=min((v for v in functions(ts) if v[0]<=i<=v[1]),key=lambda v:v[1]-v[0]);body=''.join(t for t,_ in ts[lo:hi+1])
        is_audit=name=='web100ConcurrentAuditEventsStayIndependent'
        if is_audit:
            assert all(v in body for v in ('Executors.newFixedThreadPool(8)','i<100','pool.invokeAll(jobs)','job.get(10,TimeUnit.SECONDS)','synchronized(audit)'))
        else:
            assert name=='batchRec007SixtyFourParallelSuccessesKeepExactCountAndMaximumTime' and all(v in body for v in ('Executors.newFixedThreadPool(8)','IntStream.range(0,64)','pool.invokeAll(jobs)','assertTrue(result.get())','assertEquals(64.0,'))
        thread=a['rule']=='DoNotUseThreads';assert thread or a['rule']=='AvoidSynchronizedStatement'
        reason=('Dedicated JavaSE JUnit owns eight TWR workers for100 in-memory audit events or64 injected MockClock/SimpleMeterRegistry updates. The audited source keeps all fixed count/maximum/actor checks. Audit gets have10-second bounds; metric gets and invokeAll are locally unbounded. The owned outer JVM240-second timeout and actual normal terminal are independently verified, without claiming local per-get bounds. No application-managed thread, exporter, external HTTP, business Batch, DB, MQ or Root operation.' if thread else 'The test thread deliberately holds the public audit monitor while other workers invoke the same audit instance. Their bounded successful completion independently proves no synchronization on this externally accessible monitor. Replacing it with another lock removes the oracle. The100 finite events, original get10 and outer240 normal terminal remain verified; not production shared-state synchronization.')
        case=next(c for c in host['begin']['cases'] if c['path']==path and c['method']==name);assert any(c['classname']==case['className'] and c['name']==name and not c['nonPass'] for c in host['cases'])
        rows.append(dict(id=ident['id'],path=path,rule=a['rule'],attributes=a,originalRowSha256=ident['rowSha256'],source=SOURCE,sourceSha256=data.sha(text.encode()),sourceSpanSha256=data.sha(text[start:end].encode()),method=name,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),currentCase=case,kind=('OWN_AUDIT100_JAVASE_WORKERS' if is_audit else 'OWN_METRIC64_JAVASE_WORKERS') if thread else 'PUBLIC_AUDIT_MONITOR_INDEPENDENCE_ORACLE',disposition='CONTEXT_NOT_APPLICABLE' if thread else 'REQUIRED_CONTRACT',reason=reason,previousReferenceRetainedAsHistorical=thread,newSourceReason=not thread,currentWholeJoinPending=True,productTestsExecutedByReview=0,oldRuntimeReassigned=False))
    assert len(rows)==len({r['id'] for r in rows})==5 and sum(r['newSourceReason'] for r in rows)==1;return rows
def main():
    invocation=capture(__file__);assert not OUT.exists();rows=review();verify(invocation);OUT.mkdir();data.write(OUT/'review.json',dict(source=SOURCE,rows=rows));data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=5,existingThreadReferencesReauthenticated=4,newSourceReasons=1,rawRetained=3,productTestsExecuted=0,wholeF03Accepted=False,newAccepted=0,coverage=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
