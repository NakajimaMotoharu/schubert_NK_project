package dev.codex.schubert.nk.batch.monitoring;

import static dev.codex.schubert.nk.batch.monitoring.MaintenanceUpdateAssessment.Decision.CONDITIONS_MET;
import static dev.codex.schubert.nk.batch.monitoring.MaintenanceUpdateAssessment.Decision.CONDITIONS_MET_WITH_WARNING;
import static dev.codex.schubert.nk.batch.monitoring.MaintenanceUpdateAssessment.Decision.KEEP_PRIVATE;
import static dev.codex.schubert.nk.batch.monitoring.MaintenanceUpdateAssessment.Observation.CONFIRMED_SAFE;
import static dev.codex.schubert.nk.batch.monitoring.MaintenanceUpdateAssessment.Observation.UNSAFE;
import static dev.codex.schubert.nk.batch.monitoring.MaintenanceUpdateAssessment.Observation.UNVERIFIED;
import static dev.codex.schubert.nk.batch.monitoring.MaintenanceUpdateAssessment.UpdateResult.SUCCESS;
import static dev.codex.schubert.nk.batch.monitoring.MaintenanceUpdateAssessment.UpdateResult.WARNING;
import static org.junit.jupiter.api.Assertions.assertEquals;

import dev.codex.schubert.nk.batch.monitoring.MaintenanceStopAssessment.Result;
import dev.codex.schubert.nk.batch.monitoring.MaintenanceStopAssessment.Stage;
import dev.codex.schubert.nk.batch.monitoring.MaintenanceStopAssessment.StopReceipt;
import dev.codex.schubert.nk.batch.monitoring.MaintenanceUpdateAssessment.SafetyChecks;
import dev.codex.schubert.nk.batch.monitoring.MaintenanceUpdateAssessment.UpdateReceipt;
import dev.codex.schubert.nk.batch.monitoring.MaintenanceUpdateAssessment.UpdateResult;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;

final class MaintenanceUpdateAssessmentTest {
  private static final UUID RUN = new UUID(0, 1);
  private static final Instant STOPS_CONFIRMED = Instant.parse("2026-11-01T20:01:00Z");
  private static final SafetyChecks ALL_CONFIRMED =
      new SafetyChecks(
          CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE);
  private static final List<StopReceipt> STOPS =
      List.of(
          new StopReceipt(RUN, Stage.CADDY, Result.CONFIRMED, Duration.ofSeconds(1)),
          new StopReceipt(RUN, Stage.WEB, Result.CONFIRMED, Duration.ofSeconds(30)),
          new StopReceipt(RUN, Stage.API, Result.CONFIRMED, Duration.ofSeconds(60)),
          new StopReceipt(RUN, Stage.ARTEMIS, Result.CONFIRMED, Duration.ofSeconds(2)),
          new StopReceipt(RUN, Stage.POSTGRESQL, Result.CONFIRMED, Duration.ofSeconds(3)));

  @Test
  void u01SuccessfulUpdateMeetsAllFiveVerifiedConditions() {
    assertEquals(CONDITIONS_MET, MaintenanceUpdateAssessment.assess(SUCCESS, ALL_CONFIRMED));
  }

  @Test
  void u02UpdateWarningRemainsVisibleWithAllFiveConditionsVerified() {
    assertEquals(
        CONDITIONS_MET_WITH_WARNING, MaintenanceUpdateAssessment.assess(WARNING, ALL_CONFIRMED));
  }

  @Test
  void u03EachUnsafeConditionKeepsBothUpdateOutcomesPrivate() {
    List<SafetyChecks> unsafeChecks =
        List.of(
            new SafetyChecks(
                UNSAFE, CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE),
            new SafetyChecks(
                CONFIRMED_SAFE, UNSAFE, CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE),
            new SafetyChecks(
                CONFIRMED_SAFE, CONFIRMED_SAFE, UNSAFE, CONFIRMED_SAFE, CONFIRMED_SAFE),
            new SafetyChecks(
                CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE, UNSAFE, CONFIRMED_SAFE),
            new SafetyChecks(
                CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE, UNSAFE));
    for (SafetyChecks checks : unsafeChecks) {
      assertEquals(KEEP_PRIVATE, MaintenanceUpdateAssessment.assess(SUCCESS, checks));
      assertEquals(KEEP_PRIVATE, MaintenanceUpdateAssessment.assess(WARNING, checks));
    }
  }

  @Test
  void u04MissingUpdateOrCheckReceiptCannotMeetTheConditions() {
    assertEquals(KEEP_PRIVATE, MaintenanceUpdateAssessment.assess(null, ALL_CONFIRMED));
    assertEquals(
        KEEP_PRIVATE, MaintenanceUpdateAssessment.assess(UpdateResult.UNVERIFIED, ALL_CONFIRMED));
    assertEquals(KEEP_PRIVATE, MaintenanceUpdateAssessment.assess(SUCCESS, null));
  }

  @Test
  void u05EachUnverifiedObservationKeepsTheWarningPrivate() {
    List<SafetyChecks> unverifiedChecks =
        List.of(
            new SafetyChecks(
                UNVERIFIED, CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE),
            new SafetyChecks(
                CONFIRMED_SAFE, UNVERIFIED, CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE),
            new SafetyChecks(
                CONFIRMED_SAFE, CONFIRMED_SAFE, UNVERIFIED, CONFIRMED_SAFE, CONFIRMED_SAFE),
            new SafetyChecks(
                CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE, UNVERIFIED, CONFIRMED_SAFE),
            new SafetyChecks(
                CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE, CONFIRMED_SAFE, UNVERIFIED));
    for (SafetyChecks checks : unverifiedChecks) {
      assertEquals(KEEP_PRIVATE, MaintenanceUpdateAssessment.assess(WARNING, checks));
    }
  }

  @Test
  void u06NullObservationsRemainUnverifiedAndCannotRetainAnOldSuccess() {
    SafetyChecks absent = new SafetyChecks(null, null, null, null, null);
    assertEquals(UNVERIFIED, absent.packageManagerLock());
    assertEquals(UNVERIFIED, absent.packageConsistency());
    assertEquals(UNVERIFIED, absent.filesystem());
    assertEquals(UNVERIFIED, absent.bootPartition());
    assertEquals(UNVERIFIED, absent.kernelAndInitramfs());
    assertEquals(KEEP_PRIVATE, MaintenanceUpdateAssessment.assess(SUCCESS, absent));
  }

  @Test
  void u07OrderedStopAndUpdateEvidenceKeepsSuccessAndWarningDistinct() {
    assertEquals(
        CONDITIONS_MET,
        MaintenanceUpdateAssessment.assessAfterStops(
            RUN,
            STOPS,
            STOPS_CONFIRMED,
            new UpdateReceipt(RUN, STOPS_CONFIRMED.plusSeconds(1), SUCCESS, ALL_CONFIRMED)));
    assertEquals(
        CONDITIONS_MET_WITH_WARNING,
        MaintenanceUpdateAssessment.assessAfterStops(
            RUN,
            STOPS,
            STOPS_CONFIRMED,
            new UpdateReceipt(RUN, STOPS_CONFIRMED.plusNanos(1), WARNING, ALL_CONFIRMED)));
  }

  @Test
  void u08GoodUpdateCannotReplaceMissingFailedOrOutOfOrderStops() {
    var update = new UpdateReceipt(RUN, STOPS_CONFIRMED.plusSeconds(1), SUCCESS, ALL_CONFIRMED);
    var failed = new ArrayList<>(STOPS);
    failed.set(1, new StopReceipt(RUN, Stage.WEB, Result.FAILED, Duration.ofSeconds(2)));
    var outOfOrder = new ArrayList<>(STOPS);
    Collections.swap(outOfOrder, 1, 2);
    assertEquals(
        KEEP_PRIVATE,
        MaintenanceUpdateAssessment.assessAfterStops(RUN, null, STOPS_CONFIRMED, update));
    for (List<StopReceipt> stops : List.of(STOPS.subList(0, 4), failed, outOfOrder)) {
      assertEquals(
          KEEP_PRIVATE,
          MaintenanceUpdateAssessment.assessAfterStops(RUN, stops, STOPS_CONFIRMED, update));
    }
  }

  @Test
  void u09MissingOrStaleUpdateAndEarlierStartKeepTheSystemPrivate() {
    var update = new UpdateReceipt(RUN, STOPS_CONFIRMED.plusSeconds(1), SUCCESS, ALL_CONFIRMED);
    assertEquals(
        KEEP_PRIVATE, MaintenanceUpdateAssessment.assessAfterStops(RUN, STOPS, null, update));
    assertEquals(
        KEEP_PRIVATE,
        MaintenanceUpdateAssessment.assessAfterStops(RUN, STOPS, STOPS_CONFIRMED, null));
    for (UpdateReceipt invalid :
        List.of(
            new UpdateReceipt(new UUID(0, 2), STOPS_CONFIRMED, SUCCESS, ALL_CONFIRMED),
            new UpdateReceipt(null, STOPS_CONFIRMED, SUCCESS, ALL_CONFIRMED),
            new UpdateReceipt(RUN, null, SUCCESS, ALL_CONFIRMED),
            new UpdateReceipt(RUN, STOPS_CONFIRMED, SUCCESS, ALL_CONFIRMED),
            new UpdateReceipt(RUN, STOPS_CONFIRMED.minusNanos(1), SUCCESS, ALL_CONFIRMED))) {
      assertEquals(
          KEEP_PRIVATE,
          MaintenanceUpdateAssessment.assessAfterStops(RUN, STOPS, STOPS_CONFIRMED, invalid));
    }
    assertEquals(
        KEEP_PRIVATE,
        MaintenanceUpdateAssessment.assessAfterStops(null, STOPS, STOPS_CONFIRMED, update));
  }

  @Test
  void u10AValidStopNeverWaivesUnverifiedUpdateSafety() {
    var missingFilesystem =
        new SafetyChecks(CONFIRMED_SAFE, CONFIRMED_SAFE, null, CONFIRMED_SAFE, CONFIRMED_SAFE);
    for (UpdateReceipt invalid :
        List.of(
            new UpdateReceipt(RUN, STOPS_CONFIRMED.plusNanos(1), null, ALL_CONFIRMED),
            new UpdateReceipt(RUN, STOPS_CONFIRMED.plusNanos(1), WARNING, missingFilesystem))) {
      assertEquals(
          KEEP_PRIVATE,
          MaintenanceUpdateAssessment.assessAfterStops(RUN, STOPS, STOPS_CONFIRMED, invalid));
    }
  }
}
