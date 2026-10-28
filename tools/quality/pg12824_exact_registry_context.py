"""Three raw sync/thread nodes: explicit private-state atomicity and owned finite fixture context."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match

SOURCE='0124b5938a50f4ceea542486c336ba12146cb1b4'
OUT=data.BASE/'PG12824-exact-registry-context-v1'
CONTROLS={
 'dbTime002IndependentSecondsHistogramCdfAndTwoMaximumSamplesNeverLongWrap':['Map<Double,Double>counts=newHashMap<>()','counts.put(bucket.bucket(),bucket.count())','assertEquals(2.0,counts.get(.001).doubleValue())'],
 'dbTime007ConcurrentSampleCountSumAndMaximumUsePrecomputedIntegerInputs':['varexecutor=Executors.newFixedThreadPool(8)','index<64','counts.merge(key,1L,Long::sum)','sums.merge(key,ns,Long::sum)','maxima.merge(key,ns,Long::max)','recorder.record(query,outcome,ns);returnnull;','executor.invokeAll(tasks)','result.get(5,TimeUnit.SECONDS)','assertEquals(64,registry.records.get())'],
 'record':['synchronized(stateLock){sampleCount++;total+=amount;maximum=Math.max(maximum,amount);for(inti=0;i<BOUNDARIES.length;i++)if(amount<=BOUNDARIES[i])buckets[i]++;}'],
 'takeSnapshot':['synchronized(stateLock){','varcounts=newCountAtBucket[BOUNDARIES.length]','counts[i]=newCountAtBucket(BOUNDARIES[i],buckets[i])','newHistogramSnapshot(sampleCount,total,maximum,newValueAtPercentile[0],counts,null)'],
 'exDur009ConcurrentUpdatesAndSnapshotsHaveConsistentIndependentIdentity':['try(varregistry=registry();varexecutor=Executors.newFixedThreadPool(5))','thread<4','i<64','i<128','start.await(5,TimeUnit.SECONDS)','start.countDown()','future.get(10,TimeUnit.SECONDS)','assertEquals(256,summary.count())','cdf(summary,0,0,0,256,256)']}


def main():
    invocation=capture(__file__);assert not OUT.exists()
    host=data.read_checked(data.BASE/'PG12839-exact-registry-caller-host-v2/manifest.json','70426a057be6c8f8b53e7b52ea98f2a3e2e9269039864c73da0d6a81ad562291')
    static=data.read_checked(data.BASE/'PG12840-exact-registry-caller-static-v1/manifest.json','bc41a92bde38e75c3589339c5c4ba3540c6199061767c48aeb8bd64199b07bd5')
    proof=data.read_checked(data.BASE/'PG12842-exact-registry-caller-post-v1/manifest.json','3ba0058d651605f37b1a03293001919b431ce83471ebc14464de1a14bbe00aa3')
    assert host['source']==static['source']==proof['source']==SOURCE and host['actualExit']==proof['actualExit']==0 and host['observedTestExecutions']==19 and static['actualExit']==1
    raw=(data.BASE/'PG12840-exact-registry-caller-static-v1/pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),node) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for node in f if node.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');rows=[]
    for path,node in actual:
        identity=original_match(path,node,original,actual);a=dict(node.attrib);method=a['method'];text=(data.ROOT/path).read_text();assert data.sha(text.encode())==host['begin']['sourceInputHashes'][path]
        ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];lines=text.splitlines(keepends=True)
        start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        point=next(i for i,(_,p) in enumerate(ts) if p==start);lo,hi,name=min((v for v in functions(ts) if v[0]<=point<=v[1]),key=lambda v:v[1]-v[0]);assert name==method
        compact=''.join(t for t,_ in ts[lo:hi+1]);whole=''.join(t for t,_ in ts);controls=CONTROLS[method];assert all(c in compact for c in controls)
        if a['rule']=='AvoidSynchronizedStatement':
            assert method in ['record','takeSnapshot'] and a['class']=='ExactDurationMeterRegistry.ExactSummary'
            assert whole.count('privatefinalObjectstateLock=newObject();')==1 and whole.count('synchronized(stateLock)')==2 and 'synchronized(this)' not in whole
            cases=[c for c in host['begin']['cases'] if any(c['method'].startswith('exDur'+v) for v in ['001','002','003','004','008','009','010'])];assert len(cases)==7
            kind='PRIVATE_FINAL_MONITOR_CONSTANT_MEMORY_ATOMIC_SNAPSHOT'
            reason='411 section9 explicitly requires private-final state lock. Same private stateLock protects count/total/max/all five cumulative buckets in record and fresh defensive snapshot copy. No public this/class monitor, nested lock, blocking I/O, callback or external authority in either critical section. SDK snapshot allocations only; monitor exits release on ordinary exception. ReentrantLock is a generic PMD preference, not a stronger project contract. Current whole boundary/defensive/concurrent tests and full selected counters support this source, not all JVM scheduling/OOME possibilities.'
        elif method.startswith('exDur009'):
            assert a['rule']=='DoNotUseThreads'
            cases=[c for c in host['begin']['cases'] if c['method']==method];assert len(cases)==1
            kind='OWNED_FINITE_FIVE_WORKER_EXACT_SNAPSHOT_FIXTURE'
            reason='Standalone own SDK fixture, four writers each64 records plus one observer128 snapshots, own CountDownLatch wait5seconds and Future.get10seconds. TWR closes executor then registry. TWR local absolute deadline absent; distinct outer JVM240seconds. No application process, DB, network, filesystem, VM, Root, native, keys or authority. Existing historical thread context is source-rebound only; raw warning retained.'
        else:
            assert method.startswith('dbTime00') and a['rule'] in ['DoNotUseThreads','UseConcurrentHashMap']
            cases=[c for c in host['begin']['cases'] if c['path']==path and c['method']==method];assert len(cases)==1
            if a['rule']=='UseConcurrentHashMap':
                kind='THREAD_CONFINED_INDEPENDENT_ORACLE_MAP_NOT_SHARED_WITH_TASKS'
                reason='Whole source shows002 CDF map created/read only on calling thread. In007 counts/sums/maxima are filled on parent before invokeAll and read after join; submitted lambda captures only recorder/query/outcome/ns, never the maps. They are independent expected values, not shared Product state. No ConcurrentHashMap requirement for these thread-confined maps; historical ref source-rebound, raw retained.'
            else:
                assert method.startswith('dbTime007')
                kind='OWNED_FINITE_EIGHT_WORKER_DB_DURATION_FIXTURE'
                reason='Own SDK registry, eight standalone workers/64 finite scalar-record callbacks, parent independent count/sum/max, TWR reverse close. invokeAll and TWR lack local absolute deadline; later Future.get5seconds and outer JVM240seconds distinguished. No SQL/JDBC/DB/network/VM/Root/native/authority operations. Historical thread refs source-rebound, raw retained.'
        assert all(any(v['classname']==c['className'] and v['name']==c['method'] and not v['nonPass'] for v in host['cases']) for c in cases)
        rows.append(dict(id=identity['id'],path=path,rule=a['rule'],attributes=a,originalRowSha256=identity['rowSha256'],source=SOURCE,sourceSha256=data.sha(text.encode()),sourceSpanSha256=data.sha(text[start:end].encode()),scopeName=method,scopeKind='METHOD',scopeTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),controls=controls,currentCases=cases,kind=kind,disposition='CONTEXT_NOT_APPLICABLE',reason=reason,currentWholeJoinPending=True,oldRuntimeReassigned=False,productTestsExecutedByReview=0,newAccepted=0))
    assert {r['id'] for r in rows}=={'PMD-00358','PMD-00359','PMD-02175',*{'PMD-'+str(n).zfill(5) for n in range(2168,2174)}}
    verify(invocation);OUT.mkdir();data.write(OUT/'review.json',dict(source=SOURCE,rows=rows))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=9,rawRetained=9,rawRetainedMeaning='COUNT_UNIQUE_SELECTED_REVIEWED_RETAINED_FINDING_IDS',wholeStaticScopeRaw=9,newPrivateMonitorContexts=2,historicalThreadAndMapSourceRebindings=7,sourceCorrections=0,productTestsExecuted=0,newAccepted=0,wholeF03Accepted=False,whole451Accepted=False,coverage=None));print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
