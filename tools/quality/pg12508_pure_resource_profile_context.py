"""Nine retained original Test thread applicability reasons from actual current34 and static XML."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match

SOURCE='c099786934c864f31a6fb520184366c22c84f6ea'
OUT=data.BASE/'PG12508-pure-resource-profile-context-v1'
METHOD_CONTROLS={'concurrentScopes': ['Executors.newVirtualThreadPerTaskExecutor()', 'i<64', 'pool.submit(', 'futures.get(i).get()', 'assertEquals(64,closed.get())'], 'factory012NestedAndParallelScopesKeepIndependentOwnership': ['Executors.newFixedThreadPool(2)', 'first.get()', 'second.get()', 'a.closed()', 'b.closed()', 'assertNotSame(a.token,b.token)'], 'factory018ParallelCompleteOwnersNeverShareTransferState': ['newCountDownLatch(2)', 'ready.await(10,TimeUnit.SECONDS)', 'Thread.currentThread().interrupt()', 'Executors.newFixedThreadPool(2)', 'first.get()', 'second.get()', 'assertEquals(0,closed.get())']}

def main():
    invocation=capture(__file__);assert not OUT.exists()
    hp=data.BASE/'PG12502-pure-resource-profile-host-v1/manifest.json';host=data.read_checked(hp,'2ddb3ff1cfc6b145dc3a785ab8e9067243d694f4fd57a33e7899ce249998d652');assert host['source']==SOURCE and host['actualExit']==0 and host['observedTestExecutions']==34
    sp=data.BASE/'PG12504-pure-resource-profile-static-v1';st=data.read_checked(sp/'manifest.json','133577cdab5e74deceb505cca099830b4b06afc1800fd986efc372031e74ef04');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256'] and st['reports']['pmd']['findings']==9 and st['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');rows=[]
    for path,node in actual:
        ident=original_match(path,node,original,actual);a=dict(node.attrib);rule=a['rule'];method=a.get('method');text=(data.ROOT/path).read_text();sha=data.sha(text.encode());assert sha==host['begin']['sourceInputHashes'][path]
        ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        point=next(i for i,(_,p) in enumerate(ts) if p==start)
        assert method in METHOD_CONTROLS;lo,hi,name=min((v for v in functions(ts) if v[0]<=point<=v[1]),key=lambda v:v[1]-v[0]);assert name==method;holder=method;controls=METHOD_CONTROLS[method]
        assert rule=='DoNotUseThreads'
        kind='FINITE_OWNED_STANDALONE_RESOURCE_FIXTURE_WORKERS'
        reason='Original JavaSE JUnit owns one virtual executor/64 finite callbacks or two-worker pools/independent memory Tokens, all in TWR. Factory018 latch await10seconds restores interrupted flag before declared fixture IOException. Existing future.get has no per-call timeout; all submitted callbacks are bounded and the dedicated JVM has a distinct240second bound. Ownership/close counts and token identities are independent assertions. No J2EE application worker, actual IO/native/file/Root/DB/JMS/network/keys or real heap exhaustion.'
        body=''.join(t for t,_ in ts[lo:hi+1]);assert all(c in body for c in controls)
        case_refs=[c for c in host['begin']['cases'] if c['path']==path and c['method']==method];assert case_refs
        assert all(any(a['classname']==c['className'] and a['name']==c['method'] and not a['nonPass'] for a in host['cases']) for c in case_refs)
        rows.append(dict(id=ident['id'],path=path,rule=rule,attributes=a,originalRowSha256=ident['rowSha256'],source=SOURCE,sourceSha256=sha,sourceSpanSha256=data.sha(text[start:end].encode()),scopeName=holder,scopeKind='OWNER_CLASS' if method is None else 'METHOD',scopeTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),controls=controls,currentCases=case_refs,kind=kind,disposition='CONTEXT_NOT_APPLICABLE',reason=reason,currentWholeJoinPending=True,oldRuntimeReassigned=False,productTestsExecutedByReview=0,newAccepted=0))
    count=len({r['id'] for r in rows});assert count==len(rows)==9
    verify(invocation);OUT.mkdir();data.write(OUT/'review.json',dict(source=SOURCE,rows=rows));data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=count,rawRetained=count,rawRetainedMeaning='COUNT_UNIQUE_SELECTED_REVIEWED_RETAINED_FINDING_IDS',wholeStaticScopeRaw=count,productTestsExecuted=0,sourceCorrections=0,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,coverage=None,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
