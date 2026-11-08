"""Single Test fixture repair. Static byte preservation; no compile, JVM, database or Test run."""
from pathlib import Path
import datetime
import hashlib
import json

B=Path('evidence/01_PT/018_NK-OPS-001')
P=Path('src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/admin/UserCommandServiceTest.java')
OLD=B/'evidence/PG24176-admin-concurrency-wait-before-v1'
O=B/'evidence/PG24180-admin-concurrency-wait-static-v1'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert not O.exists()
before=P.read_bytes();m=json.loads((OLD/'manifest.json').read_bytes())
assert sha(before)==m['beforeSha256'] and before==(OLD/P.name).read_bytes()
old=b'start.await();';new=b'assertTrue(start.await(5, TimeUnit.SECONDS));'
assert before.count(old)==1 and new not in before
assert b'CountDownLatch start = new CountDownLatch(1);' in before
assert b'void adm022ConcurrentMutationsPreserveAdminAndVersionInvariants()' in before
assert b'import java.util.concurrent.TimeUnit;' in before
assert b'import static org.junit.jupiter.api.Assertions.assertTrue;' in before
body=before[before.index(b'void adm022ConcurrentMutationsPreserveAdminAndVersionInvariants()'):]
assert body.index(b'pool.submit(')<body.index(old)<body.index(b'start.countDown();')
after=before.replace(old,new,1)
assert after.replace(new,old,1)==before
P.write_bytes(after);O.mkdir()
(O/'source-change.json').write_text(json.dumps(dict(path=str(P),beforeSha256=sha(before),afterSha256=sha(after),method='adm022ConcurrentMutationsPreserveAdminAndVersionInvariants',old='start.await();',new='assertTrue(start.await(5, TimeUnit.SECONDS));',sites=1,allOtherBytesUnchanged=True),ensure_ascii=False,indent=2)+'\n')
result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source='7aed8eace7c844c2f79f2e39db766faf914890d5',sourceChangeSha256=sha((O/'source-change.json').read_bytes()),beforeManifest=dict(path=str(OLD/'manifest.json'),sha256=sha((OLD/'manifest.json').read_bytes())),target=str(P),beforeSha256=sha(before),afterSha256=sha(after),changedSites=1,allOtherBytesUnchanged=True,fixtureAndIndependentDbOraclesUnchanged=True,dynamicTestState='NOT_RUN_HOLD_ACTUAL_DATABASE_FIXTURE',compilerOrJvmExecuted=False,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None,bugs=['BUG-2519'],ykts=['YKT-2177'],tool=dict(path=str(Path(__file__)),sha256=sha(Path(__file__).read_bytes())))
(O/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,changedSites=1,allOtherBytesUnchanged=True,manifestSha256=sha((O/'manifest.json').read_bytes()))))
