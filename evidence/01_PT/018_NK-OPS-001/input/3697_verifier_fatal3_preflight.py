"""Concrete eight in-memory fixture static sites, exact current Main quality and old9 inverse."""
from pathlib import Path
import hashlib,json
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pp=b/'evidence/PG34202-verifier-fatal3-prepare-v1/manifest.json';m=ld(pp);out=b/'evidence/PG34204-verifier-fatal3-preflight-v1';assert not out.exists();assert m['actualExit']==0 and m['expectedTests']==12 and m['newDefinitions']==3 and m['necessaryPriorDefinitions']==9 and not m['MainCompilationRepeated'];assert all(sha(r/p)==h for p,h in m['inputHashes'].items()) and all(sha(Path(p))==h for p,h in m['dependencies'].items())
for label,v in m['stages'].items():
 assert v['actualExit']==(4 if label=='pmd' else 0) and not v['timedOut']
 for stream in ['stdout','stderr']:assert sha(pp.parent/(label+'.'+stream))==v[stream+'Sha256']
assert m['processingErrors']==[] and m['checkstyleFindings']==0;expected={'UseProperClassLoader':['77'],'UseConcurrentHashMap':['81','93'],'CloseResource':['415'],'DoNotUseThreads':['415','420','433','434']};assert len(m['rawFindings'])==8 and sorted((x['rule'],x['line']) for x in m['rawFindings'])==sorted((rule,line) for rule,lines in expected.items() for line in lines);source=r/m['apiTestSources'][0];s=source.read_text();classified=[]
for x in m['rawFindings']:
 line=s.splitlines()[int(x['line'])-1];rule=x['rule']
 if rule=='UseProperClassLoader':
  assert 'type.getClassLoader()' in s;reason='Standalone hardcoded JDK Connection/PreparedStatement/ResultSet proxy interfaces use defining loader. No Class.forName/private reflection/backend or held-type substitute; no newly exposed loader configuration.'
 elif rule=='UseConcurrentHashMap':
  assert 'final Map<String, Throwable> injectedFailures = new HashMap<>();' in s;reason='Every synchronous negative case and parallel worker owns a fresh Fixture/field map/statement binding/fault map. Error controls are populated before same-thread invocation; no service/global/shared mutable map. Parent reads after Future completion only.'
 else:
  assert rule in ['CloseResource','DoNotUseThreads'] and 'assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));' in s;reason='Standalone JUnit pool rather than J2EE threads; Future.get10 plus finally shutdownNow/await10assert/classTimeout30 proves finite ownership. Failed worker stop cannot pass.'
 classified.append(dict(**x,sourceLine=line,sourceSha256=sha(source),disposition='NOT_APPLICABLE_EXACT_JDK_PROXY_OR_CONFINED_FIXTURE',reason=reason))
ap=r/m['exactMainStatic']['path'];a=ld(ap);cp=r/m['exactMainCompile']['path'];c=ld(cp);assert sha(ap)==m['exactMainStatic']['sha256'] and sha(cp)==m['exactMainCompile']['sha256'] and a['actualExit']==c['actualExit']==0 and a['staticApplicable']==a['unclassified']==a['processingErrors']==0 and a['rootNullAwayFresh'];assert all(a['inputHashes'][p]==m['inputHashes'][p] for p in m['inputHashes'] if p not in m['apiTestSources']);assert c['dependencies']==m['dependencies'];policy.compiler_element();proofp=b/'evidence/PG34200-verifier-fatal3-source-binding-v1/manifest.json';proof=ld(proofp);assert proof['actualExit']==0 and proof['old9InverseFormattedExact'] and proof['allMainAndPomsUnchanged'] and proof['currentSyntheticCases']==42;work=r.parent/'pgpt-runs/PG379/pg34202-verifier-fatal3-v1'
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:
 for n in m[key]:policy.relative_name(n)
 assert {n:sha(work/folder/n) for n in m[key]}==m[key]
assert len(m['physicalClassHashes'])==191;v=dict(actualExit=0,inputHashes=m['inputHashes'],dependencies=m['dependencies'],prepare=ref(pp),expectedTests=12,newDefinitions=3,necessaryPriorDefinitions=9,currentSyntheticFaultCases=42,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugsApplicable=0,rootNullAwayFresh=False,rootNullAwayReusedExactCurrentMain=True,originalMainStatic=ref(ap),classified=classified,original9Inverse=ref(proofp),declaredTargets=a['declaredTargets'],privateCarrierAllThreeMethodsIncluded=True,manualSuppressionAdded=False,actualBackendOrHeldActions=0,applicationTestsExecuted=0,newAcceptance=0,whole451Accepted=False);out.mkdir();(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=12,rawStatic=8,applicable=0,mainRebuilt=False,old9InverseExact=True,syntheticCases=42)))
