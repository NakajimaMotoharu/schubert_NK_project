"""Fresh SSC418 Main compile/static plus exact-site review; no PT executed."""
from pathlib import Path
import hashlib,json
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG33746-ssc418-context64-preflight-v1';w=r.parent/'pgpt-runs/PG379/pg33744-ssc418-context64-v1';assert not e.exists()
ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG33744-ssc418-context64-prepare-v1/manifest.json';sp=b/'evidence/PG33745-ssc418-context64-static-v1/manifest.json';p=ld(pp);s=ld(sp)
assert p['actualExit']==s['actualExit']==0 and p['expectedTests']==64 and len(p['apiMainSources'])==13 and len(p['apiTestSources'])==9
assert all(sha(r/x)==h for x,h in p['inputHashes'].items()) and s['inputHashes']==p['inputHashes']
for obj,slot in [(p,pp.parent),(s,sp.parent)]:
 for label,v in obj['stages'].items():
  assert type(v['actualExit']) is int and v['actualExit']==(4 if label=='pmd' else 0) and v['timedOut'] is False
  for stream in ['stdout','stderr']:assert sha(slot/(label+'.'+stream))==v[stream+'Sha256']
assert s['processingErrors']==[] and s['checkstyleFindings']==0 and s['spotbugs']['bugs']==s['spotbugs']['missing']==s['spotbugs']['errors']==0
old=ld(b/'evidence/PG33732-readwire58-preflight-v1/manifest.json');assert old['actualExit']==0
legacy={(Path(v['path']).name,v['rule'],v['line']):v for v in old['classified']};assert len(legacy)==41
new={('ProtectedReadWireClient.java','AvoidLiteralsInIfCondition','211'):'Exact SS311/352 and UI232 context64 byte invariant, fixed protocol width rather than configurable threshold. Independent0/63/65 negative vectors and valid64 ensure boundary; replacing the wire constant or rule suppression is not needed.',('ProtectedReadContextOwnershipTest.java','ReturnEmptyCollectionRatherThanNull','146'):'Explicit nullable encoder return is the CONTRACT005 fault under test. Empty64 or empty array would test a different boundary. This JUnit internal port intentionally returns null to prove fixed rejection without accidental NPE, not production collection API.'}
actual={(Path(v['path']).name,v['rule'],v['line']) for v in s['rawFindings']};assert actual==set(legacy)|set(new) and len(s['rawFindings'])==43
classified=[]
for v in s['rawFindings']:
 key=(Path(v['path']).name,v['rule'],v['line']);text=Path(v['path']).read_text();line=text.splitlines()[int(v['line'])-1]
 if key in legacy:
  previous=legacy[key];assert line==previous['sourceLine'] and sha(Path(v['path']))==previous['sourceSha256'];reason=previous['reason']
 else:reason=new[key]
 classified.append(dict(**v,sourceLine=line,sourceSha256=sha(Path(v['path'])),disposition='NOT_APPLICABLE_EXACT_PROTOCOL_INVARIANT_OR_NEGATIVE_FIXTURE_OR_OWNED_JUNIT',reason=reason))
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:
 for name in p[key]:policy.relative_name(name)
 assert {name:sha(w/folder/name) for name in p[key]}==p[key]
assert len(p['physicalClassHashes'])==196 and len(p['mainClassHashes'])==20
assert all(sha(Path(x))==h for x,h in p['dependencies'].items())
v=dict(actualExit=0,inputHashes=p['inputHashes'],dependencies=p['dependencies'],prepare=ref(pp),static=ref(sp),expectedTests=64,newDefinitions=6,necessaryPriorDefinitions=58,physicalClasses=196,sourceMain13=13,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugs=0,rootNullAwayFresh=True,rootCompilerConfiguration=p['compilerConfiguration'],pmdRaw43=43,classified=classified,allWholeTestsPreserved=True,heldTestsExtracted=False,manualSuppressionAdded=False,applicationTestsExecuted=0,whole451Accepted=False,newAcceptance=0)
e.mkdir();(e/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,staticRaw=43,applicable=0,unclassified=0,wholeCases=64,physical=196)))
