"""Independent single-site inverse and failure-control review, not dynamic PT."""
from pathlib import Path
import datetime
import hashlib
import json

B=Path('evidence/01_PT/018_NK-OPS-001')
O=B/'evidence/PG24182-admin-concurrency-wait-independent-v1'
P=Path('src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/admin/UserCommandServiceTest.java')
BEFORE=B/'evidence/PG24176-admin-concurrency-wait-before-v1'
PRODUCER=B/'evidence/PG24180-admin-concurrency-wait-static-v1'
sha=lambda b:hashlib.sha256(b).hexdigest()

def verify(before,after):
    old=b'start.await();'
    new=b'assertTrue(start.await(5, TimeUnit.SECONDS));'
    assert before.count(old)==1 and after.count(new)==1
    assert old not in after
    assert after.replace(new,old,1)==before
    # CountDownLatch is a real declared type, not inferred from await/get name.
    start=before.index(b'void adm022ConcurrentMutationsPreserveAdminAndVersionInvariants()')
    body=before[start:before.index(b'    seed();',start)]
    assert b'try (var pool = Executors.newFixedThreadPool(10))' in body
    assert b'CountDownLatch start = new CountDownLatch(1);' in body
    assert body.index(b'for (int i = 0; i < 100; i++)')<body.index(b'pool.submit(')<body.index(old)<body.index(b'start.countDown();')<body.index(b'for (var job : jobs)')
    # Five seconds applies to fixture release only, not the independent database result.
    assert b'job.get(30, TimeUnit.SECONDS)' in body
    assert b'assertEquals(1, success);' in body and b'assertEquals(99, conflict);' in body
    assert b'finally' not in body[body.index(b'CountDownLatch start'):body.index(b'start.countDown();')]

assert not O.exists()
before=(BEFORE/P.name).read_bytes();after=P.read_bytes();original=json.loads((BEFORE/'manifest.json').read_bytes());producer=json.loads((PRODUCER/'manifest.json').read_bytes())
assert sha(before)==original['beforeSha256']==producer['beforeSha256']
assert sha(after)==producer['afterSha256']
verify(before,after)
negatives=[]
for label,candidate in [('unbounded-original',before),('bound-changed',after.replace(b'await(5, TimeUnit.SECONDS)',b'await(50, TimeUnit.SECONDS)')),
                        ('unchecked-timeout',after.replace(b'assertTrue(start.await(5, TimeUnit.SECONDS));',b'start.await(5, TimeUnit.SECONDS);')),
                        ('wrong-time-unit',after.replace(b'start.await(5, TimeUnit.SECONDS)',b'start.await(5, TimeUnit.MILLISECONDS)')),
                        ('oracle-change',after.replace(b'assertEquals(99, conflict);',b'assertEquals(98, conflict);')),
                        ('trial-count-change',after.replace(b'i < 100',b'i < 99'))]:
    assert candidate!=after
    try:verify(before,candidate)
    except AssertionError:negatives.append(label)
    else:raise AssertionError(label)
O.mkdir()
result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source='7aed8eace7c844c2f79f2e39db766faf914890d5',target=str(P),beforeSha256=sha(before),afterSha256=sha(after),producerManifest=dict(path=str(PRODUCER/'manifest.json'),sha256=sha((PRODUCER/'manifest.json').read_bytes())),changedSites=1,allOtherBytesUnchanged=True,typedLatchAndSubmissionFailurePathReviewed=True,fixtureAndIndependentDbOraclesUnchanged=True,metadataNegativeChecks=negatives,originalClassTestMethods=after.count(b'  @Test\n'),newTestMethods=0,dynamicTestState='NOT_RUN_HOLD_ACTUAL_DATABASE_FIXTURE',bugClosure='SOURCE_FIXED_REVIEWED_DYNAMIC_RETEST_HOLD',globalYktWaitSafetyAccepted=False,oldCurrentSyntaxIndexSourceEntryNowHistorical=True,compilerOrJvmExecuted=False,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None,bugs=['BUG-2519'],ykts=['YKT-2177'],tool=dict(path=str(Path(__file__)),sha256=sha(Path(__file__).read_bytes())))
(O/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,changedSites=1,negativeChecks=len(negatives),originalClassTestMethods=result['originalClassTestMethods'],dynamicTestState=result['dynamicTestState'],manifestSha256=sha((O/'manifest.json').read_bytes()))))
