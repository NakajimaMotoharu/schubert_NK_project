package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.repository.BackupFailureSnapshot;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.BatchStep;
import dev.codex.schubert.nk.batch.repository.BatchStepAttempt;
import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/**
 * SS343/SSC124; PT-CORR-CFREQ-001..002. Public memory values; no DB, files, recovery or receipt.
 */
final class FailedProfileBoundaryTest {
  private static final String GOLDEN =
      """
      NKCLEANFAIL1
      run=11111111-2222-4333-8444-555555555555
      activation=21111111-2222-4333-8444-555555555555
      cutoff=2026-09-27T15:00:00Z
      boot=31111111-2222-4333-8444-555555555555
      epoch=41111111-2222-4333-8444-555555555555
      backup_invocation=51111111-2222-4333-8444-555555555555
      backup_started_monotonic=1000000000
      backup_ended_monotonic=2000000000
      backup_exit=30
      database=7,4,2026-09-28,2026-09-30T01:02:03.123456Z,2026-09-30T01:02:05.654321Z,FAILED,1,0,1,0,COMMAND_FAILURE,batch command failed
      configuration=8,4,2026-09-28,2026-09-30T01:02:03.123456Z,2026-09-30T01:02:05.654321Z,FAILED,1,0,1,0,COMMAND_FAILURE,batch command failed
      """;

  @Test
  void failedBoundary001DelAndSameRowCountTailRejectAndEraseOwnedBytes() {
    for (String literal : List.of("\u007f", GOLDEN + "X")) {
      byte[] owned = literal.getBytes(StandardCharsets.US_ASCII);
      var failure =
          assertThrows(
              IllegalArgumentException.class, () -> CleanupFailedBackupRequest.consume(owned));
      assertEquals("failed cleanup profile invalid", failure.getMessage());
      assertNull(failure.getCause());
      assertArrayEquals(new byte[owned.length], owned);
    }
  }

  @Test
  void failedBoundary002InternallyValidPairFromDifferentRunCannotMatchOuterClaim() {
    Instant cutoff = Instant.parse("2026-09-27T15:00:00Z");
    Instant started = Instant.parse("2026-09-30T01:02:03.123456Z");
    Instant ended = Instant.parse("2026-09-30T01:02:05.654321Z");
    var otherRun = new BatchRun(UUID.fromString("61111111-2222-4333-8444-555555555555"), cutoff);
    var database = new BatchStepAttempt(7, otherRun, BatchStep.BACKUP_DB, 4, started, false);
    var configuration =
        new BatchStepAttempt(8, otherRun, BatchStep.BACKUP_CONFIG, 4, started, false);
    var pair = new BackupFailureSnapshot(database, configuration, ended);
    assertSame(database, pair.database());
    assertSame(configuration, pair.configuration());
    var failure =
        assertThrows(
            IllegalArgumentException.class,
            () ->
                new CleanupFailedBackupRequest(
                    UUID.fromString("11111111-2222-4333-8444-555555555555"),
                    UUID.fromString("21111111-2222-4333-8444-555555555555"),
                    cutoff,
                    UUID.fromString("31111111-2222-4333-8444-555555555555"),
                    UUID.fromString("41111111-2222-4333-8444-555555555555"),
                    UUID.fromString("51111111-2222-4333-8444-555555555555"),
                    new BigInteger("1000000000"),
                    new BigInteger("2000000000"),
                    30,
                    pair));
    assertEquals("failed cleanup profile invalid", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
