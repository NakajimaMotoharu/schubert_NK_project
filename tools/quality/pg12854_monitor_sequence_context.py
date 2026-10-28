"""Current17 exact nodes: private state serialization, identity-preserving gap catch, nullable sentinel and owned fixture threads."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match

SOURCE='f8ad1ae16aa52db0119fefbad9e2cea6d6affe55'
OUT=data.BASE/'PG12854-monitor-sequence-context-v1'
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
    invocation=capture(__file__);assert not OUT.exists()
    host=data.read_checked(data.BASE/'PG12848-monitor-sequence-host-v1/manifest.json','89f4bac39fcdfe6410e3f3badbe50d03c13899241317f516133592cc2138e733')
    static=data.read_checked(data.BASE/'PG12850-monitor-sequence-static-v1/manifest.json','77ddcdcd19da753042dca663d3940012a6ef1fdfae74bf463e546a122ff8c3e3')
    proof=data.read_checked(data.BASE/'PG12852-monitor-sequence-post-v1/manifest.json','a3297ed8bbdb614f3ffb237edb34638a45d2375eb8dab20ed852244f4e271923')
    assert host['source']==static['source']==proof['source']==SOURCE and host['actualExit']==proof['actualExit']==0 and host['observedTestExecutions']==24 and static['actualExit']==1
    raw=(data.BASE/'PG12850-monitor-sequence-static-v1/pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),node) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for node in f if node.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');rows=[]
    for path,node in actual:
        identity=original_match(path,node,original,actual);a=dict(node.attrib);method=a['method'];stem=Path(path).stem;text=(data.ROOT/path).read_text();assert data.sha(text.encode())==host['begin']['sourceInputHashes'][path]
        ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];lines=text.splitlines(keepends=True)
        start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        point=next(i for i,(_,p) in enumerate(ts) if p==start);lo,hi,name=min((v for v in functions(ts) if v[0]<=point<=v[1]),key=lambda v:v[1]-v[0]);assert name==method
        compact=''.join(t for t,_ in ts[lo:hi+1]);whole=''.join(t for t,_ in ts);controls=CONTROLS[(stem,method)];assert all(c in compact for c in controls)
        if stem.endswith('Test'):
            assert a['rule']=='DoNotUseThreads'
            cases=[c for c in host['begin']['cases'] if c['path']==path and c['method']==method];assert len(cases)==1
            kind='STANDALONE_OWNED_FINITE_MONITOR_FIXTURE_WORKERS'
            reason='Standalone whole JUnit owns only local pool and fixed values. Window has4workers/64calls/invokeAll10seconds and original shutdownNow-await10seconds; clock/poller have8workers/64finite calls and independent set1..64. Clock/poller invokeAll/get and all TWR closes have no local absolute deadline; distinct outer JVM240seconds. No application process, actual clock mutation, FS, DB, network, Root, VM, native, keys or authority. Historical refs source-rebound, raw retained.'
        else:
            if stem=='MonitoringPoller' and method=='observeNow':
                cases=[c for c in host['begin']['cases'] if c['method'].startswith(('poll004','poll005','poll008','obsClock008'))];assert len(cases)==4
            else:
                testname=stem+'Test';cases=[c for c in host['begin']['cases'] if Path(c['path']).stem==testname];assert len(cases)==8
            if a['rule']=='NullAssignment':
                assert stem=='ContinuousConditionWindow' and 'private@NullableDurationviolationStart;' in whole
                kind='EXPLICIT_NULLABLE_RESET_SENTINEL_NOT_HIDDEN_NPE'
                reason='Explicit @Nullable private period sentinel is cleared only for NORMAL/UNKNOWN under same lock; next violation reestablishes elapsed when null before subtraction. Independent rejected-input/state/gap vectors plus normal NullAway checks apply. This is not a null boundary contract relaxation or caught NPE treated as success; prior nullable review is source-rebound only.'
            elif a['rule']=='AvoidCatchingGenericException':
                assert stem=='MonitoringPoller' and method in ['observeNow','observeLocked']
                kind='IDENTITY_RETHROW_AFTER_MARKING_ONE_CONTINUITY_GAP'
                reason='Private one-owner poll must mark any unchecked provider/action failure as interrupted then rethrow the identical RuntimeException/Error; no retry, swallowing, formatting, compensation or normal result. Null-result NPE also propagates and cannot commit later elapsed. Independent exception identity/no-call/next-gap tests cover intended source contract; no actual external failure recovery or all implicit JVM errors inferred.'
            else:
                assert a['rule']=='AvoidSynchronizedStatement' and whole.count('privatefinalObjectlock=newObject();')==1 and 'synchronized(this)' not in whole
                kind='PRIVATE_FINAL_ONE_OWNER_OBSERVATION_SEQUENCE_MONITOR'
                reason='411 section9 requires private-final state lock, not public this/class monitor. Window protects previous/start as one transition; clock captures supplied ticks/UTC and commits only after valid context; poller serializes supplied time/input/action with gap/commit state. ReentrantLock suggestion is not a project requirement. Internal order is poller->clock then observation/window/lifecycle, no reverse calls in reviewed pure closure. Callback duration, actual collectors/stop authority are outer responsibilities, not a locally bounded-runtime claim. Finite standalone serialization tests validate this source only.'
        assert all(any(v['classname']==c['className'] and v['name']==c['method'] and not v['nonPass'] for v in host['cases']) for c in cases)
        rows.append(dict(id=identity['id'],path=path,rule=a['rule'],attributes=a,originalRowSha256=identity['rowSha256'],source=SOURCE,sourceSha256=data.sha(text.encode()),sourceSpanSha256=data.sha(text[start:end].encode()),scopeName=method,scopeKind='METHOD',scopeTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),controls=controls,currentCases=cases,kind=kind,disposition='CONTEXT_NOT_APPLICABLE',reason=reason,currentWholeJoinPending=True,oldRuntimeReassigned=False,productTestsExecutedByReview=0,newAccepted=0))
    assert len(rows)==len({r['id'] for r in rows})==17
    verify(invocation);OUT.mkdir();data.write(OUT/'review.json',dict(source=SOURCE,rows=rows))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=17,rawRetained=17,rawRetainedMeaning='COUNT_UNIQUE_SELECTED_REVIEWED_RETAINED_FINDING_IDS',wholeStaticScopeRaw=17,newMainContexts=8,historicalNullableThreadSourceRebindings=9,sourceCorrections=0,productTestsExecuted=0,newAccepted=0,wholeF03Accepted=False,whole451Accepted=False,coverage=None));print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
