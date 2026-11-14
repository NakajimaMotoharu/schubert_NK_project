"""Fresh third shared fixture and two corrected counters; unchanged individual review remains exact."""
from pathlib import Path
from collections import defaultdict,Counter
import json,hashlib
r=Path.cwd();i=r/'evidence/01_PT/018_NK-OPS-001/input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'3192_deferred948_corrected_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp);assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors']);old=load(i/'3185_deferred948_static_admission.json');oldstatic=load(r/old['static']['path']);by=defaultdict(list);base='src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/migration/';changed={base+'MigrationCleanupIdentityTest.java',base+'MigrationMasterFinalizerTest.java'}
for x in old['sourceAnchors']:by[(x['path'],x['rule'],x['sourceAnchor'],x['message'])].append(x)
for path in changed:
 t=(r/path).read_text();assert all(x in t for x in ['WORKERS = 8','TASKS = 64','WAIT_SECONDS = 5','TERMINATION_SECONDS = 10','future.get(WAIT_SECONDS, TimeUnit.SECONDS)','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'])
rows=[];counts=Counter()
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();key=(path,raw['rule'],anchor,raw['message']);assert by[key],key;x=dict(by[key].pop(0))
 if path in changed:
  assert raw['rule'] in ['AvoidCatchingGenericException','CompareObjectsWithEquals','UseProperClassLoader','NullAssignment','CloseResource','DoNotUseThreads'],key
  x['reason']+=' Re-reviewed SSC407 current third-fixture/counter correction: this exact flagged statement retains original identity, proxy or finite-resource meaning. Cleanup test bodies remain byte-identical; only exact SET0/next-warning-null and subject3 prefix are accepted. Unknown operations remain errors, Main/Target Test are unchanged; whole948 independently retries all original faults and cleanup with no DB resource.';counts['changedSourceSites']+=1
 else:assert sha(r/path)==oldstatic['inputHashes'][path] and line==x['sourceLine'];counts['sameByteSites']+=1
 x['sourceLine']=line;rows.append(x)
assert all(not v for v in by.values()) and len(rows)==541
(i/'3193_deferred948_corrected_static_admission.json').open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,raw=541,counts=dict(counts),applicable=0,unclassified=0))
