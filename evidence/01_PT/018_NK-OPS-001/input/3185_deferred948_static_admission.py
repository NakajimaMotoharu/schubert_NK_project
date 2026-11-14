"""Fresh finalization resource and identity sites; exact unchanged classifications remain byte-bound."""
from pathlib import Path
from collections import defaultdict,Counter
import json,hashlib
r=Path.cwd();i=r/'evidence/01_PT/018_NK-OPS-001/input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'3184_deferred948_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp);assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors']);old=load(i/'3172_default944_static_admission.json');oldstatic=load(r/old['static']['path']);by=defaultdict(list);base='src/schubert-nk-bootstrap/src/';changed={base+k+'/java/dev/codex/schubert/nk/migration/'+name+suffix+'.java' for k,suffix in [('main',''),('test','Test')] for name in ['MigrationMasterFinalizer','MigrationMasterTargetPublisher']}
for x in old['sourceAnchors']:by[(x['path'],x['rule'],x['sourceAnchor'],x['message'])].append(x)
for path in changed:
 t=(r/path).read_text()
 if '/test/' in path:assert all(x in t for x in ['WORKERS = 8','TASKS = 64','WAIT_SECONDS = 5','TERMINATION_SECONDS = 10','future.get(WAIT_SECONDS, TimeUnit.SECONDS)','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'])
 elif path.endswith('Finalizer.java'):assert 'SET CONSTRAINTS schubert.ck_entry_audio_links_entry_type_limit IMMEDIATE' in t
 else:assert 'PT-MIG-TARGET001..038' in t
rows=[];counts=Counter()
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();key=(path,raw['rule'],anchor,raw['message'])
 if not by[key]:
  assert '/test/' in path and path in changed and raw['rule']=='CompareObjectsWithEquals' and anchor in ['assertEquals(secondary == primary ? 0 : 1, primary.getSuppressed().length);','if (secondary != primary) assertSame(secondary, primary.getSuppressed()[0]);'],key
  x=dict(path=path,rule=raw['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason='Exact JUnit oracle compares Throwable reference identity, not equals value. It verifies same-object self-suppression is absent and distinct cleanup is retained once by reference; each phase/kind/cleanup invocation creates a fresh primary. Replacing identity with equals would invalidate the API contract. It acquires only independent memory proxies and no DB/process/native resource.',disposition='NOT_APPLICABLE');counts['newIdentityOracle']+=1
 else:
  x=dict(by[key].pop(0))
  if path in changed:
   assert raw['rule'] in ['AvoidCatchingGenericException','CompareObjectsWithEquals','UseProperClassLoader','NullAssignment','CloseResource','DoNotUseThreads'],key
   x['reason']+=' Re-reviewed SSC406 current deferred-flush path: this exact flagged statement retains original owned-resource, Throwable-identity, finite-worker or memory-only proxy semantics. The new flush and warning phases preserve primary/outer-close and forbid MAX/setval on failure; Final029030/Target037038 and whole948 verify them without actual DB/transaction authority.';counts['changedSourceSites']+=1
  else:assert sha(r/path)==oldstatic['inputHashes'][path] and line==x['sourceLine'];counts['sameByteSites']+=1
 x['sourceLine']=line;rows.append(x)
assert all(not v for v in by.values()) and counts['newIdentityOracle']==4 and len(rows)==541
(i/'3185_deferred948_static_admission.json').open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,raw=541,counts=dict(counts),applicable=0,unclassified=0))
