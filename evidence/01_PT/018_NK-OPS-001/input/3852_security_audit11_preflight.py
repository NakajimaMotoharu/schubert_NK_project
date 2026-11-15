"""Admit nine concrete memory-servlet fixture sites and freshRoot seven safe Web Main sources."""
from pathlib import Path
import hashlib,json,zipfile
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pp=b/'evidence/PG34642-security-audit11-prepare-v1/manifest.json';sp=b/'evidence/PG34644-security-audit11-static-v1/manifest.json';cp=b/'evidence/PG34640-security-audit11-source-inverse-v1/manifest.json';m=ld(pp);st=ld(sp);proof=ld(cp);out=b/'evidence/PG34646-security-audit11-preflight-v1';assert not out.exists();assert m['actualExit']==st['actualExit']==proof['actualExit']==0 and m['expectedTests']==11 and len(m['apiMainSources'])==2 and len(m['apiTestSources'])==1;assert m['inputHashes']==st['inputHashes'] and all(sha(r/n)==h for n,h in m['inputHashes'].items())
for obj,slot in [(m,pp.parent),(st,sp.parent)]:
 for label,v in obj['stages'].items():
  assert v['actualExit']==(4 if label=='pmd' else 0) and not v['timedOut']
  for stream in ['stdout','stderr']:assert sha(slot/(label+'.'+stream))==v[stream+'Sha256']
assert st['processingErrors']==[] and st['checkstyleFindings']==0 and st['spotbugs']['bugs']==st['spotbugs']['errors']==st['spotbugs']['missing']==0;assert proof['originalTenAssertionsInverseFormattedExact'] and proof['mainSourcesUnchanged'] and proof['original2Workers8TasksGet10Preserved'];expected={'CloseResource':['527'],'DoNotUseThreads':['527','533','547','548']};assert sorted((x['rule'],x['line']) for x in st['rawFindings'])==sorted((rule,line) for rule,lines in expected.items() for line in lines);source=r/m['apiTestSources'][0];text=source.read_text();classified=[]
for x in st['rawFindings']:
 line=text.splitlines()[int(x['line'])-1];assert Path(x['path'])==source and x['rule'] in ['CloseResource','DoNotUseThreads'] and 'assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));' in text and 'future.get(10, TimeUnit.SECONDS)' in text
 reason='Standalone JUnit existingeight tasks/two workers, each actor/request immutable and only own concurrent logger queue shared. Futureget10/finallyshutdownNow/await10assert/classTimeout30. Any failed termination fails the test; no container/loggerprovider/backend/service operation.'
 classified.append(dict(**x,sourceLine=line,sourceSha256=sha(source),disposition='NOT_APPLICABLE_CONCRETE_BOUNDED_MEMORY_FIXTURE',reason=reason))
work=r.parent/'pgpt-runs/PG379/pg34642-security-audit11-v1'
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:
 for n in m[key]:policy.relative_name(n)
 assert {n:sha(work/folder/n) for n in m[key]}==m[key]
assert len(m['physicalClassHashes'])==180 and len(m['mainClassHashes'])==4 and {v.replace('.','/')+'.class' for v in st['spotbugs']['classStats']}==set(m['mainClassHashes']);assert all(sha(Path(p))==h for p,h in m['dependencies'].items());providers={}
for p in m['dependencies']:
 with zipfile.ZipFile(p) as z:providers[p]=[n for n in z.namelist() if n=='META-INF/services/java.sql.Driver']
assert all(not values for values in providers.values());v=dict(actualExit=0,inputHashes=m['inputHashes'],dependencies=m['dependencies'],prepare=ref(pp),static=ref(sp),expectedTests=11,newDefinitions=1,necessaryPriorDefinitions=10,physicalClasses=180,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugsApplicable=0,spotbugsRaw=0,rootNullAwayFresh=True,original10InverseExact=True,sourceInverse=ref(cp),pmdRaw5=5,classified=classified,declaredTargets=proof['targets'],manualSuppressionAdded=False,currentClasspathSqlDriverDescriptors=providers,pureFormNoJdbcOrBackendScope=True,explicitServletAndSpringSdkHashes=proof['sdkHashes'],actualBackendOrHeldActions=0,applicationTestsExecuted=0,newAcceptance=0,whole451Accepted=False);out.mkdir();(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=11,physical=180,rootMain2Fresh=True,staticRaw=5,applicable=0,spotbugs=0)))
