"""Same-byte prior sites; fresh exact Target catalog-content fixture anchors, no suppression."""
from pathlib import Path
import json,hashlib,collections
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'2920_target_column619_alias_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp)
assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
target='src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/migration/MigrationMasterTargetPublisherTest.java';prior={}
for file in ['2894_target_content589_static_admission.json','2908_master_column22_static_admission.json']:
 a=load(i/file);old=load(r/a['static']['path'])
 for x in a['sourceAnchors']:
  if x['path']==target:continue
  assert sha(r/x['path'])==old['inputHashes'][x['path']];key=(x['path'],x['rule'],x['sourceLine'],x['sourceAnchor'],x['message']);assert key not in prior;prior[key]=x
assert len(prior)==317
text=(r/target).read_text();assert all(x in text for x in ['WORKERS = 8','TASKS = 64','WAIT_SECONDS = 5','TERMINATION_SECONDS = 10']) and text.count('future.get(WAIT_SECONDS, TimeUnit.SECONDS)')==3 and text.count('executor.shutdownNow();')==3 and text.count('assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));')==3
rows=[];seen=set();counts=collections.Counter()
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);source=(r/path).read_text().splitlines();anchor=source[line-1].strip();key=(path,raw['rule'],line,anchor,raw['message'])
 if path!=target:
  assert key in prior and key not in seen;seen.add(key);rows.append(prior[key]);continue
 if raw['rule']=='CloseResource' and anchor in ['var conn = f.connection();','var connection = f.connection();']:
  counts['borrowedMemoryConnection']+=1;reason='Exact memory-only JUnit Proxy Connection is borrowed by the publisher path; it owns no real DB/pool/FD. Any close/commit/rollback or unknown operation fails the fixture. Every production Statement and Result has independent ownership assertions. Closing this borrowed memory connection would contradict its caller-owned transaction contract.'
 elif raw['rule']=='UseProperClassLoader':
  assert anchor in ['Connection.class.getClassLoader(),','Statement.class.getClassLoader(),','PreparedStatement.class.getClassLoader(),','ResultSet.class.getClassLoader(),'];counts['jdkProxy']+=1;reason='Exact standalone JDBC interface Proxy uses the same JDK interface loader, without application-server lookup, held product classes, driver or physical database. Scalar, content and catalog ResultSet fixtures have independent fixed method/column contracts and unexpected operations fail. No ambient application loader or external connection is required.'
 elif raw['rule']=='NullAssignment':
  assert 'nullCatalogValue' in '\n'.join(source[max(0,line-4):line+3]) or 'nullContentValue' in '\n'.join(source[max(0,line-4):line+3]);counts['sqlNullNegative']+=1;reason='Exact synthetic ResultSet assigns SQL NULL only under the explicit catalog or typed-content negative-test flag, with independent wasNull state. Production must reject the selected metadata/payload mismatch before staging or finalization. Replacing this null would remove required SQL NULL versus zero/false/empty boundary coverage; it acquires no database resource.'
 else:
  assert raw['rule'] in ['CloseResource','DoNotUseThreads'] and anchor in ['var executor = Executors.newFixedThreadPool(WORKERS);','executor.submit(','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'];counts['finiteWorker']+=1;reason='Exact standalone JUnit executor owns eight workers and64 independent memory-only publisher fixtures. Success, content-failure and catalog-failure matrices each join every Future within5 seconds and finally shutdownNow plus checked awaitTermination10. No DB/native/process resource is acquired; implicit executor close does not supply the required finite shutdown postcondition.'
 rows.append(dict(path=path,rule=raw['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE'))
assert seen==set(prior) and counts==dict(borrowedMemoryConnection=2,finiteWorker=15,jdkProxy=6,sqlNullNegative=2) and len(rows)==342
(i/'2921_target_column619_static_admission.json').open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,oldSameByte=317,newRevalidated=dict(counts),applicable=0,unclassified=0))
