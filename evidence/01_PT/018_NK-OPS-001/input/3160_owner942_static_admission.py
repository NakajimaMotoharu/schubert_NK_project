"""Fresh line-bound reviews of changed owner fixtures; preserve exact unchanged site classifications."""
from pathlib import Path
from collections import defaultdict,Counter
import json,hashlib
r=Path.cwd();i=r/'evidence/01_PT/018_NK-OPS-001/input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'3162_owner942_corrected_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp);assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors']);old=load(i/'3143_games940_static_admission.json');oldstatic=load(r/old['static']['path']);by=defaultdict(list);base='src/schubert-nk-bootstrap/src/';changed={base+'main/java/dev/codex/schubert/nk/migration/MigrationMasterColumnVerifier.java',base+'test/java/dev/codex/schubert/nk/migration/MigrationMasterColumnVerifierTest.java',base+'test/java/dev/codex/schubert/nk/migration/MigrationMasterTargetPublisherTest.java'}
for x in old['sourceAnchors']:by[(x['path'],x['rule'],x['sourceAnchor'],x['message'])].append(x)
for path in changed:
 t=(r/path).read_text()
 if '/test/' in path:
  assert all(x in t for x in ['WORKERS = 8','TASKS = 64','WAIT_SECONDS = 5','TERMINATION_SECONDS = 10','future.get(WAIT_SECONDS, TimeUnit.SECONDS)','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'])
 else:assert 'if (!"nk_owner".equals(result.getString(10))) throw invalid();' in t
rows=[];counts=Counter()
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();key=(path,raw['rule'],anchor,raw['message']);assert by[key],key;x=dict(by[key].pop(0))
 if path in changed:
  # Every original flagged site remains exact-token identical. Existing reason was read and
  # re-evaluated for tenth-owner-field: JDBC close/rethrow/identity, finite JUnit workers,
  # JDK-interface Proxy loader, deliberate test-only SQLNULL mutation, borrowed proxy connection.
  assert raw['rule'] in ['AvoidCatchingGenericException','CompareObjectsWithEquals','UseProperClassLoader','NullAssignment','CloseResource','DoNotUseThreads'],(path,raw['rule'],anchor)
  x['reason']+=' Re-reviewed SSC404 current owner10 projection: this exact unchanged flagged statement has identical ownership/thread/null semantics; new owner mismatch/NULL negatives do not grant authority, repair data or acquire DB resources. New Column025/Target035 and all942 qualify the extended same-source path.'
  counts['changedSourceSites']+=1
 else:
  assert sha(r/path)==oldstatic['inputHashes'][path] and line==x['sourceLine'];counts['sameByteSites']+=1
 x['sourceLine']=line;rows.append(x)
assert all(not v for v in by.values()) and len(rows)==len(old['sourceAnchors'])==537
p=i/'3160_owner942_static_admission.json';p.open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,raw=537,counts=dict(counts),applicable=0,unclassified=0))
