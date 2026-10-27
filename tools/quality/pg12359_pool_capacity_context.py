"""Twenty-four selected fixture applicability reasons from actual static XML and original29 execution."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match

SOURCE='e2a04c5d5775b8629ce3c4f17259d8378b2bb5f9'
OUT=data.BASE/'PG12359-pool-capacity-context-v1'
METHOD_CONTROLS={
 'poolRead007ParallelOwnedInterfacesCannotShareMutableObservationState':['Executors.newFixedThreadPool(8)','i<64','newFixture()','pool.invokeAll(tasks)','actual.get(i).get()'],
 'webPoolRead007ParallelOwnedInterfacesCannotShareMutableObservationState':['Executors.newFixedThreadPool(8)','i<64','newFixture()','pool.invokeAll(tasks,5,java.util.concurrent.TimeUnit.SECONDS)','actual.get(i).get(5,java.util.concurrent.TimeUnit.SECONDS)'],
 'opMis007ParallelObservationsHaveExactCountsWithoutCardinalityGrowth':['Executors.newFixedThreadPool(8)','i<64','executor.invokeAll(tasks)','assertTrue(result.get())','assertEquals(64,registry.increments.get())'],
 'c03OnlyOneOf100SimultaneousReservationsCanCrossEachCriticalBoundary':['Executors.newFixedThreadPool(16)','i<100','executor.invokeAll(tasks)','future.get(10,TimeUnit.SECONDS)','assertEquals(1,accepted)'],
 'c03CallerMonitorsCannotBlockReservationMetricsRetainOrClose':['Executors.newVirtualThreadPerTaskExecutor()','synchronized(capacity)','synchronized(reservation)','reservation.retain();reservation.close();','get(5,TimeUnit.SECONDS)'],
 'c01EveryByteAndFileAlertBoundaryMatchesFixedThresholds':['varreservation=capacity.reserve(bytes);','reservation.close();'],
 'c02RetainAndReleaseAreExactlyOnceIncludingUndeletedPartialFile':['first.retain();first.close();','second.close();second.close();','capacity.reserve(4800).retain();'],
 'c02InFlightAdmissionCanReachCriticalButNeverExhaustTheFiveGbDesignBudget':['varreservation=capacity.reserve(48_000_000);','reservation.close();','capacity.reserve(1).retain();'],
 'pool':['HikariPoolMXBean.class.cast(Proxy.newProxyInstance(HikariPoolMXBean.class.getClassLoader(),','newClass<?>[]{HikariPoolMXBean.class}'],
 'config':['HikariConfigMXBean.class.cast(Proxy.newProxyInstance(HikariConfigMXBean.class.getClassLoader(),','newClass<?>[]{HikariConfigMXBean.class}']}

def fixture_block(ts):
    starts=[i+1 for i in range(len(ts)-2) if ts[i][0]=='class' and ts[i+1][0]=='Fixture' and ts[i+2][0]=='{'];assert len(starts)==1
    lo=starts[0];depth=0
    for i in range(lo+1,len(ts)):
        if ts[i][0]=='{':depth+=1
        elif ts[i][0]=='}':
            depth-=1
            if depth==0:return lo,i
    raise ValueError('complete Fixture owner block required')

def main():
    invocation=capture(__file__);assert not OUT.exists()
    hp=data.BASE/'PG12354-pool-capacity-host-v1/manifest.json';host=data.read_checked(hp,'4ff7ea2da45aeae1e1e91d69c8f9b30cd5f943905b126231426908398ac706aa');assert host['source']==SOURCE and host['actualExit']==0 and host['observedTestExecutions']==29
    sp=data.BASE/'PG12356-pool-capacity-static-v1';st=data.read_checked(sp/'manifest.json','fce42d8b4757ef8be42f5d7d8f9436f5f5cf52928e1c4b9535fca984e5387b16');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256'] and st['reports']['pmd']['findings']==24 and st['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');rows=[]
    for path,node in actual:
        ident=original_match(path,node,original,actual);a=dict(node.attrib);rule=a['rule'];method=a.get('method');text=(data.ROOT/path).read_text();sha=data.sha(text.encode());assert sha==host['begin']['sourceInputHashes'][path]
        ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        point=next(i for i,(_,p) in enumerate(ts) if p==start)
        if rule=='UseConcurrentHashMap':
            assert method is None and a['variable']=='faults';lo,hi=fixture_block(ts);holder='Fixture';controls=['finalMap<String,Throwable>faults=newHashMap<>();','faults.get(point)','beforeActive.execute()']
            kind='PER_CASE_OR_PER_TASK_FIXTURE_FAULT_MAP';reason='Each serial test or each of64 concurrent tasks creates its own Fixture, including its mutable faults map/calls list. Fault insertion precedes only that fixture\'s synchronous typed getter calls; shared observation is stateless. No field map crosses an owner/task; a ConcurrentHashMap replacement would not establish any additional cross-owner invariant.'
        else:
            assert method in METHOD_CONTROLS;lo,hi,name=min((v for v in functions(ts) if v[0]<=point<=v[1]),key=lambda v:v[1]-v[0]);assert name==method;holder=method;controls=METHOD_CONTROLS[method]
            if rule=='UseProperClassLoader':
                kind='EXACT_SDK_INTERFACE_PROXY_LOADER';reason='JDK Proxy implements the exact borrowed public Hikari MXBean interface using its defining class loader and an allowlisted fake getter handler. This preserves SDK interface identity, creates no pool/config/JMX connection and exposes no credential/control getter. Dependency hashes and all original cases are frozen; no context-classloader fallback or reflective access.'
            elif rule=='DoNotUseThreads':
                kind='FINITE_OWNED_STANDALONE_FIXTURE_WORKERS';reason='Standalone JavaSE JUnit owns and closes finite8/16/virtual workers with64/100 tasks, fake getters or memory counters only. API pool and operation invokeAll/get have no local timeout; outer JVM240 seconds and actual normal terminal bound this execution. Web pool has5-second invokeAll/get; Transfer has5/10-second gets. No EJB or application worker/resources, real DB/file/network/Root operation.'
            elif rule=='CloseResource':
                kind='MEMORY_RESERVATION_EXPLICIT_RETAIN_RELEASE_ORACLE';reason='Reservation is a memory-accounting token, not an FD/stream or externally acquired resource. Original case explicitly checks close/repeated close, ownership transfer and retained bytes; retain deliberately prevents rollback and one callback performs retain/close. Replacing this oracle with implicit TWR rollback changes the tested lifetime. Every fixture is local; no physical file or capacity scan exists.'
            else:
                assert rule=='AvoidSynchronizedStatement';kind='CALLER_MONITOR_INDEPENDENCE_ORACLE';reason='The test deliberately holds each publicly visible capacity/reservation monitor while a separately owned worker completes reserve/retain/close with5-second deadline. Production uses its own ReentrantLock. This is a negative caller-monitor independence oracle, not production synchronization; replacing the held monitor removes that oracle.'
        body=''.join(t for t,_ in ts[lo:hi+1]);assert all(c in body for c in controls)
        case_refs=[c for c in host['begin']['cases'] if c['path']==path and (c['method']==method or method in (None,'pool','config'))];assert case_refs
        assert all(any(a['classname']==c['className'] and a['name']==c['method'] and not a['nonPass'] for a in host['cases']) for c in case_refs)
        rows.append(dict(id=ident['id'],path=path,rule=rule,attributes=a,originalRowSha256=ident['rowSha256'],source=SOURCE,sourceSha256=sha,sourceSpanSha256=data.sha(text[start:end].encode()),scopeName=holder,scopeKind='OWNER_CLASS' if method is None else 'METHOD',scopeTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),controls=controls,currentCases=case_refs,kind=kind,disposition='CONTEXT_NOT_APPLICABLE',reason=reason,currentWholeJoinPending=True,oldRuntimeReassigned=False,productTestsExecutedByReview=0,newAccepted=0))
    count=len({r['id'] for r in rows});assert count==len(rows)==24
    verify(invocation);OUT.mkdir();data.write(OUT/'review.json',dict(source=SOURCE,rows=rows));data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=count,rawRetained=count,rawRetainedMeaning='COUNT_UNIQUE_SELECTED_REVIEWED_RETAINED_FINDING_IDS',wholeStaticScopeRaw=count,productTestsExecuted=0,sourceCorrections=0,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,coverage=None,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
