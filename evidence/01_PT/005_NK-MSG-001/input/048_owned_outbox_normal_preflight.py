"""Declared normal EMPTY SqlConnectionProvider contract, independent of held cleanup-failure tests."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess,zipfile
R=Path.cwd();B=R/'evidence/01_PT/005_NK-MSG-001';RUNS=R.parent/'pgpt-runs/PG379';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cfg=load(B/'input/046_owned_outbox_normal_scope.json');O=R/cfg['preflightManifest'];assert not O.parent.exists()
p=load(RUNS/cfg['compileSlot']/'manifest.json');s=load(RUNS/cfg['staticSlot']/'manifest.json');assert p['actualExit']==0 and p['inputHashes']==s['inputHashes']
for path,h in p['inputHashes'].items():assert sha(R/path)==h
oldpf=B/'evidence/PG24258-owned-outbox-bounded-preflight-v1/manifest.json';old=load(oldpf);assert old['actualExit']==0 and old['heldAttachSecondaryUnreachable']
oldtest=next(k for k in cfg['testClasses'] if k.endswith('/OwnedOutboxDispatcherTest.java'));assert sha(R/oldtest)==old['inputHashes'][oldtest]
newtest=next(k for k in cfg['testClasses'] if k.endswith('/OwnedOutboxNormalCyclePortTest.java'));source=(R/newtest).read_text();assert len(re.findall(r'@Test\s+void\s+\w+\(',source))==1
for name in ['DriverManager','java.net','ProcessBuilder','ServiceLoader','Class.forName','TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','setAccessible','@Before','@After'] :assert name not in source
# Cleanup callbacks are unconditional ordinary records/returns even when other calls reject.
for body in ['case "close":\n                    calls.add("result.close");\n                    return null;', 'case "close":\n                    calls.add("statement.close");\n                    return null;', 'case "rollback":\n                    calls.add("rollback");\n                    return null;', 'case "close":\n                    calls.add("connection.close");\n                    completed.countDown();\n                    return null;']:assert body in source
assert 'assertTrue(completed.await(5, TimeUnit.SECONDS));' in source and '} finally {\n      owned.close();\n    }' in source
assert 'return false;' in source and 'return claim.connection;' in source and 'Clock.fixed(NOW, ZoneOffset.UTC)' in source
assert len(s['reports']['pmd']['items'])==20 and not s['reports']['pmd']['processingErrors'] and not s['reports']['checkstyle']['items'] and not s['reports']['checkstyle']['processingErrors']
oldsites={(v['finding']['class'],v['finding']['rule'],v['finding']['beginline']):v['reason'] for v in old['staticClassifications']};classifications=[]
for item in s['reports']['pmd']['items']:
 key=(item['class'],item['rule'],item['beginline'])
 if key in oldsites:reason=oldsites[key]
 elif key==('OwnedOutboxNormalCyclePortTest','UseProperClassLoader','32'):reason='Proxy for fixed java.sql API interface only; its declaring module loader is required for visibility. No untrusted name, context-loader changes, downloaded classes, provider discovery or driver loading.'
 elif key==('OwnedOutboxNormalCyclePortTest.EmptyClaim','UseConcurrentHashMap','40'):reason='Each EmptyClaim and parameter HashMap is confined to the one owned worker; parent reads only after owned.close joins it. ConcurrentLinkedQueue publishes claims, and latch plus final join publishes all writes. No concurrent map read or mutation.'
 else:raise AssertionError(key)
 classifications.append(dict(finding=item,applicableViolation=False,reason=reason))
normal=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)==old['normalManifestSha256'];nm=load(normal)
base='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/';names=['OwnedOutboxDispatcher','OutboxDispatcher','JdbcOutboxRepository','OutboxEntry','OutboxJmsSender','OutboxDispatchReport'];sources={base+n+'.java':sha(R/(base+n+'.java')) for n in names};assert all(nm['begin']['inputHashes'][k]==h for k,h in sources.items())
repo=(R/(base+'JdbcOutboxRepository.java')).read_text();dispatcher=(R/(base+'OutboxDispatcher.java')).read_text()
assert 'Instant leaseUntil = now.plusSeconds(10);' in repo and 'while (result.next())' in repo
assert 'connection.commit();\n        return claimed;' in dispatcher and 'return new OutboxDispatchReport(entries.size(), sent, failed, leaseLost);' in dispatcher
# Every successful result.next is false: no row decoder, OutboxEntry construction, JMS acquisition,
# markSent/markFailure, payload/key path or retry jitter call. Unexpected body assertions still
# see nonthrowing rollback/close, so retainFailure/held attachSecondary cannot be invoked.
review=[dict(callee='transaction',path='fixed Connection proxy open -> setAutoCommit(false) returns'),dict(callee='repository.claim',path='getAutoCommit false -> scalar validowner/now/limit -> SQL binds -> result.next false -> List.copyOf empty; no read/requireValue'),dict(callee='claim cleanup',path='result/statement close unconditional -> commit returns -> connection close unconditional; rollback also unconditional in any assertion error'),dict(callee='dispatch',path='empty list -> no sender/mark -> OutboxDispatchReport(0,0,0,0) -> normal run return'),dict(callee='owned stop',path='no callback wait; parent5s latch bounded; finallyclose wakes own monitor and joins only own worker; no external lifetime/resource')]
for path,h in p['dependencies'].items():assert sha(Path(path))==h
for path,h in cfg['sdkDependencies'].items():
 with zipfile.ZipFile(path) as z:
  members=set(z.namelist());assert not members.intersection({'META-INF/services/java.sql.Driver','META-INF/services/javax.annotation.processing.Processor','META-INF/services/com.sun.source.util.Plugin'})
  text=z.read('META-INF/MANIFEST.MF').decode() if 'META-INF/MANIFEST.MF' in members else '';assert not re.search('^Class-Path:',text,re.M)
refs={}
for path in ['documents/300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md','documents/300_SS/320_メッセージング/324_Outbox・Inbox・冪等性・再送設計.md']:
 data=subprocess.check_output(['git','show','origin/main:'+path]);refs[path]=hashlib.sha256(data).hexdigest()
 if '/332_' in path:assert b"interval '10 seconds'" in data and b'for update skip locked' in data
index=load(R/old['normalPositiveMainIndex']['path']);physical={n:v['sha256'] for n,v in index.items() if v['path'] in cfg['mainPaths']};assert physical==cfg['currentMainPhysical']
O.parent.mkdir();v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),inputHashes=p['inputHashes'],compileManifestSha256=sha(RUNS/cfg['compileSlot']/'manifest.json'),staticManifestSha256=sha(RUNS/cfg['staticSlot']/'manifest.json'),normalManifestSha256=sha(normal),normalPositiveMainIndex=old['normalPositiveMainIndex'],oldSixEligibilityManifest=dict(path=str(oldpf.relative_to(R)),sha256=sha(oldpf)),originalSixSourceUnchanged=True,newWholeClassMethods=1,originalWholeClassMethods=6,reviewedNormalTestSha256=sha(R/newtest),helperSourceHashes=sources,callPathReview=review,independentDesignBlobHashes=refs,canonicalDesignBranch='origin/main',normalEmptyResultOnly=True,cleanupCallbacksNonThrowing=True,heldAttachSecondaryUnreachable=True,noJmsContextAcquired=True,noDriverOrActualBackendOperations=True,noOldRootOrHeldFixtureExtraction=True,pmdRawFindings=20,applicableStaticViolations=0,checkstyleFindings=0,processingErrors=0,staticClassifications=classifications,suppressionAdded=False,physical=physical,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None,toolSha256=sha(Path(__file__)))
O.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,wholeClasses=2,expectedTests=7,staticApplicable=0,manifestSha256=sha(O))))
