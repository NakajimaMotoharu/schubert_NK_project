"""Same-byte498, ten inverse-proven fixture sites, seven individually reviewed assembly Test sites."""
from pathlib import Path
import json,hashlib
r=Path.cwd();i=r/'evidence/01_PT/018_NK-OPS-001/input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'3125_current_assembly918_style_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp);assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors']);a=load(i/'3111_current_snapshot898_static_admission.json');old=load(r/a['static']['path']);prior={};changed='src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/migration/CurrentMigrationProjectionTest.java';newtest=changed.replace('CurrentMigrationProjectionTest','CurrentMigrationAssemblerTest');proof=load(r/'evidence/01_PT/018_NK-OPS-001/evidence/PG32876-current-assembly918-source-v1/manifest.json');seam=proof['fixtureVisibilitySeam'];assert seam['path']==changed and seam['currentSha256']==sha(r/changed) and seam['priorSha256']==old['inputHashes'][changed] and seam['onlyTwoVisibilityTokensChanged'] and seam['oldTwelveTestsAndFixtureBodiesUnchanged'];paths=set(pf['mainSources']+[x['path'] for x in pf['testSources']])
for x in a['sourceAnchors']:
 path=x['path'];assert path in paths
 if path!=changed:assert sha(r/path)==old['inputHashes'][path]
 key=(path,x['rule'],x['sourceLine'],x['sourceAnchor'],x['message']);assert key not in prior;prior[key]=x
text=(r/newtest).read_text();assert all(x in text for x in ['WORKERS = 8','TASKS = 64','WAIT_SECONDS = 5','TERMINATION_SECONDS = 10','future.get(WAIT_SECONDS, TimeUnit.SECONDS)','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));','var f = CurrentMigrationProjectionTest.normal();']);rows=[];seen=set();same=0;fixture=0;fresh=[]
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();key=(path,raw['rule'],line,anchor,raw['message'])
 if path!=newtest:
  assert key in prior and key not in seen,key;seen.add(key);before=prior[key]
  if path==changed:
   reason='SSC402 fresh review on the shared synthetic fixture: two visibility modifiers alone changed; the inverse source-token proof preserves all twelve Test methods and fixture bodies. New assembly workers also create one independent fixture per call, so this exact site retains its original ownership/loader/thread confinement rationale. '+before['reason'];rows.append(dict(before,reason=reason));fixture+=1
  else:rows.append(before);same+=1
  continue
 if raw['rule']=='NullAssignment':
  assert anchor=='f.tables.get(2).get(0)[9] = null;'
  reason='Exact synthetic Current script_entries raw_block SQL NULL fixture is required: the source reader preserves nullable raw text while target entry Row rejects missing raw. The assembly test proves no invented empty-string repair or partial Master result. This assignment changes only the test-owned in-memory source, never Current data or production state.'
 elif raw['rule']=='CloseResource' and anchor=='for (var sink : output) assertEquals(0, sink.size());':
  assert 'private static List<ByteArrayOutputStream> sinks()' in text and text.count('new ByteArrayOutputStream()')==7
  reason='These six exact sinks come from the private sinks() factory, which constructs only JDK ByteArrayOutputStream memory buffers. They own no FD, socket, database, external stream or close-sensitive resource; close is documented as a no-op. The test asserts every buffer remains empty for empty assembly. Borrowed stream ownership is preserved and no operating-system handle is acquired.'
 else:
  assert raw['rule'] in ['CloseResource','DoNotUseThreads'] and anchor in ['var executor = Executors.newFixedThreadPool(WORKERS);','executor.submit(','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'],(raw['rule'],anchor)
  reason='Exact standalone JUnit executor owns8 workers and64 memory-only Current projection/assembly fixtures. Each Future joins5 seconds; finally shutdownNow and asserted10-second awaitTermination apply to every path. Every fixture/Proxy/fault map is task-local, with no backend/native/process resource or shared connection. Automatic close would not establish this finite termination postcondition.'
 rows.append(dict(path=path,rule=raw['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE'));fresh.append(dict(rule=raw['rule'],line=line,anchor=anchor))
assert seen==set(prior) and same==498 and fixture==10 and len(fresh)==7 and len(rows)==515
review=r/pf['slots']['static']/'assembly-site-review.json';review.open('x').write(json.dumps(dict(actualExit=0,sameByteSites=same,visibilityOnlyFixtureSites=fixture,fixtureProof=ref(r/'evidence/01_PT/018_NK-OPS-001/evidence/PG32876-current-assembly918-source-v1/manifest.json'),freshSites=fresh,applicable=0,unclassified=0,scope='FULL44_MIGRATION_MAIN_ROOT_RULES_NO_SUPPRESSION'),ensure_ascii=False,indent=2)+'\n');p=i/'3126_current_assembly918_static_admission.json';p.open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,sameByte=same,fixtureFresh=fixture,newSites=7,rawPmd=515,applicable=0,unclassified=0))
