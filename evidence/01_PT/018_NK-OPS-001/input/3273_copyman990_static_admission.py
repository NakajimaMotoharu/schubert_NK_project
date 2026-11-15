"""Classify exact current static sites without suppressing rules or reusing changed-source assertions."""
from pathlib import Path
from collections import defaultdict,Counter
import json,hashlib
r=Path.cwd();i=r/'evidence/01_PT/018_NK-OPS-001/input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'3272_copyman990_constants_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp)
assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
old=load(i/'3251_mapverify976_column_admission.json');oldstatic=load(r/old['static']['path']);by=defaultdict(list)
for x in old['sourceAnchors']:by[(x['path'],x['rule'],x['sourceAnchor'],x['message'])].append(x)
base='src/schubert-nk-bootstrap/src/';main=base+'main/java/dev/codex/schubert/nk/migration/MigrationMasterCopyManifest.java';test=main.replace('/main/','/test/').replace('.java','Test.java');changed={main.replace('MigrationMasterCopyManifest','CurrentMigrationAssembler'),test.replace('MigrationMasterCopyManifestTest','CurrentMigrationAssemblerTest'),test.replace('MigrationMasterCopyManifestTest','MigrationMasterCopyFingerprintTest')}
t=(r/test).read_text();assert all(x in t for x in ['WORKERS = 8','TASKS = 64','WAIT_SECONDS = 5','TERMINATION_SECONDS = 10','future.get(WAIT_SECONDS, TimeUnit.SECONDS)','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'])
rows=[];counts=Counter()
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();key=(path,raw['rule'],anchor,raw['message'])
 if path in [main,test]:
  assert path==test and raw['rule'] in ['CloseResource','DoNotUseThreads'] and anchor in ['var executor = Executors.newFixedThreadPool(WORKERS);','executor.submit(','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'],key
  x=dict(path=path,rule=raw['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason='Exact standalone JUnit8-worker64-call executor. Shared mapping and six-table dataset are final immutable values; every task constructs private fingerprint digest sinks, counters, StringBuilder and manifest bytes. No external IO, role/authority, resource ownership or mutable source fixture is shared. Every Future has5-second get and finally shutdownNow/asserted10-second awaitTermination. No production web container worker is created; cleanup is explicitly verified.',disposition='NOT_APPLICABLE');counts['newBoundedWorkers']+=1
 else:
  assert by[key],key;x=dict(by[key].pop(0))
  if path in changed:
   x['reason']+=' SSC410 current-source re-review: exact original worker/resource statement and corresponding test bodies remain unchanged. New assembler factory only joins same immutable mapping/declared COPY values with in-memory digest sinks; the fingerprint fixture normal method only changes visibility, without resource, lifecycle or assertion changes.';counts['changedSourceSites']+=1
  else:assert sha(r/path)==oldstatic['inputHashes'][path] and line==x['sourceLine'];counts['sameByteSites']+=1
 x['sourceLine']=line;rows.append(x)
assert all(not v for v in by.values()) and counts['newBoundedWorkers']==5 and len(rows)==557
(i/'3273_copyman990_static_admission.json').open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,raw=557,counts=dict(counts),applicable=0,unclassified=0))
