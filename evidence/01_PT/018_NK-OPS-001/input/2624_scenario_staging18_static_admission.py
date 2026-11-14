"""Classify each current whole-source finding; no rule suppression or backend admission."""
from pathlib import Path
import hashlib,json
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';ld=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
c=ld(i/'2623_scenario_staging18_literal_fixed_profile.json');p=r/c['slots']['prepare']/'manifest.json';s=r/c['slots']['static']/'manifest.json';v=ld(s);rows=[];assert len(v['rawFindings'])==9
for x in v['rawFindings']:
 path=str(Path(x['path']).relative_to(r));line=int(x['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();rule=x['rule']
 if '/main/' in path:
  assert rule=='CloseResource' and anchor=='@Nullable Statement created = connection.createStatement();'
  reason='The exact nullable factory result is rejected before use or assigned as the sole try-with-resources Statement. All success/SQL/Runtime/Error exits close it once; primary-plus-close failure is suppressed by Java, close failure cannot succeed. Borrowed Connection is not owned. Whole18 explicitly verifies these resource paths; no suppression or ignored resource.'
 elif rule=='UseProperClassLoader':
  assert 'Proxy.newProxyInstance(' not in anchor and '.class.getClassLoader(),' in anchor
  reason='This exact standalone JUnit memory fixture creates only a Proxy for fixed JDK java.sql.Connection/Statement interfaces, using their defining platform loader. No J2EE/web container, untrusted class name, plugin/context loader or actual JDBC implementation is used. Every non-whitelisted connection/statement call fails an assertion; no acquired handle exists.'
 elif rule=='CloseResource' and 'connection = fixture.connection()' in anchor:
  reason='This exact fixture Connection is a Java Proxy with no JDBC driver, database, native stream, socket or file. It owns no closeable OS resource and deliberately rejects close/commit/rollback/setAutoCommit to prove borrowed-connection ownership in both invocations. Statement.close is a separate asserted memory counter, not delegated to any backend.'
 else:
  assert rule in ['CloseResource','DoNotUseThreads'] and any(word in anchor for word in ['newFixedThreadPool','executor.submit','shutdownNow','awaitTermination'])
  reason='This exact standalone JUnit concurrency fixture is outside managed J2EE. Eight owned workers execute64 memory-only JDBC-proxy assertions; every Future joins within5s, finally always shutdownNow and asserts awaitTermination within10s. No driver/DB/network/file/native/service action. Bounded explicit shutdown avoids unbounded implicit ExecutorService.close and is not a blanket Test exclusion.'
 rows.append(dict(path=path,rule=rule,sourceLine=line,sourceAnchor=anchor,occurrences=1,message=x['message'],reason=reason,disposition='NOT_APPLICABLE'))
out=i/'2624_scenario_staging18_static_admission.json';assert not out.exists();out.write_text(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=c['id'],prepare=ref(p),static=ref(s),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,raw9IndividuallyClassified=True,noSuppression=True)))
