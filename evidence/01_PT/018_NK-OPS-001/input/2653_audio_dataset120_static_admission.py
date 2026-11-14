"""Join unchanged-byte prior exact findings and individually review new memory-only fixture sites."""
from pathlib import Path
from collections import Counter
import hashlib,json
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
c=ld(i/'2651_audio_dataset120_profile.json');pp=r/c['slots']['prepare']/'manifest.json';sp=r/c['slots']['static']/'manifest.json';v=ld(sp);old={}
for name in ['2614_copy_stream113_static_admission.json','2644_audio_copy_row28_static_admission.json']:
 a=ld(i/name);st=ld(r/a['static']['path']);assert sha(r/a['static']['path'])==a['static']['sha256']
 for item in a['sourceAnchors']:
  if item['path'] in c['mainSources']+[x['path'] for x in c['testSources']]:
   assert sha(r/item['path'])==st['inputHashes'][item['path']]
   old[(item['path'],item['rule'],str(item.get('sourceLine')),item['message'])]=item
rows=[];new=0
for x in v['rawFindings']:
 path=str(Path(x['path']).relative_to(r));key=(path,x['rule'],x['line'],x['message'])
 if key in old:rows.append(dict(old[key]));continue
 assert path.endswith('/AudioCopyDatasetTest.java');line=int(x['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();rule=x['rule'];assert rule in ['CloseResource','DoNotUseThreads']
 if 'MemorySink' in anchor or 'FailingSink' in anchor:
  assert rule=='CloseResource';reason='This exact source-owned synthetic sink is ByteArrayOutputStream plus close/flush memory flags, or OutputStream whose write only throws a fixed supplied synthetic IOException. It constructs no file/socket/driver/native/OS handle, retains no external resource. The test must prove the production borrower never calls close/flush, including failure; wrapping it in try-with-resources would erase this ownership assertion.'
 else:
  assert any(word in anchor for word in ['newFixedThreadPool','executor.submit','shutdownNow','awaitTermination']);reason='This exact standalone JUnit site owns8 workers for64 immutable dataset memory-stream golden assertions, not a managed J2EE webapp. Every Future joins5s; finally shutdownNow and assert awaitTermination10s prove finite termination without unbounded implicit close. No DB/driver/file/socket/native/Root/service action and no blanket Test exclusion.'
 rows.append(dict(path=path,rule=rule,sourceLine=line,sourceAnchor=anchor,occurrences=1,message=x['message'],reason=reason,disposition='NOT_APPLICABLE'));new+=1
assert new==13 and len(rows)==len(v['rawFindings']);out=i/'2653_audio_dataset120_static_admission.json';assert not out.exists();out.write_text(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=c['id'],prepare=ref(pp),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,raw=len(rows),new13IndividuallyClassified=True,unchangedBytePriorSites=len(rows)-new,rules=dict(Counter(x['rule'] for x in rows)),noSuppression=True)))
