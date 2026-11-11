"""Whole original correlation5 preservation and two independent normal methods; no Main edits."""
from pathlib import Path
import datetime,hashlib,json,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG26416-correlation-manufacture-v1';assert not O.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=B/'evidence/PG26410-correlation-worker-owner-before-v1';plan=json.loads((before/'manifest.json').read_bytes());p=R/plan['testPath'];old=p.read_text();assert sha(p)==plan['testSha256'] and old==(before/'original-whole-test.java.txt').read_text();s=old
start='    try (ExecutorService executor = Executors.newFixedThreadPool(16)) {';startNew='    ExecutorService executor = Executors.newFixedThreadPool(16);\n    try {';assert s.count(start)==1;s=s.replace(start,startNew,1)
end="""        task.get(5, TimeUnit.SECONDS);
      }
    }
    assertEquals(1, winners.get());""";endNew="""        task.get(5, TimeUnit.SECONDS);
      }
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(5, TimeUnit.SECONDS));
    }
    assertEquals(1, winners.get());""";assert s.count(end)==1;s=s.replace(end,endNew,1)
addition="""  // CORRELATION006007-BEGIN: independent terminal-state and returned-view contracts.
  @Test
  void allSixTerminalOrdersReturnOnePermitAndKeepTheFirstLiteralOutcome() {
    int[][] orders = {{0, 1, 2}, {0, 2, 1}, {1, 0, 2}, {1, 2, 0}, {2, 0, 1}, {2, 1, 0}};
    for (int[] order : orders) {
      var registry = new ReplyCorrelationRegistry(1);
      PendingReply pending = registry.register(ID_1, DEADLINE, NOW).orElseThrow();
      int winners = 0;
      for (int action : order) {
        boolean terminal = switch (action) {
          case 0 -> registry.complete(ID_1, new byte[] {4, 5, 6}, NOW.plusSeconds(1));
          case 1 -> registry.expire(ID_1, DEADLINE);
          case 2 -> registry.cancel(ID_1);
          default -> throw new AssertionError("independent three-action fixture is invalid");
        };
        assertEquals(action == order[0], terminal);
        if (terminal) winners++;
      }
      assertEquals(1, winners);
      assertEquals(0, registry.pendingCount());
      if (order[0] == 0) {
        var completion = pending.completion().toCompletableFuture();
        assertTrue(completion.isDone());
        assertArrayEquals(new byte[] {4, 5, 6}, completion.join());
        assertEquals(0L, registry.lateResponseCount());
      } else {
        assertExceptional(pending, order[0] == 1
            ? java.util.concurrent.TimeoutException.class : java.util.concurrent.CancellationException.class);
        assertEquals(1L, registry.lateResponseCount());
      }
      registry.register(ID_2, DEADLINE, NOW).orElseThrow();
      assertTrue(registry.register(ID_3, DEADLINE, NOW).isEmpty());
      assertTrue(registry.cancel(ID_2));
    }
  }

  @Test
  void callerCompletedOrCancelledViewsNeverChangeTheOwnedPromiseAndNullIsRejected() {
    assertThrows(NullPointerException.class, () -> new PendingReply(null, DEADLINE));
    assertThrows(NullPointerException.class, () -> new PendingReply(ID_1, null));
    var registry = new ReplyCorrelationRegistry(1);
    PendingReply pending = registry.register(ID_1, DEADLINE, NOW).orElseThrow();
    var callerCompleted = pending.completion().toCompletableFuture();
    var callerCancelled = pending.completion().toCompletableFuture();
    assertTrue(callerCompleted.complete(new byte[] {9}));
    assertTrue(callerCancelled.cancel(false));
    var genuine = pending.completion().toCompletableFuture();
    assertFalse(genuine.isDone());
    assertEquals(1, registry.pendingCount());
    assertTrue(registry.complete(ID_1, new byte[] {4, 5, 6}, NOW.plusSeconds(1)));
    assertTrue(genuine.isDone());
    assertArrayEquals(new byte[] {4, 5, 6}, genuine.join());
    assertArrayEquals(new byte[] {9}, callerCompleted.join());
    assertTrue(callerCancelled.isCancelled());
    var independent = pending.completion().toCompletableFuture();
    assertTrue(independent.isDone());
    assertArrayEquals(new byte[] {4, 5, 6}, independent.join());
    assertEquals(0, registry.pendingCount());
    assertEquals(0L, registry.lateResponseCount());
  }
  // CORRELATION006007-END

"""
needle='  private static void assertExceptional(';assert s.count(needle)==1;s=s.replace(needle,addition+needle,1);inverse=s.replace(addition,'',1).replace(endNew,end,1).replace(startNew,start,1);assert inverse==old
cmd=[str(R.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(R.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'-']
def fmt(text):
 v=subprocess.run(cmd,input=text.encode(),capture_output=True,timeout=30);assert v.returncode==0;return v.stdout
fixed=fmt(s);assert fmt(fixed.decode())==fixed and fmt(inverse)==fmt(old);O.mkdir();(O/'addition.java.txt').write_text(addition.rstrip()+'\n');p.write_bytes(fixed);m=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),beforeManifestSha256=sha(before/'manifest.json'),testPath=plan['testPath'],oldTestSha256=plan['testSha256'],testSha256=sha(p),oldFiveExactInverseBeforeFormatting=True,oldFiveCanonicalInverseExact=True,formatIdempotent=True,newJUnitDefinitions=2,expectedWholeCases=7,terminalPermutations=6,terminalActionObservations=18,newConstructorNullInputs=2,callerViewIsolationChecks=3,finiteFinallyOwners=1,ownerJoinDeadlineSeconds=5,oldConcurrent100AssertionsPreserved=True,MainChanged=False,productTestsExecuted=0,files={q.name:sha(q) for q in O.iterdir()},toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,old5InverseExact=True,newDefinitions=2,expectedTests=7,manifestSha256=sha(O/'manifest.json'))))
