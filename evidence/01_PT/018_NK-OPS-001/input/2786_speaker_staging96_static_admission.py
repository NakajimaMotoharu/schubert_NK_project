"""Same-byte old47 and exact new19 resource-contract sites; no PMD suppression."""
from pathlib import Path
import json,hashlib,collections
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'2785_speaker_staging96_explicit_fixture_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp)
assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
newmain=pf['mainSources'][0];newtest=pf['testSources'][0]['path'];oldpaths=set(pf['mainSources'][1:]+[x['path'] for x in pf['testSources'][1:]])
a=load(i/'2761_staging_cleanup403_static_admission.json');old=load(r/a['static']['path']);prior={}
for x in a['sourceAnchors']:
 if x['path'] not in oldpaths:continue
 assert sha(r/x['path'])==old['inputHashes'][x['path']]
 prior[(x['path'],x['rule'],x['sourceLine'],x['sourceAnchor'],x['message'])]=x
main=(r/newmain).read_text();test=(r/newtest).read_text()
assert all(x in test for x in ['WORKERS = 8','TASKS = 64','WAIT_SECONDS = 5','TERMINATION_SECONDS = 10','future.get(WAIT_SECONDS, TimeUnit.SECONDS)','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'])
assert all(x in main for x in ['throw failure;','primary.addSuppressed(cleanup);','closeStatement(statement, primary);','closeResult(result, primary);'])
rows=[];seen=set();counts=collections.Counter()
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();key=(path,raw['rule'],line,anchor,raw['message'])
 if path in oldpaths:
  assert key in prior and key not in seen;seen.add(key);rows.append(prior[key]);continue
 if path==newmain:
  assert raw['rule']=='AvoidCatchingGenericException' and anchor in ['} catch (SQLException | RuntimeException | Error failure) {','} catch (SQLException | RuntimeException | Error cleanup) {']
  reason='Exact nonnull owned JDBC cleanup records the original SQL/runtime/Error primary and immediately rethrows the identical instance; finally closes exactly once and attaches the actual cleanup failure only when there is an original primary. It never catches NPE as success, normalizes failures, logs, retries or commits. Independent SQL/runtime/Error body+cleanup matrices and nested result/statement identity-order assertions verify Java primary/suppressed/self-suppression behavior.';counts['primary']+=1
 elif raw['rule']=='UseProperClassLoader':
  assert path==newtest and anchor in ['Connection.class.getClassLoader(),','Statement.class.getClassLoader(),','ResultSet.class.getClassLoader(),']
  reason='Exact JDK java.sql interface defining loader is used solely for an in-memory Proxy implementing that same public interface. The handler is already a loaded local test lambda, no new bytecode/classfile/native/backend load or TCCL mutation occurs, and the tests do not run in a J2EE container. Null bootstrap/platform defining-loader values are supported by the JDK Proxy contract and no external resource is acquired.';counts['loader']+=1
 elif path==newtest and raw['rule']=='CloseResource' and anchor=='var connection = f.connection();':
  reason='Exact fixture connection is a java.lang.reflect.Proxy with memory-only SQL/count/close counters and synthetic exceptions, no DB/JDBC driver/socket/FD/transaction acquired. It is deliberately borrowed across six production table stages; closing/committing/rolling back it would violate the ownership postcondition, and unexpected calls fail. Independent six-table SQL30/Statement6/Result18 and connection ownership assertions verify this contract.';counts['borrowed']+=1
 else:
  assert path==newtest and raw['rule'] in ['CloseResource','DoNotUseThreads']
  reason='Exact standalone host JUnit executor owns eight workers/64 finite independent JDBC-proxy tasks with every Future joined5 seconds and a finally shutdownNow plus checked awaitTermination10 seconds. This is outside a J2EE container, no external resource is acquired, and implicit executor close would omit the required bounded termination postcondition. No background worker survives a successful test.';counts['worker']+=1
 rows.append(dict(path=path,rule=raw['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE'))
assert seen==set(prior) and len(prior)==47 and counts==dict(primary=10,loader=3,borrowed=1,worker=5) and len(rows)==66
p=i/'2786_speaker_staging96_static_admission.json';p.open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,oldSameByte=47,newSites=dict(counts),rawPmd=66,applicable=0,unclassified=0))
