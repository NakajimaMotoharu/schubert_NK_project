"""Admit current Admin14 fixture10 concrete sites plus exact Root/Main/JDK lineage."""
from pathlib import Path
import hashlib,json,zipfile
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pp=b/'evidence/PG34276-admin-fatal3-prepare-v2/manifest.json';m=ld(pp);out=b/'evidence/PG34278-admin-fatal3-preflight-v1';assert not out.exists();assert m['actualExit']==0 and m['expectedTests']==14 and m['newDefinitions']==3 and m['necessaryPriorDefinitions']==11 and not m['MainCompilationRepeated'];assert all(sha(r/p)==h for p,h in m['inputHashes'].items()) and all(sha(Path(p))==h for p,h in m['dependencies'].items())
for label,v in m['stages'].items():
 assert v['actualExit']==(4 if label=='pmd' else 0) and not v['timedOut']
 for stream in ['stdout','stderr']:assert sha(pp.parent/(label+'.'+stream))==v[stream+'Sha256']
assert m['processingErrors']==[] and m['checkstyleFindings']==0;expected={'UseProperClassLoader':['90'],'UseConcurrentHashMap':['105','111','168'],'CloseResource':['302','485'],'DoNotUseThreads':['485','491','508','509']};assert len(m['rawFindings'])==10 and sorted((x['rule'],x['line']) for x in m['rawFindings'])==sorted((rule,line) for rule,lines in expected.items() for line in lines);source=r/m['apiTestSources'][0];s=source.read_text();classified=[]
for x in m['rawFindings']:
 line=s.splitlines()[int(x['line'])-1];rule=x['rule']
 if rule=='UseProperClassLoader':
  assert 'type.getClassLoader()' in s;reason='Standalone hardcoded JDK Connection/PreparedStatement/ResultSet proxies use defining interface loader; no class-name discovery/private reflection/backend or forbidden type substitute.'
 elif rule=='UseConcurrentHashMap':
  assert 'final Map<String, Throwable> injectedFailures = new HashMap<>();' in s;reason='Each negative case and worker owns a fresh Fixture/statement binding/fault map. Controls configured before same-thread invocation, no service/global/shared mutable map. Parent reads after Future completion.'
 elif rule=='CloseResource' and x['line']=='302':
  assert line.strip()=='Connection c = f.connection();';reason='Pure memory proxy owns no backend/socket/handle. close/commit/rollback are forbidden assertions to prove borrowed caller TX; no actual connection needs release.'
 else:
  assert rule in ['CloseResource','DoNotUseThreads'] and 'assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));' in s;reason='Standalone JUnit not J2EE, original get5 plus finally shutdownNow/await10assert/Timeout30. Failed termination cannot pass, each worker owns resources.'
 classified.append(dict(**x,sourceLine=line,sourceSha256=sha(source),disposition='NOT_APPLICABLE_EXACT_JDK_PROXY_OR_CONFINED_FIXTURE',reason=reason))
ap=r/m['exactMainStatic']['path'];a=ld(ap);cp=r/m['exactMainCompile']['path'];c=ld(cp);assert sha(ap)==m['exactMainStatic']['sha256'] and sha(cp)==m['exactMainCompile']['sha256'] and a['actualExit']==c['actualExit']==0 and a['staticApplicable']==a['unclassified']==a['processingErrors']==0 and a['rootNullAwayFresh'];assert all(a['inputHashes'][p]==m['inputHashes'][p] for p in m['inputHashes'] if p not in m['apiTestSources']);assert c['dependencies']==m['dependencies'];policy.compiler_element();proofp=b/'evidence/PG34274-admin-fatal3-source-binding-v2/manifest.json';proof=ld(proofp);assert proof['actualExit']==0 and proof['old11InverseFormattedExact'] and proof['allMainAndPomsUnchanged'] and proof['currentSyntheticCases']==60;work=r.parent/'pgpt-runs/PG379/pg34276-admin-fatal3-v2'
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:
 for n in m[key]:policy.relative_name(n)
 assert {n:sha(work/folder/n) for n in m[key]}==m[key]
assert len(m['physicalClassHashes'])==195;jp=r/a['jdkExceptionStaticReference']['path'];j=ld(jp);assert sha(jp)==a['jdkExceptionStaticReference']['sha256'];jdk=r.parent/'toolchain/jdk-25.0.4';assert sha(jdk/'lib/modules')==j['jdkModulesSha256'] and sha(jdk/'bin/javap')==j['jdkJavapSha256']
for p,h in j['staticArtifacts'].items():
 assert p.startswith('evidence/01_PT/007_NK-AUT-001/evidence/PG20876-admin-prelude-jdk-static-review-v1/') and Path(p).suffix in ['.stdout','.stderr','.json'];assert sha(r/p)==h
providers={}
for p in m['dependencies']:
 with zipfile.ZipFile(p) as z:providers[p]=[n for n in z.namelist() if n=='META-INF/services/java.sql.Driver']
for folder in ['component','test-classes']:providers[str(work/folder)]=[str(work/folder/'META-INF/services/java.sql.Driver')] if (work/folder/'META-INF/services/java.sql.Driver').exists() else []
assert all(not x for x in providers.values());v=dict(actualExit=0,inputHashes=m['inputHashes'],dependencies=m['dependencies'],prepare=ref(pp),expectedTests=14,newDefinitions=3,necessaryPriorDefinitions=11,currentSyntheticFaultCases=60,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugsApplicable=0,rootNullAwayFresh=False,rootNullAwayReusedExactCurrentMain=True,originalMainStatic=ref(ap),classified=classified,original11Inverse=ref(proofp),declaredTargets=a['declaredTargets'],manualSuppressionAdded=False,jdkExceptionStaticReference=ref(jp),sameJdkModuleAndJavapBytes=True,currentClasspathSqlDriverDescriptors=providers,currentUnitInitMustBindAfterRun=True,sdkSyscallActivityUnknown=True,actualBackendOrHeldActions=0,applicationTestsExecuted=0,newAcceptance=0,whole451Accepted=False);out.mkdir();(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');ledger=r/'documents/900_OTHER/910_台帳/915_障害表.md';ledger.write_text(ledger.read_text()+'\n2026-11-15 BUG3046数値追記訂正: immutable PG34272 manifest rawFindingsは実12件（適用2）、最終PG34276は10件（適用/未分類0）。初記述/3720の13は文章の数え誤りとして履歴保持し、今後はmanifest実数12→10を正とする。仕様期待/試験件数14/60条件/費用変更0、App未実行段階。\n');print(json.dumps(dict(actualExit=0,tests=14,rawStatic=10,initialRaw12Applicable2Preserved=True,applicable=0,mainRebuilt=False,old11InverseExact=True,syntheticCases=60)))
