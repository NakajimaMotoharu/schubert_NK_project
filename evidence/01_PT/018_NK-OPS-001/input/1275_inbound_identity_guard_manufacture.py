"""Two real identity-boundary inputs, one new Test; no Main/old169 assertion changes."""
from pathlib import Path
import hashlib,json,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';p=R/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/inbound/InboundTransactionPortTest.java';old=p.read_text();before=json.loads((B/'evidence/PG26584-event-connected169-v1/begin.json').read_text());assert hashlib.sha256(p.read_bytes()).hexdigest()==before['inputHashes'][str(p.relative_to(R))]
addition='''
  @Test
  void identicalIsolationAndRollbackFailuresDoNotSelfSuppressOrFakeConfirmation() {
    // PT-JMS-INPORT007; JDK self-suppression must never replace the actual phase failure.
    Fixture isolation = new Fixture();
    var sameProtocol = protocol();
    isolation.faults = Map.of(SEND, sameProtocol);
    var failed = assertThrows(FailedJmsIsolationException.class,
        () -> isolate(isolation, isolation.message(), sameProtocol));
    assertSame(sameProtocol, failed.getCause());
    assertEquals(0, failed.getSuppressed().length);
    assertEquals(0, sameProtocol.getSuppressed().length);
    assertEquals(List.of(SEND, ATTEMPTED, ROLLBACK, CONFIRMED), isolation.events);
    assertEquals(1, isolation.sends);
    assertEquals(1, isolation.rollbacks);
    assertEquals(0, isolation.commits);

    Fixture rollback = new Fixture();
    var sameFailure = new IllegalStateException("synthetic identical rollback");
    rollback.faults = Map.of(ROLLBACK, sameFailure);
    var unconfirmed = assertThrows(UnconfirmedJmsRollbackException.class,
        () -> InboundTransactions.rollbackAfterFailure(rollback.context(), sameFailure,
            () -> rollback.events.add(ATTEMPTED), () -> rollback.events.add(CONFIRMED)));
    assertSame(sameFailure, unconfirmed.getCause());
    assertEquals(0, unconfirmed.getSuppressed().length);
    assertEquals(0, sameFailure.getSuppressed().length);
    assertEquals(List.of(ATTEMPTED, ROLLBACK), rollback.events);
    assertEquals(1, rollback.rollbacks);
    assertEquals(0, rollback.commits);
    assertEquals(0, rollback.sends);
  }

''';anchor='  private static PermanentProtocolException protocol()';assert old.count(anchor)==1;new=old.replace(anchor,addition+anchor);assert new.replace(addition,'')==old
fmt=TC/'google-java-format-1.36.1-all-deps.jar'
if not fmt.exists():fmt=next(TC.rglob(fmt.name))
f=subprocess.run([str(TC/'jdk-25.0.4/bin/java'),'-jar',str(fmt),'-'],input=new,text=True,capture_output=True);assert f.returncode==0,f.stderr;p.write_text(f.stdout);O=B/'evidence/PG26592-inbound-identity-guard-manufacture-v1';assert not O.exists();O.mkdir();(O/'original-six.before.java.txt').write_text(old);v=dict(actualExit=0,path=str(p.relative_to(R)),beforeSha256=hashlib.sha256(old.encode()).hexdigest(),afterSha256=hashlib.sha256(p.read_bytes()).hexdigest(),originalSixAllTokensInverseExact=True,newDefinitions=1,independentSameInstanceInputs=2,MainChanged=False,otherFiveWholeFixturesUnchanged=True,productTestsExecuted=0);(O/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
