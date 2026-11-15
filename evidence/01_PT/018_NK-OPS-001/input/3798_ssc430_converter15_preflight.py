"""Admit nine concrete memory-servlet fixture sites and freshRoot seven safe Web Main sources."""
from pathlib import Path
import hashlib,json,zipfile
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pp=b/'evidence/PG34486-ssc430-converter15-prepare-v1/manifest.json';sp=b/'evidence/PG34488-ssc430-converter15-static-v1/manifest.json';cp=b/'evidence/PG34484-ssc430-converter-source-inverse-v1/manifest.json';m=ld(pp);st=ld(sp);proof=ld(cp);out=b/'evidence/PG34490-ssc430-converter15-preflight-v1';assert not out.exists();assert m['actualExit']==st['actualExit']==proof['actualExit']==0 and m['expectedTests']==15 and len(m['apiMainSources'])==7 and len(m['apiTestSources'])==1;assert m['inputHashes']==st['inputHashes'] and all(sha(r/n)==h for n,h in m['inputHashes'].items())
for obj,slot in [(m,pp.parent),(st,sp.parent)]:
 for label,v in obj['stages'].items():
  assert v['actualExit']==(4 if label=='pmd' else 0) and not v['timedOut']
  for stream in ['stdout','stderr']:assert sha(slot/(label+'.'+stream))==v[stream+'Sha256']
assert st['processingErrors']==[] and st['checkstyleFindings']==0 and st['spotbugs']['bugs']==st['spotbugs']['errors']==st['spotbugs']['missing']==0;assert proof['originalThirteenAssertionsInverseFormattedExact'] and proof['onlyMainGuardAndImportInverseExact'] and proof['original2Workers8TasksGet10Preserved'];expected={'UseConcurrentHashMap':['69','70'],'UseProperClassLoader':['103'],'CompareObjectsWithEquals':['120'],'CloseResource':['311'],'DoNotUseThreads':['311','317','327','328']};assert sorted((x['rule'],x['line']) for x in st['rawFindings'])==sorted((rule,line) for rule,lines in expected.items() for line in lines);source=r/m['apiTestSources'][0];text=source.read_text();classified=[]
for x in st['rawFindings']:
 line=text.splitlines()[int(x['line'])-1]
 if x['rule']=='UseConcurrentHashMap':
  assert 'new LinkedHashMap<>()' in line;reason='Each memory request fixture and both parameter/header maps belong exclusively to one worker or sequential negative case, controls set before convert; shared converter has no mutable request maps, Future completion joins observations.'
 elif x['rule']=='UseProperClassLoader':
  assert 'HttpServletRequest.class.getClassLoader()' in line;reason='Only explicitly reviewed jakarta.servlet HttpServletRequest interface JDK proxy, defining interface loader required. No configurable class loading/private reflection/held-class substitute or actual servlet container.'
 elif x['rule']=='CompareObjectsWithEquals':
  assert line.strip()=='case "equals" -> proxy == args[0];';reason='Proxy handler implements its own reference-identity equals contract. Calling proxy.equals here recursively re-enters this handler; it is not domain record/value comparison or authentication equality.'
 else:
  assert x['rule'] in ['CloseResource','DoNotUseThreads'] and 'assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));' in text and 'get(10, TimeUnit.SECONDS)' in text;reason='Standalone JUnit not J2EE, original8 requests/two workers and Futureget10 retained, finallyshutdownNow/await10assert and Timeout30. Any failed termination/test cannot pass; no container/network/DB/process started.'
 classified.append(dict(**x,sourceLine=line,sourceSha256=sha(source),disposition='NOT_APPLICABLE_CONCRETE_CONFINED_MEMORY_FIXTURE',reason=reason))
work=r.parent/'pgpt-runs/PG379/pg34486-ssc430-converter15-v1'
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:
 for n in m[key]:policy.relative_name(n)
 assert {n:sha(work/folder/n) for n in m[key]}==m[key]
assert len(m['physicalClassHashes'])==183 and len(m['mainClassHashes'])==7 and {v.replace('.','/')+'.class' for v in st['spotbugs']['classStats']}==set(m['mainClassHashes']);assert all(sha(Path(p))==h for p,h in m['dependencies'].items());providers={}
for p in m['dependencies']:
 with zipfile.ZipFile(p) as z:providers[p]=[n for n in z.namelist() if n=='META-INF/services/java.sql.Driver']
assert all(not values for values in providers.values());v=dict(actualExit=0,inputHashes=m['inputHashes'],dependencies=m['dependencies'],prepare=ref(pp),static=ref(sp),expectedTests=15,newDefinitions=2,necessaryPriorDefinitions=13,physicalClasses=183,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugsApplicable=0,spotbugsRaw=0,rootNullAwayFresh=True,original13InverseExact=True,sourceInverse=ref(cp),pmdRaw9=9,classified=classified,declaredTargets=proof['targets'],manualSuppressionAdded=False,currentClasspathSqlDriverDescriptors=providers,pureFormNoJdbcOrBackendScope=True,explicitServletAndSpringSdkHashes=proof['sdkHashes'],actualBackendOrHeldActions=0,applicationTestsExecuted=0,newAcceptance=0,whole451Accepted=False);out.mkdir();(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=15,physical=183,rootMain7Fresh=True,staticRaw=9,applicable=0,spotbugs=0)))
