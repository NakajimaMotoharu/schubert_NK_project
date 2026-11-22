package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;

import dev.codex.schubert.nk.batch.monitoring.MaintenanceRebootWatch.Marker;
import dev.codex.schubert.nk.batch.monitoring.MaintenanceStopAssessment.Result;
import dev.codex.schubert.nk.batch.monitoring.MaintenanceStopAssessment.Stage;
import dev.codex.schubert.nk.batch.monitoring.MaintenanceStopAssessment.StopReceipt;
import dev.codex.schubert.nk.batch.monitoring.MaintenanceUpdateAssessment.Observation;
import dev.codex.schubert.nk.batch.monitoring.MaintenanceUpdateAssessment.SafetyChecks;
import dev.codex.schubert.nk.batch.monitoring.MaintenanceUpdateAssessment.UpdateReceipt;
import dev.codex.schubert.nk.batch.monitoring.MaintenanceUpdateAssessment.UpdateResult;
import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-OPS-MAINT-VALUE001/002; UI251 §3 and SS341 §4.1/4.2; synthetic value observations. */
final class MaintenanceAssessmentRecordContractTest {
  private static final UUID RUN = new UUID(0L, 1L);
  private static final UUID BOOT = new UUID(0L, 2L);
  private static final UUID OTHER = new UUID(0L, 3L);
  private static final Instant OBSERVED_AT = Instant.parse("2026-09-20T12:00:00Z");
  private static final Duration ELAPSED = Duration.ofSeconds(5);
  private static final Observation SAFE = Observation.CONFIRMED_SAFE;
  private static final Observation UNSAFE = Observation.UNSAFE;

  @Test
  void value001RunBootTimeAndStopOutcomeParticipateInIdentity() {
    verifyValue(
        new Marker(RUN, BOOT, OBSERVED_AT),
        new Marker(RUN, BOOT, OBSERVED_AT),
        List.of(
            new Marker(OTHER, BOOT, OBSERVED_AT),
            new Marker(RUN, OTHER, OBSERVED_AT),
            new Marker(RUN, BOOT, OBSERVED_AT.plusSeconds(1))));

    verifyValue(
        new StopReceipt(RUN, Stage.WEB, Result.CONFIRMED, ELAPSED),
        new StopReceipt(RUN, Stage.WEB, Result.CONFIRMED, ELAPSED),
        List.of(
            new StopReceipt(OTHER, Stage.WEB, Result.CONFIRMED, ELAPSED),
            new StopReceipt(RUN, Stage.API, Result.CONFIRMED, ELAPSED),
            new StopReceipt(RUN, Stage.WEB, Result.TIMED_OUT, ELAPSED),
            new StopReceipt(RUN, Stage.WEB, Result.CONFIRMED, ELAPSED.plusSeconds(1))));
  }

  @Test
  void value002EachUpdateAndSafetyObservationParticipatesInIdentity() {
    var checks = new SafetyChecks(SAFE, SAFE, SAFE, SAFE, SAFE);
    var equal = new SafetyChecks(SAFE, SAFE, SAFE, SAFE, SAFE);
    var differentFilesystem = new SafetyChecks(SAFE, SAFE, UNSAFE, SAFE, SAFE);
    verifyValue(
        checks,
        equal,
        List.of(
            new SafetyChecks(UNSAFE, SAFE, SAFE, SAFE, SAFE),
            new SafetyChecks(SAFE, UNSAFE, SAFE, SAFE, SAFE),
            differentFilesystem,
            new SafetyChecks(SAFE, SAFE, SAFE, UNSAFE, SAFE),
            new SafetyChecks(SAFE, SAFE, SAFE, SAFE, UNSAFE)));

    verifyValue(
        new UpdateReceipt(RUN, OBSERVED_AT, UpdateResult.SUCCESS, checks),
        new UpdateReceipt(RUN, OBSERVED_AT, UpdateResult.SUCCESS, equal),
        List.of(
            new UpdateReceipt(OTHER, OBSERVED_AT, UpdateResult.SUCCESS, checks),
            new UpdateReceipt(RUN, OBSERVED_AT.plusSeconds(1), UpdateResult.SUCCESS, checks),
            new UpdateReceipt(RUN, OBSERVED_AT, UpdateResult.WARNING, checks),
            new UpdateReceipt(RUN, OBSERVED_AT, UpdateResult.SUCCESS, differentFilesystem)));
  }

  private static <T> void verifyValue(T value, T equal, List<T> differences) {
    assertEquals(value, equal);
    assertEquals(value.hashCode(), equal.hashCode());
    for (T different : differences) {
      assertNotEquals(value, different);
    }
  }
}
