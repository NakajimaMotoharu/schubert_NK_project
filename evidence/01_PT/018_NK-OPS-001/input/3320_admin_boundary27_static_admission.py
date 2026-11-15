"""Current exact host-only JDBC port applicability; no suppression, filters or service operations."""
from pathlib import Path
from collections import Counter
import json,hashlib
r=Path.cwd();i=r/'evidence/01_PT/018_NK-OPS-001/input';load=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=hashlib.sha256(p.read_bytes()).hexdigest());pf=load(i/'3319_admin_boundary27_increment_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp)
assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
test='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/admin/BootstrapAdminServiceBoundaryTest.java';t=(r/test).read_text();assert all(x in t for x in ['WORKERS = 8','TASKS = 64','WAIT_SECONDS = 5','TERMINATION_SECONDS = 10','future.get(WAIT_SECONDS, TimeUnit.SECONDS)','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'])
rows=[];counts=Counter()
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));assert path==test;line=int(raw['line']);anchor=t.splitlines()[line-1].strip();rule=raw['rule']
 if rule in ['CloseResource','DoNotUseThreads']:
  assert anchor in ['var executor = Executors.newFixedThreadPool(WORKERS);','executor.submit(','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));']
  reason='Exact standalone JUnit shared-service8-worker64-call negative-leak test. Every task creates its own memory-only JDBC Port, password array, row lists and fault map. Shared service returns ALREADY_EXISTS before password hashing/inserts/audits, verified by exact first4 SQL and wiped private input. Every Future has5-second get and finally shutdownNow with asserted10-second awaitTermination. No container/application thread or actual database/resource authority is created.';counts['boundedWorker']+=1
 elif rule=='EqualsNull':
  assert anchor in ['assertFalse(META.equals(null));','assertFalse(name.equals(null));']
  reason='Intentional independent negative equals(null)==false assertion for generated record contracts, not an application null test. Replacing it with reference comparison would stop executing/verifying the record method and miss the specified null behavior. Both return and absence of an exception are observed; no production null handling or exception is suppressed.';counts['recordNullContract']+=1
 elif rule=='CompareObjectsWithEquals':
  assert anchor=='case OBJECT_EQUALS -> proxy == args[0];'
  reason='This exact JDBC dynamic-proxy Object.equals implementation deliberately implements identity equality. Calling proxy.equals recursively re-enters the same InvocationHandler and never terminates. The compared reference is the proxy itself; no domain value comparison occurs. The memory-only fixture needs identity, not application equality semantics.';counts['proxyIdentity']+=1
 elif rule=='UseConcurrentHashMap':
  assert anchor=='final Map<String, Throwable> faults = new HashMap<>();'
  reason='Per-Port private fault configuration; every sequential test and each concurrent task creates a separate Port. No Port/fault map is static, published or shared across tasks; mutation precedes the same-thread service call. Concurrent test shares only the service and immutable metadata, never a Port. ConcurrentHashMap would add no required thread-safety contract.';counts['threadConfinedFaultMap']+=1
 elif rule=='UseProperClassLoader':
  assert anchor in [n+'.class.getClassLoader(),' for n in ['Connection','Statement','PreparedStatement','ResultSet']]
  reason='Standalone JUnit memory-only JDBC dynamic proxy, not J2EE code. This exact loader owns the fixed java.sql interface and establishes its visibility for Proxy.newProxyInstance. No application/plugin interface, context loader selection, service lookup or deployment occurs; using a mutable Thread context loader would introduce unrelated ambient state. All4 interfaces use the same explicit interface-owned loader policy.';counts['jdkInterfaceLoader']+=1
 else:raise AssertionError((rule,anchor))
 rows.append(dict(path=path,rule=rule,sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE'))
assert len(rows)==13 and counts==Counter(boundedWorker=5,recordNullContract=2,proxyIdentity=1,threadConfinedFaultMap=1,jdkInterfaceLoader=4)
(i/'3320_admin_boundary27_static_admission.json').open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,raw=13,counts=dict(counts),applicable=0,unclassified=0))
