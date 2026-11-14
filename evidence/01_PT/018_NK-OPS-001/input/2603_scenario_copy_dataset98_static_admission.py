"""Exact current raw-site join to unchanged reviewed support and the new owned finite worker."""
from pathlib import Path
import collections,hashlib,json
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pf=ld(i/'2601_scenario_copy_dataset98_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=ld(sp);assert not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors']) and not any('/main/' in x['path'] for x in s['rawFindings'])
prior=ld(i/'2554_entry_copy_batch72_static_admission.json')['sourceAnchors']+ld(i/'2594_file_copy_batch38_static_admission.json')['sourceAnchors'];bykey={}
for row in prior:
 key=(row['path'],row['rule'],row['sourceLine'],row['message'])
 if key in bykey:assert bykey[key]['sourceAnchor']==row['sourceAnchor']
 else:bykey[key]=row
assert len(bykey)==36
proof=ld(b/'evidence/PG30858-scenario-copy-dataset-source-and-twelve-definitions-v1/manifest.json');pins={x['path']:x['sha256'] for x in proof['unchangedNecessaryClosure']}
newTest=pf['testSources'][0]['path'];text=(r/newTest).read_text();assert newTest.endswith('/ScenarioCopyDatasetTest.java') and all(x in text for x in ['Executors.newFixedThreadPool(8)','index < 64','future.get(5, TimeUnit.SECONDS)','finally {','executor.shutdownNow();','assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));'])
rows=[];used=set();new=0
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);source=(r/path).read_text();anchor=source.splitlines()[line-1].strip();key=(path,raw['rule'],line,raw['message'])
 if path==newTest:
  assert raw['rule'] in ['CloseResource','DoNotUseThreads'] and source.count(anchor)==1
  reason=('The exact locally acquired JUnit executor has every-exit finally shutdownNow and asserted awaitTermination10; all64 Future5 joins and both fixed stream byte assertions are finite, no implicit unbounded close.' if raw['rule']=='CloseResource' else 'This exact standalone pure immutable dataset JUnit site is not a J2EE webapp; eight locally owned workers perform64 independent two-stream golden checks. Future5 and finally shutdownNow/await10 are checked, no actual DB/FS/process/native/Root/service use.')
  row=dict(path=path,rule=raw['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE');new+=1
 else:
  assert key in bykey and path in pins and sha(r/path)==pins[path];row=bykey[key];assert row['sourceAnchor']==anchor and source.count(anchor)==row['occurrences'];used.add(key)
 rows.append(row)
assert new==5 and used==set(bykey) and len(rows)==41
p=i/'2603_scenario_copy_dataset98_static_admission.json';assert not p.exists();p.write_text(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,raw=41,perSiteReviewed=41,unchangedSupport36ExactByte=True,newFiniteWorkerSites=5,applicable=0,unclassified=0,sourceSuppressions=0)))
