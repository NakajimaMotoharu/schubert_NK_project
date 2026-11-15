"""Admit current Admin14 fixture10 concrete sites plus exact Root/Main/JDK lineage."""
from pathlib import Path
import hashlib,json,zipfile
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pp=b/'evidence/PG34366-login-fatal3-prepare-v2/manifest.json';m=ld(pp);out=b/'evidence/PG34368-login-fatal3-preflight-v1';assert not out.exists();assert m['actualExit']==0 and m['expectedTests']==25 and m['newDefinitions']==3 and m['necessaryPriorDefinitions']==22 and not m['MainCompilationRepeated'];assert all(sha(r/p)==h for p,h in m['inputHashes'].items()) and all(sha(Path(p))==h for p,h in m['dependencies'].items())
for label,v in m['stages'].items():
 assert v['actualExit']==(4 if label=='pmd' else 0) and not v['timedOut']
 for stream in ['stdout','stderr']:assert sha(pp.parent/(label+'.'+stream))==v[stream+'Sha256']
assert m['processingErrors']==[] and m['checkstyleFindings']==0;expected={'UseProperClassLoader':['906'],'UseConcurrentHashMap':['549','561','775','820','837'],'AvoidUsingVolatile':['568'],'CloseResource':['451'],'DoNotUseThreads':['451','456','461','479','480']};assert len(m['rawFindings'])==13 and sorted((x['rule'],x['line']) for x in m['rawFindings'])==sorted((rule,line) for rule,lines in expected.items() for line in lines);source=r/m['apiTestSources'][0];s=source.read_text();classified=[]
for x in m['rawFindings']:
 line=s.splitlines()[int(x['line'])-1];rule=x['rule']
 if rule=='UseProperClassLoader':
  assert 'type.getClassLoader()' in s;reason='Standalone hardcoded JDK Connection/PreparedStatement/ResultSet proxies use defining interface loader; no class-name discovery/private reflection/backend or forbidden type substitute.'
 elif rule=='UseConcurrentHashMap':
  if x['line']=='561':assert line.strip()=='final Map<Stage, Map<Site, Throwable>> additionalFailures =' and s.splitlines()[561].strip()=='new java.util.EnumMap<>(Stage.class);'
  else:assert 'new HashMap<>()' in line
  reason='Each case and worker owns distinct Fixture/statement bindings/update count and row maps. Controls fixed before invoking; parent reads after Future completion, no concurrently shared map.'
 elif rule=='AvoidUsingVolatile':
  assert 'volatile String observedStoredHash' in line;reason='Immutable scalar fixture observation, no compound update; Future completion provides joining, volatile conservative publication not an atomicity substitute.'
 else:
  assert rule in ['CloseResource','DoNotUseThreads'] and 'assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));' in s;reason='Standalone two-task JUnit, Future.get5/stop-await10assert/Timeout30 and no fixture close until termination confirmed; failure cannot pass. No actual server/J2EE execution.'
 classified.append(dict(**x,sourceLine=line,sourceSha256=sha(source),disposition='NOT_APPLICABLE_EXACT_JDK_PROXY_OR_CONFINED_FIXTURE',reason=reason))
ap=r/m['exactMainStatic']['path'];a=ld(ap);cp=r/m['exactMainCompile']['path'];c=ld(cp);assert sha(ap)==m['exactMainStatic']['sha256'] and sha(cp)==m['exactMainCompile']['sha256'] and a['actualExit']==c['actualExit']==0 and a['staticApplicable']==a['unclassified']==a['processingErrors']==0 and a['rootNullAwayFresh'];assert all(a['inputHashes'][p]==m['inputHashes'][p] for p in m['inputHashes'] if p not in m['apiTestSources']);assert c['dependencies']==m['dependencies'];policy.compiler_element();proofp=b/'evidence/PG34360-login-fatal3-source-inverse-v1/manifest.json';proof=ld(proofp);oraclep=b/'evidence/PG34364-login-fatal3-oracle-before-unit-v1/manifest.json';oracle=ld(oraclep);assert proof['actualExit']==oracle['actualExit']==0 and proof['original22InverseFormattedExact'] and oracle['existing22PrefixUnchanged'] and oracle['syntheticCasesUnchanged']==67 and oracle['sourceAfterSha256']==sha(source);work=r.parent/'pgpt-runs/PG379/pg34366-login-fatal3-v2'
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:
 for n in m[key]:policy.relative_name(n)
 assert {n:sha(work/folder/n) for n in m[key]}==m[key]
assert len(m['physicalClassHashes'])==210;jp=r/a['jdkExceptionStaticReference']['path'];j=ld(jp);assert sha(jp)==a['jdkExceptionStaticReference']['sha256'];jdk=r.parent/'toolchain/jdk-25.0.4';assert sha(jdk/'lib/modules')==j['jdkModulesSha256'] and sha(jdk/'bin/javap')==j['jdkJavapSha256']
for p,h in j['staticArtifacts'].items():
 assert p.startswith('evidence/01_PT/007_NK-AUT-001/evidence/PG20876-admin-prelude-jdk-static-review-v1/') and Path(p).suffix in ['.stdout','.stderr','.json'];assert sha(r/p)==h
providers={}
for p in m['dependencies']:
 with zipfile.ZipFile(p) as z:providers[p]=[n for n in z.namelist() if n=='META-INF/services/java.sql.Driver']
for folder in ['component','test-classes']:providers[str(work/folder)]=[str(work/folder/'META-INF/services/java.sql.Driver')] if (work/folder/'META-INF/services/java.sql.Driver').exists() else []
assert all(not x for x in providers.values());v=dict(actualExit=0,inputHashes=m['inputHashes'],dependencies=m['dependencies'],prepare=ref(pp),expectedTests=25,newDefinitions=3,necessaryPriorDefinitions=22,syntheticCases=67,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugsApplicable=0,rootNullAwayFresh=False,rootNullAwayReusedExactCurrentMain=True,originalMainStatic=ref(ap),classified=classified,original22Inverse=ref(proofp),declaredTargets=a['declaredTargets'],manualSuppressionAdded=False,jdkExceptionStaticReference=ref(jp),sameJdkModuleAndJavapBytes=True,currentClasspathSqlDriverDescriptors=providers,currentUnitInitMustBindAfterRun=True,sdkSyscallActivityUnknown=True,actualBackendOrHeldActions=0,applicationTestsExecuted=0,newAcceptance=0,whole451Accepted=False);out.mkdir();(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=25,rawStatic=13,initialRaw14Applicable1AndPreUnitOracleCorrectionPreserved=True,applicable=0,mainRebuilt=False,original22InverseExact=True,syntheticCases=67)))
