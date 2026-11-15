"""Four independent terminal-result data contracts, without repository or reflective fixtures."""
from pathlib import Path
import hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();main='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/BatchStepResult.java';assert (r/main).read_bytes()==subprocess.check_output(['git','show','HEAD:'+main]);test='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/BatchStepResultContractTest.java';p=r/test;assert not p.exists();p.write_text('''package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.repository.BatchStepResult.Reason;
import dev.codex.schubert.nk.batch.repository.BatchStepResult.Status;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** PT-BAT-RESULT001..004; SS331/341/451: terminal data only, never command/DB/owner proof. */
final class BatchStepResultContractTest {
  private static final String[] STATUSES = {"SUCCESS", "WARNING", "FAILED", "SKIPPED"};
  private static final String[] REASONS = {"NONE", "ALREADY_SUCCESSFUL", "BACKUP_UNAVAILABLE", "PROTECTED_RECORDS", "ABANDONED", "DATABASE_FAILURE", "COMMAND_FAILURE", "SAFETY_FAILURE", "IO_FAILURE", "TIMEOUT", "INTERRUPTED"};
  private static final String UNKNOWN = "PUBLIC_UNKNOWN";

  @Test
  void result001ExplicitFortyFourCellMatrixAndElevenDiagnosticsAreExact() {
    boolean[][] accepted = {
      {true, false, false, false}, {false, false, false, true}, {false, false, false, true},
      {false, true, false, false}, {false, false, true, false},
      {false, true, true, false}, {false, true, true, false}, {false, true, true, false},
      {false, true, true, false}, {false, true, true, false}, {false, true, true, false}
    };
    String[] summaries = {null, "step already successful for business date", "verified backup unavailable", "protected records retained", "previous same-run attempt abandoned", "batch database operation failed", "batch command failed", "batch safety check failed", "batch file operation failed", "batch step deadline reached", "batch step interrupted"};
    int acceptedCount = 0;
    int rejectedCount = 0;
    for (int row = 0; row < REASONS.length; row++) {
      Reason reason = Reason.valueOf(REASONS[row]);
      assertEquals(row == 0 ? null : REASONS[row], reason.code());
      assertEquals(summaries[row], reason.summary());
      for (int col = 0; col < STATUSES.length; col++) {
        Status status = Status.valueOf(STATUSES[col]);
        if (accepted[row][col]) {
          var actual = new BatchStepResult(status, 0, 0, 0, 0, reason);
          assertSame(status, actual.status()); assertSame(reason, actual.reason());
          assertEquals(0, actual.target()); assertEquals(0, actual.success());
          assertEquals(0, actual.failure()); assertEquals(0, actual.bytes());
          acceptedCount++;
        } else {
          assertThrows(IllegalArgumentException.class, () -> new BatchStepResult(status, 0, 0, 0, 0, reason));
          rejectedCount++;
        }
      }
    }
    assertEquals(17, acceptedCount); assertEquals(27, rejectedCount);
  }

  @Test
  void result002CounterBoundsDoNotInventSumOrNormalizeSkippedOrFailedCounts() {
    for (int index = 0; index < 4; index++) {
      for (long invalid : List.of(-1L, Long.MIN_VALUE)) {
        long[] counts = {0, 0, 0, 0}; counts[index] = invalid;
        assertThrows(IllegalArgumentException.class, () -> new BatchStepResult(Status.WARNING, counts[0], counts[1], counts[2], counts[3], Reason.IO_FAILURE));
      }
      long[] counts = {0, 0, 0, 0}; counts[index] = 1;
      assertThrows(IllegalArgumentException.class, () -> new BatchStepResult(Status.SKIPPED, counts[0], counts[1], counts[2], counts[3], Reason.BACKUP_UNAVAILABLE));
    }
    assertThrows(IllegalArgumentException.class, () -> new BatchStepResult(Status.SUCCESS, 1, 1, 1, 0, Reason.NONE));
    var max = new BatchStepResult(Status.FAILED, Long.MAX_VALUE, Long.MAX_VALUE, Long.MAX_VALUE, Long.MAX_VALUE, Reason.TIMEOUT);
    assertEquals(Long.MAX_VALUE, max.target()); assertEquals(Long.MAX_VALUE, max.success());
    assertEquals(Long.MAX_VALUE, max.failure()); assertEquals(Long.MAX_VALUE, max.bytes());
    // These observations are independent counters; SS331 has no target=success+failure invariant.
    var independent = new BatchStepResult(Status.SUCCESS, 1, 2, 0, Long.MAX_VALUE, Reason.NONE);
    assertEquals(1, independent.target()); assertEquals(2, independent.success());
    assertEquals(0, independent.failure()); assertEquals(Long.MAX_VALUE, independent.bytes());
  }

  @Test
  void result003ClosedEnumsLookupAndDefensiveArraysKeepExactSymbols() {
    assertArrayEquals(STATUSES, Arrays.stream(Status.values()).map(Enum::name).toArray(String[]::new));
    assertArrayEquals(REASONS, Arrays.stream(Reason.values()).map(Enum::name).toArray(String[]::new));
    for (String status : STATUSES) assertEquals(status, Status.valueOf(status).name());
    for (String reason : REASONS) assertEquals(reason, Reason.valueOf(reason).name());
    var statuses = Status.values(); statuses[0] = Status.SKIPPED;
    var reasons = Reason.values(); reasons[0] = Reason.INTERRUPTED;
    assertSame(Status.SUCCESS, Status.values()[0]); assertSame(Reason.NONE, Reason.values()[0]);
    for (String unknown : List.of("", "success", UNKNOWN)) assertThrows(IllegalArgumentException.class, () -> Status.valueOf(unknown));
    for (String unknown : List.of("", "none", UNKNOWN)) assertThrows(IllegalArgumentException.class, () -> Reason.valueOf(unknown));
    assertThrows(NullPointerException.class, () -> Status.valueOf(null));
    assertThrows(NullPointerException.class, () -> Reason.valueOf(null));
  }

  @Test
  void result004AllSixValueComponentsHashLookupNullsAndDiagnosticAreExact() {
    var actual = new BatchStepResult(Status.WARNING, 5, 2, 1, 3, Reason.DATABASE_FAILURE);
    var equal = new BatchStepResult(Status.WARNING, 5, 2, 1, 3, Reason.DATABASE_FAILURE);
    assertEquals(actual, actual); assertEquals(actual, equal); assertEquals(equal, actual);
    assertEquals(actual.hashCode(), equal.hashCode()); assertEquals("found", Map.of(actual, "found").get(equal));
    assertSame(Status.WARNING, actual.status()); assertEquals(5, actual.target()); assertEquals(2, actual.success());
    assertEquals(1, actual.failure()); assertEquals(3, actual.bytes()); assertSame(Reason.DATABASE_FAILURE, actual.reason());
    for (var other : List.of(new BatchStepResult(Status.FAILED, 5, 2, 1, 3, Reason.DATABASE_FAILURE),
        new BatchStepResult(Status.WARNING, 6, 2, 1, 3, Reason.DATABASE_FAILURE),
        new BatchStepResult(Status.WARNING, 5, 3, 1, 3, Reason.DATABASE_FAILURE),
        new BatchStepResult(Status.WARNING, 5, 2, 2, 3, Reason.DATABASE_FAILURE),
        new BatchStepResult(Status.WARNING, 5, 2, 1, 4, Reason.DATABASE_FAILURE),
        new BatchStepResult(Status.WARNING, 5, 2, 1, 3, Reason.COMMAND_FAILURE))) {
      assertNotEquals(actual, other); assertNotEquals(other, actual);
    }
    assertNotEquals(actual, null); assertNotEquals(actual, UNKNOWN);
    assertEquals("BatchStepResult[observation=<redacted>]", actual.toString());
    assertThrows(NullPointerException.class, () -> new BatchStepResult(null, 0, 0, 0, 0, Reason.NONE));
    assertThrows(NullPointerException.class, () -> new BatchStepResult(Status.SUCCESS, 0, 0, 0, 0, null));
  }
}
''');subprocess.run([str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(p)],check=True,timeout=30);assert (r/main).read_bytes()==subprocess.check_output(['git','show','HEAD:'+main]);o=b/'evidence/PG35130-batch-result4-source-v1';o.mkdir();v=dict(actualExit=0,mainSources=[main],testSources=[dict(path=test,tests=4)],inputHashes={n:sha(r/n) for n in [main,test]},sdkHashes={},mainSourcesUnchanged=True,newDefinitions=4,necessaryPriorDefinitions=0,expectedTests=4,expectedMatrixCells=44,expectedAcceptedCells=17,expectedRejectedCells=27,targets=['dev/codex/schubert/nk/batch/repository/BatchStepResult'+s for s in ['', '$Status', '$Reason']],independentFixedLiteralMatrixAndDiagnostics=True,noRepositoryReflectionOrHeldFixtureExtraction=True,applicationTestsExecuted=0,newAcceptance=0);(o/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,main=1,tests=4,matrixCells=44,accepted=17,rejected=27)))
