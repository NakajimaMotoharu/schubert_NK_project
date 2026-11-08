"""Original whole six form fixtures: value/DTO/codec contracts and exact bounded executor edits."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess
R=Path.cwd();B=R/'evidence/01_PT/015_NK-WEB-001';RUNS=R.parent/'pgpt-runs/PG379';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cfg=load(B/'input/067_web_six_form_scope.json');O=R/cfg['preflightManifest'];assert not O.parent.exists();pm=load(RUNS/cfg['compileSlot']/'manifest.json');sm=load(RUNS/cfg['staticSlot']/'manifest.json');assert pm['actualExit']==0 and pm['inputHashes']==sm['inputHashes']
for path,h in pm['inputHashes'].items():assert sha(R/path)==h
before=load(R/cfg['beforeMetadataPath']);rows={v['path']:v for v in before['originalWholeTestSources']};assert len(rows)==6 and before['source']==cfg['beforeGitCommit'];checks=[];cases=[]
for path,cls in cfg['testClasses'].items():
 row=rows[path];original=subprocess.check_output(['git','show',cfg['beforeGitCommit']+':'+path]);assert hashlib.sha256(original).hexdigest()==row['sourceSha256'];text=(R/path).read_text();var=row['poolVariable']
 a='var '+var+' = Executors.newFixedThreadPool(8);\n    try {';b='} finally {\n      '+var+'.shutdownNow();\n      assertTrue('+var+'.awaitTermination(10, TimeUnit.SECONDS));\n    }';assert text.count(a)==text.count(b)==1;inverse=text.replace(a,'try (var '+var+' = Executors.newFixedThreadPool(8)) {',1).replace(b,'}',1)
 if row['invokeAllBoundAdded']:
  a='for (var future : executor.invokeAll(tasks, 30, TimeUnit.SECONDS))\n        future.get(30, TimeUnit.SECONDS);';assert inverse.count(a)==1;inverse=inverse.replace(a,'for (var future : executor.invokeAll(tasks)) future.get(30, TimeUnit.SECONDS);',1)
 assert inverse.encode()==original
 methods=re.findall(cfg['declarationRegex'],text);assert len(methods)==(16 if Path(path).name=='UserMutationFormTest.java' else 8);cases.extend(cls+'#'+m+'()' for m in methods)
 assert not any(n in text for n in ['java.sql.','java.net.http.','java.net.Socket','openConnection(','java.nio.file.','Files.','ProcessBuilder','DriverManager','ServiceLoader','Class.forName','@Before','@After','@TempDir','TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'])
 assert 'PayloadCodec' in text or Path(path).name in ['ScenarioSearchFormTest.java','LogSearchFormTest.java']
 checks.append(dict(path=path,currentSha256=sha(R/path),beforeSha256=row['sourceSha256'],rawExactInverse=True,methods=len(methods),fixedPoolOwnerBounded=1,invokeAllThirtySecondsAdded=row['invokeAllBoundAdded'],allOtherStringBytesAndOriginalFutureBoundsUnchanged=True))
assert len(cases)==len(set(cases))==56
assert len(sm['reports']['pmd']['items'])==34 and not sm['reports']['pmd']['processingErrors'] and not sm['reports']['checkstyle']['items'] and not sm['reports']['checkstyle']['processingErrors']
classifications=[]
for finding in sm['reports']['pmd']['items']:
 assert finding['rule'] in ['CloseResource','DoNotUseThreads'] and finding['class'] in {Path(p).stem for p in cfg['testClasses']}
 if finding['rule']=='CloseResource' and finding.get('variable')=='f':
  assert finding['class']=='UserMutationFormTest' and finding['method']=='bind' and int(finding['beginline']) in [68,72,76,80]
  reason='Ownership is transferred into the existing AutoCloseable Form record through f::close, with exact owner retained and close() invoking closer.run(). Callers use TWR or the explicit terminal-close oracle; not an unclosed borrowed resource.'
 elif finding['rule']=='CloseResource':
  assert finding.get('variable') in ['pool','executor'];reason='Exact owned fixed executor is shut down in finally and its actual awaitTermination10s is asserted. Using TWR close would reintroduce the unbounded join being fixed.'
 else:reason='JUnit-only owned task/executor and finite invokeAll/get/termination, outside J2EE; body binds synthetic DTO/value objects and independent wire arrays, never sends to a backend.'
 classifications.append(dict(finding=finding,applicableViolation=False,reason=reason))
mutation=next(p for p in cfg['testClasses'] if p.endswith('/UserMutationFormTest.java'));source=(R/mutation).read_text();assert source.count('yield new Form(f, f::close, f::isValid, f::getIssues, f::displayValues, f::toRequest);')==4 and 'closer.run();' in source and 'executor.invokeAll(tasks, 30, TimeUnit.SECONDS)' in source
normal=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';nm=load(normal);assert nm['source']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
for path in cfg['mainPaths']:
 text=(R/path).read_text();assert sha(R/path)==nm['begin']['inputHashes'][path]
 assert not any(n in text for n in ['java.sql.','java.net.','Files.','ProcessBuilder','DriverManager','ServiceLoader','Class.forName','TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','java.security.','javax.crypto.'])
 # All form implementation imports are declared value/codec/JDK/nullability, not a service adapter.
 imports=re.findall(r'^import ([^;]+);',text,re.M);assert all(n.startswith(('java.','dev.codex.schubert.nk.protocol.','org.jspecify.')) for n in imports)
for path,h in pm['dependencies'].items():assert sha(Path(path))==h
assert cfg['sdkDependencies']=={}
interface=cfg['noCodeInterface'];metadata=load(R/'evidence/01_PT/018_NK-OPS-001/evidence/PG23972-current-main-method-delta42-v1/class-method-inventory.json');row=next(v for v in metadata if v['sourcePath']==interface);assert row['sourceSha256']==sha(R/interface)==nm['begin']['inputHashes'][interface];assert len(row['structure']['methods'])==5 and all(not v['hasCode'] for v in row['structure']['methods']);assert 'public sealed interface UserChangeForm extends AutoCloseable' in (R/interface).read_text()
index_path=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG23360-base59-named-proof-supplement-v1/current-normal-physical-index.json';index=load(index_path);physical={n:v['sha256'] for n,v in index.items() if v['path'] in cfg['mainPaths']};assert len(physical)==16 and physical==cfg['currentMainPhysical']
# Complete current test/Main source is the eligibility basis. Existing specs are oracle/context
# references, not old runtime/code counters copied into this run.
refs=[]
for path in ['evidence/01_PT/018_NK-OPS-001/2623_Web三form元whole二十四件_単体テスト仕様書.md','evidence/01_PT/018_NK-OPS-001/2627_UserCreateForm元whole八件_単体テスト仕様書.md','evidence/01_PT/016_NK-WEB-002/065_NK-WEB-002_質問要求入力単体テスト仕様書.md','evidence/01_PT/016_NK-WEB-002/069_NK-WEB-002_User更新入力単体テスト仕様書.md']:
 refs.append(dict(path=path,sha256=sha(R/path)))
O.parent.mkdir();v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),inputHashes=pm['inputHashes'],compileManifestSha256=sha(RUNS/cfg['compileSlot']/'manifest.json'),staticManifestSha256=sha(RUNS/cfg['staticSlot']/'manifest.json'),normalManifestSha256=sha(normal),normalPositiveMainIndex=dict(path=str(index_path.relative_to(R)),sha256=sha(index_path)),beforeGitCommit=cfg['beforeGitCommit'],sourceEditReviews=checks,originalWholeMethods=56,wholeTestClasses=6,sourcePrograms=12,physicalClasses=16,allOriginalOtherBytesAndOraclesPreserved=True,sixFixedPoolOwnersBounded=True,singleInvokeAllBoundSeconds=30,originalFutureGet5TenThirtySecondsUnchanged=True,noFixtureOrMethodExtraction=True,noSyntheticPasswordTokenOrBodyDuplicatedInEvidence=True,noActualAccountRoleStatusPasswordUpdateOrAuthentication=True,onlySyntheticValueDtoAndCodecBodies=True,actualDbJmsHttpRootVmNativeKeyActions=False,noExtraSdkArtifactsRequired=True,pmdRawFindings=34,applicableStaticViolations=0,checkstyleFindings=0,processingErrors=0,staticClassifications=classifications,suppressionAdded=False,noCodeInterface=dict(path=interface,sourceSha256=row['sourceSha256'],physicalSha256=row['classSha256'],abstractMethods=5,codeMethods=0,coverageRate=None),existingSpecRefs=refs,physical=physical,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None,toolSha256=sha(Path(__file__)))
O.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,whole56=56,codePhysical=16,noCodeInterfaceAbstractMethods=5,applicableStatic=0,manifestSha256=sha(O))))
