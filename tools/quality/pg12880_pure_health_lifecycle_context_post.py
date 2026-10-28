"""Independent22 XML/span/enclosing-scope/owner/current-case contexts and25 nonvacuous metadata vectors."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg12248_main_local_maps_post import enclosing_method
from pg11054_api_request_context import original_match

SOURCE='105fd644e90918945607b3ac3e4962843c7762bf'
PIN='75365584df3268405f71f92cfd55ef22bb9c03352699882ddbe542286fe7eb69'
OUT=data.BASE/'PG12880-pure-health-lifecycle-context-post-v1'
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


def main():
    invocation=capture(__file__);assert not OUT.exists();directory=data.BASE/'PG12878-pure-health-lifecycle-context-v1'
    m=data.read_checked(directory/'manifest.json',PIN);rows=data.read_checked(directory/'review.json',m['reviewSha256'])['rows']
    host=data.read_checked(data.BASE/'PG12873-pure-health-lifecycle-host-v2/manifest.json','629cb07806640f9e8a2ec1c35306ca1fccf1b0471e0e16bf6aab5eaadf471330')
    static=data.read_checked(data.BASE/'PG12874-pure-health-lifecycle-static-v1/manifest.json','2369a8378b3be015e6ab03f034cbe38d4d4feb9d31797aa2119d13551fa2e90e')
    raw=(data.BASE/'PG12874-pure-health-lifecycle-static-v1/pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),node) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for node in f if node.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    mapped={original_match(path,node,original,actual)['id']:(path,node) for path,node in actual};assert len(mapped)==len(rows)==len({r['id'] for r in rows})==22 and set(mapped)=={r['id'] for r in rows}
    def validate(row):
        if row.get('id') not in mapped:raise ValueError('known current original ID required')
        path,node=mapped[row['id']];a=dict(node.attrib);method=a['method'];stem=Path(path).stem;text=(data.ROOT/path).read_text();digest=data.sha(text.encode());assert digest==host['begin']['sourceInputHashes'][path]
        ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];lines=text.splitlines(keepends=True)
        start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        point=next(i for i,(_,p) in enumerate(ts) if p==start);lo,hi=enclosing_method(ts,method,point);controls=CONTROLS[(stem,method)]
        compact=''.join(t for t,_ in ts[lo:hi+1]);whole=''.join(t for t,_ in ts);assert all(c in compact for c in controls)
        if stem.endswith('Test'):
            cases=[c for c in host['begin']['cases'] if Path(c['path']).stem==stem and c['method']==method];assert len(cases)==1
            if a['rule']=='AvoidSynchronizedStatement':
                assert stem=='AlertLifecycleTest' and method.startswith('alert009');kind='INTENTIONAL_PUBLIC_OWNER_MONITOR_DEFENSE_CHECK'
            else:
                assert a['rule']=='DoNotUseThreads';kind='OWNED_FINITE_PURE_HEALTH_ALERT_FIXTURE_WORKERS'
        else:
            assert a['rule']=='AvoidSynchronizedStatement' and whole.count('privatefinalObjectlock=newObject();')==1 and 'synchronized(this)' not in whole
            kind='PRIVATE_FINAL_PURE_ALERT_OR_TIMED_STATE_MONITOR'
            if stem=='AlertLifecycle':
                if method=='interruptContinuity':cases=[c for c in host['begin']['cases'] if Path(c['path']).stem=='AlertContinuityTest'];assert len(cases)==2
                elif method=='snapshot':cases=[c for c in host['begin']['cases'] if c['method'].startswith(('alert001','alert003','alert006','alert007','alert009','protectedAlert001','protectedAlert002'))];assert len(cases)==7
                else:cases=[c for c in host['begin']['cases'] if Path(c['path']).stem in ['AlertLifecycleTest','AlertContinuityTest']];assert len(cases)==14
            else:
                assert stem=='TimedFilesystemMonitor'
                cases=[c for c in host['begin']['cases'] if Path(c['path']).stem=='TimedFilesystemMonitorTest' and (method!='snapshot' or not c['method'].startswith('timedFs004'))];assert len(cases)==(5 if method=='snapshot' else 6)
        assert all(any(v['classname']==c['className'] and v['name']==c['method'] and not v['nonPass'] for v in host['cases']) for c in cases)
        identity=original_match(path,node,original,actual)
        expected=dict(path=path,rule=a['rule'],attributes=a,originalRowSha256=identity['rowSha256'],source=SOURCE,sourceSha256=digest,sourceSpanSha256=data.sha(text[start:end].encode()),scopeName=method,scopeKind='METHOD',scopeTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),controls=controls,currentCases=cases,kind=kind,disposition='CONTEXT_NOT_APPLICABLE',currentWholeJoinPending=True,oldRuntimeReassigned=False,productTestsExecutedByReview=0,newAccepted=0)
        if any(row.get(k)!=v for k,v in expected.items()) or not row.get('reason'):raise ValueError('exact current source/span/scope/owner/cases required')
    for row in rows:validate(row)
    labels=[]
    for field,value in [('id','foreign'),('source','0'*40),('sourceSha256','0'*64),('sourceSpanSha256','0'*64),('scopeName','foreign'),('scopeKind','UNKNOWN'),('scopeTokenSha256','0'*64),('controls',[]),('currentCases',[]),('kind','EXEMPT'),('disposition','SUPPRESSED'),('reason',''),('currentWholeJoinPending',False),('oldRuntimeReassigned',True),('productTestsExecutedByReview',1),('newAccepted',1)]:
        bad=copy.deepcopy(rows[0]);assert bad.get(field)!=value;bad[field]=value
        try:validate(bad)
        except ValueError:labels.append(field)
        else:raise AssertionError('wrong context accepted')
    def counts(v):
        if v.get('sourceContexts')!=22 or v.get('rawRetained')!=22 or v.get('wholeStaticScopeRaw')!=22 or v.get('newMainContexts')!=5 or v.get('newTestPrivateMonitorOracleContext')!=1 or v.get('historicalThreadSourceRebindings')!=16 or v.get('rawRetainedMeaning')!='COUNT_UNIQUE_SELECTED_REVIEWED_RETAINED_FINDING_IDS' or v.get('sourceCorrections')!=0 or v.get('newAccepted')!=0:raise ValueError('selected context counts, no raw correction/global credit')
    counts(m)
    for field,value in [('sourceContexts',23),('rawRetained',3),('wholeStaticScopeRaw',0),('rawRetainedMeaning','WHOLE_GLOBAL_RAW'),('sourceCorrections',24),('newAccepted',1),('newMainContexts',0),('newTestPrivateMonitorOracleContext',0),('historicalThreadSourceRebindings',0)]:
        bad=dict(m);assert bad.get(field)!=value;bad[field]=value
        try:counts(bad)
        except ValueError:labels.append('manifest.'+field)
        else:raise AssertionError('wrong context counts accepted')
    assert len(labels)==25 and host['source']==SOURCE and host['actualExit']==0 and host['observedTestExecutions']==38
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewManifestSha256=PIN,sourceContexts=22,rawRetained=22,metadataNegativeVectors=len(labels),metadataNegativeLabels=labels,productTestsExecuted=0,sourceCorrections=0,newAccepted=0,coverage=None,wholeF03Accepted=False,whole451Accepted=False));print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
