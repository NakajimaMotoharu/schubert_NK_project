"""Twenty-four selected fixture applicability reasons from actual static XML and original29 execution."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match

SOURCE='14198cb1878ec73319511ba1067133992d335e63'
OUT=data.BASE/'PG12386-pool-batch-context-v1'
METHOD_CONTROLS={'poolConn006OneOwnerSerializesGettersThroughPublication': ['Executors.newFixedThreadPool(2)', 'release.await(5,TimeUnit.SECONDS)', 'enteredSecond.await(100,TimeUnit.MILLISECONDS)', 'one.get(5,TimeUnit.SECONDS)', 'release.countDown()'], 'webPoolConn006OneOwnerSerializesGettersThroughPublication': ['Executors.newFixedThreadPool(2)', 'release.await(5,TimeUnit.SECONDS)', 'Thread.State.BLOCKED', 'TimeUnit.SECONDS.toNanos(2)', 'one.get(5,TimeUnit.SECONDS)', 'release.countDown()'], 'poolConn007ParallelFakeSourcesHaveCompleteIndependentReturnedCounts': ['Executors.newFixedThreadPool(8)', 'i<64', 'newFixture()', 'executor.invokeAll(tasks)', 'actual.get(i).get()'], 'webPoolConn007ParallelFakeSourcesHaveCompleteIndependentReturnedCounts': ['Executors.newFixedThreadPool(8)', 'i<64', 'newFixture()', 'executor.invokeAll(tasks,5,TimeUnit.SECONDS)', 'actual.get(i).get(5,java.util.concurrent.TimeUnit.SECONDS)'], 'metric006ConcurrentCallersObserveOnlyOriginalCatalog': ['Executors.newFixedThreadPool(4)', 'index<64', 'executor.invokeAll(tasks)', 'future.get()', 'executor.shutdownNow()', 'executor.awaitTermination(10,TimeUnit.SECONDS)'], 'retConf007ParallelModeVerificationCannotMutateOrShareOtherModesConfiguration': ['Executors.newFixedThreadPool(8)', 'i<64', 'executor.invokeAll(tasks)', 'result.get()'], 'retConf008GeneratedConfigurationUsesIndependentIntegerLongHashAndFixedTextOracles': ['assertFalse(value.equals(null))', 'assertEquals(705033170,value.hashCode())', 'assertEquals(-31,newRetentionConfiguration(Integer.MAX_VALUE,Long.MAX_VALUE).hashCode())'], 'transferMet007ConcurrentAtomicSnapshotNeverMixesCohortsOrChangesOldValues': ['Executors.newFixedThreadPool(8)', 'IntStream.range(0,64)', 'snapshot==first||snapshot==second', 'pool.invokeAll(jobs)', 'result.get()']}

def main():
    invocation=capture(__file__);assert not OUT.exists()
    hp=data.BASE/'PG12380-pool-batch-host-v1/manifest.json';host=data.read_checked(hp,'d12e56ad21684f4c31b690880763c69db7744be141228db54119ce0dcf71c12f');assert host['source']==SOURCE and host['actualExit']==0 and host['observedTestExecutions']==38
    sp=data.BASE/'PG12382-pool-batch-static-v1';st=data.read_checked(sp/'manifest.json','ef847e28425796fadd1e804a7367c5f4fca93da901c84a8ea544838b0e277d5e');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256'] and st['reports']['pmd']['findings']==26 and st['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');rows=[]
    for path,node in actual:
        ident=original_match(path,node,original,actual);a=dict(node.attrib);rule=a['rule'];method=a.get('method');text=(data.ROOT/path).read_text();sha=data.sha(text.encode());assert sha==host['begin']['sourceInputHashes'][path]
        ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        point=next(i for i,(_,p) in enumerate(ts) if p==start)
        assert method in METHOD_CONTROLS;lo,hi,name=min((v for v in functions(ts) if v[0]<=point<=v[1]),key=lambda v:v[1]-v[0]);assert name==method;holder=method;controls=METHOD_CONTROLS[method]
        if rule=='DoNotUseThreads':
            kind='FINITE_OWNED_STANDALONE_FIXTURE_WORKERS';reason='Standalone JavaSE original JUnit owns finite2/4/8-worker pools and finite64-task workloads, with fake MXBean getters or supplied immutable values only. API collector, transfer, retention and catalog invokeAll/get preserve no local timeout; Web collector uses5-second deadlines. Publication latches5seconds, Web BLOCKED poll2seconds and100ms negative observation are original contract. TWR or catalog finally shutdownNow+awaitTermination10seconds closes caller pools. Actual normal JVM terminal and outer240seconds are distinct from those local bounds. No application/EJB worker, live pool/DB/JMX/network/VM/Root activity.'
        elif rule=='CloseResource':
            kind='EXPLICIT_EXECUTOR_FINALLY_SHUTDOWN_ORACLE';reason='Original catalog fixture constructs one owned executor before try and closes it in unconditional finally using shutdownNow plus asserted awaitTermination10seconds. Every submitted callable only examines immutable enum metadata/approved TSV values. No production lifecycle ownership or handle is borrowed. Preserve explicit termination oracle; no suppressed diagnostics or application resource.'
        elif rule=='CompareObjectsWithEquals':
            kind='ATOMIC_SNAPSHOT_REFERENCE_IDENTITY_ORACLE';reason='Two preconstructed immutable Usage instances are concurrently recorded. Snapshot must be exactly one original instance, never a reconstructed or mixed cohort. Reference identity is the observable ownership contract deliberately asserted; replacing with equals weakens that oracle. Old supplied objects and original fixed counts are independently checked after workers terminate.'
        else:
            assert rule=='EqualsNull';kind='GENERATED_RECORD_NULL_EQUALS_CONTRACT';reason='The original generated record equality contract must return false for null, wrong type and unequal fields, while fixed independent hash/text vectors are preserved. equals(null) intentionally tests generated equals rather than checking local reference nonnull. Replacing with identity/null expression removes that behavior check.'
        body=''.join(t for t,_ in ts[lo:hi+1]);assert all(c in body for c in controls)
        case_refs=[c for c in host['begin']['cases'] if c['path']==path and c['method']==method];assert case_refs
        assert all(any(a['classname']==c['className'] and a['name']==c['method'] and not a['nonPass'] for a in host['cases']) for c in case_refs)
        rows.append(dict(id=ident['id'],path=path,rule=rule,attributes=a,originalRowSha256=ident['rowSha256'],source=SOURCE,sourceSha256=sha,sourceSpanSha256=data.sha(text[start:end].encode()),scopeName=holder,scopeKind='OWNER_CLASS' if method is None else 'METHOD',scopeTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),controls=controls,currentCases=case_refs,kind=kind,disposition='CONTEXT_NOT_APPLICABLE',reason=reason,currentWholeJoinPending=True,oldRuntimeReassigned=False,productTestsExecutedByReview=0,newAccepted=0))
    count=len({r['id'] for r in rows});assert count==len(rows)==26
    verify(invocation);OUT.mkdir();data.write(OUT/'review.json',dict(source=SOURCE,rows=rows));data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=count,rawRetained=count,rawRetainedMeaning='COUNT_UNIQUE_SELECTED_REVIEWED_RETAINED_FINDING_IDS',wholeStaticScopeRaw=count,productTestsExecuted=0,sourceCorrections=0,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,coverage=None,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
