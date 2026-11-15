"""Classify current-source sites; preserve rules and reject all unknown applicable findings."""
from pathlib import Path
from collections import defaultdict,Counter
import json,hashlib
r=Path.cwd();i=r/'evidence/01_PT/018_NK-OPS-001/input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'3365_current_transfer1030_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp)
assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
old=load(i/'3356_coordinator1010_static_admission.json');oldstatic=load(r/old['static']['path']);by=defaultdict(list)
for x in old['sourceAnchors']:by[(x['path'],x['rule'],x['sourceAnchor'],x['message'])].append(x)
base='src/schubert-nk-bootstrap/src/';main=base+'main/java/dev/codex/schubert/nk/migration/CurrentMigrationTransfer.java';test=main.replace('/main/','/test/').replace('.java','Test.java');changed={test.replace('CurrentMigrationTransferTest','MigrationMasterTargetPublisherTest')}
t=(r/test).read_text();assert all(x in t for x in ['WORKERS = 8','TASKS = 64','WAIT_SECONDS = 5','TERMINATION_SECONDS = 10','future.get(WAIT_SECONDS, TimeUnit.SECONDS)','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'])
rows=[];counts=Counter()
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();key=(path,raw['rule'],anchor,raw['message'])
 if path==test:
  assert raw['rule'] in ['CloseResource','DoNotUseThreads'] and anchor in ['var executor = Executors.newFixedThreadPool(WORKERS);','executor.submit(','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'],key
  x=dict(path=path,rule=raw['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason='Standalone host-only JUnit bounded8worker64task contract. Immutable shared coordinator/mapping/dataset; each task owns fresh private JDBC proxy, SQL list and callback counter. No actual DB/driver/native/authority. Every Future has5s get, finally shutdownNow and asserted10s awaitTermination. No container-owned production executor.',disposition='NOT_APPLICABLE');counts['newBoundedWorkers']+=1
 else:
  assert by[key],key;x=dict(by[key].pop(0))
  if path in changed:
   x['reason']+=' SSC415 current-source re-review: exact original whole Test bodies and resource/worker statements preserved; only shared test-only shared test-only content override map added. Per-task JDBC proxy is private and never actual DB. No lifecycle, SQL literal or normal assertion change.';counts['changedSourceSites']+=1
  else:assert sha(r/path)==oldstatic['inputHashes'][path] and line==x['sourceLine'];counts['sameByteSites']+=1
 x['sourceLine']=line;rows.append(x)
assert all(not v for v in by.values()) and counts['newBoundedWorkers']==5 and len(rows)==567
(i/'3366_current_transfer1030_static_admission.json').open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,raw=len(rows),counts=dict(counts),applicable=0,unclassified=0))
