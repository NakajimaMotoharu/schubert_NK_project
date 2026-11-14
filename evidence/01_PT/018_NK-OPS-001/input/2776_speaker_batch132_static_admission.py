"""Exact prior62 sites and ten new finite-worker/memory-double sites; no rule suppression."""
from pathlib import Path
import json,hashlib,collections
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'2775_speaker_batch132_prefix_fixed_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp);assert not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors']) and len(s['rawFindings'])==72
new=next(x['path'] for x in pf['testSources'] if x['path'].endswith('/SpeakerCopyBatchTest.java'));oldpaths={x['path'] for x in pf['testSources']} - {new};prior={}
for name in ['2761_staging_cleanup403_static_admission.json','2768_speaker_row28_static_admission.json']:
 a=load(i/name);old=load(r/a['static']['path'])
 for x in a['sourceAnchors']:
  if x['path'] not in oldpaths:continue
  assert sha(r/x['path'])==old['inputHashes'][x['path']];key=(x['path'],x['rule'],x['sourceLine'],x['sourceAnchor'],x['message']);prior[key]=x
assert len(prior)==62;text=(r/new).read_text();assert all(x in text for x in ['WORKERS = 8','TASKS = 64','WAIT_SECONDS = 5','TERMINATION_SECONDS = 10','future.get(WAIT_SECONDS, TimeUnit.SECONDS)','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));','private static final class MemorySink extends ByteArrayOutputStream','private static final class FailingSink extends OutputStream','private final ByteArrayOutputStream output = new ByteArrayOutputStream();','PREFIX_BYTES = 2'])
rows=[];seen=set();counts=collections.Counter()
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();key=(path,raw['rule'],line,anchor,raw['message'])
 if path!=new:
  assert key in prior and key not in seen;seen.add(key);rows.append(prior[key]);continue
 if raw['rule']=='CloseResource' and 'executor' not in anchor:
  assert anchor.startswith(('var sink = new MemorySink','var sink = new FailingSink','new OutputStream()')) or anchor=='var sink ='
  reason='Exact sink is a final ByteArrayOutputStream memory double with close/flush counters, a final FailingSink containing only an in-memory buffer and retained synthetic IOException, or an anonymous OutputStream whose write throws a synthetic runtime/Error. No file/socket/FD/DB/process/native resource is acquired. Closing or flushing the borrowed sink would invalidate the deliberately checked ownership and partial-output postconditions; memory-only doubles require no external cleanup.';counts['memory']+=1
 else:
  assert raw['rule'] in ['CloseResource','DoNotUseThreads'];reason='Exact standalone host JUnit-owned executor runs eight workers/64 immutable speaker-copy and entry-reference tasks, all Futures join5 and finally shutdownNow plus checked awaitTermination10 on every path. This is outside J2EE and acquires no external IO/database/native/Root resource. Implicit executor close omits the required finite postcondition.';counts['worker']+=1
 rows.append(dict(path=path,rule=raw['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE'))
assert seen==set(prior) and counts==dict(memory=5,worker=5)
p=i/'2776_speaker_batch132_static_admission.json';p.open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,oldSameByteSites=62,newMemorySites=5,newFiniteWorkerSites=5,rawPmd=72,applicable=0,unclassified=0))
