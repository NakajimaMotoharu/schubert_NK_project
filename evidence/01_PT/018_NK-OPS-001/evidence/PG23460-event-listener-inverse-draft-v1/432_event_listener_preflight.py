"""Passive supplied-interface source/command/static preflight; no Product initialization."""
from pathlib import Path
import json,hashlib,datetime,os,re,zipfile
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';RUN=R.parent/'pgpt-runs/PG379';O=B/'evidence/PG23432-event-listener-preflight-v1'
load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cfg=load(B/'input/431_event_listener_scope.json');cp=RUN/'pg23446-event-listener-compile-v1/manifest.json';sp=RUN/'pg23448-event-listener-static-v1/manifest.json';c=load(cp);s=load(sp);assert c['actualExit']==0 and c['inputHashes']==s['inputHashes'];assert not s['reports']['pmd']['processingErrors'] and not s['reports']['checkstyle']['items'];assert s['stages']['pmd']['actualExit']==4 and s['stages']['checkstyle']['actualExit']==0
for n,h in c['inputHashes'].items():assert sha(R/n)==h
p=next(iter(cfg['testClasses']));t=(R/p).read_text();lines=t.splitlines();assert t.count('@Test')==6 and '@Timeout(10)' in t
classifications=[]
for item in s['reports']['pmd']['items']:
 line=int(item['beginline']);span='\n'.join(lines[max(0,line-3):int(item['endline'])+2])
 if item['rule']=='CloseResource':
  assert item['method'].startswith(('port003','port004','port005','port006')) and item['variable']=='context' and 'port.context()' in span
  reason='Own synchronous memory-only JMSContext Proxy, not a provider resource. Only mode/commit/rollback allowed; close/createProducer/createConsumer/start/stop all reject. The caller retains its supplied interface and no external or worker resource is created. Closing the borrowed port inside listener would violate its ownership contract.'
 elif item['rule']=='UseProperClassLoader':
  assert item['method'] in ['message','context'] and '.class.getClassLoader()' in span
  reason='JDK Proxy uses the exact JMS interface defining loader, preserving pinned interface identity. No context loader, reflective target loading or external provider discovery.'
 else:raise AssertionError(item)
 classifications.append(dict(finding=item,path=p,sourceSha256=sha(R/p),sourceSpanSha256=hashlib.sha256(span.encode()).hexdigest(),classification='NOT_APPLICABLE',reason=reason))
assert len(classifications)==6 and sum(x['finding']['rule']=='CloseResource' for x in classifications)==4
normal=load(RUN/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json');deps=c['dependencies'];assert len(deps)==10 and all(sha(Path(n))==h for n,h in deps.items());assert not any(x in n.lower() for n in deps for x in ['storage','bootstrap','postgresql','artemis-server','otel','spring'])
# Conservative protocol source identity closure is larger than actual observed execution;
# no full-coverage or runtime qualification of that dependency closure is asserted.
graph=set(cfg['mainPaths']);graph.update(n for n in normal['begin']['inputHashes'] if n.startswith('src/schubert-nk-protocol/src/main/java/') and n.endswith('.java'));pins={n:sha(R/n) for n in sorted(graph)};assert all(normal['begin']['inputHashes'][n]==h for n,h in pins.items())
for n in graph:
 if '/schubert-nk-protocol/' in n:
  text=(R/n).read_text()
  assert not any(v in text for v in ['java.lang.foreign','java.net.','java.sql.','java.nio.file.','ProcessBuilder','Runtime.getRuntime'])
wrapper=[(R/n).read_text() for n in cfg['mainPaths'][:2]];assert all('delegate.onMessage(context, message);' in x and 'delegate.onMessage(context, message, attempted, confirmed);' in x for x in wrapper)
base='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/';tx=(R/(base+'inbound/InboundTransactions.java')).read_text();assert 'private static final DlqSender DLQ = new DlqSender();' in tx;rollback=tx[tx.index('    attempted.run();'):];assert rollback.index('context.rollback();')<rollback.index('confirmed.run();');dlq=(R/(base+'outbound/DlqSender.java')).read_text();assert 'public DlqSender(' not in dlq
req=['assertEquals(3, observed.getFirst().deliveryCount());','assertEquals(TRANSPORT_ID, observed.getFirst().transportMessageId());','assertEquals(RECEIVED, observed.getFirst().receivedAt());','assertEquals(Instant.parse("2026-11-08T00:00:00Z"), event.header().sentAt());','assertArrayEquals(data(question), event.payload().copyData());','assertEquals(0, failure.getSuppressed().length);','assertSame( failure, assertThrows( IllegalStateException.class,','List.of(PHASE_MODE, PHASE_PROCESS, PHASE_ATTEMPTED, PHASE_ROLLBACK, PHASE_CONFIRMED)','ascii(bytes, 181, question ? "000064" : "002080");','ascii(bytes, 199, question ? "000000320" : "000002336");','ascii(bytes, 26, "000000000061");','ascii(bytes, 38, "000000000062");','ascii(bytes, 617, "00000000-0000-0000-0000-000000000073");','ascii(bytes, 917, "200");','ascii(bytes, 920, "0");'];flat=' '.join(t.split());assert all(x in flat for x in req)
for v in ['FixedWidthEncoder','EmbeddedActiveMQ','ActiveMQConnectionFactory','QuestionWorkerService','WebLogIngestService','TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','java.sql','Files.','ProcessBuilder','Thread.','System.setProperty','randomUUID','Class.forName']:assert v not in t
runner=(B/'input/430_event_listener_qualifier.py').read_text();assert "cmd+=['--select-class'" in runner and '--scan-classpath' not in runner and '--enable-native-access' not in runner;assert not any(os.environ.get(k) for k in ['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS'])
sdk=[]
for label in ['PG23450-event-queue-sdk-passive-v1','PG23452-event-queue-parent-passive-v1','PG23454-event-queue-uri-passive-v1']:
 p2=B/'evidence'/label/'manifest.json';m=load(p2);assert m['actualExit']==0 and m['productTestsExecuted']==m['classesInitialized']==0;sdk.append(dict(path=str(p2.relative_to(R)),sha256=sha(p2)))
x=(B/'evidence/PG23454-event-queue-uri-passive-v1/sdkjavap.stdout').read_text();chunk=x[x.index('public static boolean containsQuery(org.apache'):x.index('private static void parseParameters')];assert 'SimpleString.contains:(C)Z' in chunk and '63' in chunk
before=B/'evidence/PG23442-event-listener-style-before-v1';bm=load(before/'manifest.json');back=t
for k,v in bm['constants'].items():back=back.replace('  private static final String '+k+' = '+v+';\n','')
for k,v in bm['constants'].items():back=back.replace(k,v)
assert back==(before/Path(p).name).read_text()
assert not O.exists();O.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),inputHashes=c['inputHashes'],dependencySourceHashes=pins,compileManifestSha256=sha(cp),staticManifestSha256=sha(sp),normalMainStaticUnchanged=s['unchangedMainStaticSha256'],dependencies=deps,pmdRaw=6,pmdApplicable=0,checkstyle=0,unclassified=0,staticClassifications=classifications,sdkPassiveReviews=sdk,expectedTests=6,newUniqueTests=6,sourceAssertionRecipes=req,styleInverse=True,bug='BUG-2486',horizontal='YKT-2224',productTestsExecuted=0,productClassesInitialized=0,heldFourInitializations=0,actualBackendActions=0,sdkEffects='Pinned Artemis queue value/URI containsQuery/enum/String bytes only; no session/provider/consumer/producer/server/JNDI lookup. Own JVM/JDK charset/time-zone/classpath effects not syscall-zero.',wholeDelegateQualified=False,formalUpdated=False);(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=6,staticRaw=6,applicable=0,cs=0,sourceGraph=len(pins),manifestSha256=sha(O/'manifest.json'))))
