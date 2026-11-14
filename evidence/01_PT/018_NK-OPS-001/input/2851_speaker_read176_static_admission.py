"""Same-byte prior78 plus exact primary/identity, SQL NULL, JDK loader and finite worker sites."""
from pathlib import Path
import json,hashlib,collections
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'2850_speaker_read176_fixture_fixed_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp);assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
newmain=next(p for p in pf['mainSources'] if p.endswith('/CurrentSpeakerProjectionReader.java'));newtest=newmain.replace('/main/','/test/').replace('.java','Test.java');oldpaths=set(pf['mainSources']+[x['path'] for x in pf['testSources']])-{newmain,newtest};a=load(i/'2842_speaker_map156_static_admission.json');old=load(r/a['static']['path']);prior={}
for x in a['sourceAnchors']:
 assert x['path'] in oldpaths and sha(r/x['path'])==old['inputHashes'][x['path']]
 prior[(x['path'],x['rule'],x['sourceLine'],x['sourceAnchor'],x['message'])]=x
text=(r/newtest).read_text();assert all(x in text for x in ['WORKERS = 8','TASKS = 64','WAIT_SECONDS = 5','TERMINATION_SECONDS = 10','future.get(WAIT_SECONDS, TimeUnit.SECONDS)','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));']);rows=[];seen=set();counts=collections.Counter()
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();key=(path,raw['rule'],line,anchor,raw['message'])
 if path in oldpaths:
  assert key in prior and key not in seen;seen.add(key);rows.append(prior[key]);continue
 if path==newmain and raw['rule']=='AvoidCatchingGenericException':
  assert anchor in ['} catch (SQLException | RuntimeException | Error failure) {','} catch (SQLException | RuntimeException | Error cleanup) {']
  reason='Exact owned JDBC resource boundary preserves the original SQL/runtime/Error instance and rethrows it. The result is closed before the statement and cleanup failures remain suppressed in order. No exception is converted to success, retried or logged with raw values. Independent every-getter occurrence and all primary/cleanup fault-kind matrices verify this resource contract.';counts['primaryCleanup']+=1
 elif path==newmain and raw['rule']=='CompareObjectsWithEquals':
  assert anchor=='if (cleanup != primary) primary.addSuppressed(cleanup);'
  reason='Throwable.addSuppressed forbids the identical primary object as its own suppression. This exact reference identity guard is required even when different exception instances compare equal through a subclass equals implementation. It does not compare value objects. SQL/runtime/Error same-instance faults independently verify original-primary preservation and termination.';counts['selfIdentity']+=1
 elif path==newtest and raw['rule']=='NullAssignment':
  assert anchor in ['f.data.get(0)[0] = null;','f.data.get(0)[index] = null;']
  reason='Exact synthetic JDBC row fixture assigns SQL NULL for the primary key, name, normalized name and boolean negative cases. Production input is not mutated and no null is treated as an allowed required value. The getter/wasNull assertions and owned resource postconditions prove rejection; removing this assignment would omit mandatory null-boundary tests.';counts['sqlNullFixture']+=1
 elif path==newtest and raw['rule']=='UseProperClassLoader':
  assert anchor in ['Connection.class.getClassLoader(),','Statement.class.getClassLoader(),','ResultSet.class.getClassLoader(),']
  reason='Exact JDK java.sql interface loader is used by a standalone in-memory Proxy for that same interface, with no application server, ambient context-loader discovery, actual driver or network operation. Unexpected methods fail the test. This explicit loader cannot materialize held product classes and the fixture exercises only the qualified projection contract.';counts['jdkProxy']+=1
 else:
  assert path==newtest and raw['rule'] in ['CloseResource','DoNotUseThreads'] and anchor in ['var executor = Executors.newFixedThreadPool(WORKERS);','executor.submit(','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));']
  reason='Exact standalone host JUnit executor owns eight workers/64 independent memory-only JDBC fixtures on one stateless reader. Every Future joins5 seconds and finally shutdownNow plus checked awaitTermination10 applies on every path. No database/native/process resource is acquired. Implicit executor close does not establish the required finite termination postcondition.';counts['worker']+=1
 rows.append(dict(path=path,rule=raw['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE'))
assert seen==set(prior) and len(prior)==78 and counts==dict(primaryCleanup=8,selfIdentity=2,sqlNullFixture=2,jdkProxy=3,worker=5) and len(rows)==98
(i/'2851_speaker_read176_static_admission.json').open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,oldSameByte=78,newSites=dict(counts),rawPmd=98,applicable=0,unclassified=0))
