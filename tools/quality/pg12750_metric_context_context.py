"""Current 38 applicability contexts, four ownership false positives and 34 historical thread refs."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match

SOURCE='f75d2fea05a98fe40d731d1a3046a64d20bbbb65'
OUT=data.BASE/'PG12750-metric-context-context-v1'
CONTROL_SUFFIX={
 '021':['try(varexecutor=Executors.newSingleThreadExecutor())','active.get(30,TimeUnit.SECONDS)','release.countDown()','executor.shutdownNow()','executor.awaitTermination(30,TimeUnit.SECONDS)'],
 '023':['try(varexecutor=Executors.newSingleThreadExecutor())','List.of(true,false)','init.get(30,TimeUnit.SECONDS)','release.countDown()','executor.shutdownNow()','executor.awaitTermination(30,TimeUnit.SECONDS)'],
 '024':['try(varexecutor=Executors.newSingleThreadExecutor())','init.get(30,TimeUnit.SECONDS)','release.countDown()','executor.shutdownNow()','executor.awaitTermination(30,TimeUnit.SECONDS)'],
 '033':['try(varworker=Executors.newSingleThreadExecutor())','future.get(30,TimeUnit.SECONDS)','proceed.countDown()','worker.shutdownNow()','worker.awaitTermination(30,TimeUnit.SECONDS)','context.close()'],
 '032':['context.initialize()','context.render(true)','finally{context.close();}','assertTrue(observed.get().isClosed())']}


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    host=data.read_checked(data.BASE/'PG12744-metric-context-host-v1/manifest.json','c3c41d37e0ade8e22f6c50f2424fc1e6d6ecd67cc4f5c6e5346e94fa60d45381')
    static=data.read_checked(data.BASE/'PG12746-metric-context-static-v1/manifest.json','6ea3560962d32afd4d0921d7c81f2ef47f101c3c7aca7bca3f0c0ab38f6b9e75')
    proof=data.read_checked(data.BASE/'PG12748-metric-context-post-v1/manifest.json','01190b958bf4c5fa867e158b1a5642f014eb57aae4df5353a01d3109cfb14486')
    assert host['source']==static['source']==proof['source']==SOURCE and host['actualExit']==proof['actualExit']==0 and host['observedTestExecutions']==66 and static['actualExit']==1
    raw=(data.BASE/'PG12746-metric-context-static-v1/pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    rows=[]
    for path,node in actual:
        identity=original_match(path,node,original,actual)
        attributes=dict(node.attrib);method=attributes['method'];text=(data.ROOT/path).read_text()
        assert data.sha(text.encode())==host['begin']['sourceInputHashes'][path]
        tokens=[(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
        lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(attributes['beginline'])-1]))+int(attributes['begincolumn'])-1;end=sum(map(len,lines[:int(attributes['endline'])-1]))+int(attributes['endcolumn'])
        point=next(index for index,(_,offset) in enumerate(tokens) if offset==start)
        lo,hi,name=min((row for row in functions(tokens) if row[0]<=point<=row[1]),key=lambda row:row[1]-row[0]);assert name==method
        compact=''.join(value for value,_ in tokens[lo:hi+1]);whole=''.join(value for value,_ in tokens)
        role='api' if '/nk/api/' in path else 'web';title=role.title();prefix=role+'mctx'
        cases=[row for row in host['begin']['cases'] if row['path']==path]
        if method=='Harness':
            assert attributes['rule']=='CloseResource' and attributes['variable']=='standardOwner'
            controls=['varstandardOwner=new'+title+'StandardMetricSource(this::standard,(registry,gc)->{});','context=new'+title+'MetricContext<T>','this::custom,standardOwner']
            owner_controls=['context.close();','if(!customRegistry.isClosed())customRegistry.close();','if(!standardRegistry.isClosed())standardRegistry.close();']
            assert all(value in whole for value in owner_controls)
            selected=[]
            scopes=functions(tokens)
            for case in cases:
                c_lo,c_hi,_=next(row for row in scopes if row[2]==case['method'])
                if 'newHarness<' in ''.join(value for value,_ in tokens[c_lo:c_hi+1]):
                    selected.append(case)
            assert len(selected)==23
            kind='UNBOUND_RESOURCE_FREE_OWNER_TRANSFERRED_TO_HARNESS_CONTEXT'
            reason='Private fixture uses only valid fixed modes. New StandardMetricSource constructor acquires no registry/GC; its ownership transfers into retained context before initialize. Harness owns and explicitly closes context and unused synthetic registries. Early TWR-close of the transferred alias would be wrong. No universal constructor-allocation/OOME cleanup guarantee or real application-owner qualification inferred.'
        elif method=='await':
            assert attributes['rule']=='DoNotUseThreads'
            controls=['latch.await(30,TimeUnit.SECONDS)','catch(InterruptedExceptioninterrupted)','Thread.currentThread().interrupt()']
            owner_controls=[]
            selected=[case for case in cases if any(case['method'].startswith(prefix+suffix) for suffix in ['021','023','024','033'])]
            assert len(selected)==4
            kind='PRIVATE_BOUNDED_LATCH_AND_INTERRUPT_STATUS_RESTORE_NOT_J2EE'
            reason='Private helper waits on own finite latches, restores interrupt state on the current test thread only. Caller cases are current whole-fixture executions; the InterruptedException helper branch is not injected and fixture branch100 is not claimed. No application worker, target process or privileged operation.'
        else:
            suffix=method[len(prefix):len(prefix)+3];assert suffix in CONTROL_SUFFIX
            controls=CONTROL_SUFFIX[suffix];owner_controls=[]
            selected=[case for case in cases if case['method']==method];assert len(selected)==1
            if suffix=='032':
                assert attributes['rule']=='CloseResource' and attributes['variable']=='context'
                kind='RESOURCE_FREE_CONTEXT_PUBLISHED_BEFORE_INIT_WITH_EXPLICIT_FINALLY_CLOSE'
                reason='Context construction/owner publication acquires no SDK. Actual initialization and intentional reentrant-stop negative call are inside explicit try/finally context.close, followed by independent registry-closed assertion. Early implicit close or removing finally would alter the ownership test. This does not authenticate real shutdown/native resources.'
            else:
                assert attributes['rule']=='DoNotUseThreads'
                kind='OWNED_FINITE_STANDALONE_SDK_FIXTURE_WORKERS_NOT_J2EE'
                reason='Standalone JUnit owns one worker per case (023 two sequential iterations). All task actions are local metadata/SDK context calls, release latch in original finally, shutdownNow and awaitTermination30seconds, Future.get30seconds. TWR close itself has no local absolute deadline, distinct outer JVM240seconds. Actual pass proves these fixtures only, not real service/VM/Root ownership or stop budget.'
        assert all(value in compact for value in controls)
        assert selected and all(any(actual_case['classname']==case['className'] and actual_case['name']==case['method'] and not actual_case['nonPass'] for actual_case in host['cases']) for case in selected)
        rows.append(dict(id=identity['id'],path=path,rule=attributes['rule'],attributes=attributes,originalRowSha256=identity['rowSha256'],source=SOURCE,sourceSha256=data.sha(text.encode()),sourceSpanSha256=data.sha(text[start:end].encode()),scopeName=method,scopeKind='CONSTRUCTOR' if method=='Harness' else 'METHOD',scopeTokenSha256=data.sha('\0'.join(value for value,_ in tokens[lo:hi+1]).encode()),controls=controls,ownerControls=owner_controls,currentCases=selected,kind=kind,disposition='CONTEXT_NOT_APPLICABLE',reason=reason,currentWholeJoinPending=True,oldRuntimeReassigned=False,productTestsExecutedByReview=0,newAccepted=0))
    assert len(rows)==len({row['id'] for row in rows})==38
    assert sum(row['rule']=='CloseResource' for row in rows)==4
    verify(invocation);OUT.mkdir()
    data.write(OUT/'review.json',dict(source=SOURCE,rows=rows))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=38,rawRetained=38,rawRetainedMeaning='COUNT_UNIQUE_SELECTED_REVIEWED_RETAINED_FINDING_IDS',wholeStaticScopeRaw=38,historicalThreadSourceRebindings=34,newOwnershipContexts=4,productTestsExecuted=0,sourceCorrections=0,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,coverage=None,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
