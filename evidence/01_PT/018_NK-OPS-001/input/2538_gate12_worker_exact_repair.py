"""BUG2873: retain original twelve test oracles; make owned worker termination explicit."""
from pathlib import Path
import hashlib,json,datetime
r=Path.cwd();e=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG30584-gate12-worker-source-repair-v1'
p=r/'program/characterization/tests/java/dev/codex/schubert/characterization/GateCliTest.java'
main=r/'program/characterization/src/main/java/dev/codex/schubert/characterization/GateCli.java'
assert '## BUG-2873 ' in (r/'documents/900_OTHER/910_台帳/915_障害表.md').read_text()
assert not e.exists();e.mkdir();before=p.read_text();(e/'GateCliTest.before.java.txt').write_text(before)
old='    try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {\n'
new='    var executor = Executors.newVirtualThreadPerTaskExecutor();\n    try {\n'
assert before.count(old)==1
oldend='      first.get(5, TimeUnit.SECONDS);\n    }\n'
newend='      first.get(5, TimeUnit.SECONDS);\n    } finally {\n      releaseSerialization.countDown();\n      executor.shutdownNow();\n      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));\n    }\n'
assert before.count(oldend)==1
after=before.replace(old,new).replace(oldend,newend)
assert after.replace(new,old).replace(newend,oldend)==before
assert after.count('@Test')==before.count('@Test')==12
p.write_text(after)
sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
m=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),bug='BUG-2873',horizontal='YKT-2387',originalTestCount=12,newTestDefinitions=0,beforeSha256=hashlib.sha256(before.encode()).hexdigest(),afterSha256=sha(p),mainSha256=sha(main),mainUnchanged=True,exactInversePreservesAllOtherSourceBytes=True,blockingHelperStillHasFiveSecondTimeout=True,futureStillFiveSeconds=True,finallyReleasesLatchAndInterruptsOwnedWorker=True,explicitTerminationSeconds=10,testsExecuted=0,coverage=None,bugState='OPEN_PENDING_ACTUAL_NORMAL_WHOLE12_AND_INDEPENDENT_POST',externalOperations=0)
(e/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m))
