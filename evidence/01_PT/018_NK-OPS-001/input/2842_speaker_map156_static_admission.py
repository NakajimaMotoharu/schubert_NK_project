"""Same-byte prior72 plus exact record null-contract and finite worker sites."""
from pathlib import Path
import json,hashlib,collections
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'2841_speaker_map156_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp);assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
newmain=next(p for p in pf['mainSources'] if p.endswith('/SpeakerMigrationMap.java'));newtest=newmain.replace('/main/','/test/').replace('.java','Test.java');oldpaths=set(pf['mainSources']+[x['path'] for x in pf['testSources']])-{newmain,newtest};a=load(i/'2776_speaker_batch132_static_admission.json');old=load(r/a['static']['path']);prior={}
for x in a['sourceAnchors']:
 assert x['path'] in oldpaths and sha(r/x['path'])==old['inputHashes'][x['path']]
 prior[(x['path'],x['rule'],x['sourceLine'],x['sourceAnchor'],x['message'])]=x
text=(r/newtest).read_text();assert all(x in text for x in ['WORKERS = 8','TASKS = 64','WAIT_SECONDS = 5','TERMINATION_SECONDS = 10','future.get(WAIT_SECONDS, TimeUnit.SECONDS)','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'])
rows=[];seen=set();counts=collections.Counter()
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();key=(path,raw['rule'],line,anchor,raw['message'])
 if path in oldpaths:
  assert key in prior and key not in seen;seen.add(key);rows.append(prior[key]);continue
 assert path==newtest
 if raw['rule']=='EqualsNull':
  assert anchor=='assertFalse(first.equals(null));'
  reason='Exact JUnit assertion independently verifies the public generated SpeakerMapping.equals(Object) contract returns false for a null peer. This is the method under test, not an application null check or a substitute for identity/nullness validation. Replacing it by first==null would stop testing the required generated-record null behavior and invalidate the independent oracle.';counts['recordNullOracle']+=1
 else:
  assert raw['rule'] in ['CloseResource','DoNotUseThreads'] and anchor in ['var executor = Executors.newFixedThreadPool(WORKERS);','executor.submit(','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));']
  reason='Exact standalone host JUnit executor owns eight workers/64 shared immutable speaker-map lookups and independent selected-row COPY batches. Every Future joins5 seconds and finally shutdownNow plus checked awaitTermination10 applies on all paths. No external database/native FD/process is acquired; this is outside J2EE. Implicit executor close omits the mandatory bounded termination postcondition.';counts['worker']+=1
 rows.append(dict(path=path,rule=raw['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE'))
assert seen==set(prior) and len(prior)==72 and counts==dict(recordNullOracle=1,worker=5) and len(rows)==78
(i/'2842_speaker_map156_static_admission.json').open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,oldSameByte=72,newSites=dict(counts),rawPmd=78,applicable=0,unclassified=0))
