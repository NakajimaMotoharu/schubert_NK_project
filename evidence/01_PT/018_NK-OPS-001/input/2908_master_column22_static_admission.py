"""Exact18 standalone column JDBC primary/identity and finite-memory fixture sites; no suppression."""
from pathlib import Path
import json,hashlib,collections
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'2907_master_column22_fixed_queries_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp);assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors']);main=pf['mainSources'][0];test=pf['testSources'][0]['path'];text=(r/test).read_text();assert all(x in text for x in ['WORKERS = 8','TASKS = 64','WAIT_SECONDS = 5','TERMINATION_SECONDS = 10','future.get(WAIT_SECONDS, TimeUnit.SECONDS)','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));']);rows=[];counts=collections.Counter()
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip()
 if path==main and raw['rule']=='AvoidCatchingGenericException':
  assert anchor in ['} catch (SQLException | RuntimeException | Error failure) {','} catch (SQLException | RuntimeException | Error cleanup) {'];counts['primaryCleanup']+=1
  reason='Exact owned JDBC boundary rethrows the original SQL/runtime/Error identity and closes Result before Statement. Cleanup remains ordered suppression rather than success, retry or raw-value logging. Independent faults at every metadata getter/wasNull/next and both close phases verify original identity, exact resource counts and termination for all three fault kinds.'
 elif path==main and raw['rule']=='CompareObjectsWithEquals':
  assert anchor=='if (cleanup != primary) primary.addSuppressed(cleanup);';counts['selfIdentity']+=1
  reason='Throwable.addSuppressed prohibits adding the identical primary object to itself. This reference guard preserves original SQL/runtime/Error even when both resources return the same instance. Different but equal-valued exception objects are still suppressed, including duplicate cleanup attempts. Independent identity assertions verify that this is not a domain value comparison.'
 elif path==test and raw['rule']=='UseProperClassLoader':
  assert anchor in ['Connection.class.getClassLoader(),','Statement.class.getClassLoader(),','ResultSet.class.getClassLoader(),'];counts['jdkProxy']+=1
  reason='Exact standalone JUnit memory-only Proxy uses the explicit loader of the same JDK java.sql interface. It acquires no application-server loader, external driver, held product class, real database or network. Unexpected methods fail the fixture, so the independent catalog SQL/getter/resource protocol has no ambient context-loader dependency.'
 else:
  assert path==test and raw['rule'] in ['CloseResource','DoNotUseThreads'] and anchor in ['var executor = Executors.newFixedThreadPool(WORKERS);','executor.submit(','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'];counts['worker']+=1
  reason='Exact standalone JUnit executor owns eight workers/64 independent synthetic catalog transactions sharing only a stateless verifier. Every Future joins5 seconds and finally shutdownNow plus checked awaitTermination10 applies on every path. No DB/native/process resource is acquired; implicit executor close does not establish the required finite termination postcondition.'
 rows.append(dict(path=path,rule=raw['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE'))
assert counts==dict(primaryCleanup=8,selfIdentity=2,worker=5,jdkProxy=3) and len(rows)==18
(i/'2908_master_column22_static_admission.json').open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,exactSites=dict(counts),applicable=0,unclassified=0))
