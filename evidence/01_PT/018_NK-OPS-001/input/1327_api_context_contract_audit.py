"""P00703 context authorization public contract and bounded proof correspondence; no product execution."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess

R = Path.cwd()
B = R / 'evidence/01_PT/018_NK-OPS-001'
P = R / 'evidence/01_PT/007_NK-AUT-001'
O = B / 'evidence/PG26732-api-context-contract-v1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
ref = lambda p: dict(path=str(p.relative_to(R)), sha256=sha(p))
assert not O.exists()
task = next(t for t in load(R / 'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json')['tasks'] if t['id'] == 'WBS-P007-03')
assert len(task['ownedArtifacts']) == 15
own = {p: sha(R / p) for p in task['ownedArtifacts']}
normal = load(B / 'evidence/PG22106-api-stop-static-independent-input-v1/normal.json')
index = load(B / 'evidence/PG23360-base59-named-proof-supplement-v1/current-normal-physical-index.json')
for p, h in own.items():
    assert normal['begin']['inputHashes'][p] == h
retained = []
for relative, count in [('evidence/PG20840-authentication-verifier-jdbc-six-v1/manifest.json', 6), ('evidence/PG20874-admin-prelude-jdbc-eight-v1/manifest.json', 8)]:
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
issue_post = P / 'evidence/PG20850-authentication-jdbc-independent-post-v1/manifest.json'
ip = load(issue_post)
assert ip['actualExit'] == 0 and ip['tests'] == 6
assert sha(R / ip['originalPost']['path']) == ip['originalPost']['sha256']
admission = []
for p in task['evidencePlan']['candidateTestFiles']:
    text = (R / p).read_text()
    isdb = 'ApiLogDatabaseFixture' in text
    admission.append(dict(path=p, sha256=sha(R/p), fullPublicSourceReviewed=not isdb, publicMethodIndexReviewed=True, tests=text.count('@Test'), status='HOLD_WHOLE_REAL_DATABASE_FIXTURE_NO_PARTIAL_SELECTION' if isdb else ('CURRENT_WHOLE_AUTHORIZATION2_WITH_PROTOCOL130_QUALIFIED' if Path(p).stem=='AuthorizationServiceTest' else 'NOT_RUN_FINITE_WORKER_CLOSE_AND_CRYPTO_RESTORE_QUALIFICATION_PENDING'), independentExpectations='Literal role-owner 403/404 matrix, source-independent JCA/DataOutputStream encryption/hash vectors; realDB lock/identity/SQL/TX expectations remain unexecuted.'))

commit = subprocess.check_output(['git', 'rev-parse', 'origin/main'], text=True).strip()
design = task['evidencePlan']['designFiles'][0]
data = subprocess.check_output(['git', 'show', commit + ':' + design])
text = data.decode()
assert all(x in text for x in ['notification owner=actor','ADMIN拡張なし','User群昇順lock','expires_at>now'])
checks = [
 dict(id='P00703-PG01', sources=['AuthenticationContextVerifier','AuthenticatedActor','ContextHash','AuthenticationContextException','AuthenticationInfrastructureException'], expectation='Caller explicit TX User→session lock; raw64lowerhex SHA256 ASCII lookup, revoked=false/expiry>now/ACTIVE, latest DB username/role/N12 actor, guardedtouch greatest(lastaccess,now) and greatest(expiry,now+8h) affected1. Readonlyinspect explicitreadonly/one nonlockingread/noidlechange not finalgrant. SQL NULL/unknownrole/fault fixed9000, semanticinvalid0102; fatal graph seen-identity cycle protection.', testIds=['PT-AUT-007-01..06','PT-AUT-007-R01..04','PG20840 pure original6'], limitation='DB whole fixture10 not executed; old pure6 target2 unchanged only, wholecurrent dependencies and unknown same-type provider origin not qualified.'),
 dict(id='P00703-PG02', sources=['AdminCommandAuthenticator'], expectation='CREATE targetabsent/otherspresent N12, candidate lookup not grant, decreasing membership advisory71419601 then all relevant Users ascending lock before lockedcontextowner equality/fresh verifier/latestADMIN. Identityalone cannotgrantADMIN. Caller owns TX/criticalaudit/Inbox.', testIds=['PT-ADM-008..013','PT-ADM-074','PG20874 pure original8'], limitation='DB whole fixture7 held, old8 target2 unchanged only; no current actual locks/activeADMIN mutation accepted.'),
 dict(id='P00703-PG03', sources=['AuthorizationService','AuthorizationException','AuthenticatedActor'], expectation='USER/ADMIN owner notification only; othernotification always0104, otherquestion ADMINallowed/USER0104, adminoperation USER0103. OwnerN12/nonnullactor/closed403404 exception. Fixed no identity/target detail in display.', testIds=['PT-AUT-008-01','PT-AUT-008-02'], limitation='Current normal whole2+Protocol130 genuine132, no JDBC predicates/HTTP/application actual authorization claim. Actor username getBytes scalar/site8 remains globalYKT2328 pending, not closed by byte count test.'),
 dict(id='P00703-PG04', sources=['AuthContextCodec','AuthContextIdentity','AuthContextCryptoException','EncryptedAuthContext','IssuedContext','RevokedContext','package-info'], expectation='API-exclusive currentwrite/currentpreviousread NKENC1 AES256GCM/nonce12/AAD six lengthprefix ASCII fields, strict version/key/envelope64context/unknownkeys typed; clonedownedbuffers private lock/wipe/close. Issued expires>issued, revokedsuccess0000/0200 only, no identity/context in display.', testIds=['PT-AUT-005-C01..04','PT-AUT-005-H01/H02','PT-AUT-005-I','PT-AUT-008-R01/R04'], limitation='Publicsynthetic Test source oracles reviewed, codec7/hash3 not freshly run because unbounded future/executorclose ownership needs finite qualification before current normal run. Actualcredential/key/session/DB/held4 operations remain absent.')]
current=B/'evidence/PG26744-authorization-current-independent-v1/manifest.json';cm=load(current);assert cm['actualExit']==0 and cm['tests']==132 and all(x['missed']==0 for x in cm['coverage'].values())

v = dict(actualExit=0, atJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(), source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(), productionCoreMain='62960fc3b5d4a67cf7bd9df887b668169d10f87f', ownedSourceHashes=own, design=dict(path=design, commit=commit, sha256=hashlib.sha256(data).hexdigest()), checks=checks, retainedOriginalProofs=retained, originalVerifierIndependentPost=ref(issue_post), currentAuthorizationWhole132=ref(current), candidateAdmission=admission, completedOriginalPreparationWorkIds=['WBS-P007-03/1'], endingStatus='WBS-P007-03/2_NOT_ACCEPTED_REAL_DB_CRYPTO_FINITE_LIFETIME_UNICODE_ACTOR_DEPENDENCIES_AND_WHOLE451', productTestsExecuted=132, newDefinitions=0, MainOrTestChanged=False, newAcceptance=0, formalUpdated=False, effortRate=None, actualBackendAndHeldClassBinaryActions=0, verifier=ref(Path(__file__).resolve()))
O.mkdir()
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0, ownSources=15, retainedOriginalTests=[6,8], newProductExecutions=132, manifestSha256=sha(O/'manifest.json'))))
