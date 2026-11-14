"""One owned memory-only digest sink site and five finite standalone worker sites."""
from pathlib import Path
import json,hashlib,collections
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'2837_master_finger403_fixed_vectors_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp);assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
newmain=next(p for p in pf['mainSources'] if p.endswith('/MigrationMasterCopyFingerprint.java'));newtest=newmain.replace('/main/','/test/').replace('.java','Test.java');oldpaths=set(pf['mainSources']+[x['path'] for x in pf['testSources']])-{newmain,newtest};a=load(i/'2795_master_six383_static_admission.json');old=load(r/a['static']['path']);prior={}
for x in a['sourceAnchors']:
 assert x['path'] in oldpaths and sha(r/x['path'])==old['inputHashes'][x['path']]
 prior[(x['path'],x['rule'],x['sourceLine'],x['sourceAnchor'],x['message'])]=x
main=(r/newmain).read_text();test=(r/newtest).read_text();assert all(x in main for x in ['private static final class DigestSink extends OutputStream','private final MessageDigest digest;','digest = MessageDigest.getInstance("SHA-256");','digest.update((byte) value);','count = Math.incrementExact(count);']);assert all(x in test for x in ['WORKERS = 8','TASKS = 64','WAIT_SECONDS = 5','TERMINATION_SECONDS = 10','future.get(WAIT_SECONDS, TimeUnit.SECONDS)','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'])
rows=[];seen=set();counts=collections.Counter()
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();key=(path,raw['rule'],line,anchor,raw['message'])
 if path in oldpaths:
  assert key in prior and key not in seen;seen.add(key);rows.append(prior[key]);continue
 if path==newmain:
  assert raw['rule']=='CloseResource' and anchor=='var sink = sinks.get(index);'
  reason='Exact sink is the private final DigestSink created locally with only a pinned-Java SHA256 MessageDigest and long byte counter. It acquires no file/socket/DB/native FD and stores no raw wire. Its inherited OutputStream.close is a no-op, and neither sink nor digest escapes: only immutable table/row/byte/hex metadata is returned. Digest completion is explicit before return; all six independent fixed hash/count vectors and fresh/parallel invocation tests verify owned state isolation. Closing a memory-only sink provides no external cleanup.';counts['ownedMemoryDigest']+=1
 else:
  assert path==newtest and raw['rule'] in ['CloseResource','DoNotUseThreads'] and anchor in ['var executor = Executors.newFixedThreadPool(WORKERS);','futures.add(executor.submit(() -> metadata(fingerprint.fingerprint(source))));','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));']
  reason='Exact standalone host JUnit executor owns eight workers/64 immutable master fingerprints, with six fresh memory digest sinks per call. Every Future joins5 seconds and finally shutdownNow plus checked awaitTermination10 holds on all paths. No external DB/native FD/process is acquired; this is outside J2EE. Implicit executor close omits the specifically required bounded termination assertion.';counts['worker']+=1
 rows.append(dict(path=path,rule=raw['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE'))
assert seen==set(prior) and len(prior)==159 and counts==dict(ownedMemoryDigest=1,worker=5) and len(rows)==165
(i/'2833_master_finger403_static_admission.json').open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,oldSameByte=159,newSites=dict(counts),rawPmd=165,applicable=0,unclassified=0))
