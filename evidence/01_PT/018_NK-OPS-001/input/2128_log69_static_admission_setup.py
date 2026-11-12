from pathlib import Path
import collections,hashlib,json,sys
R=Path.cwd();sys.path.insert(0,str(R/'tools/quality'));import pgpt_closed_host_stages as s
B=R/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));c=ld(B/'input/2126_log_whole21_qualified_profile.json');st=ld(R/c['slots']['static']/'manifest.json');groups=collections.defaultdict(list)
for row in st['rawFindings']:
 p=Path(row['path']);path=str(p.relative_to(R));line=p.read_text().splitlines()[int(row['line'])-1].strip();groups[(path,row['rule'],row['message'],line)].append(int(row['line']))
anchors=[]
for (path,rule,message,anchor),lines in groups.items():
 name=Path(path).name;sourceLine=None
 if name in ['LogCleanupService.java','CleanupRepository.java'] and rule=='AvoidCatchingGenericException':
  assert anchor in ['} catch (SQLException | RuntimeException | Error primary) {','} catch (SQLException | RuntimeException | Error secondary) {','} catch (SQLException | RuntimeException | Error failure) {','} catch (SQLException | RuntimeException | Error cleanupFailure) {'];assert message in ['Avoid catching RuntimeException in try-catch block','Avoid catching Error in try-catch block'];reason='SS332/341 SSC063/337 direct owned JDBC and transaction recovery require all unknown Runtime/Error identities to be retained, with fixed redacted secondary and original known/unknown type priority. These exact catches rethrow failure, never treat NPE as normal, and never emit provider diagnostics.'
 elif name in ['LogCleanupService.java','CleanupRepository.java'] and rule=='DoNotThrowExceptionInFinally':
  assert anchor=='} finally {' and len(lines)==4;reason='SS332/341 direct ResultSet/Statement close is once-only in these four exact finally sites. A selected unknown cleanup must supersede known SQL according to the approved matrix; values are returned only after both closes. Replacing this with generic TWR would alter the approved same-Throwable/type priority.'
 elif name=='LogCleanupService.java' and rule=='DoNotUseThreads':
  assert anchor=='if (Thread.currentThread().isInterrupted())' and len(lines)==2;reason='Batch CLI checks the current interrupt flag twice around the borrowed clock boundary under SS341 parent budget. These two sites create no thread or pool, do not clear a flag, and are unrelated to a J2EE web-container-managed thread prohibition.'
 elif name=='MaintenanceMutationGuard.java' and rule=='CloseResource':
  assert anchor in ['var checked = Objects.requireNonNull(statement, "timeout statement");','var row = Objects.requireNonNull(rows, "timeout result");'];reason='These are nonnull aliases of the exact original PreparedStatement/ResultSet already owned by the surrounding two try-with-resources declarations. No new resource is acquired by requireNonNull; the original owner closes it once on every return/throw, including null-provider contract rejection.'
 elif name=='LogCleanupTransactionPortTest.java':
  if rule=='DoNotUseThreads':
   assert anchor in ['assertFalse(Thread.currentThread().isInterrupted());','Thread.currentThread().interrupt();','assertTrue(Thread.currentThread().isInterrupted());','Thread.interrupted();','var workers = Executors.newFixedThreadPool(2);','workers.submit(','workers.shutdownNow();','if (!workers.awaitTermination(10, TimeUnit.SECONDS))'];reason='Independent JUnit owns this thread-state fixture and two-worker pool, not a J2EE application container. IRQ injection is always cleared in finally; all twenty independent memory-JDBC tasks have Future3 seconds and finally shutdownNow/await10 seconds. No service/native/shared connection is operated.'
  elif rule=='CloseResource':
   assert anchor=='var workers = Executors.newFixedThreadPool(2);';reason='The test owns the only executor and always executes finally shutdownNow plus bounded awaitTermination10, including failed/timed Future3. Explicit finite cleanup replaces the unbounded ExecutorService.close contract; all original twenty task assertions are retained by byte-inverse proof BUG2755.'
  elif rule=='DoNotThrowExceptionInFinally':
   assert anchor=='} finally {' and lines==[362];sourceLine=362;reason='Only the worker cleanup finally at immutable source line362 fails with AssertionError when its owned pool does not terminate within ten seconds. The other two identical finally anchors only restore IRQ state and have no finding. This bounded cleanup failure must not be fabricated as test success.'
  elif rule=='UseConcurrentHashMap':
   assert anchor in ['final Map<String, Throwable> failures = new HashMap<>();','final Map<String, Integer> hits = new HashMap<>();','final Map<String, String> modes = new HashMap<>();'];reason='Each Fixture creates its own three mutable maps and is confined to exactly one test thread or one submitted task. Twenty tasks allocate twenty distinct Fixture/Connection instances; main-thread inspection happens only after Future.get handoff. No map has concurrent access or production shared state.'
  elif rule=='UseProperClassLoader':
   assert anchor=='return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));';reason='This independent memory fixture implements only the explicit JDK Connection/PreparedStatement/ResultSet interface passed by the test. Its defining interface loader is required for typed Proxy identity; no application or native class discovery or J2EE context loader is used.'
  else:raise AssertionError((name,rule))
 else:raise AssertionError((name,rule))
 value=dict(path=path,rule=rule,message=message,sourceAnchor=anchor,occurrences=len(lines),reason=reason,disposition='NOT_APPLICABLE')
 if sourceLine is not None:value['sourceLine']=sourceLine
 anchors.append(value)
assert len(st['rawFindings'])==69;classified=s.classify_source_findings(c['mainSources']+[x['path'] for x in c['testSources']],anchors,st['rawFindings'],lambda p:(R/p).read_text());assert len(classified)==69;a=dict(schema='PGPT_STATIC_ADMISSION_V1',profile=c['id'],prepare=ref(R/c['slots']['prepare']/'manifest.json'),static=ref(R/c['slots']['static']/'manifest.json'),sourceAnchors=anchors);p=B/'input/2128_log69_static_admission.json';assert not p.exists();p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,classifiedFindings=69,sourceAnchorGroups=len(anchors),localFinallyLine=362,ruleSuppressionAdded=False)))
