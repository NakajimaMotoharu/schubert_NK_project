"""Independent source/oracle, SDK and raw-static preflight; no target execution."""
from pathlib import Path
import collections, datetime, hashlib, json, os, re, zipfile
import class_reference_metadata as metadata

R=Path(__file__).resolve().parents[4]; B=R/'evidence/01_PT/007_NK-AUT-001'
RUN=R.parent/'pgpt-runs/PG379'
# The runner deliberately uses the common OPS support location for preflight only.
O=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG23798-authentication-memory-port-preflight-v1'
load=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cfg=load(B/'input/017_authentication_memory_port_scope.json')
cp=RUN/'pg23806-authentication-memory-port-compile-v1/manifest.json'
sp=RUN/'pg23808-authentication-memory-port-static-v1/manifest.json'
cm=load(cp); sm=load(sp)
assert not O.exists() and type(cm['actualExit']) is int and cm['actualExit']==0
assert cm['inputHashes']==sm['inputHashes']
assert all(sha(R/n)==h for n,h in cm['inputHashes'].items())
assert sm['stages']['pmd']['actualExit'] in (0,4) and sm['stages']['checkstyle']['actualExit']==0
assert not sm['reports']['pmd']['processingErrors'] and not sm['reports']['checkstyle']['items']
normal=RUN/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json'
assert sha(normal)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27'
nm=load(normal); assert nm['actualExit']==0 and nm['source']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
assert len(cfg['mainPaths'])==28 and cfg['modules']==['api','protocol']
assert all(nm['begin']['inputHashes'][p]==sha(R/p) for p in cfg['mainPaths'])
expected={nm['jars'][m]['path']:nm['jars'][m]['sha256'] for m in cfg['modules']}
expected.update(cfg['sdkDependencies']); assert expected==cm['dependencies']
console=R.parent/'toolchain/junit-platform-console-standalone-1.13.4.jar'
assert sha(console)==cm['consoleSha256']=='3fdfc37e29744a9a67dd5365e81467e26fbde0b7aa204e6f8bbe79eeaa7ae892'
sdk=[]
for p,h in {**expected,str(console):sha(console)}.items():
 assert sha(Path(p))==h
 with zipfile.ZipFile(p) as z:
  names=set(z.namelist())
  assert not names.intersection({'META-INF/services/java.sql.Driver','META-INF/services/javax.annotation.processing.Processor','META-INF/services/com.sun.source.util.Plugin'})
  manifest=z.read('META-INF/MANIFEST.MF').decode() if 'META-INF/MANIFEST.MF' in names else ''
  assert not re.search(r'^Class-Path:',manifest,re.M)
 sdk.append(dict(path=p,sha256=h,jdbcDriverDescriptors=0,compilerPluginDescriptors=0,manifestClasspath=False))
indexp=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG23360-base59-named-proof-supplement-v1/current-normal-physical-index.json'
assert sha(indexp)=='db6581ac589b42bdaa6e51ac101dac365d02a8fabab7d689eb5f12de29319723'
index=load(indexp); paths=set(cfg['mainPaths']); graph=[]; held={'TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'}
for n,v in index.items():
 if v['path'] not in paths:continue
 assert not held.intersection(n.split('/')[-1].split('$'))
 module='api' if '/schubert-nk-api/' in v['path'] else 'protocol'
 with zipfile.ZipFile(nm['jars'][module]['path']) as z: raw=z.read(n+'.class')
 assert hashlib.sha256(raw).hexdigest()==v['sha256']
 m=metadata.read(raw); product=[ref for ref in m['references'] if ref.startswith('dev/codex/schubert/nk/') and not ref.endswith('/package-info')]
 assert all(ref in index and index[ref]['path'] in paths for ref in product)
 graph.append(dict(className=n,source=v['path'],sourceSha256=sha(R/v['path']),productReferences=product))
assert {v['source'] for v in graph}==paths
target={n for n,v in index.items() if v['path'].endswith('/AuthenticationService.java')}
assert target==set(cfg['targetPhysical']) and len(target)==1
p=next(iter(cfg['testClasses'])); text=(R/p).read_text()
assert text.count('@Test')==16 and len(set(re.findall(r'void\s+(memory\d{3}\w+)\s*\(',text)))==16
tokens=lambda s:''.join(re.findall(r'"(?:\\.|[^"\\])*"|\S',s))
recipes=[
 'private static final Instant AT = Instant.parse("2026-09-08T00:00:00.123456Z");',
 'private static final Instant EXPIRES = Instant.parse("2026-09-08T08:00:00.123456Z");',
 'assertEquals(7, result.actor().userId());','assertEquals("Ålice", result.actor().username());',
 'assertEquals(Role.USER, result.actor().role());','assertEquals(Role.ADMIN, result.actor().role());',
 'assertEquals(0, f.param(Stage.UPDATE_USER, 1));','assertNull(f.param(Stage.UPDATE_USER, 2));',
 'assertNull(f.param(Stage.UPDATE_USER, 3));','assertEquals(true, f.param(Stage.UPDATE_USER, 4));',
 'assertEquals(3, f.param(Stage.UPDATE_USER, 1));','assertEquals(4, f.param(Stage.UPDATE_IP, 1));',
 'assertEquals(900, result.retryAfterSeconds());','assertEquals(240, result.retryAfterSeconds());',
 'new int[] {4, 0}','new int[] {0, 9}','new int[] {4, 9}',
 'new long[] {1_000, 1}','new long[] {1_000_001_000L, 2}','new long[] {899_999_999_000L, 900}','new long[] {900_000_001_000L, 900}',
 'f.userWindow = AT.minusSeconds(900);','f.userLock = Optional.of(AT);',
 'f.userWindow = AT.minusSeconds(900).minusNanos(1_000);','assertEquals(1, f.param(Stage.UPDATE_USER, 1));',
 'assertArrayEquals(new char[16], password);','assertEquals(1, statement.closed);','assertEquals(1, cursor.closed);',
 'assertEquals(STORAGE_ERROR, failure.getMessage());','assertNull(failure.getCause());','assertEquals(0, failure.getSuppressed().length);',
 'assertSame(fatal, assertThrows(AssertionError.class, f::call));','assertEquals(1, f.count(Stage.SESSION_REPLACE));',
 'assertTrue(oldest.equals(f.param(Stage.SESSION_REPLACE, 2)));','assertEquals(Set.of("targetUserId", REASON_KEY, RESULT_CODE_KEY), audit.keySet());',
 'assertEquals(code, details.get(RESULT_CODE_KEY).getAsString());','assertEquals(reason, details.get(REASON_KEY).getAsString());',
 'assertEquals(expectedClient, param(Stage.LOGIN_AUDIT, 9));','assertEquals(expectedDisplay, param(Stage.LOGIN_AUDIT, 8));',
 'assertEquals(messageId, param(Stage.LOGIN_AUDIT, 5));','assertEquals(correlationId, param(Stage.LOGIN_AUDIT, 6));',
 'case "getAutoCommit" -> false;','throw new AssertionError("borrowed connection operation is forbidden: " + method);',
 'assertTrue(statement.parameters.containsKey(index), "required bound index is missing");',
 'assertNotSame(first.connection, second.connection);','assertEquals(8, secondResult.actor().userId());','assertEquals("Bob", secondResult.actor().username());',
 'one.get(5, TimeUnit.SECONDS)','two.get(5, TimeUnit.SECONDS)',
 'client = InetAddress.ofLiteral("192.0.2.11");','messageId = new UUID(0, 21);','correlationId = new UUID(0, 22);'
]
assert all(tokens(s) in tokens(text) for s in recipes)
for forbidden in [*held,'ApiLogDatabaseFixture','DriverManager','ProcessBuilder','Class.forName','setAccessible','java.lang.foreign','Socket','java.nio.file','System.setProperty','@SuppressWarnings','NOPMD']:
 assert forbidden not in text
assert text.count('new PasswordHasher()')==1 and 'defaultChecker.matches' not in text and 'defaultChecker.encode' not in text
case001=text[text.index('void memory001'):text.index('void memory002')]
assert 'f.userLock = Optional.of(AT.plusSeconds(30));' in case001 and 'f.call(defaultService)' in case001
# Assertions must precede fixture cleanup: cleanup itself wipes all arrays and is not an oracle.
assert text.count('f.verifyReleasedAndConsumed();')==19
assert 'first.verifyReleasedAndConsumed();\n      second.verifyReleasedAndConsumed();' in text
raw=sm['reports']['pmd']['items']; assert len(raw)==8
assert collections.Counter(i['rule'] for i in raw)=={'DoNotUseThreads':3,'AvoidUsingVolatile':1,'UseConcurrentHashMap':3,'UseProperClassLoader':1}
classified=[]
for item in raw:
 line=int(item['beginline']); snippet='\n'.join(text.splitlines()[max(0,line-2):line+5]); rule=item['rule']
 if rule=='DoNotUseThreads':
  assert item['method'].startswith('memory016') and any(x in snippet for x in ['Executors.newFixedThreadPool(2)','executor.submit('])
  reason='Standalone JUnit owns exactly two tasks and its executor; two Future waits5s, outer Unit180s. Not a J2EE/container thread or live process.'
 elif rule=='AvoidUsingVolatile':
  assert item['variable']=='observedStoredHash' and 'volatile String observedStoredHash' in snippet
  reason='One synthetic checker-observation scalar explicitly published across two owned tasks. AtomicInteger handles counters; no transaction invariants or multi-field protocol use volatile. Future joins precede observation.'
 elif rule=='UseConcurrentHashMap':
  assert item['variable'] in ('parameters','row') and 'new HashMap<>()' in snippet
  reason='Each parameters/user/IP map belongs only to its distinct caller Fixture/Connection; no map shared between tasks. JDBC NULL cells are intentional and disallow ConcurrentHashMap substitution; Future completion publishes results.'
 else:
  assert rule=='UseProperClassLoader' and item['method']=='proxy' and 'type.getClassLoader()' in snippet
  reason='Exactly the defining loader of supplied standard JDK Connection/PreparedStatement/ResultSet interface for own Proxy. Standalone JUnit, no container or context loader contract.'
 classified.append(dict(raw=item,disposition='NOT_APPLICABLE_TO_THIS_EXPLICIT_TEST_CONTEXT',reason=reason))
before=B/'evidence/PG23802-authentication-port-static-before-v1'; bm=load(before/'manifest.json')
assert sha(before/'AuthenticationServiceMemoryPortTest.java')==bm['beforeSourceSha256']
restored=tokens(text)
for name,value in [('DENIED','DENIED'),('REASON_KEY','reason'),('RESULT_CODE_KEY','resultCode')]:
 declaration=tokens('private static final String '+name+' = '+json.dumps(value)+';')
 assert restored.count(declaration)==1
 restored=restored.replace(declaration,'',1)
 restored=re.sub(r'\b'+name+r'\b',json.dumps(value),restored)
assert restored==tokens((before/'AuthenticationServiceMemoryPortTest.java').read_text())
runner=(B/'input/018_authentication_memory_port_qualifier.py').read_text()
assert '--scan-classpath' not in runner and '--enable-native-access' not in runner
assert "cmd+=['--select-class'" in runner and "'-proc:none','-implicit:none'" in runner and "timeout=180" in runner
assert not any(os.environ.get(k) for k in ['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS'])
assert sm['unchangedMainStaticSha256']=='0580a14592d3fc00820183034c584208e45b002802d2e3e173b5f752c7cf19f2'
O.mkdir()
out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),inputHashes=cm['inputHashes'],compileManifestSha256=sha(cp),staticManifestSha256=sha(sp),normalMainStaticUnchanged=sm['unchangedMainStaticSha256'],sdkClasspathGuard=sdk,sourceGraph=graph,graphLimit='Pinned ClassFile symbols plus full manual Main bodies and intended operation review; metadata alone never grants execution',sourceAssertionRecipes=recipes,expectedTests=16,newUniqueTests=16,fullSourceFilePhysicalClasses=sorted(target),manualCoverageExclusions=[],styleInverse=True,pmdRaw=8,pmdApplicable=0,checkstyle=0,unclassified=0,staticClassifications=classified,actualBackendActions=0,actualJdbcDriverOrDatabaseActions=0,actualLoginOrSessionAgainstServer=False,ownLocalSyntheticJca=True,ownFixedJvmTasks=2,defaultMatcherInvoked=False,heldFourInitializations=0,originalRealDatabaseTestOrFixtureCompiledOrRun=False,productTestsExecuted=0,productClassesInitialized=0,whole451Accepted=False,formalUpdated=False,bugs=['BUG-2499'],ykts=['YKT-2237'])
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,plannedTests=16,pmdRaw=8,pmdApplicable=0,cs=0,graphSourceCount=len(paths),graphPhysicalCount=len(graph),manifestSha256=sha(O/'manifest.json'))))
