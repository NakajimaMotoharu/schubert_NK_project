"""Seven complete original pure display fixtures and exact executor-owner changes; no product execution."""
from pathlib import Path
import hashlib,json,datetime,re,subprocess,zipfile
R=Path.cwd();B=R/'evidence/01_PT/015_NK-WEB-001';RUNS=R.parent/'pgpt-runs/PG379';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cfg=load(B/'input/062_pure_view_seven_scope.json');O=R/cfg['preflightManifest'];assert not O.parent.exists();pm=load(RUNS/cfg['compileSlot']/'manifest.json');sm=load(RUNS/cfg['staticSlot']/'manifest.json');assert pm['actualExit']==0 and pm['inputHashes']==sm['inputHashes']
for path,h in pm['inputHashes'].items():assert sha(R/path)==h
before=load(R/cfg['beforeMetadataPath']);assert before['source']==cfg['beforeGitCommit'] and len(before['originalWholeTestSources'])==7
snapshots={r['path']:r for r in before['originalWholeTestSources']};tok=lambda x:''.join(re.findall(r'"(?:\\.|[^"\\])*"|\S',x));cases=[];sourcechecks=[]
for path,cls in cfg['testClasses'].items():
 row=snapshots[path];text=(R/path).read_text();original=subprocess.check_output(['git','show',cfg['beforeGitCommit']+':'+path]);assert hashlib.sha256(original).hexdigest()==row['sourceSha256'];assert subprocess.check_output(['git','rev-parse',cfg['beforeGitCommit']+':'+path],text=True).strip()==row['gitBlob']
 var=row['poolVariable'];a=tok(text);needle='var'+var+'=Executors.newFixedThreadPool(8);try{';assert a.count(needle)==1;a=a.replace(needle,'try(var'+var+'=Executors.newFixedThreadPool(8)){',1)
 needle='}finally{'+var+'.shutdownNow();assertTrue('+var+'.awaitTermination(10,TimeUnit.SECONDS));}';assert a.count(needle)==1;a=a.replace(needle,'}',1);assert a==tok(original.decode())
 methods=re.findall(cfg['declarationRegex'],text);assert len(methods)==(12 if Path(path).stem in ['ScenarioHierarchyViewModelTest','ScenarioDetailViewModelTest'] else 8)
 assert len(methods)==len(set(methods));cases.extend(cls+'#'+m+'()' for m in methods)
 assert not any(n in text for n in ['java.sql.','java.net.http.','java.net.Socket','openConnection(','ProcessBuilder','DriverManager','@TempDir','@Before','@After','Files.','Class.forName','ServiceLoader','TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'])
 assert 'StringTemplateResolver' in text and 'SpringTemplateEngine' in text and 'Jsoup.parse' in text and 'TimeUnit.SECONDS' in text
 # Any displayed Path/FILE or fake SessionPrincipal is only a value, never a resolved resource/account.
 assert 'new SessionPrincipal' in text or Path(path).name=='PageViewModelTest.java'
 sourcechecks.append(dict(path=path,currentSha256=sha(R/path),beforeSha256=row['sourceSha256'],methods=len(methods),otherTokensAndAllOraclesUnchanged=True,boundedFixedPoolOwner=1,annotationsPreserved=True,onlyMemoryTemplateAndValueCallbacks=True))
assert len(cases)==len(set(cases))==64
page=next(p for p in cfg['testClasses'] if p.endswith('/PageViewModelTest.java'));assert (R/page).read_text().count('@DisplayName(')==8 and len(re.findall(cfg['declarationRegex'],(R/page).read_text()))==8
assert len(sm['reports']['pmd']['items'])==35 and not sm['reports']['pmd']['processingErrors'] and not sm['reports']['checkstyle']['items'] and not sm['reports']['checkstyle']['processingErrors']
classifications=[]
for item in sm['reports']['pmd']['items']:
 assert item['class'] in {Path(p).stem for p in cfg['testClasses']} and item['rule'] in ['CloseResource','DoNotUseThreads']
 reason=('Owned executor finally always requests shutdownNow and asserts actual awaitTermination10s; TWR close would reintroduce unbounded failure cleanup. Existing Future10s bounds unchanged.' if item['rule']=='CloseResource' else 'JUnit-only explicit private executor, submit/shutdown/finite actual termination, outside J2EE; pure value projections only inside task, no service threads.')
 classifications.append(dict(finding=item,applicableViolation=False,reason=reason))
normal=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';nm=load(normal);assert nm['source']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
for path in cfg['mainPaths']:
 text=(R/path).read_text();assert sha(R/path)==nm['begin']['inputHashes'][path]
 assert not any(n in text for n in ['java.sql.','java.net.http.','java.net.Socket','openConnection(','Files.','ProcessBuilder','DriverManager','TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','ServiceLoader'])
helper='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/SessionPrincipal.java';assert sha(R/helper)==nm['begin']['inputHashes'][helper];assert 'implements java.security.Principal' in (R/helper).read_text()
# SDK source graph is the existing memory StringTemplateResolver + SpringEL closed getter
# evaluation and Jsoup.parse(String). UriUtils is pure percent encoding, not HTTP or URI resolution.
assert len(cfg['sdkDependencies'])==13;sdk=[]
source=load(R/cfg['sdkWitness']['path']);assert sha(R/cfg['sdkWitness']['path'])==cfg['sdkWitness']['sha256']
for path,h in cfg['sdkDependencies'].items():
 assert source['begin']['dependencyHashes'][path]==h==sha(Path(path))
 with zipfile.ZipFile(path) as z:
  names=set(z.namelist());assert not names.intersection({'META-INF/services/java.sql.Driver','META-INF/services/javax.annotation.processing.Processor','META-INF/services/com.sun.source.util.Plugin'})
  manifest=z.read('META-INF/MANIFEST.MF').decode() if 'META-INF/MANIFEST.MF' in names else '';assert not re.search(r'^Class-Path:',manifest,re.M)
 sdk.append(dict(path=path,sha256=h,externalCompilerClasspathOrSqlDriver=False))
for path,h in pm['dependencies'].items():assert sha(Path(path))==h
proofrefs=[]
for ref in cfg['originalPublicProofs']:
 v=load(R/ref['path']);assert sha(R/ref['path'])==ref['sha256'] and v['actualExit']==0 and v['rootMainInvoked'] is False
 assert all(type(v[k]) is int and v[k]==0 for k in ['actualDatabaseActions','actualNetworkActions','actualServiceActions','actualVmActions'])
 proofrefs.append(dict(**ref,usage='historical full fixture/source review context only, old execution not transferred'))
index_path=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG23360-base59-named-proof-supplement-v1/current-normal-physical-index.json';index=load(index_path);physical={n:v['sha256'] for n,v in index.items() if v['path'] in cfg['mainPaths']};assert len(physical)==24 and physical==cfg['currentMainPhysical']
O.parent.mkdir();v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),inputHashes=pm['inputHashes'],compileManifestSha256=sha(RUNS/cfg['compileSlot']/'manifest.json'),staticManifestSha256=sha(RUNS/cfg['staticSlot']/'manifest.json'),normalManifestSha256=sha(normal),normalPositiveMainIndex=dict(path=str(index_path.relative_to(R)),sha256=sha(index_path)),beforeGitCommit=cfg['beforeGitCommit'],wholeOriginalTestSources=sourcechecks,originalWholeMethods=64,wholeTestClasses=7,sourcePrograms=11,physicalClasses=24,allOriginalOtherTokensAndOraclesPreserved=True,sevenFixedPoolOwnersBounded=True,pageEightDisplayNamesAndMethodsRetained=True,noFixtureOrMethodExtraction=True,noSourceDataDuplicatedInEvidence=True,pmdRawFindings=35,applicableStaticViolations=0,checkstyleFindings=0,processingErrors=0,staticClassifications=classifications,suppressionAdded=False,sdkReview=sdk,sdkDiscoveryBeforeUnit='PG24373: UriUtils spring-web exact13th dependency; originalformat reused with unchangedTest hashes, freshcompile24374/static24376; no runtime before review',historicalFixtureReviewRefs=proofrefs,helperSourceHashes={helper:sha(R/helper)},physical=physical,actualTemplateFileBrowserHttpDbJmsAuthKeyRootVmNativeActions=False,onlyMemoryStringTemplateAndJsoupValues=True,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None,toolSha256=sha(Path(__file__)))
O.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,whole64=64,physical=24,sdk=13,applicableStatic=0,manifestSha256=sha(O))))
