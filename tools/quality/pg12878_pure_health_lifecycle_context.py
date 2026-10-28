"""Current22 private-state/test monitor and owned-thread contexts from original38; raw preserved."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match

SOURCE='105fd644e90918945607b3ac3e4962843c7762bf'
OUT=data.BASE/'PG12878-pure-health-lifecycle-context-v1'
CONTROLS={
 ('AlertLifecycle','observe'):['synchronized(lock)','lastElapsed=Optional.of(elapsed)','if(observed==Severity.NORMAL)returnnormal(clearance,elapsed)','active=Optional.of(newEvent(conditionKey,serviceKey,level,first,at,count,true))'],
 ('AlertLifecycle','interruptContinuity'):['if(elapsed.isNegative())','synchronized(lock)','elapsed.compareTo(lastElapsed.orElseThrow())<0','lastElapsed=Optional.of(elapsed)','recoveringSince=Optional.empty()'],
 ('AlertLifecycle','snapshot'):['synchronized(lock){returnactive;}'],
 ('TimedFilesystemMonitor','observe'):['synchronized(lock)','lastElapsed=Optional.of(elapsed)','warning.observe(State.UNKNOWN,elapsed,consecutive)','critical.observe(State.UNKNOWN,elapsed,consecutive)','if(!consecutive)lifecycle.interruptContinuity(elapsed)','thresholds.filesystem(value,above80,above90)'],
 ('TimedFilesystemMonitor','snapshot'):['synchronized(lock){returnlifecycle.snapshot();}'],
 ('AlertLifecycleTest','alert009ConcurrentSameTickCountsAndPrivateMonitor'):['try(varexecutor=Executors.newFixedThreadPool(4))','index<64','synchronized(owner)','executor.invokeAll(tasks,10,TimeUnit.SECONDS)','value<=65','assertEquals(expected,counts)','executor.shutdownNow()','assertTrue(executor.awaitTermination(10,TimeUnit.SECONDS))'],
 ('AlertLifecycleTest','protectedAlert002ConcurrentNormalSamplesCannotRetireOrChangeProtectedEvent'):['newCondition[]{Condition.DLQ,Condition.INTEGRITY_CONFIG}','i<64','try(varexecutor=Executors.newFixedThreadPool(8))','executor.invokeAll(tasks,10,TimeUnit.SECONDS)','assertSame(first,result.get())','assertSame(first,owner.snapshot().orElseThrow())'],
 ('TimedFilesystemMonitorTest','timedFs006ConcurrentOwnerAndLocalStatusLiteral'):['try(varexecutor=Executors.newFixedThreadPool(4))','index<64','executor.invokeAll(tasks,10,TimeUnit.SECONDS)','executor.shutdownNow()','assertTrue(executor.awaitTermination(10,TimeUnit.SECONDS))','assertEquals(BigInteger.valueOf(65),current.count())'],
 ('FilesystemHealthObservationTest','fsInput007NullAndConcurrentIndependentReadsDoNotAcquireOwnership'):['try(varpool=Executors.newFixedThreadPool(8))','IntStream.range(0,64)','pool.invokeAll(jobs)','assertEquals(80,result.get())','assertEquals(64,store.totalReads.get())','assertEquals(64,store.usableReads.get())'],
 ('FilesystemHealthObservationTest','fsInput010NullBackwardsGapAndConcurrentPollHaveOneSerializedOwner'):['try(varpool=Executors.newFixedThreadPool(8))','IntStream.range(0,64)','pool.invokeAll(jobs)','assertEquals(Severity.CRITICAL,result.get())','assertEquals(BigInteger.valueOf(65),monitor.snapshot().orElseThrow().count())'],
 ('MonitoringObservationClockTest','obsClock007ConcurrentContextsHaveUniqueMonotonicSnapshots'):['try(varpool=Executors.newFixedThreadPool(8))','IntStream.range(0,64)','pool.invokeAll(jobs)','result.get()','for(inti=1;i<=64;i++)expected.add(Duration.ofNanos(i))','assertEquals(expected,actual)','assertEquals(65,ticks.get())','assertEquals(64,wall.reads.get())']}


def cases_for(host,stem,method):
    if stem.endswith('Test'):
        return [c for c in host['begin']['cases'] if Path(c['path']).stem==stem and c['method']==method]
    if stem=='AlertLifecycle':
        if method=='interruptContinuity':return [c for c in host['begin']['cases'] if Path(c['path']).stem=='AlertContinuityTest']
        if method=='snapshot':return [c for c in host['begin']['cases'] if c['method'].startswith(('alert001','alert003','alert006','alert007','alert009','protectedAlert001','protectedAlert002'))]
        return [c for c in host['begin']['cases'] if Path(c['path']).stem in ['AlertLifecycleTest','AlertContinuityTest']]
    return [c for c in host['begin']['cases'] if Path(c['path']).stem=='TimedFilesystemMonitorTest' and (method!='snapshot' or not c['method'].startswith('timedFs004'))]


def main():
    invocation=capture(__file__);assert not OUT.exists()
    host=data.read_checked(data.BASE/'PG12873-pure-health-lifecycle-host-v2/manifest.json','629cb07806640f9e8a2ec1c35306ca1fccf1b0471e0e16bf6aab5eaadf471330')
    static=data.read_checked(data.BASE/'PG12874-pure-health-lifecycle-static-v1/manifest.json','2369a8378b3be015e6ab03f034cbe38d4d4feb9d31797aa2119d13551fa2e90e')
    proof=data.read_checked(data.BASE/'PG12876-pure-health-lifecycle-post-v1/manifest.json','927664b9e53c777f78d399ca5448afce4e4b15c39870934a25a6529f809249d4')
    assert host['source']==static['source']==proof['source']==SOURCE and host['actualExit']==proof['actualExit']==0 and host['observedTestExecutions']==38 and static['actualExit']==1
    raw=(data.BASE/'PG12874-pure-health-lifecycle-static-v1/pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),node) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for node in f if node.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');rows=[]
    for path,node in actual:
        identity=original_match(path,node,original,actual);a=dict(node.attrib);method=a['method'];stem=Path(path).stem;text=(data.ROOT/path).read_text();assert data.sha(text.encode())==host['begin']['sourceInputHashes'][path]
        ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];lines=text.splitlines(keepends=True)
        start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        point=next(i for i,(_,p) in enumerate(ts) if p==start);lo,hi,name=min((v for v in functions(ts) if v[0]<=point<=v[1]),key=lambda v:v[1]-v[0]);assert name==method
        compact=''.join(t for t,_ in ts[lo:hi+1]);whole=''.join(t for t,_ in ts);controls=CONTROLS[(stem,method)];assert all(c in compact for c in controls)
        cases=cases_for(host,stem,method);assert cases
        if not stem.endswith('Test'):
            assert a['rule']=='AvoidSynchronizedStatement' and whole.count('privatefinalObjectlock=newObject();')==1 and 'synchronized(this)' not in whole
            kind='PRIVATE_FINAL_PURE_ALERT_OR_TIMED_STATE_MONITOR'
            reason='411 section9 requires private-final state lock. Alert transition/gap/snapshot and timed threshold windows/alert projection are each one atomic local observation, no public this/class monitor. No I/O/callback inside these primary critical sections; nested window/lifecycle lock order is one direction in reviewed closure. ReentrantLock suggestion is not a stronger project contract. Boundary/rejected-state/private-owner/finite concurrent tests cover source contract, not all scheduling/OOME or actual system observation.'
        elif a['rule']=='AvoidSynchronizedStatement':
            assert stem=='AlertLifecycleTest' and method.startswith('alert009') and len(cases)==1
            kind='INTENTIONAL_PUBLIC_OWNER_MONITOR_DEFENSE_CHECK'
            reason='Test deliberately holds public owner monitor while separate workers update owner: successful independent counts2..65 prove Main uses a distinct private monitor. Replacing this fixture lock would remove the safety oracle. Owned four-worker invokeAll10seconds/TWR+original finally and outer240seconds remain; no external object/process locking or authority.'
        else:
            assert a['rule']=='DoNotUseThreads' and len(cases)==1
            kind='OWNED_FINITE_PURE_HEALTH_ALERT_FIXTURE_WORKERS'
            reason='Standalone local pools, four/eight workers and64 finite scalar/stub calls; protected alert test is logical enum state only. Alert/Timed invokeAll/await10seconds where explicit; Filesystem/Clock invokeAll and get, plus all TWR close, have no local absolute deadline. Distinct outer JVM240seconds. FileStore methods are fixed overridden values/counters, not actual filesystem or identity; no DB/network/VM/Root/native/key/permission operation. Existing thread refs source-rebound, raw retained.'
        assert all(any(v['classname']==c['className'] and v['name']==c['method'] and not v['nonPass'] for v in host['cases']) for c in cases)
        rows.append(dict(id=identity['id'],path=path,rule=a['rule'],attributes=a,originalRowSha256=identity['rowSha256'],source=SOURCE,sourceSha256=data.sha(text.encode()),sourceSpanSha256=data.sha(text[start:end].encode()),scopeName=method,scopeKind='METHOD',scopeTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),controls=controls,currentCases=cases,kind=kind,disposition='CONTEXT_NOT_APPLICABLE',reason=reason,currentWholeJoinPending=True,oldRuntimeReassigned=False,productTestsExecutedByReview=0,newAccepted=0))
    assert len(rows)==len({r['id'] for r in rows})==22
    verify(invocation);OUT.mkdir();data.write(OUT/'review.json',dict(source=SOURCE,rows=rows))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=22,rawRetained=22,rawRetainedMeaning='COUNT_UNIQUE_SELECTED_REVIEWED_RETAINED_FINDING_IDS',wholeStaticScopeRaw=22,newMainContexts=5,newTestPrivateMonitorOracleContext=1,historicalThreadSourceRebindings=16,sourceCorrections=0,productTestsExecuted=0,newAccepted=0,wholeF03Accepted=False,whole451Accepted=False,coverage=None));print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
