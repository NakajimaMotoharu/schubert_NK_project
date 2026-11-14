"""Fresh Game JDBC boundary and whole Target fixture site review; unchanged490 retained byte-exact."""
from pathlib import Path
import json,hashlib,collections
r=Path.cwd();i=r/'evidence/01_PT/018_NK-OPS-001/input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'3142_games940_fixture_style_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp);assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors']);a=load(i/'3126_current_assembly918_static_admission.json');old=load(r/a['static']['path']);base='src/schubert-nk-bootstrap/src/';main=base+'main/java/dev/codex/schubert/nk/migration/MigrationGamesVerifier.java';test=main.replace('/main/','/test/').replace('.java','Test.java');target=test.replace('MigrationGamesVerifierTest','MigrationMasterTargetPublisherTest');paths=set(pf['mainSources']+[x['path'] for x in pf['testSources']]);prior={}
for x in a['sourceAnchors']:
 path=x['path']
 if path==target:continue
 assert path in paths and sha(r/path)==old['inputHashes'][path];key=(path,x['rule'],x['sourceLine'],x['sourceAnchor'],x['message']);assert key not in prior;prior[key]=x
for p in [test,target]:
 text=(r/p).read_text();assert all(x in text for x in ['WORKERS = 8','TASKS = 64','WAIT_SECONDS = 5','TERMINATION_SECONDS = 10','future.get(WAIT_SECONDS, TimeUnit.SECONDS)','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'])
text=(r/main).read_text();assert 'actual.add(stamp == null ? null : stamp.toInstant().toString());' in text and 'getTimestamp(5)' in text and 'Timestamp.from' not in text;rows=[];seen=set();counts=collections.Counter();fresh=[]
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();key=(path,raw['rule'],line,anchor,raw['message']);rule=raw['rule']
 if path not in [main,test,target]:
  assert key in prior and key not in seen,key;seen.add(key);rows.append(prior[key]);counts['sameByte']+=1;continue
 if path==main:
  if rule=='AvoidCatchingGenericException':
   assert anchor in ['} catch (SQLException | RuntimeException | Error failure) {','} catch (SQLException | RuntimeException | Error cleanup) {']
   reason='Exact JDBC ownership boundary rethrows the original SQL/runtime/Error while closing its new ResultSet then Statement once. Cleanup failures remain ordered suppressed and no error is turned into success, retry or raw log. Every phase/occurrence and all three fault kinds are independently tested.'
  elif rule=='CompareObjectsWithEquals':
   assert anchor=='if (cleanup != primary) primary.addSuppressed(cleanup);'
   reason='Throwable self-suppression is forbidden by reference identity, not equals value semantics. The exact identity guard avoids IllegalArgumentException for the same object while retaining distinct equal-valued SQLException instances. Independent self/EqualSql tests verify both cases and termination.'
  else:
   assert rule=='ReplaceJavaUtilDate' and anchor=='@Nullable Timestamp stamp = result.getTimestamp(5);'
   reason='This exact java.sql.Timestamp is the declared standard JDBC getTimestamp boundary for V004 timestamptz. It is nullable and converted immediately through toInstant to canonical UTC text; no legacy Date arithmetic, mutable date state, ambient timezone comparison or domain date API is introduced. Independent exact/microsecond/null vectors verify the conversion without a driver.'
  counts['newGameMain']+=1
 elif rule=='UseProperClassLoader':
  assert anchor in ['Connection.class.getClassLoader(),','Statement.class.getClassLoader(),','PreparedStatement.class.getClassLoader(),','ResultSet.class.getClassLoader(),']
  reason='Exact JDK java.sql interface class loader is used only for an in-memory Proxy of that same interface. No context-loader discovery, application server, actual driver, network or held application class is materialized. Unknown methods fail the independent fixture.';counts['gameTest' if path==test else 'targetFresh']+=1
 elif rule=='NullAssignment':
  assert (path==test and anchor=='f.data.get(row)[column] = null;') or (path==target and anchor=='? null')
  reason='Exact synthetic SQL-NULL fixture deliberately mutates only test-owned column values. Required numbers use immediate wasNull and nullable timestamp/text must fail the fixed expected-row comparison; source metadata and content NULL controls remain unchanged. No production state is modified or missing value repaired.';counts['gameTest' if path==test else 'targetFresh']+=1
 elif path==target and rule=='CloseResource' and anchor in ['var conn = f.connection();','var connection = f.connection();']:
  reason='Exact test-owned java.sql.Connection is an in-memory Proxy borrowed by the target workflow; caller close/commit/rollback/setters are prohibited by the production contract and throw immediately in the fixture. It owns no real database/socket/FD. Closing it would contradict the ownership postcondition rather than release an actual resource.';counts['targetFresh']+=1
 else:
  assert rule in ['CloseResource','DoNotUseThreads'] and anchor in ['var executor = Executors.newFixedThreadPool(WORKERS);','executor.submit(','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'],(path,rule,anchor)
  reason='Exact standalone JUnit executor owns8 workers and64 independent memory-only JDBC fixture calls. Every Future has5-second get and finally shutdownNow with asserted10-second awaitTermination runs on every path. Each task has its own connection, cursor and fault objects; no backend/native/process resource or shared Throwable state is acquired. Automatic close would not assert the finite cleanup contract.';counts['gameTest' if path==test else 'targetFresh']+=1
 rows.append(dict(path=path,rule=rule,sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE'));fresh.append(dict(path=path,rule=rule,line=line,anchor=anchor))
assert seen==set(prior) and counts==dict(sameByte=490,newGameMain=11,gameTest=9,targetFresh=27) and len(rows)==537
review=r/pf['slots']['static']/'games-target-site-review.json';review.open('x').write(json.dumps(dict(actualExit=0,counts=dict(counts),freshSites=fresh,applicable=0,unclassified=0,scope='FULL45_MIGRATION_MAIN_ROOT_RULES_NO_SUPPRESSION'),ensure_ascii=False,indent=2)+'\n');p=i/'3143_games940_static_admission.json';p.open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,counts=dict(counts),rawPmd=537,applicable=0,unclassified=0))
