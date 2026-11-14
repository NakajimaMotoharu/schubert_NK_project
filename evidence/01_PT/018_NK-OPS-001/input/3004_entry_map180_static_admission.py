"""Reuse same-byte78 explicitly keyed sites, review each of five new finite memory executor sites."""
from pathlib import Path
import json,hashlib,collections
r=Path.cwd();i=r/'evidence/01_PT/018_NK-OPS-001/input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'3003_entry_map180_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp);assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
a=load(i/'2842_speaker_map156_static_admission.json');old=load(r/a['static']['path']);prior={}
for x in a['sourceAnchors']:
 assert sha(r/x['path'])==old['inputHashes'][x['path']];prior[(x['path'],x['rule'],x['sourceLine'],x['sourceAnchor'],x['message'])]=x
newtest=pf['testSources'][-1]['path'];text=(r/newtest).read_text();assert all(x in text for x in ['WORKERS = 8','TASKS = 64','WAIT_SECONDS = 5','TERMINATION_SECONDS = 10','future.get(WAIT_SECONDS, TimeUnit.SECONDS)','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));']);rows=[];seen=set();fresh=0
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();key=(path,raw['rule'],line,anchor,raw['message'])
 if path!=newtest:
  assert key in prior and key not in seen;seen.add(key);rows.append(prior[key]);continue
 assert raw['rule'] in ['CloseResource','DoNotUseThreads'] and anchor in ['var executor = Executors.newFixedThreadPool(WORKERS);','executor.submit(() -> m.copyRows(normal(), at()).rows().get(0).fields().get(0)));','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));']
 rows.append(dict(path=path,rule=raw['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason='Exact standalone host JUnit executor owns eight workers and64 memory-only value conversions using one immutable mapper. Every Future joins5 seconds, and finally shutdownNow plus asserted awaitTermination10 applies on all paths. No database/native/process resource is acquired. Automatic close would not prove the specified finite termination postcondition.',disposition='NOT_APPLICABLE'));fresh+=1
assert seen==set(prior) and len(prior)==78 and fresh==5 and len(rows)==83
(i/'3004_entry_map180_static_admission.json').open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,oldSameByte=78,newSites=5,rawPmd=83,applicable=0,unclassified=0))
