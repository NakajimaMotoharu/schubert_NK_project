"""Per-site root rules applicability, retaining every raw finding and exact source anchor."""
from pathlib import Path
import json,hashlib,collections
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'2813_master_ref403_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp)
assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
newmain=next(p for p in pf['mainSources'] if p.endswith('/MigrationMasterReferenceVerifier.java'));newtest=newmain.replace('/main/','/test/').replace('.java','Test.java');oldpaths=set(pf['mainSources']+[x['path'] for x in pf['testSources']])-{newmain,newtest};a=load(i/'2795_master_six383_static_admission.json');old=load(r/a['static']['path']);prior={}
for x in a['sourceAnchors']:
 assert x['path'] in oldpaths and sha(r/x['path'])==old['inputHashes'][x['path']]
 prior[(x['path'],x['rule'],x['sourceLine'],x['sourceAnchor'],x['message'])]=x
rows=[];seen=set();counts=collections.Counter()
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();key=(path,raw['rule'],line,anchor,raw['message'])
 if path in oldpaths:
  assert key in prior and key not in seen;seen.add(key);rows.append(prior[key]);continue
 if path==newmain and raw['rule']=='AvoidCatchingGenericException':
  assert anchor in ['} catch (SQLException | RuntimeException | Error failure) {','} catch (SQLException | RuntimeException | Error cleanup) {']
  reason='Exact nonnull JDBC owned-resource scope records and immediately rethrows the identical SQL/runtime/Error primary only to preserve finally cleanup suppression. It never catches NPE as success or logs/normalizes/retries/commits a failed operation. Independent read/result/outer dual-close failure matrices verify primary identity, ordering and exact close attempts, including JDK self-suppression failure.';counts['primary']+=1
 elif path==newtest and raw['rule']=='UseProperClassLoader':
  assert anchor in ['Connection.class.getClassLoader(),','Statement.class.getClassLoader(),','PreparedStatement.class.getClassLoader(),','ResultSet.class.getClassLoader(),']
  reason='Exact JDK java.sql interface defining loader is used only for an in-memory Proxy implementing that same loaded public interface. No external JDBC driver/DB/socket/native/FD/classfile inspection or TCCL mutation occurs. This standalone JUnit host fixture is outside J2EE and the JDK Proxy contract accepts the defining loader, including null where applicable.';counts['loader']+=1
 elif path==newtest and raw['rule']=='CloseResource' and anchor=='var conn = f.connection();':
  reason='Exact Connection is a memory-only Proxy whose handler rejects close/commit/rollback/role/autoCommit mutation. It is borrowed into the null-argument prevalidation test and must receive zero calls. No driver, database connection, socket or FD is acquired, and closing it would invalidate the required no-side-effect contract.';counts['borrowed']+=1
 else:
  assert path==newtest and raw['rule'] in ['CloseResource','DoNotUseThreads'] and anchor in ['var executor = Executors.newFixedThreadPool(WORKERS);','executor.submit(','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));']
  reason='Exact standalone JUnit executor owns eight workers/64 immutable declared master and independent JDBC-proxy tasks. Every Future joins5 seconds; finally shutdownNow and checked awaitTermination10 apply on all paths. No external DB/native/FD/process is acquired and this is outside J2EE. Implicit executor close omits the mandatory bounded termination assertion.';counts['worker']+=1
 rows.append(dict(path=path,rule=raw['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE'))
assert seen==set(prior) and len(prior)==159
# Actual new-site counts are preserved, never a guessed denominator.
assert counts==dict(primary=8,loader=3,borrowed=1,worker=5)
p=i/'2814_master_ref403_static_admission.json';p.open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,oldSameByte=159,newSites=dict(counts),rawPmd=len(rows),applicable=0,unclassified=0))
