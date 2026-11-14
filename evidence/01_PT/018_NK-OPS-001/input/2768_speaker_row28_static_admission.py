"""Review five new owned finite-worker sites; retain unchanged codec five-site qualification."""
from pathlib import Path
import json,hashlib
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'2767_speaker_row28_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp);assert not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors']) and len(s['rawFindings'])==10
old=load(i/'2761_staging_cleanup403_static_admission.json');oldstatic=load(r/old['static']['path']);codec=next(x['path'] for x in pf['testSources'] if x['path'].endswith('/PostgresCopyTextEncoderTest.java'));prior=[x for x in old['sourceAnchors'] if x['path']==codec];assert len(prior)==5 and sha(r/codec)==oldstatic['inputHashes'][codec]
new=next(x['path'] for x in pf['testSources'] if x['path'].endswith('/SpeakerCopyRowTest.java'));text=(r/new).read_text();assert all(x in text for x in ['WORKERS = 8','TASKS = 64','WAIT_SECONDS = 5','TERMINATION_SECONDS = 10','Executors.newFixedThreadPool(WORKERS)','future.get(WAIT_SECONDS, TimeUnit.SECONDS)','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'])
rows=[];seen=[]
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip()
 if path==codec:
  found=[(n,x) for n,x in enumerate(prior) if x['sourceLine']==line and x['sourceAnchor']==anchor and x['rule']==raw['rule'] and x['message']==raw['message']];assert len(found)==1;n,row=found[0];assert n not in seen;seen.append(n);rows.append(row);continue
 assert path==new and raw['rule'] in ['CloseResource','DoNotUseThreads'];reason='Exact standalone host JUnit-owned eight-worker/64-task executor uses immutable synthetic speaker metadata and independent literal bytes only, with Future5 and finally shutdownNow plus checked awaitTermination10 on every path. No J2EE executor or DB/FS/socket/native/Root operation. Implicit close would omit the finite cleanup postcondition required by this test.'
 rows.append(dict(path=path,rule=raw['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE'))
assert len(seen)==5 and len(rows)==10
p=i/'2768_speaker_row28_static_admission.json';p.open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,oldExactByteSites=5,newFiniteWorkerSites=5,applicable=0,unclassified=0))
