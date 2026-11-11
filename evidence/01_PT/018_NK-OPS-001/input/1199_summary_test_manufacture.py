"""Bounded Test-only owner correction and independent negative/value oracles; no product execution."""
from pathlib import Path
import hashlib,json,datetime,re
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';p=R/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/InspectionSummaryPortTest.java';before=B/'evidence/PG26334-summary-worker-owner-before-v1/original-whole-test.java.txt';original=before.read_text();assert p.read_text()==original;out=B/'evidence/PG26336-summary-test-manufacture-v1';assert not out.exists()
s=original.replace('import java.time.ZoneOffset;','import java.time.OffsetDateTime;',1).replace('Instant.parse("2026-11-05T00:00:00.123456Z").atOffset(ZoneOffset.UTC)','OffsetDateTime.parse("2026-11-05T00:00:00.123456Z")',1);assert 'ZoneOffset' not in s;s=s.replace('for (int type = 0; type < 3; type++)','for (int type = 0; type < 5; type++)',1);s=s.replace('    try (var worker = Executors.newSingleThreadExecutor()) {','    var worker = Executors.newSingleThreadExecutor();\n    try {',1);closing='''    }
    assertEquals(parentFlag, Thread.currentThread().isInterrupted());''';fixed='''    } finally {
      worker.shutdownNow();
      assertTrue(worker.awaitTermination(5, TimeUnit.SECONDS));
    }
    assertEquals(parentFlag, Thread.currentThread().isInterrupted());''';assert closing in s;s=s.replace(closing,fixed,1)
s=s.replace('      case 2 -> new AssertionError("private fatal");','      case 2 -> new AssertionError("private fatal");\n      case 3 -> new IllegalArgumentException("private provider argument");\n      case 4 -> new NullPointerException("private provider null");',1)
block='''  // INSPPORT009-BEGIN: source-independent DTO contract, no DB fixture lifecycle.
  @Test
  void summaryValueNullsAndLiteralGettersAreIndependentOfTheDatabaseFixture() {
    assertThrows(
        NullPointerException.class,
        () -> new InspectionSummary(null, new CleanupCounts(0, 0, 0), false));
    assertThrows(NullPointerException.class, () -> new InspectionSummary(RUN, null, false));
    for (boolean complete : List.of(false, true)) {
      var actual = new InspectionSummary(RUN, new CleanupCounts(3, 2, 1), complete);
      assertEquals(new UUID(0, 1), actual.run().id());
      assertEquals(Instant.parse("2026-11-05T00:00:00.123456Z"), actual.run().cutoff());
      assertEquals(3, actual.counts().target());
      assertEquals(2, actual.counts().deleted());
      assertEquals(1, actual.counts().skipped());
      assertEquals(complete, actual.complete());
      assertEquals("InspectionSummary[observation=<redacted>]", actual.toString());
    }
  }
  // INSPPORT009-END

''';marker='  private static Map<String, Object> literal() {';assert marker in s;s=s.replace(marker,block+marker,1);assert s.count('@Test')==9
# Invert only the described substitutions, including literal expected UTC equivalence; old assertions exact.
inverse=s.replace(block,'',1).replace('import java.time.OffsetDateTime;','import java.time.ZoneOffset;',1).replace('OffsetDateTime.parse("2026-11-05T00:00:00.123456Z")','Instant.parse("2026-11-05T00:00:00.123456Z").atOffset(ZoneOffset.UTC)',1).replace('for (int type = 0; type < 5; type++)','for (int type = 0; type < 3; type++)',1).replace('    var worker = Executors.newSingleThreadExecutor();\n    try {','    try (var worker = Executors.newSingleThreadExecutor()) {',1).replace(fixed,closing,1).replace('      case 3 -> new IllegalArgumentException("private provider argument");\n      case 4 -> new NullPointerException("private provider null");\n','',1);assert inverse==original
p.write_text(s);out.mkdir();v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),originalTestSha256=hashlib.sha256(original.encode()).hexdigest(),newTestSha256=hashlib.sha256(s.encode()).hexdigest(),old8BodiesAndAssertionsInverseExact=True,independentUtcExpected='OffsetDateTime.parse fixed +00 UTC literal replaces Java Instant.atOffset conversion; exact original expected value preserved',newIaENpeFaultObservations=32,oldThreeType48ObservationsPreserved=True,oldPriority18CellsUnchanged=True,newDtoTestDefinition=1,newDtoNullCases=2,finiteOwnerFinallyShutdownNowAndAwaitSeconds=5,productTestsExecuted=0,MainSourceChanged=False,bug='BUG-2653',ykt='YKT-2333',toolSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest());(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,newTestDefinitions=1,wholeTestMethods=9,additionalProviderInputs=32,old8InverseExact=True,productTestsExecuted=0)))
