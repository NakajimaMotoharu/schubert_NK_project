"""Current declared-map artifact memory ownership and finite test workers; whole old scope remains bound."""
from pathlib import Path
from collections import defaultdict,Counter
import json,hashlib
r=Path.cwd();i=r/'evidence/01_PT/018_NK-OPS-001/input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'3218_mapping958_corrected_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp);assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors']);old=load(i/'3200_deferred948_constant_static_admission.json');oldstatic=load(r/old['static']['path']);by=defaultdict(list);base='src/schubert-nk-bootstrap/src/';main=base+'main/java/dev/codex/schubert/nk/migration/CurrentMigrationMappingManifest.java';test=main.replace('/main/','/test/').replace('.java','Test.java');assembly=main.replace('CurrentMigrationMappingManifest','CurrentMigrationAssembler');at=test.replace('CurrentMigrationMappingManifestTest','CurrentMigrationAssemblerTest');changed={assembly,at}
for x in old['sourceAnchors']:by[(x['path'],x['rule'],x['sourceAnchor'],x['message'])].append(x)
for path in [test,at]:
 t=(r/path).read_text();assert all(x in t for x in ['WORKERS = 8','TASKS = 64','WAIT_SECONDS = 5','TERMINATION_SECONDS = 10','future.get(WAIT_SECONDS, TimeUnit.SECONDS)','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'])
rows=[];counts=Counter()
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();key=(path,raw['rule'],anchor,raw['message']);rule=raw['rule']
 if path in [main,test]:
  if path==main:
   assert rule=='CloseResource' and anchor=='var output = new ByteArrayOutputStream();',key
   reason='Exact ByteArrayOutputStream is an owned memory buffer, with no file/socket/FD or external stream. All appended data is declared numeric correspondence; toByteArray copies it into a private field and canonicalBytes clones it. Closing this JDK buffer releases no resource and does not change its state. Byte/hash/clone/empty/binding and finite-reader tests verify lifetime and immutability; no actual persistence or authority is claimed.';counts['newMemoryMain']+=1
  else:
   assert rule in ['CloseResource','DoNotUseThreads'] and anchor in ['var executor = Executors.newFixedThreadPool(WORKERS);','futures.add(','executor.submit(','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'],key
   reason='Exact JUnit-owned8-worker64-reader executor operates on a shared immutable memory manifest; each call receives a private cloned byte array and checks independent literal data/hash/counts. Every Future has5-second get, finally shutdownNow and asserted10-second awaitTermination. No external DB, native FD, process or shared mutable digest is acquired. This exact finite ownership contract is checked, not skipped.';counts['newBoundedWorkers']+=1
  x=dict(path=path,rule=rule,sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE')
 else:
  assert by[key],key;x=dict(by[key].pop(0))
  if path in changed:
   x['reason']+=' Re-reviewed SSC408 four-map manifest factory: this exact old flagged statement has unchanged memory/projection/thread semantics and old20 test bodies remain byte-identical. Added field references are immutable validated maps, and the new factory/ten independent tests introduce no DB/file/authority operation.';counts['changedAssemblySites']+=1
  else:assert sha(r/path)==oldstatic['inputHashes'][path] and line==x['sourceLine'];counts['sameByteSites']+=1
 x['sourceLine']=line;rows.append(x)
assert all(not v for v in by.values());assert counts['newMemoryMain']==0 and counts['newBoundedWorkers']==5 and len(rows)==546
(i/'3219_mapping958_corrected_static_admission.json').open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,raw=546,counts=dict(counts),applicable=0,unclassified=0))
