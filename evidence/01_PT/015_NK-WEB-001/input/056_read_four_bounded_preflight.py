"""Original four whole facade fixtures: exact bounded-owner edits and established in-memory graph."""
from pathlib import Path
import hashlib,json,datetime,re,zipfile,subprocess
R=Path.cwd();B=R/'evidence/01_PT/015_NK-WEB-001';RUNS=R.parent/'pgpt-runs/PG379';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cfg=load(B/'input/054_read_four_bounded_scope.json');O=R/cfg['preflightManifest'];assert not O.parent.exists()
p=load(RUNS/cfg['compileSlot']/'manifest.json');s=load(RUNS/cfg['staticSlot']/'manifest.json');assert p['actualExit']==0 and p['inputHashes']==s['inputHashes']
for path,h in p['inputHashes'].items():assert sha(R/path)==h
normal=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';nm=load(normal);assert sha(normal)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27' and nm['source']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
# Inverse exact-token proof preserves all literals, error/interrupt branches, concurrency counts and body ownership.
tok=lambda v:''.join(re.findall(r'"(?:\\.|[^"\\])*"|\S',v));checks=[];new_methods=0
for path,cls in cfg['testClasses'].items():
 text=(R/path).read_text();old=(R/cfg['beforeDirectory']/Path(path).name).read_text();a=tok(text);oldtoken=tok(old);is_scenario=Path(path).name=='ScenarioWireClientTest.java'
 if not is_scenario:
  atom='importjava.util.concurrent.TimeUnit;';assert a.count(atom)==1;a=a.replace(atom,'',1)
  atom='for(varfuture:futures)future.get(10,TimeUnit.SECONDS);';assert a.count(atom)==1;a=a.replace(atom,'for(varfuture:futures)future.get();',1)
 atom='varpool=Executors.newFixedThreadPool(8);try{';assert a.count(atom)==1;a=a.replace(atom,'try(varpool=Executors.newFixedThreadPool(8)){',1)
 atom='}finally{pool.shutdownNow();assertTrue(pool.awaitTermination(10,TimeUnit.SECONDS));}';assert a.count(atom)==1;a=a.replace(atom,'}',1)
 assert a==oldtoken
 methods=re.findall(r'@Test\s+void\s+(\w+)\s*\(',text);assert len(methods)==8;new_methods+=len(methods)
 assert not any(x in text for x in ['java.net.','java.sql.','java.nio.file.','Files.','ProcessBuilder','DriverManager','Class.forName','ServiceLoader','@TempDir','@Before','@After','setAccessible','TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'])
 assert 'ArrayList<Future<?>>' in text and 'pool.submit(' in text
 if is_scenario:assert 'task.get(10, TimeUnit.SECONDS)' in text and 'release.await(5, TimeUnit.SECONDS)' in text
 checks.append(dict(path=path,currentSha256=sha(R/path),beforeSha256=sha(R/cfg['beforeDirectory']/Path(path).name),originalWholeMethods=8,otherTokensAndAllOraclesUnchanged=True,fixedPoolsNowFinite=1,rawFutureGetsChanged=0 if is_scenario else 1))
assert new_methods==32 and len(checks)==4
raw=s['reports']['pmd']['items'];assert len(raw)==26 and not s['reports']['pmd']['processingErrors'] and not s['reports']['checkstyle']['items'] and not s['reports']['checkstyle']['processingErrors']
classifications=[]
for x in raw:
 assert x['rule'] in ['DoNotUseThreads','CloseResource'] and x['class'] in {Path(p).stem for p in cfg['testClasses']}
 reason=('Explicit executor owner finally always requests shutdownNow and observes actual awaitTermination10s; using AutoCloseable.close/TWR instead would introduce the unbounded join being fixed. Postcondition is asserted, not assumed.' if x['rule']=='CloseResource' else 'JUnit thread/interrupt/concurrency fixture outside J2EE; finite Future and executor waits. Scenario existing finite release5s and explicit interrupt restoration retained. Own worker/task only; no service threads.')
 classifications.append(dict(finding=x,applicableViolation=False,reason=reason))
for path,h in p['dependencies'].items():assert sha(Path(path))==h
assert len(cfg['sdkDependencies'])==1
for path in cfg['sdkDependencies']:
 with zipfile.ZipFile(path) as z:
  assert not set(z.namelist()).intersection({'META-INF/services/java.sql.Driver','META-INF/services/javax.annotation.processing.Processor','META-INF/services/com.sun.source.util.Plugin','META-INF/services/jakarta.jms.ConnectionFactory'})
# Reuse the already source-reviewed/current ordinary registry/request client graph; no product replay.
core=R/'evidence/01_PT/005_NK-MSG-001/evidence/PG24238-jms-memory-bounded-preflight-v1/manifest.json';co=load(core);assert co['actualExit']==0 and co['noNewFixtureOrMethodExtraction']
for path,h in co['inputHashes'].items():
 if '/src/main/' in path:assert sha(R/path)==h==nm['begin']['inputHashes'][path]
helpers=['ProtectedReadWireClient','ProtectedReadWireException','ScenarioWireException','JmsRequestReplyClient','JmsRequestReplyException','ReplyCorrelationRegistry','PendingReply']
mainbase='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/';helperpins={}
for name in helpers:
 path=mainbase+name+'.java';text=(R/path).read_text();helperpins[path]=sha(R/path);assert helperpins[path]==nm['begin']['inputHashes'][path]
 assert not any(v in text for v in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','java.net.','java.sql.','DriverManager','Files.','ProcessBuilder','ServiceLoader','Class.forName'])
# Current complete helper and target Source review: API consists only of declared codec/data/JDK callbacks.
assert 'MessageDigest.isEqual' in (R/(mainbase+'ProtectedReadWireClient.java')).read_text()
index_path=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG23360-base59-named-proof-supplement-v1/current-normal-physical-index.json';index=load(index_path);physical={n:v['sha256'] for n,v in index.items() if v['path'] in cfg['mainPaths']};assert physical==cfg['currentMainPhysical'] and len(physical)==5
for path in cfg['mainPaths']:assert sha(R/path)==nm['begin']['inputHashes'][path]
proofs=[]
for name in ['PG15632-protected-facades-twenty-four-post-v1','PG15648-lgs-reply-fourteen-post-v1']:
 path=R/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'/name/'manifest.json';v=load(path);assert v['actualExit']==0 and not any(v[k] for k in ['actualAuthenticationOrSessionIssued','actualBoundSockets','actualBrokerOrListenerStarted','actualCredentialValuesUsed','actualDatabaseActions','actualFilesOpenedByProduct','actualJmsConnectionsCreated','actualJmsContextsCreated','actualNetworkActions','actualPrivateFilesOpened','actualSecretKeysLoaded','actualServiceActions','actualVmActions'])
 proofs.append(dict(path=str(path.relative_to(R)),sha256=sha(path),usedFor='prior full fixture graph/control review only, not old execution or counters reused into this run'))
O.parent.mkdir();v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),inputHashes=p['inputHashes'],compileManifestSha256=sha(RUNS/cfg['compileSlot']/'manifest.json'),staticManifestSha256=sha(RUNS/cfg['staticSlot']/'manifest.json'),normalManifestSha256=sha(normal),normalPositiveMainIndex=dict(path=str(index_path.relative_to(R)),sha256=sha(index_path)),corePreflight=dict(path=str(core.relative_to(R)),sha256=sha(core)),originalTestEdits=checks,helperSourceHashes=helperpins,originalGraphProofReferences=proofs,originalWholeMethods=32,allOriginalOtherTokensAndOraclesPreserved=True,noOriginalMethodExtractionOrSubstitute=True,rawFutureGetSitesFixed=3,fixedPoolOwnersBounded=4,scenarioExistingBoundedOtherPoolRetained=True,declaredSdkJmsApiOnly=True,cryptoApi='MessageDigest.isEqual public synthetic context comparison only',actualKeysOrCredentialOperations=False,pmdRawFindings=26,applicableStaticViolations=0,checkstyleFindings=0,processingErrors=0,staticClassifications=classifications,physical=physical,targetNaturalZeroBranchSources=4,strictNonemptyBranchCounter100Expected=False,noActualBackendOrRootOrVmOrNativeOperations=True,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None,toolSha256=sha(Path(__file__)))
O.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,whole32=32,staticApplicable=0,targetPhysical=5,naturalBranch0=True,manifestSha256=sha(O))))
