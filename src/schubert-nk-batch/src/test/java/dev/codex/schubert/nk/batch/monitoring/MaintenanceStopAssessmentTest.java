package dev.codex.schubert.nk.batch.monitoring;

import static dev.codex.schubert.nk.batch.monitoring.MaintenanceStopAssessment.Result.CONFIRMED;
import static dev.codex.schubert.nk.batch.monitoring.MaintenanceStopAssessment.Result.FAILED;
import static dev.codex.schubert.nk.batch.monitoring.MaintenanceStopAssessment.Result.TIMED_OUT;
import static dev.codex.schubert.nk.batch.monitoring.MaintenanceStopAssessment.Result.UNVERIFIED;
import static dev.codex.schubert.nk.batch.monitoring.MaintenanceStopAssessment.Stage.API;
import static dev.codex.schubert.nk.batch.monitoring.MaintenanceStopAssessment.Stage.ARTEMIS;
import static dev.codex.schubert.nk.batch.monitoring.MaintenanceStopAssessment.Stage.CADDY;
import static dev.codex.schubert.nk.batch.monitoring.MaintenanceStopAssessment.Stage.POSTGRESQL;
import static dev.codex.schubert.nk.batch.monitoring.MaintenanceStopAssessment.Stage.WEB;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.MaintenanceStopAssessment.Result;
import dev.codex.schubert.nk.batch.monitoring.MaintenanceStopAssessment.StopReceipt;
import java.time.Duration;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.UUID;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

final class MaintenanceStopAssessmentTest {
  private static final UUID RUN = UUID.fromString("73235846-200a-40ea-b179-763e7620b5ce");
  private static final UUID OLD_RUN = UUID.fromString("087d59a9-1070-44fe-a0fa-3302d360c5f2");
  private static final List<StopReceipt> COMPLETE =
      List.of(
          new StopReceipt(RUN, CADDY, CONFIRMED, Duration.ZERO),
          new StopReceipt(RUN, WEB, CONFIRMED, Duration.ofSeconds(30)),
          new StopReceipt(RUN, API, CONFIRMED, Duration.ofSeconds(60)),
          new StopReceipt(RUN, ARTEMIS, CONFIRMED, Duration.ofSeconds(7)),
          new StopReceipt(RUN, POSTGRESQL, CONFIRMED, Duration.ofSeconds(8)));

  @Test
  void s01TheApprovedSequenceAcceptsBothExactGraceBoundaries() {
    assertTrue(MaintenanceStopAssessment.hasConfirmedStops(RUN, COMPLETE));
    var faster = new StopReceipt(RUN, WEB, CONFIRMED, Duration.ofMillis(29_999));
    assertTrue(MaintenanceStopAssessment.hasConfirmedStops(RUN, replacing(1, faster)));
  }

  @Test
  void s02ReorderedMissingExtraAndRepeatedStagesAreRejected() {
    var reversed = new ArrayList<>(COMPLETE);
    Collections.swap(reversed, 1, 2);
    assertFalse(MaintenanceStopAssessment.hasConfirmedStops(RUN, reversed));
    assertFalse(MaintenanceStopAssessment.hasConfirmedStops(RUN, COMPLETE.subList(0, 4)));
    var extra = new ArrayList<>(COMPLETE);
    extra.add(COMPLETE.getFirst());
    assertFalse(MaintenanceStopAssessment.hasConfirmedStops(RUN, extra));
    assertFalse(
        MaintenanceStopAssessment.hasConfirmedStops(RUN, replacing(4, COMPLETE.getFirst())));
  }

  @Test
  void s03OneNanosecondAboveEitherGraceAndInvalidElapsedAreRejected() {
    var webLate = new StopReceipt(RUN, WEB, CONFIRMED, Duration.ofSeconds(30, 1));
    var apiLate = new StopReceipt(RUN, API, CONFIRMED, Duration.ofSeconds(60, 1));
    var negative = new StopReceipt(RUN, CADDY, CONFIRMED, Duration.ofNanos(-1));
    var missing = new StopReceipt(RUN, ARTEMIS, CONFIRMED, null);
    assertFalse(MaintenanceStopAssessment.hasConfirmedStops(RUN, replacing(1, webLate)));
    assertFalse(MaintenanceStopAssessment.hasConfirmedStops(RUN, replacing(2, apiLate)));
    assertFalse(MaintenanceStopAssessment.hasConfirmedStops(RUN, replacing(0, negative)));
    assertFalse(MaintenanceStopAssessment.hasConfirmedStops(RUN, replacing(3, missing)));
  }

  @Test
  void s04AnyNonconfirmedStageBlocksTheUpdateCondition() {
    for (int i = 0; i < COMPLETE.size(); i++) {
      StopReceipt approved = COMPLETE.get(i);
      for (Result badResult : List.of(FAILED, TIMED_OUT, UNVERIFIED)) {
        var invalid = new StopReceipt(RUN, approved.stage(), badResult, approved.elapsed());
        assertFalse(MaintenanceStopAssessment.hasConfirmedStops(RUN, replacing(i, invalid)));
      }
    }
  }

  @Test
  void s05StaleAndMissingReceiptsNeverAuthorizeAContinuation() {
    var old = new StopReceipt(OLD_RUN, WEB, CONFIRMED, Duration.ofSeconds(30));
    var noStage = new StopReceipt(RUN, null, CONFIRMED, Duration.ofSeconds(30));
    var noResult = new StopReceipt(RUN, WEB, null, Duration.ofSeconds(30));
    assertFalse(MaintenanceStopAssessment.hasConfirmedStops(RUN, replacing(1, old)));
    assertFalse(MaintenanceStopAssessment.hasConfirmedStops(RUN, replacing(1, noStage)));
    assertFalse(MaintenanceStopAssessment.hasConfirmedStops(RUN, replacing(1, noResult)));
    assertFalse(MaintenanceStopAssessment.hasConfirmedStops(RUN, replacing(1, null)));
    assertFalse(MaintenanceStopAssessment.hasConfirmedStops(null, COMPLETE));
    assertFalse(MaintenanceStopAssessment.hasConfirmedStops(RUN, null));
  }

  private static List<@Nullable StopReceipt> replacing(int index, @Nullable StopReceipt value) {
    List<@Nullable StopReceipt> modified = new ArrayList<>(COMPLETE);
    modified.set(index, value);
    return modified;
  }
}
