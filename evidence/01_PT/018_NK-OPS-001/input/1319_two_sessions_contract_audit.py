"""P00702 public contract and bounded historical proof correspondence; no product execution."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess

R = Path.cwd()
B = R / 'evidence/01_PT/018_NK-OPS-001'
P = R / 'evidence/01_PT/007_NK-AUT-001'
O = B / 'evidence/PG26724-two-session-contract-v1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
ref = lambda p: dict(path=str(p.relative_to(R)), sha256=sha(p))
assert not O.exists()
task = next(t for t in load(R / 'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json')['tasks'] if t['id'] == 'WBS-P007-02')
assert len(task['ownedArtifacts']) == 3
own = {p: sha(R / p) for p in task['ownedArtifacts']}
normal = load(B / 'evidence/PG22106-api-stop-static-independent-input-v1/normal.json')
index = load(B / 'evidence/PG23360-base59-named-proof-supplement-v1/current-normal-physical-index.json')
for p, h in own.items():
    assert normal['begin']['inputHashes'][p] == h
retained = []
for relative, count in [('evidence/PG20914-session-issue-jdbc-eight-v1/manifest.json', 8), ('evidence/PG19788-session-audit-nine-v1/manifest.json', 9)]:
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
issue_post = P / 'evidence/PG20920-session-issue-independent-post-v1/manifest.json'
ip = load(issue_post)
assert ip['actualExit'] == 0 and ip['tests'] == 8
assert sha(R / ip['originalPost']['path']) == ip['originalPost']['sha256']
admission = []
for p in task['evidencePlan']['candidateTestFiles']:
    text = (R / p).read_text()
    assert 'ApiLogDatabaseFixture' in text
    admission.append(dict(path=p, sha256=sha(R / p), fullPublicSourceReviewed=True, tests=text.count('@Test'), status='HOLD_WHOLE_REAL_DATABASE_FIXTURE_NO_PARTIAL_SELECTION', independentExpectations='literal SQL counts/last-access and PostgreSQL UUID order, independent JCA hash/AES-GCM AAD, caller rollback and critical audit atomicity; 100-issue real concurrency not executed'))
commit = subprocess.check_output(['git', 'rev-parse', 'origin/main'], text=True).strip()
design = task['evidencePlan']['designFiles'][0]
data = subprocess.check_output(['git', 'show', commit + ':' + design])
text = data.decode()
assert all(x in text for x in ['last_accessed_at,id', '最大2', 'DIF-016', 'Login成功transaction'])
checks = [
    dict(id='P00702-PG01', source='AuthSessionService.issue', expectation='Explicit caller transaction; app_users row lock first, missing/disabled denied before issuance; insert same user context then select nonrevoked expires_at>issuedAt rows ordered last_accessed_at,id FOR UPDATE. Replace exactly size-2 oldest entries, requiring affected1. No implicit issue-time ordering or absolute lifetime.', testIds=['PT-AUT-ISS002', 'PT-AUT-005-I/006'], limitation='Memory JDBC checks exact SQL/order/binding, not live PostgreSQL lock serialization.'),
    dict(id='P00702-PG02', source='AuthSessionService.issue', expectation='32 random bytes lowercase64; SHA256 lookup, AES-GCM encrypted envelope and identity-bound AAD; microsecond UTC issuance/last-access, +8h expiry; raw temporary bytes and borrowed ciphertext wiped on every acquired path. No raw context/lookup hash/envelope/identifier logged.', testIds=['PT-AUT-ISS001', 'PT-AUT-ISS003', 'PT-AUT-ISS007'], limitation='Original independent public deterministic vector only, never actual key/session issuance. Whole current crypto dependency closure not newly qualified.'),
    dict(id='P00702-PG03', source='SessionAuditWriter.write/SessionRevocationReason', expectation='Critical SESSION_REVOKED SECURITY INFO in caller business transaction after each replacement; reason REPLACED/result0000, current login verified IP, actor/target user and message/correlation IDs. Six closed reasons, optional IP uses SQL NULL, exact insert1. No borrowed commit/rollback/close.', testIds=['PT-AUT-ISS002', 'AUT-SESSION-AUDIT001..009'], limitation='Original audit9 fixed bindings/SQL/failure resource graph; SDK initialization review null in historical proof retained as limitation, not silently promoted.'),
    dict(id='P00702-PG04', source='AuthSessionService.issue/SessionAuditWriter.write', expectation='SQL/required SQL NULL/affected-count/owned-close faults cannot return success; fixed infrastructure redaction; semantic missing/disabled context rejection and owned close failure distinguished; caller rollback required, Inbox replay caller must not reissue.', testIds=['PT-AUT-ISS004..008', 'AUT-SESSION-AUDIT001..009'], limitation='Unknown runtime original test uses IllegalStateException. Provider-thrown AuthenticationContextException origin and fatal/aliased graphs are not claimed completely tested. New DB transaction, same-user concurrency, and ending dependency proof remain absent.')]
v = dict(actualExit=0, atJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(), source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(), productionCoreMain='62960fc3b5d4a67cf7bd9df887b668169d10f87f', ownedSourceHashes=own, design=dict(path=design, commit=commit, sha256=hashlib.sha256(data).hexdigest()), checks=checks, retainedOriginalProofs=retained, originalIssueIndependentPost=ref(issue_post), candidateAdmission=admission, completedOriginalPreparationWorkIds=['WBS-P007-02/1'], endingStatus='WBS-P007-02/2_NOT_ACCEPTED_REAL_DB_CONCURRENCY_TRANSACTION_DEPENDENCIES_AND_WHOLE451', productTestsExecuted=0, newDefinitions=0, MainOrTestChanged=False, newAcceptance=0, formalUpdated=False, effortRate=None, actualBackendAndHeldClassBinaryActions=0, verifier=ref(Path(__file__).resolve()))
O.mkdir()
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0, ownSources=3, retainedOriginalTests=[8,9], newProductExecutions=0, manifestSha256=sha(O/'manifest.json'))))
