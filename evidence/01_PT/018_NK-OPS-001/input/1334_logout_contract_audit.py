"""P00705 logout fence public contract and bounded historical proof correspondence; no product execution."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess

R = Path.cwd()
B = R / 'evidence/01_PT/018_NK-OPS-001'
P = R / 'evidence/01_PT/007_NK-AUT-001'
O = B / 'evidence/PG26762-logout-contract-v2'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
ref = lambda p: dict(path=str(p.relative_to(R)), sha256=sha(p))
assert not O.exists()
task = next(t for t in load(R / 'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json')['tasks'] if t['id'] == 'WBS-P007-05')
assert len(task['ownedArtifacts']) == 3
own = {p: sha(R / p) for p in task['ownedArtifacts']}
normal = load(B / 'evidence/PG22106-api-stop-static-independent-input-v1/normal.json')
index = load(B / 'evidence/PG23360-base59-named-proof-supplement-v1/current-normal-physical-index.json')
for p, h in own.items():
    assert normal['begin']['inputHashes'][p] == h
retained = []
for relative, count in [('evidence/PG20958-session-revocation-oracle-fixed-eight-v1/manifest.json', 8)]:
    path = P / relative
    old = load(path)
    assert old['actualExit'] == 0 and old['tests'] == count
    assert all(old[k] == 0 for k in ['failures', 'errors', 'skipped', 'aborted'])
    for p, h in old['inputHashes'].items():
        assert sha(R / p) == h
    for n, h in old['physicalHashes'].items():
        assert normal['normalPhysicalClassHashes']['api:' + n + '.class'] == h == index[n]['sha256']
        assert index[n]['crc64'].zfill(16) == old['physicalClassIds'][n].zfill(16)
    assert len(old['selectedTestMethods']) == count
    for cls, method in old['selectedTestMethods']:
        text = (R / ('src/schubert-nk-api/src/test/java/' + cls.replace('.', '/') + '.java')).read_text()
        assert re.search(r'\bvoid\s+' + re.escape(method) + r'\s*\(', text)
    assert all(c['missed'] == 0 for counters in old['coverage'].values() for c in counters.values())
    retained.append(dict(proof=ref(path), originalSource=old['source'], originalMain=old['productionCoreMain'], originalTests=count, inputHashes=old['inputHashes'], physical=old['physicalHashes'], counters=old['coverage'], status='ORIGINAL_RUN_TARGET_SOURCE_TEST_AND_PHYSICAL_IDENTICAL_NOT_CURRENT_WHOLE_DEPENDENCY_QUALIFICATION', newExecutions=0))
issue_post = P / 'evidence/PG20964-session-revocation-independent-post-v1/manifest.json'
ip = load(issue_post)
assert ip['actualExit'] == 0 and ip['tests'] == 8
assert sha(R / ip['originalPost']['path']) == ip['originalPost']['sha256']
admission = []
for p in task['evidencePlan']['candidateTestFiles']:
    text = (R / p).read_text()
    assert 'ApiLogDatabaseFixture' in text
    admission.append(dict(path=p, sha256=sha(R / p), fullPublicSourceReviewed=False, publicMethodIndexReviewed=True, tests=text.count('@Test'), status='HOLD_WHOLE_REAL_DATABASE_FIXTURE_NO_PARTIAL_SELECTION', independentExpectations='Currentclock after User/session locks, literal expiry equality/oldrevokedAt/0102 fence SQL postconditions and critical audit atomicity, snapshot/state/ref/replay context binding; actualDB not executed'))
commit = subprocess.check_output(['git', 'rev-parse', 'origin/main'], text=True).strip()
design = task['evidencePlan']['designFiles'][0]
data = subprocess.check_output(['git', 'show', commit + ':' + design])
text = data.decode()
required314=['User→session lock','元のrevoked_at/0200','324 §6.2'];required324=['Logout Inbox','LOGREQ01','AUTH_SESSION','保持は更新requestとして完了+7日']
assert all(x in text for x in required314)
supplement='documents/300_SS/320_メッセージング/324_Outbox・Inbox・冪等性・再送設計.md';extra=subprocess.check_output(['git','show',commit+':'+supplement]);extraText=extra.decode();assert all(x in extraText for x in required324)
assert not all(x in text for x in required324)
# Negative tests are metadata predicates only; neither invokes any product method.
assert not all(x in extraText.replace('保持は更新requestとして完了+7日','') for x in required324)

checks = [
 dict(id='P00705-PG01',source='AuthSessionRevocationService.logout/logoutCurrent',testIds=['PT-AUT-008-R01..04','PG20958 eight synthetic JDBC'],expectation='Explicit callerTX User→session lock then clock sampled micros. Known alreadyrevoked returns originalrevokedAt/0200 without actor/touch or newrevoke; otherwise expiry<=now stagesEXPIRED+0102 criticalaudit then denies, ACTIVEonlynewLOGOUT+0000. Separate request audit once, InboxsameMessage replay does not call revoke. SQL NULL/affected1/close faults fixed9000; no session ID/raw/hash/cipher log.'),
 dict(id='P00705-PG02',source='AuthSessionRevocationService.revokeAll',testIds=['PT-AUT-008-R03/R04','PG20958 eight synthetic JDBC'],expectation='Fresh DB-authenticatedADMIN supplied by caller, targetN12 and reasonsDISABLED/PASSWORD_RESET/ADMIN only. Userlock then activeunrevoked sessionUUIDascending lock; each guardedupdate1 and correspondingactor/target/message/corr criticalaudit in samebusinessTX. No owncommit/rollback/close or unauthorized principal grant.'),
 dict(id='P00705-PG03',source='LogoutInboxService.execute/owner',testIds=['PT-AUT-LOGOUT-INBOX-001..006','expiry-fence additional cases in whole fixture'],expectation='LOGREQ01 validated, rawhash owner-only Userlock; unknownowner0102/noInbox; no active actor/authentication/touch at lookup. Knownowner Inbox ownerdecimal/LOGREQ01/001 targetREQUEST:LOGREQ01 DATA0/notoken/headercontext outsidefingerprint, seven-day retention; NEWonlylogoutCurrent. Invalidexpiry persistsEXPIRED fence+0102snapshot by callerTX; IN_PROGRESS9000/nonpersisted; sameowner sameMessage replay never revokes another context.'),
 dict(id='P00705-PG04',source='LogoutReplayService.captureSuccess/captureDenied/failure/restore/validateSession/wire',testIds=['PT-AUT-LOGOUT-INBOX-001..006','metadata tamper/expiry cases in whole fixture'],expectation='Initial280byte/24DATA frozenencrypted, successCOMPLETED/AUTH_SESSION vs0102ERROR/NONE. AAD request/layout001/owner. Restore closedheader/length/correlation/layout/state/code/fullsemantic; successsnapshot original context hash matches referenced UUID/owner/revoked=true/originalrevokedAt millis. Freshresponse Message/time/correlation=requestMessage/currentrequestcontext; successful replay0200, failed0102 retained, no DB updates/idle/authgrant. Buffers wiped and fixed9000.')]

v = dict(actualExit=0, atJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(), source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(), productionCoreMain='62960fc3b5d4a67cf7bd9df887b668169d10f87f', ownedSourceHashes=own, design=dict(path=design, commit=commit, sha256=hashlib.sha256(data).hexdigest()), checks=checks, retainedOriginalProofs=retained, originalRevocationIndependentPost=ref(issue_post), candidateAdmission=admission, supplementaryDesign=dict(path=supplement, commit=commit, sha256=hashlib.sha256(extra).hexdigest()), designBindingMetadataChecks=dict(positive=2,negative=2,productionTests=0), priorMetadataWithoutSupplementFields=ref(B/'evidence/PG26756-logout-contract-v1/manifest.json'), completedOriginalPreparationWorkIds=['WBS-P007-05/1'], endingStatus='WBS-P007-05/2_NOT_ACCEPTED_ACTUAL_DB_EXPIRY_FENCE_SNAPSHOT_REPLAY_ADMIN_DEPENDENCIES_AND_WHOLE451', productTestsExecuted=0, newDefinitions=0, MainOrTestChanged=False, newAcceptance=0, formalUpdated=False, effortRate=None, actualBackendAndHeldClassBinaryActions=0, verifier=ref(Path(__file__).resolve()))
O.mkdir()
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0, ownSources=3, retainedOriginalTests=[8], newProductExecutions=0, manifestSha256=sha(O/'manifest.json'))))
