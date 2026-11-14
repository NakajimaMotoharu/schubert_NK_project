"""Same-byte159 prior sites plus exact typed-JDBC timestamp, primary identity and memory fixture19."""
from pathlib import Path
import json,hashlib,collections
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'2885_master_content411_named_tags_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp);assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors']);newmain=next(p for p in pf['mainSources'] if p.endswith('/MigrationMasterContentVerifier.java'));newtest=newmain.replace('/main/','/test/').replace('.java','Test.java');oldpaths=set(pf['mainSources']+[x['path'] for x in pf['testSources']])-{newmain,newtest};a=load(i/'2795_master_six383_static_admission.json');old=load(r/a['static']['path']);prior={}
for x in a['sourceAnchors']:
 assert x['path'] in oldpaths and sha(r/x['path'])==old['inputHashes'][x['path']];prior[(x['path'],x['rule'],x['sourceLine'],x['sourceAnchor'],x['message'])]=x
text=(r/newtest).read_text();assert all(x in text for x in ['WORKERS = 8','TASKS = 64','WAIT_SECONDS = 5','TERMINATION_SECONDS = 10','future.get(WAIT_SECONDS, TimeUnit.SECONDS)','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));']);rows=[];seen=set();counts=collections.Counter()
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();key=(path,raw['rule'],line,anchor,raw['message'])
 if path in oldpaths:
  assert key in prior and key not in seen;seen.add(key);rows.append(prior[key]);continue
 if path==newmain and raw['rule']=='AvoidCatchingGenericException':
  assert anchor in ['} catch (SQLException | RuntimeException | Error failure) {','} catch (SQLException | RuntimeException | Error cleanup) {'];counts['primaryCleanup']+=1
  reason='Exact owned JDBC boundary preserves and rethrows the original SQL/runtime/Error instance and closes the Result before the Statement. Cleanup failures remain ordered suppressed values and never success or retry. Independent faults at every getter/wasNull/next occurrence and both close phases verify original identity, counts and resource termination, including Error.'
 elif path==newmain and raw['rule']=='CompareObjectsWithEquals':
  assert anchor=='if (cleanup != primary) primary.addSuppressed(cleanup);';counts['selfIdentity']+=1
  reason='Throwable.addSuppressed forbids adding the identical primary object to itself. This exact reference guard is required independently of subclass value equals semantics. Different but equal-valued failures remain suppressed; same-primary aliases and duplicate distinct cleanup objects are independently tested. This is a Throwable identity protocol rather than a domain value comparison.'
 elif path==newmain and raw['rule']=='ReplaceJavaUtilDate':
  assert anchor=='@Nullable Timestamp actual = result.getTimestamp(column);';counts['jdbcTimestamp']+=1
  reason='Exact standard java.sql.Timestamp is received at the typed JDBC timestamptz boundary and immediately converted to immutable Instant canonical UTC text. No Date arithmetic, mutable timestamp retention, system clock or timezone-default formatting is used. Independent SQL NULL, Instant offset, microsecond and years0001/9999 fixtures verify the explicit JDBC conversion contract.'
 elif path==newtest and raw['rule']=='UseProperClassLoader':
  assert anchor in ['Connection.class.getClassLoader(),','Statement.class.getClassLoader(),','ResultSet.class.getClassLoader(),'];counts['jdkProxy']+=1
  reason='Exact standalone memory-only JUnit Proxy uses the explicit loader of the same JDK java.sql interface. No application-server context loader, external driver, held product class, DB or network operation is acquired. Unexpected interface calls fail the test. This preserves the independent SQL/resource protocol without an ambient application-loader dependency.'
 else:
  assert path==newtest and raw['rule'] in ['CloseResource','DoNotUseThreads'] and anchor in ['var executor = Executors.newFixedThreadPool(WORKERS);','executor.submit(','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'];counts['worker']+=1
  reason='Exact standalone host executor owns eight workers/64 independent memory JDBC fixtures sharing only the stateless verifier and immutable declaration. Every Future joins5 seconds and finally shutdownNow plus checked awaitTermination10 applies on all paths. No DB/native/process resource is acquired. Implicit executor close omits the required finite termination postcondition.'
 rows.append(dict(path=path,rule=raw['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE'))
assert seen==set(prior) and len(prior)==159 and counts==dict(primaryCleanup=8,selfIdentity=2,jdbcTimestamp=1,worker=5,jdkProxy=3) and len(rows)==178
(i/'2886_master_content411_static_admission.json').open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,oldSameByte=159,newSites=dict(counts),applicable=0,unclassified=0))
