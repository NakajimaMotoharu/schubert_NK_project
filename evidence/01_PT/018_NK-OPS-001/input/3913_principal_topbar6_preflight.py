"""Concrete source sites, closed local JMS-interface path and exact JDK SQL-exception metadata."""
from pathlib import Path
import hashlib,json,zipfile
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pp=b/'evidence/PG34802-principal-topbar6-prepare-v1/manifest.json';sp=b/'evidence/PG34804-principal-topbar6-static-v1/manifest.json';cp=b/'evidence/PG34800-principal-topbar6-source-v1/manifest.json';m=ld(pp);st=ld(sp);proof=ld(cp);out=b/'evidence/PG34806-principal-topbar6-preflight-v1';assert not out.exists();assert m['actualExit']==st['actualExit']==proof['actualExit']==0 and m['expectedTests']==6 and len(m['apiMainSources'])==5 and len(m['apiTestSources'])==2;assert m['inputHashes']==st['inputHashes'] and all(sha(r/n)==h for n,h in m['inputHashes'].items())
for obj,slot in [(m,pp.parent),(st,sp.parent)]:
 for label,v in obj['stages'].items():
  assert v['actualExit']==0 and not v['timedOut']
  for stream in ['stdout','stderr']:assert sha(slot/(label+'.'+stream))==v[stream+'Sha256']
assert st['processingErrors']==[] and st['checkstyleFindings']==0 and st['spotbugs']['bugs']==st['spotbugs']['errors']==st['spotbugs']['missing']==0;assert proof['mainSourcesUnchanged'] and proof['oldClosedFourByteExact'] and proof['newDefinitions']==2 and proof['necessaryPriorDefinitions']==4 and st['rawFindings']==[];classified=[]
work=r.parent/'pgpt-runs/PG379/pg34802-principal-topbar6-v1'
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:
 for n in m[key]:policy.relative_name(n)
 assert {n:sha(work/folder/n) for n in m[key]}==m[key]
assert len(m['physicalClassHashes'])==181 and len(m['mainClassHashes'])==5 and {v.replace('.','/')+'.class' for v in st['spotbugs']['classStats']}==set(m['mainClassHashes']);assert all(sha(Path(p))==h for p,h in m['dependencies'].items());jp=r/'evidence/01_PT/007_NK-AUT-001/evidence/PG20876-admin-prelude-jdk-static-review-v1/manifest.json';j=ld(jp);assert j['decision']=='STATIC_JDK_EXCEPTION_LOG_WRITER_CLOSURE' and j['testsReexecuted']==j['actualBackendActions']==0;assert sha(r.parent/'toolchain/jdk-25.0.4/lib/modules')==j['jdkModulesSha256'] and sha(r.parent/'toolchain/jdk-25.0.4/bin/javap')==j['jdkJavapSha256']
for path,h in j['staticArtifacts'].items():assert path.startswith('evidence/01_PT/007_NK-AUT-001/evidence/PG20876-admin-prelude-jdk-static-review-v1/') and Path(path).suffix in ['.json','.stdout','.stderr'] and sha(r/path)==h
providers={}
for path in m['dependencies']:
 with zipfile.ZipFile(path) as z:providers[path]=[n for n in z.namelist() if n=='META-INF/services/java.sql.Driver']
assert all(not names for names in providers.values());v=dict(actualExit=0,inputHashes=m['inputHashes'],dependencies=m['dependencies'],prepare=ref(pp),static=ref(sp),expectedTests=6,newDefinitions=2,necessaryPriorDefinitions=4,physicalClasses=181,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugsApplicable=0,spotbugsRaw=0,rootNullAwayFresh=True,originalClosed4ByteExact=True,sourceInverse=ref(cp),pmdRaw0=0,classified=classified,declaredTargets=proof['targets'],manualSuppressionAdded=False,jdkExceptionStaticReference=ref(jp),sameJdkModuleAndJavapBytes=True,currentClasspathSqlDriverDescriptors=providers,currentUnitInitMustBindAfterRun=True,publicClosedProjectionNotActualAuthentication=True,sdkJvmNativeHostFsActivityUnmeasured=True,applicationTestsExecuted=0,newAcceptance=0,whole451Accepted=False);out.mkdir();(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=6,physical=181,rootMain5Fresh=True,staticRaw=0,applicable=0,spotbugs=0)))
