"""Exact unchanged union sites and eleven new finite-worker/JDK-proxy ownership sites."""
from pathlib import Path
import json,hashlib,collections
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'2821_master_target543_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp)
assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
newmain=next(p for p in pf['mainSources'] if p.endswith('/MigrationMasterTargetPublisher.java'));newtest=newmain.replace('/main/','/test/').replace('.java','Test.java');oldpaths=set(pf['mainSources']+[x['path'] for x in pf['testSources']])-{newmain,newtest};prior={}
for name in ['2795_master_six383_static_admission.json','2786_speaker_staging96_static_admission.json','2805_master_final411_static_admission.json','2814_master_ref403_static_admission.json']:
 a=load(i/name);old=load(r/a['static']['path'])
 for x in a['sourceAnchors']:
  assert x['path'] in oldpaths and sha(r/x['path'])==old['inputHashes'][x['path']]
  prior[(x['path'],x['rule'],x['sourceLine'],x['sourceAnchor'],x['message'])]=x
text=(r/newtest).read_text();assert all(x in text for x in ['WORKERS = 8','TASKS = 64','WAIT_SECONDS = 5','TERMINATION_SECONDS = 10','future.get(WAIT_SECONDS, TimeUnit.SECONDS)','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'])
rows=[];seen=set();counts=collections.Counter()
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();key=(path,raw['rule'],line,anchor,raw['message'])
 if path in oldpaths:
  assert key in prior and key not in seen;seen.add(key);rows.append(prior[key]);continue
 assert path==newtest
 if raw['rule']=='UseProperClassLoader':
  assert anchor in ['Connection.class.getClassLoader(),','Statement.class.getClassLoader(),','PreparedStatement.class.getClassLoader(),','ResultSet.class.getClassLoader(),']
  reason='Exact JDK java.sql interface defining loader creates an in-memory Proxy implementing that same public JDK interface. No external driver, DB, socket, native FD, classfile inspection or TCCL mutation is involved. This standalone JUnit host fixture is outside J2EE, and defining-loader values including null are supported by the JDK Proxy contract.';counts['loader']+=1
 elif raw['rule']=='CloseResource' and anchor in ['var conn = f.connection();','var connection = f.connection();']:
  reason='Exact fixture Connection is a memory-only JDK Proxy with public synthetic SQL/scalar counters; no real JDBC connection, database, socket or FD is acquired. The Connection is deliberately borrowed across prepare and transfer or passed to null prevalidation. Every unlisted ownership/transaction/role operation throws, and exact resource postconditions require no caller Connection close/commit/rollback/autoCommit mutation.';counts['borrowed']+=1
 else:
  assert raw['rule'] in ['CloseResource','DoNotUseThreads'] and anchor in ['var executor = Executors.newFixedThreadPool(WORKERS);','executor.submit(','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));']
  reason='Exact standalone host JUnit executor owns eight workers/64 shared stateless publisher calls with independent JDBC memory proxies. Every Future joins within5 seconds; finally shutdownNow and checked awaitTermination10 apply on all paths. No real DB/native/FD/process is acquired and this is outside J2EE. Implicit executor close omits the required bounded termination postcondition.';counts['worker']+=1
 rows.append(dict(path=path,rule=raw['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE'))
assert seen==set(prior) and len(prior)==262 and counts==dict(loader=4,borrowed=2,worker=5) and len(rows)==273
(i/'2822_master_target543_static_admission.json').open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,oldSameByte=262,newSites=dict(counts),rawPmd=273,applicable=0,unclassified=0))
