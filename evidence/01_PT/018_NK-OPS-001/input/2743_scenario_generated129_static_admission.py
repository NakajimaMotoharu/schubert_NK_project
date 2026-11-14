"""Bind old same-byte57 sites and independently review six null contract assertions/five owned worker sites."""
from pathlib import Path
import json,hashlib,collections
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pf=load(i/'2742_scenario_generated129_fixed_profile.json');sp=r/pf['slots']['static']/'manifest.json';s=load(sp);oldpf=load(i/'2613_copy_stream113_state_fixed_profile.json');olds=load(r/oldpf['slots']['static']/'manifest.json');prior=load(i/'2614_copy_stream113_static_admission.json')['sourceAnchors'];assert len(prior)==57 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][x]==0 for x in ['bugs','missing','errors']);assert len(s['rawFindings'])==68
new=next(x['path'] for x in pf['testSources'] if x['path'].endswith('ScenarioGeneratedValueTest.java'));text=(r/new).read_text();assert all(x in text for x in ['Executors.newFixedThreadPool(WORKERS)','index < TASKS','future.get(WAIT_SECONDS, TimeUnit.SECONDS)','finally {','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));','WORKERS = 8','TASKS = 64','WAIT_SECONDS = 5','TERMINATION_SECONDS = 10'])
rows=[];seen=[]
for raw in s['rawFindings']:
 path=str(Path(raw['path']).relative_to(r));line=int(raw['line']);anchor=(r/path).read_text().splitlines()[line-1].strip()
 if path!=new:
  assert sha(r/path)==olds['inputHashes'][path]==s['inputHashes'][path]
  matches=[(n,x) for n,x in enumerate(prior) if x['path']==path and x['sourceLine']==line and x['rule']==raw['rule'] and x['sourceAnchor']==anchor and x['message']==raw['message']];assert len(matches)==1;n,row=matches[0];assert n not in seen;seen.append(n);rows.append(row);continue
 if raw['rule']=='EqualsNull':
  assert anchor=='assertFalse(value.equals(null));';reason='This exact assertion deliberately tests Object.equals(null)==false for a generated immutable primitive record. Replacing equals with == would test reference identity instead and destroy the independent null-contract oracle. No production null dereference, catch, suppression or nullable public acceptance is introduced.'
 elif raw['rule']=='CloseResource':
  assert anchor=='var executor = Executors.newFixedThreadPool(WORKERS);';reason='Exact JUnit-owned finite executor reaches finally shutdownNow and checked awaitTermination10 on every path; all64 Futures join5, eight locally owned workers operate immutable synthetic value mappings only. No J2EE managed thread or external resource; implicit close omits the tested finite postcondition.'
 else:
  assert raw['rule']=='DoNotUseThreads';reason='Exact standalone host JUnit site belongs to eight locally owned workers/64 synthetic immutable mapping tasks with Future5 and finally shutdownNow/await10. This is outside J2EE and invokes no filesystem, database, Root, native, service, permission or remote action.'
 rows.append(dict(path=path,rule=raw['rule'],sourceAnchor=anchor,sourceLine=line,occurrences=1,message=raw['message'],reason=reason,disposition='NOT_APPLICABLE'))
assert len(seen)==57 and set(seen)==set(range(57))
p=i/'2743_scenario_generated129_static_admission.json';p.open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=pf['id'],prepare=ref(r/pf['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=rows),ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,raw=68,oldExactByteSites=57,contractNullSites=6,finiteWorkers=5,applicable=0,unclassified=0)))
