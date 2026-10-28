"""Independent actual XML spans, enclosing scopes, owner controls, current cases and24 nonvacuous vectors."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg12248_main_local_maps_post import enclosing_method
from pg11054_api_request_context import original_match

SOURCE='f8ad1ae16aa52db0119fefbad9e2cea6d6affe55'
PIN='3273a1622d8a8121316e31c28821651d27b5f81db7944f4e62998d7cba75403e'
OUT=data.BASE/'PG12856-monitor-sequence-context-post-v1'
CONTROLS={
 ('ContinuousConditionWindow','observe'):['synchronized(lock)','previous=elapsed','if(state!=State.VIOLATING){violationStart=null;','if(!consecutive||violationStart==null)violationStart=elapsed','elapsed.minus(violationStart)'],
 ('MonitoringObservationClock','context'):['synchronized(lock)','longnow=ticks.getAsLong()','if(now-last<0||elapsed<0)','Objects.requireNonNull(utc.instant(),"observation instant")','newObservationContext(clearance,at,Duration.ofNanos(elapsed))','last=now'],
 ('MonitoringPoller','observe'):['synchronized(lock){returnobserveLocked(consecutive,context,action);}'],
 ('MonitoringPoller','observeNow'):['synchronized(lock)','context=clock.context(clearance)','catch(RuntimeException|ErrorunavailableClock){interrupted=true;throwunavailableClock;}','returnobserveLocked(consecutive,context,action)'],
 ('MonitoringPoller','observeLocked'):['action.apply(consecutive&&!interrupted,context)','lastCompleted=Optional.of(context.elapsed())','interrupted=false','catch(RuntimeException|ErrorunavailableObservation){interrupted=true;throwunavailableObservation;}'],
 ('ContinuousConditionWindowTest','monWindow007ConcurrentSamePointHasOneOrigin'):['try(varexecutor=Executors.newFixedThreadPool(4))','index<64','executor.invokeAll(tasks,10,TimeUnit.SECONDS)','assertEquals(Duration.ZERO,future.get())','executor.shutdownNow()','assertTrue(executor.awaitTermination(10,TimeUnit.SECONDS))'],
 ('MonitoringObservationClockTest','obsClock007ConcurrentContextsHaveUniqueMonotonicSnapshots'):['try(varpool=Executors.newFixedThreadPool(8))','IntStream.range(0,64)','pool.invokeAll(jobs)','result.get()','for(inti=1;i<=64;i++)expected.add(Duration.ofNanos(i))','assertEquals(expected,actual)','assertEquals(65,ticks.get())','assertEquals(64,wall.reads.get())'],
 ('MonitoringPollerTest','poll007ParallelNonAtomicActionsAreSerializedIntoOneToSixtyFour'):['try(varpool=Executors.newFixedThreadPool(8))','IntStream.range(0,64)','poll.observe(true,at(1),(continuous,context)->++count[0])','pool.invokeAll(jobs)','result.get()','for(inti=1;i<=64;i++)expected.add(i)','assertEquals(expected,actual)','assertEquals(64,count[0])']}


def main():
    invocation=capture(__file__);assert not OUT.exists();directory=data.BASE/'PG12854-monitor-sequence-context-v1'
    m=data.read_checked(directory/'manifest.json',PIN);rows=data.read_checked(directory/'review.json',m['reviewSha256'])['rows']
    host=data.read_checked(data.BASE/'PG12848-monitor-sequence-host-v1/manifest.json','89f4bac39fcdfe6410e3f3badbe50d03c13899241317f516133592cc2138e733')
    static=data.read_checked(data.BASE/'PG12850-monitor-sequence-static-v1/manifest.json','77ddcdcd19da753042dca663d3940012a6ef1fdfae74bf463e546a122ff8c3e3')
    raw=(data.BASE/'PG12850-monitor-sequence-static-v1/pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),node) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for node in f if node.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    mapped={original_match(path,node,original,actual)['id']:(path,node) for path,node in actual};assert len(mapped)==len(rows)==len({r['id'] for r in rows})==17 and set(mapped)=={r['id'] for r in rows}
    def validate(row):
        if row.get('id') not in mapped:raise ValueError('known current original ID required')
        path,node=mapped[row['id']];a=dict(node.attrib);method=a['method'];stem=Path(path).stem;text=(data.ROOT/path).read_text();digest=data.sha(text.encode());assert digest==host['begin']['sourceInputHashes'][path]
        ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];lines=text.splitlines(keepends=True)
        start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        point=next(i for i,(_,p) in enumerate(ts) if p==start);lo,hi=enclosing_method(ts,method,point)
        controls=CONTROLS[(stem,method)];compact=''.join(t for t,_ in ts[lo:hi+1]);whole=''.join(t for t,_ in ts);assert all(c in compact for c in controls)
        if stem.endswith('Test'):
            assert a['rule']=='DoNotUseThreads';kind='STANDALONE_OWNED_FINITE_MONITOR_FIXTURE_WORKERS'
            cases=[c for c in host['begin']['cases'] if c['path']==path and c['method']==method];assert len(cases)==1
        else:
            if stem=='MonitoringPoller' and method=='observeNow':
                cases=[c for c in host['begin']['cases'] if c['method'].startswith(('poll004','poll005','poll008','obsClock008'))];assert len(cases)==4
            else:
                cases=[c for c in host['begin']['cases'] if Path(c['path']).stem==stem+'Test'];assert len(cases)==8
            if a['rule']=='NullAssignment':
                assert stem=='ContinuousConditionWindow' and 'private@NullableDurationviolationStart;' in whole
                kind='EXPLICIT_NULLABLE_RESET_SENTINEL_NOT_HIDDEN_NPE'
            elif a['rule']=='AvoidCatchingGenericException':
                assert stem=='MonitoringPoller' and method in ['observeNow','observeLocked']
                kind='IDENTITY_RETHROW_AFTER_MARKING_ONE_CONTINUITY_GAP'
            else:
                assert a['rule']=='AvoidSynchronizedStatement' and whole.count('privatefinalObjectlock=newObject();')==1 and 'synchronized(this)' not in whole
                kind='PRIVATE_FINAL_ONE_OWNER_OBSERVATION_SEQUENCE_MONITOR'
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
        if v.get('sourceContexts')!=17 or v.get('rawRetained')!=17 or v.get('wholeStaticScopeRaw')!=17 or v.get('newMainContexts')!=8 or v.get('historicalNullableThreadSourceRebindings')!=9 or v.get('rawRetainedMeaning')!='COUNT_UNIQUE_SELECTED_REVIEWED_RETAINED_FINDING_IDS' or v.get('sourceCorrections')!=0 or v.get('newAccepted')!=0:raise ValueError('selected scope/current context not global/static correction credit')
    counts(m)
    for field,value in [('sourceContexts',23),('rawRetained',3),('wholeStaticScopeRaw',0),('rawRetainedMeaning','WHOLE_GLOBAL_RAW'),('sourceCorrections',24),('newAccepted',1),('newMainContexts',0),('historicalNullableThreadSourceRebindings',0)]:
        bad=dict(m);assert bad.get(field)!=value;bad[field]=value
        try:counts(bad)
        except ValueError:labels.append('manifest.'+field)
        else:raise AssertionError('wrong context counters accepted')
    assert len(labels)==24 and host['source']==SOURCE and host['actualExit']==0 and host['observedTestExecutions']==24
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewManifestSha256=PIN,sourceContexts=17,rawRetained=17,metadataNegativeVectors=len(labels),metadataNegativeLabels=labels,productTestsExecuted=0,sourceCorrections=0,newAccepted=0,coverage=None,wholeF03Accepted=False,whole451Accepted=False));print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
