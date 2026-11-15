"""Every root site tied to current readback source; fixture maps are strictly per-test, not shared."""
from pathlib import Path
from collections import defaultdict,Counter
import json,hashlib
r=Path.cwd();i=r/'evidence/01_PT/018_NK-OPS-001/input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'3250_mapverify976_column_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp);assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors']);old=load(i/'3219_mapping958_corrected_static_admission.json');oldstatic=load(r/old['static']['path']);by=defaultdict(list);base='src/schubert-nk-bootstrap/src/';main=base+'main/java/dev/codex/schubert/nk/migration/CurrentMigrationMappingVerifier.java';test=main.replace('/main/','/test/').replace('.java','Test.java');manifest=main.replace('CurrentMigrationMappingVerifier','CurrentMigrationMappingManifest');mt=test.replace('CurrentMigrationMappingVerifierTest','CurrentMigrationMappingManifestTest');changed={manifest,mt}
for x in old['sourceAnchors']:by[(x['path'],x['rule'],x['sourceAnchor'],x['message'])].append(x)
t=(r/test).read_text();a=t.index('void mapverify016');z=t.index('\n  private static',a);assert 'new Wire' not in t[a:z] and 'private static final class Wire' in t and 'private final Map<Integer, String> overrides = new HashMap<>();' in t
for path in [test,mt]:
 text=(r/path).read_text();assert all(x in text for x in ['WORKERS = 8','TASKS = 64','WAIT_SECONDS = 5','TERMINATION_SECONDS = 10','future.get(WAIT_SECONDS, TimeUnit.SECONDS)','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'])
rows=[];counts=Counter()
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();key=(path,raw['rule'],anchor,raw['message']);rule=raw['rule']
 if path in [main,test]:
  assert path==test,key
  if rule=='UseConcurrentHashMap':
   assert anchor=='private final Map<Integer, String> overrides = new HashMap<>();'
   reason='This exact private per-instance Wire fixture belongs only to one sequential malformed-input test invocation. It has no static publication, thread callbacks or cross-test sharing; concurrent case016 uses immutable literal bytes and never creates a Wire. Its header overrides intentionally model independent corrupt frames, not production shared state. All map reads/writes occur in the same test-owned call chain; ConcurrentHashMap would not establish any required production/thread safety.';counts['threadConfinedFixtureMap']+=1
  else:
   assert rule in ['CloseResource','DoNotUseThreads'] and anchor in ['var executor = Executors.newFixedThreadPool(WORKERS);','executor.submit(','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'],key
   reason='Exact standalone JUnit8-worker64-call executor shares only the stateless verifier and immutable literal expectations. Each task creates its own input byte array, validates independent counts and mutates only its private array after return. Every Future has5-second get; finally shutdownNow and asserted10-second awaitTermination verify finite cleanup. No database/socket/process/native resource or mutable fixture is shared.';counts['newBoundedWorkers']+=1
  x=dict(path=path,rule=rule,sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE')
 else:
  assert by[key],key;x=dict(by[key].pop(0))
  if path in changed:
   x['reason']+=' Re-reviewed SSC409 current expected-SHA readback entry: this exact original statement retains identical memory/finite-worker meaning; original8 Manifest test bodies remain byte-identical. New nullable byte input is checked and cloned by the new verifier, with no FS/DB/authority acquisition.';counts['changedManifestSites']+=1
  else:assert sha(r/path)==oldstatic['inputHashes'][path] and line==x['sourceLine'];counts['sameByteSites']+=1
 x['sourceLine']=line;rows.append(x)
assert all(not v for v in by.values()) and counts['newBoundedWorkers']==5 and counts['threadConfinedFixtureMap']==1 and len(rows)==552
(i/'3251_mapverify976_column_admission.json').open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,raw=552,counts=dict(counts),applicable=0,unclassified=0))
