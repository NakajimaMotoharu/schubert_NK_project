"""Finite two admitted Test owners and independent observable provider-failure release oracle."""
from pathlib import Path
import hashlib,json,subprocess,re
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG27164-question-finite2-oracle-manufacture-v1';assert not O.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/question/';receipt=R/(base+'QuestionReceiptIdTest.java');port=R/(base+'QuestionSubmitRequestPortTest.java')
rold=receipt.read_text();pold=port.read_text();assert rold==subprocess.check_output(['git','show','1cc6a646035dd5e8aa246ee41c87ab2a74a7c145:'+str(receipt.relative_to(R))],text=True);assert pold==subprocess.check_output(['git','show','1cc6a646035dd5e8aa246ee41c87ab2a74a7c145:'+str(port.relative_to(R))],text=True)
ra='    try (var executor = Executors.newFixedThreadPool(8)) {';rz='    var executor = Executors.newFixedThreadPool(8);\n    try {';ea='    }\n    assertEquals(expected, actual);';ez='    } finally {\n      executor.shutdownNow();\n      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));\n    }\n    assertEquals(expected, actual);'
assert rold.count(ra)==rold.count(ea)==1;rs=rold.replace(ra,rz).replace(ea,ez)
pa='    try (var workers = Executors.newFixedThreadPool(2)) {';pz='    var workers = Executors.newFixedThreadPool(2);\n    try {';fa='    } finally {\n      request.close();\n    }';fz='    } finally {\n      workers.shutdownNow();\n      try {\n        assertEquals(true, workers.awaitTermination(10, TimeUnit.SECONDS));\n      } finally {\n        request.close();\n      }\n    }'
i=re.search(r'  void parallel\w+\(',pold).start();prefix=pold[:i];tail=pold[i:];assert tail.count(pa)==tail.count(fa)==1;ps=prefix+tail.replace(pa,pz).replace(fa,fz)
new='''
  @Test
  @DisplayName("PT-QST-RID009 provider failure releases private state to another worker")
  void providerFailureReleasesPrivateStateToAnotherWorker() throws Exception {
    for (boolean fatal : List.of(false, true)) {
      Throwable failure =
          fatal ? new AssertionError("public provider fixture")
              : new IllegalStateException("public provider fixture");
      var calls = new AtomicInteger();
      var generator =
          new QuestionReceiptIdGenerator(
              bound -> {
                assertEquals(32, bound);
                if (calls.getAndIncrement() == 0) {
                  if (failure instanceof Error error) throw error;
                  throw (RuntimeException) failure;
                }
                return 0;
              });
      assertSame(failure, assertThrows(failure.getClass(), generator::generate));
      var worker = Executors.newSingleThreadExecutor();
      try {
        assertEquals(
            "00000000000000000000000000",
            worker.submit(generator::generate).get(5, TimeUnit.SECONDS).value());
        assertEquals(27, calls.get());
      } finally {
        worker.shutdownNow();
        assertTrue(worker.awaitTermination(10, TimeUnit.SECONDS));
      }
    }
  }
'''
# Keep the original eight cases byte-identical after removing the new case and inverse pool edit.
i=rs.rfind('\n}');assert i>0;rs=rs[:i]+new+rs[i:]
assert rs.replace(new,'').replace(rz,ra).replace(ez,ea)==rold and ps.replace(pz,pa).replace(fz,fa)==pold
receipt.write_text(rs);port.write_text(ps);O.mkdir()
v=dict(actualExit=0,changes=[dict(path=str(receipt.relative_to(R)),beforeSha256=hashlib.sha256(rold.encode()).hexdigest(),afterSha256=sha(receipt),oldTests=8,newTests=9,originalInverseExact=True),dict(path=str(port.relative_to(R)),beforeSha256=hashlib.sha256(pold.encode()).hexdigest(),afterSha256=sha(port),oldTests=8,newTests=8,originalInverseExact=True)],newTestId='PT-QST-RID009',newDefinitions=1,oracle='RuntimeException and Error original identity, followed by independent literal26zero candidate in different owned worker, total27provider calls; observable lock-release not private reflection',originalFuture5And10AndLatch10AndTaskCountsUnchanged=True,originalWorkers=[8,2],newOracleWorker=1,terminationTimeoutSeconds=10,productTestsExecuted=0,MainChanged=False,BUG2698='TWO_SOURCE_FIXED_RUNTIME_PENDING_THIRD_KEYRING_OWNER_HELD_UNFIXED',YKT2372='OPEN',verifierSha256=sha(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,finiteOriginalOwners=2,newDefinitions=1,oldOraclesInverseExact=True,manifestSha256=sha(O/'manifest.json'))))
