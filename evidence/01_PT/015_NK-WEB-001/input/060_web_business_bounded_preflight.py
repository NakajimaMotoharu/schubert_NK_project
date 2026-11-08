"""Original whole business fixture: synthetic in-memory wire graph, exact single-owner edit."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess,zipfile
R=Path.cwd();B=R/'evidence/01_PT/015_NK-WEB-001';RUNS=R.parent/'pgpt-runs/PG379';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cfg=load(B/'input/058_web_business_bounded_scope.json');O=R/cfg['preflightManifest'];assert not O.parent.exists();p=load(RUNS/cfg['compileSlot']/'manifest.json');s=load(RUNS/cfg['staticSlot']/'manifest.json');assert p['actualExit']==0 and p['inputHashes']==s['inputHashes']
for n,h in p['inputHashes'].items():assert sha(R/n)==h
path=next(iter(cfg['testClasses']));oldbytes=subprocess.check_output(['git','show',cfg['beforeGitCommit']+':'+path]);assert hashlib.sha256(oldbytes).hexdigest()==cfg['beforeTestSha256'];old=oldbytes.decode();text=(R/path).read_text();tok=lambda x:''.join(re.findall(r'"(?:\\.|[^"\\])*"|\S',x));a=tok(text)
needle='varpool=Executors.newFixedThreadPool(8);try{';assert a.count(needle)==1;a=a.replace(needle,'try(varpool=Executors.newFixedThreadPool(8)){',1)
needle='}finally{pool.shutdownNow();assertTrue(pool.awaitTermination(10,TimeUnit.SECONDS));}';assert a.count(needle)==1;a=a.replace(needle,'}',1);assert a==tok(old)
assert len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==12 and 'for (int n = 0; n < 180; n++)' in text and 'task.get(10, TimeUnit.SECONDS)' in text
assert not any(v in text for v in ['java.net.','java.sql.','java.nio.file.','Files.','@Before','@After','@TempDir','ProcessBuilder','DriverManager','ServiceLoader','Class.forName','setAccessible','createConnection','createContext','TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'])
assert 'final JmsRequestSender sender =' in text and 'wire.onReply(' in text
assert len(s['reports']['pmd']['items'])==5 and not s['reports']['pmd']['processingErrors'] and not s['reports']['checkstyle']['items'] and not s['reports']['checkstyle']['processingErrors']
classifications=[]
for row in s['reports']['pmd']['items']:
 assert row['class']=='WebBusinessWireClientsTest' and row['rule'] in ['CloseResource','DoNotUseThreads']
 reason=('Explicit pool finally shutdownNow plus actual awaitTermination10s asserted; TWR AutoCloseable.close would reintroduce indefinite join after failure. No borrowed pool closed.' if row['rule']=='CloseResource' else 'JUnit-only own fixed executor/tasks and explicit finite termination, outside J2EE; business wire calls all use the existing in-memory reply callback and 2s bounded coordinator.')
 classifications.append(dict(finding=row,applicableViolation=False,reason=reason))
normal=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';nm=load(normal);assert nm['source']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
for n,h in p['dependencies'].items():assert sha(Path(n))==h
prior=R/'evidence/01_PT/015_NK-WEB-001/evidence/PG24322-read-four-bounded-preflight-v1/manifest.json';pf=load(prior);assert pf['actualExit']==0 and pf['noActualBackendOrRootOrVmOrNativeOperations']
for n,h in pf['helperSourceHashes'].items():assert sha(R/n)==h==nm['begin']['inputHashes'][n]
for n in cfg['mainPaths']:
 source=(R/n).read_text();assert sha(R/n)==nm['begin']['inputHashes'][n]
 assert not any(v in source for v in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','java.net.','java.sql.','Files.','ProcessBuilder','createConnection','createContext','ServiceLoader'])
oldproof=R/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14314-web-business-wire-whole-twelve-post-v1/manifest.json';op=load(oldproof);assert sha(oldproof)=='06f8b8d26d79ec31f64c588144f6c7d54b74a35bfa72ef44fe72ca2e53e0719e' and op['actualExit']==0
# No old execution is copied: current normal/JDK callback graph is used; old proof supplies complete fixture context.
def old_review_metadata(value):
 for field in ['actualDatabaseActions','actualNetworkActions','actualServiceActions','actualVmActions']:
  assert field in value and type(value[field]) is int and value[field]==0
 assert value['rootMainInvoked'] is False and value['onlySuppliedObservationsAndOwnThreads'] is True
 assert 'actualAuthenticationOrSessionIssued' not in value and 'actualSecretKeysLoaded' not in value
 return True
assert old_review_metadata(op)
# Missing historical auth/key counters stay unknown. Current eligibility instead follows the
# exact supplied source callback graph and no external/provider acquisition above.
old_schema_negative=[]
import copy
for label,mutate in [('missing-network',lambda v:v.pop('actualNetworkActions')),('wrong-counter-type',lambda v:v.update(actualVmActions=False)),('nonzero-network',lambda v:v.update(actualNetworkActions=1)),('root-main',lambda v:v.update(rootMainInvoked=True)),('not-only-own-threads',lambda v:v.update(onlySuppliedObservationsAndOwnThreads=False)),('unexpected-new-auth-field',lambda v:v.update(actualAuthenticationOrSessionIssued=0))]:
 altered=copy.deepcopy(op);mutate(altered)
 try:old_review_metadata(altered)
 except (AssertionError,KeyError):old_schema_negative.append(label)
 else:raise AssertionError(label)
for n in cfg['sdkDependencies']:
 with zipfile.ZipFile(n) as z:assert not set(z.namelist()).intersection({'META-INF/services/java.sql.Driver','META-INF/services/javax.annotation.processing.Processor','META-INF/services/com.sun.source.util.Plugin','META-INF/services/jakarta.jms.ConnectionFactory'})
index_path=R/pf['normalPositiveMainIndex']['path'];assert sha(index_path)==pf['normalPositiveMainIndex']['sha256'];index=load(index_path);physical={n:v['sha256'] for n,v in index.items() if v['path'] in cfg['mainPaths']};assert physical==cfg['currentMainPhysical'] and len(physical)==7
O.parent.mkdir();v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),inputHashes=p['inputHashes'],compileManifestSha256=sha(RUNS/cfg['compileSlot']/'manifest.json'),staticManifestSha256=sha(RUNS/cfg['staticSlot']/'manifest.json'),normalManifestSha256=sha(normal),normalPositiveMainIndex=pf['normalPositiveMainIndex'],priorPureGraphReview=dict(path=str(prior.relative_to(R)),sha256=sha(prior)),originalWholeProofContext=dict(path=str(oldproof.relative_to(R)),sha256=sha(oldproof),oldExecutionOrCountersTransferred=False,missingHistoricalAuthAndKeyCounters=None,exactOldSchemaNegativeChecks=old_schema_negative),beforeGitCommit=cfg['beforeGitCommit'],beforeTestSha256=cfg['beforeTestSha256'],originalWholeMethods=12,allOriginalOtherTokensAndOraclesPreserved=True,singleFixedPoolOwnerBounded=True,futureGet10SecondsUnchanged=True,original180ConcurrentFacadeRequestsPreserved=True,noFixtureOrMethodExtraction=True,noSourceDuplicateOrSyntheticPasswordEvidenceOutput=True,cryptoApi='MessageDigest.isEqual/independent public fixture SHA vectors only; no actual key or credential operations',actualBackendOrAccountOrRootVmNativeActions=False,pmdRawFindings=5,applicableStaticViolations=0,checkstyleFindings=0,processingErrors=0,staticClassifications=classifications,suppressionAdded=False,physical=physical,sourcePrograms=6,physicalClasses=7,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None,toolSha256=sha(Path(__file__)))
O.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,whole12=12,targetPhysical=7,staticApplicable=0,manifestSha256=sha(O))))
