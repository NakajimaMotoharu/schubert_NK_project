"""Original-source reproduction: same-byte50 Main sites and exact finite-worker/JDK Proxy8."""
from pathlib import Path
import json,hashlib,collections
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'2864_cleanup_identity_repro10_relative_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp);assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors']);old=load(i/'2827_master_target543_static_admission.json');oldstatic=load(r/old['static']['path']);prior={}
for x in old['sourceAnchors']:
 if x['path'] not in pf['mainSources']:continue
 assert sha(r/x['path'])==oldstatic['inputHashes'][x['path']];prior[(x['path'],x['rule'],x['sourceLine'],x['sourceAnchor'],x['message'])]=x
newtest=pf['testSources'][0]['path'];text=(r/newtest).read_text();assert all(x in text for x in ['WORKERS = 8','TASKS = 64','WAIT_SECONDS = 5','TERMINATION_SECONDS = 10','future.get(WAIT_SECONDS, TimeUnit.SECONDS)','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));']);rows=[];seen=set();counts=collections.Counter()
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();key=(path,raw['rule'],line,anchor,raw['message'])
 if path in pf['mainSources']:
  assert key in prior and key not in seen;seen.add(key);rows.append(prior[key]);continue
 assert path==newtest
 if raw['rule']=='UseProperClassLoader':
  assert anchor in ['Connection.class.getClassLoader(),','Statement.class.getClassLoader(),','ResultSet.class.getClassLoader(),'];counts['jdkProxy']+=1
  reason='Exact standalone JUnit fixture creates a memory-only Proxy for the same JDK java.sql interface using its explicit interface loader. It loads no external driver or held application class, opens no network/DB and fails unexpected methods. This tests original exception identity at approved standard JDBC boundaries, outside an application-server context-loader contract.'
 else:
  assert raw['rule'] in ['CloseResource','DoNotUseThreads'] and anchor in ['var executor = Executors.newFixedThreadPool(WORKERS);','executor.submit(','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'];counts['worker']+=1
  reason='Exact standalone host JUnit executor owns eight workers/64 independent synthetic JDBC fixtures. Every Future joins5 seconds and finally shutdownNow plus checked awaitTermination10 applies even on assertion failure. No external database/native/process resource is acquired. Implicit executor close does not establish the explicit finite termination postcondition.'
 rows.append(dict(path=path,rule=raw['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE'))
assert len(prior)==50 and seen==set(prior) and counts==dict(worker=5,jdkProxy=3) and len(rows)==58
(i/'2865_cleanup_identity_repro_static_admission.json').open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,oldMain50=True,new8=True,applicable=0,unclassified=0))
