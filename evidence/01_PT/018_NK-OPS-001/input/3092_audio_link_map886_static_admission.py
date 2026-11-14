"""Exact same-byte prior492 plus fresh record-null and finite-worker sites; no rule suppression."""
from pathlib import Path
import json,hashlib
r=Path.cwd();i=r/'evidence/01_PT/018_NK-OPS-001/input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'3091_audio_link_map886_carrier_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp);assert s['actualExit']==0 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors']);prior={};paths=set(pf['mainSources']+[x['path'] for x in pf['testSources']])
for source in ['3066_audio_map842_static_admission.json','3075_audio_link_read20_static_admission.json']:
 a=load(i/source);old=load(r/a['static']['path'])
 for x in a['sourceAnchors']:
  path=x['path'];assert path in paths and sha(r/path)==old['inputHashes'][path];key=(path,x['rule'],x['sourceLine'],x['sourceAnchor'],x['message']);assert key not in prior;prior[key]=x
newtest='src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/migration/CurrentAudioLinkMapperTest.java';assert newtest in paths;text=(r/newtest).read_text();assert all(x in text for x in ['WORKERS = 8','TASKS = 64','WAIT_SECONDS = 5','TERMINATION_SECONDS = 10','future.get(WAIT_SECONDS, TimeUnit.SECONDS)','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));']);rows=[];seen=set();fresh=[]
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip();key=(path,raw['rule'],line,anchor,raw['message'])
 if path!=newtest:
  assert key in prior and key not in seen,key;seen.add(key);rows.append(prior[key]);continue
 if raw['rule']=='EqualsNull':
  assert anchor=='assertFalse(item.equals(null));'
  reason='Exact LinkOrder generated-record equality contract deliberately invokes equals(null) and asserts false. An object-null predicate would not execute or validate generated equals. This is a mandatory negative value-contract test and does not dereference a nullable argument or alter any production null boundary.'
 else:
  assert raw['rule'] in ['CloseResource','DoNotUseThreads'] and anchor in ['var executor = Executors.newFixedThreadPool(WORKERS);','executor.submit(','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'],(raw['rule'],anchor)
  reason='Exact standalone JUnit executor owns eight workers and64 in-memory pure link-map calls. Each Future has5-second get and every path runs finally shutdownNow with asserted10-second awaitTermination. Fixtures hold no DB/driver/file/native/server/process authority. Automatic close would not assert this finite postcondition; no resource or thread is left unjoined.'
 rows.append(dict(path=path,rule=raw['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE'));fresh.append(dict(rule=raw['rule'],line=line,anchor=anchor))
assert seen==set(prior) and len(prior)==492 and len(fresh)==6 and len(rows)==498
review=r/pf['slots']['static']/'link-order-site-review.json';review.open('x').write(json.dumps(dict(actualExit=0,sameByteSites=492,freshSites=fresh,applicable=0,unclassified=0,scope='FULL42_MIGRATION_MAIN_ROOT_RULES_NO_SUPPRESSION'),ensure_ascii=False,indent=2)+'\n');p=i/'3092_audio_link_map886_static_admission.json';p.open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,sameByte=492,fresh=6,rawPmd=498,applicable=0,unclassified=0))
