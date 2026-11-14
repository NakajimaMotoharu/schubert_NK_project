"""Same-byte prior498 plus ten exact new JDK Proxy, thread-confined fault-map and worker sites."""
from pathlib import Path
import json,hashlib
r=Path.cwd();i=r/'evidence/01_PT/018_NK-OPS-001/input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'3110_current_snapshot898_immutable_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp);assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors']);a=load(i/'3092_audio_link_map886_static_admission.json');old=load(r/a['static']['path']);prior={};paths=set(pf['mainSources']+[x['path'] for x in pf['testSources']])
for x in a['sourceAnchors']:
 path=x['path'];assert path in paths and sha(r/path)==old['inputHashes'][path];key=(path,x['rule'],x['sourceLine'],x['sourceAnchor'],x['message']);assert key not in prior;prior[key]=x
newtest='src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/migration/CurrentMigrationProjectionTest.java';assert newtest in paths;text=(r/newtest).read_text();assert all(x in text for x in ['WORKERS = 8','TASKS = 64','WAIT_SECONDS = 5','TERMINATION_SECONDS = 10','future.get(WAIT_SECONDS, TimeUnit.SECONDS)','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));','var f = normal();']);rows=[];seen=set();fresh=[]
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();key=(path,raw['rule'],line,anchor,raw['message'])
 if path!=newtest:
  assert key in prior and key not in seen,key;seen.add(key);rows.append(prior[key]);continue
 if raw['rule']=='UseConcurrentHashMap':
  assert anchor in ['final Map<Integer, Throwable> resultFailures = new HashMap<>();','final Map<Integer, Throwable> statementFailures = new HashMap<>();']
  reason='Exact per-call JUnit Fixture owns this fault-injection map exclusively. Fault matrices fill it before a synchronous read in the same thread, then the three JDK Proxy handlers only read it. Each of64 workers constructs its own fresh Fixture inside the task; no fixture or map is shared between threads. ConcurrentHashMap adds no missing synchronization and would obscure the intended thread-confined caller contract.'
 elif raw['rule']=='UseProperClassLoader':
  assert anchor in ['Connection.class.getClassLoader(),','Statement.class.getClassLoader(),','ResultSet.class.getClassLoader(),']
  reason='Exact standalone in-memory JDK Proxy uses the java.sql interface class loader for the same interface only. No application server/context loader discovery, real JDBC driver, network, held product type or reflected application object is used. Every unexpected connection/statement/result operation fails the independent test.'
 else:
  assert raw['rule'] in ['CloseResource','DoNotUseThreads'] and anchor in ['var executor = Executors.newFixedThreadPool(WORKERS);','executor.submit(','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'],(raw['rule'],anchor)
  reason='Exact standalone JUnit executor owns8 workers and64 independent five-table in-memory JDBC fixtures. Every Future is joined with5-second get; finally shutdownNow and asserted10-second awaitTermination apply on all paths. The mapper owns no backend or native/process resource. Automatic close would not prove the specified bounded cleanup postcondition.'
 rows.append(dict(path=path,rule=raw['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE'));fresh.append(dict(rule=raw['rule'],line=line,anchor=anchor))
assert seen==set(prior) and len(prior)==498 and len(fresh)==10 and len(rows)==508
review=r/pf['slots']['static']/'snapshot-site-review.json';review.open('x').write(json.dumps(dict(actualExit=0,sameByteSites=498,freshSites=fresh,applicable=0,unclassified=0,scope='FULL43_MIGRATION_MAIN_ROOT_RULES_NO_SUPPRESSION'),ensure_ascii=False,indent=2)+'\n');p=i/'3111_current_snapshot898_static_admission.json';p.open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,sameByte=498,fresh=10,rawPmd=508,applicable=0,unclassified=0))
